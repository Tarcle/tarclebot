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

import mysql

token = 'NjExODgxNzkxMDc4NTMxMDkz.XV3gKw.nX_ZEFo08o5IIorxqAED77S677o'
prefix = '-'
embed_color = 0x880015
emoji_num = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣']
emoji_disk = ['💾']
emoji_page = ['⬅', '➡']

# 하루에 한번씩 랭킹정보 기록 (후원자 전용)
def rank_record():
    # 후원자 목록 가져오기
    supporters = mysql.select('supporters as a', 'a.*, b.rankid', '', 'JOIN quicks as b ON a.uid = b.uid')
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
# 봇 시작
class App(discord.Client):
    async def on_ready(self):
        print('다음으로 로그인합니다: {0}'.format(self.user))
        print('===============')
        # await self.change_presence(activity=discord.Game(name='{ch} 검색 [닉네임]'.format(ch=prefix), type=1))
        # 스케쥴 스레드 실행
        t1 = threading.Thread(target=run_schedule)
        t1.start()

    async def on_message(self, message):
        if message.author.bot:
            return None
        if message.content.startswith(prefix):
            msg = message.content.split(' ')
            command = msg[0][len(prefix):]
            if command in ['검색', '전적', 'search']:
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
                        content = '```cs\n'
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
                    def check_num(reaction, user): return user == message.author and str(reaction.emoji) in emoji_num
                    try:
                        res = await self.wait_for('reaction_add', timeout=30, check=check_num)
                    except asyncio.TimeoutError: #시간초과
                        await searchlist.edit(content="시간이 초과되었습니다. 다시 시도해주세요.")
                        await clear_reactions(searchlist)
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
                    await searchlist.edit(content="", embed=embed)
                else:
                    searchlist = await message.channel.send(embed=embed)
                await clear_reactions(searchlist)

                #이모지 추가
                await searchlist.add_reaction(emoji_disk[0])
                def check_save(reaction, user):
                    return user == message.author and str(reaction.emoji) in emoji_disk
                try:
                    res = await self.wait_for('reaction_add', timeout=30, check=check_save)
                except asyncio.TimeoutError: #시간초과
                    await clear_reactions(searchlist)
                    return False

                rankid = players[sel].select('.player>a')[0].get('href').strip()[3:]
                if saveProfile(message.author.id, rankid):
                    await clear_reactions(searchlist)
                    await message.channel.send('내정보 등록이 완료되었습니다.')
            elif command in ['랭킹', '순위', '탑텐', 'top10', 'rank']:
                async with message.channel.typing():
                    country = urllib.parse.quote(' '.join(msg[1:]))
                    if len(country)>0:
                        url = "https://scoresaber.com/global?country="+country
                    else:
                        url = "https://scoresaber.com/global"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    html = urllib.request.urlopen(req).read().decode('utf-8')
                    soup = BeautifulSoup(html, 'html.parser')

                    #랭킹목록 출력
                    players = soup.select('.ranking>.ranking>tbody>tr')
                if len(players) > 0:
                    content = '```cs\n'
                    for i in range(min(10, len(players))):
                        player = players[i].select('.player>a')[0]
                        rank = players[i].select('.rank')[0]
                        pp = players[i].select('.ppValue')[0]
                        content += '{} : {} ( {} )\n'.format(i+1, player.text.strip(), pp.text.strip())
                    content += '```'
                    searchlist = await message.channel.send(content)
                else:
                    return await message.channel.send('입력하신 국가코드는 존재하지 않습니다. 다시 확인해주세요.')

                #이모지 추가
                if sel < 0:
                    for e in emoji_num: await searchlist.add_reaction(e)
                    def check2(reaction, user): return user == message.author and str(reaction.emoji) in emoji_num
                    try:
                        res = await self.wait_for('reaction_add', timeout=30, check=check2)
                    except asyncio.TimeoutError: #시간초과
                        return False
                    else:
                        sel = emoji_num.index(res[0].emoji)
            elif command in ['내정보']:
                if len(msg) > 1 and msg[1] in ['등록']:
                    if len(msg) > 2:
                        reg = re.compile('^[0-9]{17}$')
                        if not reg.match(msg[2]):
                            return await message.channel.send("스코어세이버 id 형식에 맞지 않습니다. 닉네임이 아닌 url 숫자부분을 입력해야 합니다. 다시 확인해주세요.")
                        async with message.channel.typing():
                            uid = message.author.id
                            rankid = msg[2]
                            saveProfile(uid, rankid)

                        await message.channel.send('내정보 등록이 완료되었습니다.')
                else:
                    async with message.channel.typing():
                        rows = mysql.select('quicks', '*', 'uid='+str(message.author.id))

                        if len(rows) > 0:
                            href = 'https://scoresaber.com/u/'+rows[0]['rankid']
                            req = urllib.request.Request(href, headers={'User-Agent': 'Mozilla/5.0'})
                            html = urllib.request.urlopen(req).read().decode('utf-8')
                            soup = BeautifulSoup(html, 'html.parser')

                            embed = createProfile(soup, href)
                            embed2 = createProfile(soup, href)
                    if len(rows) > 0:
                        await message.channel.send(embed=embed)
                    else:
                        await message.channel.send('등록된 계정이 없습니다. [{}내정보 등록]을 먼저 실행해주세요.'.format(prefix))
            elif command in ['기록', '성장']:
                """ SELECT a.*, c.date, c.rankid, c.rank_global, c.rank_country, c.pp FROM supporters AS a
JOIN quicks AS b ON a.uid = b.uid
JOIN rank_records AS c ON b.rankid = c.rankid
ORDER BY a.idx, c.date """

            
            #나만
            elif message.author.id == 361018280569470986:
                if command in ['dm']:
                    dm = await message.author.create_dm()
                    await dm.send('test')
                elif command in ['v']:
                    if message.author.voice == None:
                        return await message.channel.send('먼저 음성 채널에 입장해주세요.')
                    voice = message.author.voice.channel
                    vc = await voice.connect()
                    vc.play()
                elif command in ['history']:
                    history = await message.channel.history(limit=10).flatten()
                    history.reverse()
                    tmp = ""
                    for h in history:
                        tmp += h.author.name + " : " + h.content + "\n"
                    await message.channel.send(tmp)

def clear_reactions(msg):
    if msg.guild:
        perms = msg.channel.permissions_for(msg.guild.me)
        if(perms.manage_messages):
            return msg.clear_reactions()
        else:
            for e in emoji_num: return msg.remove_reaction(e, bot.user)

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

def saveProfile(uid, rankid):
    if mysql.select('quicks', 'count(*) as count', 'uid='+str(uid))[0]['count'] > 0:
        mysql.update('quicks', 'uid='+str(uid), 'rankid='+rankid)
    else:
        mysql.insert('quicks', 'uid, rankid', (uid, rankid))
    return True

bot = App()
bot.run(token)