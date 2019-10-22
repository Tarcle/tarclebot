# NjExNzkxNjY5NTQ4ODEwMjYx.XVY-aQ.ybFurqgvEOz66djiibWhgk0E3Uw <-- 스코어세이버 Bot
# NjExODgxNzkxMDc4NTMxMDkz.XV3gKw.nX_ZEFo08o5IIorxqAED77S677o <-- Test Bot

import asyncio
import discord
import urllib
from bs4 import BeautifulSoup
import pymysql
import re
import schedule
import threading
import time
import math
from datetime import date, timedelta

import mysql

import youtube_dl

token = 'NjExNzkxNjY5NTQ4ODEwMjYx.XVY-aQ.ybFurqgvEOz66djiibWhgk0E3Uw'
prefix = '-'
embed_color = 0x880015
emoji_num = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣']
emoji_disk = ['💾']
emoji_page = ['⬅', '➡']

# 하루에 한번씩 랭킹정보 기록 (후원자 전용)
def rank_record():
    # 후원자 목록 가져오기
    supporters = mysql.select('supporters as a', 'a.*, b.rankid', 'JOIN quicks as b ON a.uid = b.uid')
    if len(supporters) > 0:
        for spt in supporters:
            rankid = spt['rankid']

            href = 'https://scoresaber.com/u/' + rankid
            req = urllib.request.Request(href, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            info = soup.select('.column>ul>li')
            if len(info[0].select('a')) == 0:
                del info[0]
            rank_global = "".join(re.findall('[0-9]+', info[0].select('a')[0].text))
            rank_country = "".join(re.findall('[0-9]+', info[0].select('a')[1].text))
            pp = re.findall('[0-9]+', info[1].text.split(':')[1])
            pp = "".join(pp[:-1]) + "." + pp[-1]
            mysql.insert('rank_records', ['rankid', 'rank_global', 'rank_country', 'pp'], [rankid, rank_global, rank_country, pp])

schedule.every().day.at("09:00").do(rank_record)
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)
# 스케쥴 스레드 실행
t1 = threading.Thread(target=run_schedule)
t1.start()

# 봇 시작
#페이징
total_page = 0
curr_page = 0
class App(discord.Client):
    async def on_ready(self):
        print('logged in: {0}'.format(self.user))
        print('===============')
        # await self.change_presence(activity=discord.Game(name='{ch} 검색 [닉네임]'.format(ch=prefix), type=1))

    async def on_message(self, message):
        if message.author.bot:
            return None
        if message.content.startswith(prefix):
            msg = message.content.split(' ')
            command = msg[0][len(prefix):]
            if command in ['후원자']:
                supporters = mysql.select('supporters', 'uid, name', 'WHERE uid!="361018280569470986" ORDER BY date')
                duple = []
                content = '```json\n'
                for supporter in supporters:
                    if supporter['uid'] in duple: continue
                    content += '%10s님 (ID : %s)\n' % (supporter['name'], supporter['uid'])
                    duple.append(supporter['uid'])
                content += '%13s감사합니다.```' % ''
                await message.channel.send(content)
            elif command in ['검색', 'search', '-s']:
                search = urllib.parse.quote(' '.join(msg[1:]))
                if len(search)==0:
                    return await message.channel.send('검색할 닉네임을 입력해주세요')

                async with message.channel.typing():
                    req = urllib.request.Request("https://scoresaber.com/global?search="+search, headers={'User-Agent': 'Mozilla/5.0'})
                    html = urllib.request.urlopen(req).read().decode('utf-8')
                    soup = BeautifulSoup(html, 'html.parser')

                    sel = -1
                    #검색목록 출력
                    players = soup.select('.ranking>.ranking>tbody>tr')
                if len(players) > 0:
                    if len(players) == 1:
                        sel = 0
                    else:
                        content = '```json\n'
                        for i in range(min(5, len(players))):
                            player = players[i].select('.player>a>.pp')[0]
                            rank = players[i].select('.rank')[0]
                            pp = players[i].select('.ppValue')[0]
                            content += '{} : {} ( {} ) - {}\n'.format(i+1, player.text.strip(), pp.text.strip(), rank.text.strip())
                        content += '```'
                        searchlist = await message.channel.send(content)
                else:
                    return await message.channel.send('검색한 닉네임이 존재하지 않습니다. 다시 확인해주세요.')

                #이모지 추가
                if sel < 0:
                    for e in emoji_num[:min(5, len(players))]: await searchlist.add_reaction(e)
                    try:
                        res = await self.wait_for('reaction_add', timeout=30,
                            check=(lambda reaction, user: reaction.message.id == searchlist.id and user == message.author and str(reaction.emoji) in emoji_num))
                    except asyncio.TimeoutError: #시간초과
                        await clearReaction(searchlist)
                        return False
                    else:
                        sel = emoji_num.index(res[0].emoji)

                #페이지 이동
                async with message.channel.typing():
                    href = 'https://scoresaber.com'+players[sel].select('.player>a')[0].get('href')
                    req = urllib.request.Request(href, headers={'User-Agent': 'Mozilla/5.0'})
                    html = urllib.request.urlopen(req).read().decode('utf-8')
                    soup = BeautifulSoup(html, 'html.parser')

                    embed = createProfile(soup, href)
                    embed.set_footer(text="내정보로 등록하시려면 💾을 눌러주세요.".format(prefix=prefix))
                if 'searchlist' in locals():
                    await clearReaction(searchlist)
                    await searchlist.edit(content="", embed=embed)
                else:
                    searchlist = await message.channel.send(embed=embed)

                #이모지 추가
                await searchlist.add_reaction(emoji_disk[0])
                try:
                    res = await self.wait_for('reaction_add', timeout=30,
                        check=(lambda reaction, user: reaction.message.id == searchlist.id and user == message.author and str(reaction.emoji) in emoji_disk))
                except asyncio.TimeoutError: #시간초과
                    await clearReaction(searchlist)
                    return False

                rankid = players[sel].select('.player>a')[0].get('href').strip()[3:]
                if saveProfile(message.author.id, rankid):
                    await clearReaction(searchlist)
                    await message.channel.send('내정보 등록이 완료되었습니다.')
            elif command in ['랭킹', '순위', '탑텐', 'rank', '-r']:
                async with message.channel.typing():
                    country = ''.join(msg[1:])
                    if len(country)>0:
                        url = "https://scoresaber.com/global?country="+urllib.parse.quote(country)
                    else:
                        url = "https://scoresaber.com/global"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    html = urllib.request.urlopen(req).read().decode('utf-8')
                    soup = BeautifulSoup(html, 'html.parser')

                #랭킹목록 출력
                players = soup.select('.ranking>.ranking>tbody>tr')
                if len(players) > 0:
                    embed = createRanklist(players, country)
                    searchlist = await message.channel.send(embed=embed)
                else:
                    return await message.channel.send('입력하신 국가코드는 존재하지 않습니다. 다시 확인해주세요.')

                if len(players) < 11: return False
                #페이징
                total_page = int(len(players) / 10)
                curr_page = 0
                #이모지 추가
                for e in emoji_page: await searchlist.add_reaction(e)
                while True:
                    try:
                        res = await self.wait_for('reaction_add', timeout=30,
                            check=(lambda reaction, user: reaction.message.id == searchlist.id and user == message.author and str(reaction.emoji) in emoji_page))
                    except asyncio.TimeoutError: #시간초과
                        await clearReaction(searchlist)
                        break
                    else:
                        sel = emoji_page.index(res[0].emoji)
                        if sel: curr_page += 1
                        else: curr_page -= 1
                        curr_page = (curr_page + total_page) % total_page
                        page_start = curr_page*10
                        embed = createRanklist(players, country, page_start)
                        if(getPerms(message).manage_messages):
                            await searchlist.remove_reaction(res[0].emoji, message.author)
                        await searchlist.edit(embed=embed)
            elif command in ['내정보', '-m']:
                if len(msg) > 1 and msg[1] in ['등록']:
                    if len(msg) > 2:
                        if re.match('^((https?:\\/\\/)?scoresaber\\.com\\/u\\/)?[0-9]{17}$', msg[2]):
                            async with message.channel.typing():
                                rankid = msg[2][-17:]
                                saveProfile(message.author.id, rankid)
                            await message.channel.send('내정보 등록이 완료되었습니다.')
                        else:
                            async with message.channel.typing():
                                search = ' '.join(msg[2:])
                                req = urllib.request.Request("https://scoresaber.com/global?search="+search, headers={'User-Agent': 'Mozilla/5.0'})
                                html = urllib.request.urlopen(req).read().decode('utf-8')
                                soup = BeautifulSoup(html, 'html.parser')

                                sel = -1
                                #검색목록 출력
                                players = soup.select('.ranking>.ranking>tbody>tr')
                            if len(players) > 0:
                                if len(players) == 1:
                                    sel = 0
                                else:
                                    content = '```json\n'
                                    for i in range(min(5, len(players))):
                                        player = players[i].select('.player>a>.pp')[0]
                                        rank = players[i].select('.rank')[0]
                                        pp = players[i].select('.ppValue')[0]
                                        content += '{} : {} ( {} ) - {}\n'.format(i+1, player.text.strip(), pp.text.strip(), rank.text.strip())
                                    content += '```'
                                    searchlist = await message.channel.send(content)
                            else:
                                return await message.channel.send('검색한 닉네임이 존재하지 않습니다. 다시 확인해주세요.')

                            #이모지 추가
                            if sel < 0:
                                for e in emoji_num[:min(5, len(players))]: await searchlist.add_reaction(e)
                                try:
                                    res = await self.wait_for('reaction_add', timeout=30,
                                        check=(lambda reaction, user: reaction.message.id == searchlist.id and user == message.author and str(reaction.emoji) in emoji_num))
                                except asyncio.TimeoutError: #시간초과
                                    await clearReaction(searchlist)
                                    return False
                                else:
                                    sel = emoji_num.index(res[0].emoji)
                            rankid = players[sel].select('.player>a')[0].get('href')[-17:]
                            saveProfile(message.author.id, rankid)
                            await message.channel.send('내정보 등록이 완료되었습니다.')
                    else:
                        return await message.channel.send('닉네임 또는 스코어세이버 URL을 입력해주세요.')
                else:
                    async with message.channel.typing():
                        rows = mysql.select('quicks', '*', 'where uid='+str(message.author.id))

                        if len(rows) > 0:
                            href = 'https://scoresaber.com/u/'+rows[0]['rankid']
                            req = urllib.request.Request(href, headers={'User-Agent': 'Mozilla/5.0'})
                            html = urllib.request.urlopen(req).read().decode('utf-8')
                            soup = BeautifulSoup(html, 'html.parser')

                            embed = createProfile(soup, href)
                    if len(rows) > 0:
                        await message.channel.send(embed=embed)
                    else:
                        await message.channel.send('등록된 계정이 없습니다. [{}내정보 등록]을 먼저 실행해주세요.'.format(prefix))
            elif command in ['전적', '기록', 'history', 'record', '-h']:
                async with message.channel.typing():
                    # SELECT a.date + INTERVAL 1 MONTH AS pricedate, b.rankid, price, c.date - INTERVAL 1 day AS date, c.rank_global, c.rank_country, c.pp FROM supporters AS a
                    # left JOIN quicks AS b ON a.uid = b.uid
                    # left JOIN rank_records AS c ON b.rankid = c.rankid
                    # WHERE a.uid='361018280569470986' AND (a.date + INTERVAL 1 MONTH >= c.date - INTERVAL 1 DAY OR a.admin = 0)
                    # ORDER BY a.idx, c.date DESC
                    count = mysql.select(
                        'supporters as a', 'count(*) as count',
                        ' LEFT JOIN quicks AS b ON a.uid = b.uid' +
                        ' LEFT JOIN rank_records AS c ON b.rankid = c.rankid' +
                        ' WHERE a.uid=' + str(message.author.id)
                    )[0]['count']
                if count == 0:
                    return await message.channel.send("```\n후원자를 위한 기능입니다.\n```")
                records = mysql.select(
                    'supporters as a', 'b.rankid, c.date - interval 1 day as date, c.rank_global, c.rank_country, c.pp',
                    ' LEFT JOIN quicks AS b ON a.uid = b.uid' +
                    ' LEFT JOIN rank_records AS c ON b.rankid = c.rankid' +
                    ' WHERE a.uid=' + str(message.author.id) +
                    ' order by a.idx, c.date desc LIMIT 10'
                )
                if not records[0]['rankid']:
                    return await message.channel.send("```\n내정보를 먼저 등록해주세요.\n```")
                if not records[0]['date']:
                    return await message.channel.send("```\n아직 데이터가 존재하지 않습니다.\n내일 다시 시도해주세요.```")
                
                href = 'https://scoresaber.com/u/'+records[0]['rankid']
                req = urllib.request.Request(href, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(req).read().decode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')

                info = soup.select('.column>ul>li')
                if len(info[0].select('a')) == 0:
                    del info[0]
                rank_global = "".join(re.findall('[0-9]+', info[0].select('a')[0].text))
                rank_country = "".join(re.findall('[0-9]+', info[0].select('a')[1].text))
                pp = re.findall('[0-9]+', info[1].text.split(':')[1])
                pp = "".join(pp[:-1]) + "." + pp[-1]

                now = {'date': date.today(), 'rank_global': int(rank_global), 'rank_country': int(rank_country), 'pp': float(pp)}
                records.insert(0, now)

                recordlist = await message.channel.send(createRecordlist(records))
                
                if count > 10:
                    #페이징
                    total_page = int(math.ceil((count+1) / 10))
                    curr_page = 0
                    #이모지 추가
                    for e in emoji_page: await recordlist.add_reaction(e)
                    while True:
                        try:
                            res = await self.wait_for('reaction_add', timeout=30,
                                check=(lambda reaction, user: reaction.message.id == recordlist.id and user == message.author and str(reaction.emoji) in emoji_page))
                        except asyncio.TimeoutError: #시간초과
                            await clearReaction(recordlist)
                            break
                        else:
                            sel = emoji_page.index(res[0].emoji)
                            if sel: curr_page += 1
                            else: curr_page -= 1
                            curr_page = (curr_page + total_page) % total_page
                            page_start = max(curr_page*10-1, 0)
                            
                            records = mysql.select(
                                'supporters as a', 'b.rankid, c.date - interval 1 day as date, c.rank_global, c.rank_country, c.pp',
                                ' LEFT JOIN quicks AS b ON a.uid = b.uid' +
                                ' LEFT JOIN rank_records AS c ON b.rankid = c.rankid' +
                                ' WHERE a.uid=' + str(message.author.id) +
                                ' order by a.idx, c.date desc LIMIT 11 OFFSET ' + str(page_start)
                            )
                            if curr_page == 0:
                                records.insert(0, now)
                            if(getPerms(message).manage_messages):
                                await recordlist.remove_reaction(res[0].emoji, message.author)
                            await recordlist.edit(content=createRecordlist(records))

            #나만
            elif message.author.id == 361018280569470986:
                if command in ['dm']:
                    dm = await message.author.create_dm()
                    await dm.send('test')
                elif command in ['접속']:
                    if message.author.voice == None:
                        return await message.channel.send('먼저 음성 채널에 입장해주세요.')
                    vc = message.guild.voice_client
                    if vc == None:
                        voice = message.author.voice.channel
                        vc = await voice.connect()
                    else:
                        vc = await vc.move_to(message.author.voice.channel)
                    ''
                elif command in ['퇴장']:
                    vc = message.guild.voice_client
                    if vc != None:
                        await vc.disconnect()
                elif command in ['채팅']:
                    history = await message.channel.history(limit=int(msg[1])).flatten()
                    history.reverse()
                    tmp = ""
                    for h in history:
                        tmp += h.author.name + " : " + h.content + "\n"
                    await message.channel.send(tmp)
                elif command in ['y']:
                    url = "https://www.youtube.com/watch?v=Eq3YJ1SrWns"
                    ydl = youtube_dl.YoutubeDL({})
                    ydl.extract_info(url, download=False)
                    ''

def getPerms(msg):
    if msg.guild:
        return msg.channel.permissions_for(msg.guild.me)
    else:
        return msg.channel.permissions_for(msg.channel.me)

def clearReaction(msg):
    if msg.guild:
        if(getPerms(msg).manage_messages):
            return msg.clear_reactions()

def saveProfile(uid, rankid):
    if mysql.select('quicks', 'count(*) as count', 'where uid="'+str(uid)+'"')[0]['count'] > 0:
        mysql.update('quicks', 'uid='+str(uid), 'rankid='+rankid)
    else:
        mysql.insert('quicks', ['uid', 'rankid'], (uid, rankid))
    return True

def createProfile(soup, href):
    avatar = soup.select('.avatar>img')[0].get('src')
    if avatar.startswith('/'):
        avatar = 'https://scoresaber.com' + avatar
    country = 'https://scoresaber.com'+soup.select('.title>img')[0].get('src')
    name = soup.select('.title')[0].text.strip()
    info = soup.select('.column>ul>li')
    if len(info[0].select('a')) == 0:
        del info[0]

    rank_global = info[0].select('a')[0].text.strip()
    rank_country = info[0].select('a')[1].text.strip()
    link_global = "https://scoresaber.com/global"
    link_country = link_global + "?country=" + info[0].select('a')[1].get('href')[-2:]
    columns = list()
    columns.append(info[1].text.split(':'))
    columns.append(info[2].text.split(':'))
    columns.append(info[3].text.split(':'))
    columns.append(info[4].text.split(':'))

    embed = discord.Embed(title="자세히 보려면 여기를 클릭하세요.", description="Player Ranking: [{}]({} '글로벌 랭킹') - ( [국내 {}]({} '국내 랭킹') )".format(rank_global, link_global, rank_country, link_country), url=href, color=embed_color)
    embed.set_thumbnail(url=avatar)
    embed.set_author(name=name, icon_url=country)
    for column in columns:
        embed.add_field(name=column[0].strip(), value=column[1].strip(), inline=False)
    return embed

def createRanklist(players, country, page_start=0):
    embed = discord.Embed(title="", description="", url="", color=embed_color)
    page_end = page_start + min(10, len(players)-curr_page*10)
    i = page_start
    content = "[자세히 보려면 여기를 클릭하세요.](https://scoresaber.com/global?country="+country+")\n\n"
    for player in players[page_start:page_end]:
        i += 1
        name = player.select('.player>a')[0].text.strip()
        player_country = player.select('.player>a>img')[0].get('src')[22:24].upper()
        href = 'https://scoresaber.com' + player.select('.player>a')[0].get('href')
        pp = player.select('.ppValue')[0].text.strip()
        weekly_change = player.select('.diff>span')[0].text.strip()
        content += "#{}: [{}] [{}]({}) ( {} ) [ {} ]\n".format(str(i).zfill(2), player_country, name, href, pp, weekly_change)
    if country=="": country = "글로벌"
    embed.add_field(name=country.upper() + " 랭킹", value=content, inline=False)

    return embed

def createRecordlist(records):
    text = '```json\n'
    i = 1
    for record in records[:min(len(records), 10)]:
        text += '날짜 : %s월 %s일 | 순위 : #%d(#%d) | pp : %7.2f' % (
            str(record['date'].month).zfill(2), str(record['date'].day).zfill(2), record['rank_global'], record['rank_country'], record['pp']
        )
        if record != records[-1]:
            text += ' [+%6.2f]' % (record['pp']-records[i]['pp'])
        text += '\n'
        i += 1
    text += '```'
    return text

bot = App()
bot.run(token)
