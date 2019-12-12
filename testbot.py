# NjExNzkxNjY5NTQ4ODEwMjYx.XVY-aQ.ybFurqgvEOz66djiibWhgk0E3Uw <-- 스코어세이버 Bot
# NjExODgxNzkxMDc4NTMxMDkz.XV3gKw.nX_ZEFo08o5IIorxqAED77S677o <-- Test Bot

import asyncio
import discord
import urllib
import json
import pymysql
import re
import schedule
import threading
import time
import math
from datetime import date, timedelta

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
    supporters = mysql.select('supporters as a', 'a.*, b.rankid', 'JOIN quicks as b ON a.uid = b.uid')
    if len(supporters) > 0:
        for spt in supporters:
            rankid = spt['rankid']

            href = 'http://saber.tarcle.kr/api/profile/' + rankid
            req = urllib.request.Request(href, headers={'api': 'beatsaber'})
            text = urllib.request.urlopen(req).read().decode('utf-8')
            player = json.loads(text)
            
            mysql.insert('rank_records', ['rankid', 'rank_global', 'rank_country', 'pp'], [rankid, player['rank_global'], player['rank_country'], player['pp']])

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
            
            elif command in ['검색', 'search', '-s', '-ㄴ']:
                search = urllib.parse.quote(' '.join(msg[1:]))
                if len(search)==0:
                    return await message.channel.send('검색할 닉네임을 입력해주세요')

                async with message.channel.typing():
                    req = urllib.request.Request("http://saber.tarcle.kr/api/search/"+search, headers={'api': 'beatsaber'})
                    text = urllib.request.urlopen(req).read().decode('utf-8')
                    players = json.loads(text)

                    sel = -1
                    #검색목록 출력
                if len(players) > 0:
                    if len(players) == 1:
                        sel = 0
                    else:
                        content = '```json\n'
                        for i in range(min(5, len(players))):
                            content += '{} : {} ( {} ) - {}\n'.format(i+1, players[i]['name'], players[i]['pp'], players[i]['rank'])
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

                # 페이지 이동
                async with message.channel.typing():
                    href = 'http://saber.tarcle.kr/api/profile/'+players[sel]['url']
                    req = urllib.request.Request(href, headers={'api': 'beatsaber'})
                    text = urllib.request.urlopen(req).read().decode('utf-8')
                    player = json.loads(text)

                    embed = createProfile(player, href)
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

                rankid = players[sel]['url']
                if saveProfile(message.author.id, rankid):
                    await clearReaction(searchlist)
                    await message.channel.send('내정보 등록이 완료되었습니다.')
            
            elif command in ['랭킹', '순위', '탑텐', 'rank', '-r', '-ㄱ']:
                async with message.channel.typing():
                    country = ''.join(msg[1:])
                    if len(country)>0:
                        url = "http://saber.tarcle.kr/api/rank/"+urllib.parse.quote(country)
                    else:
                        url = "http://saber.tarcle.kr/api/rank"
                    req = urllib.request.Request(url, headers={'api': 'beatsaber'})
                    text = urllib.request.urlopen(req).read().decode('utf-8')
                    players = json.loads(text)

                #랭킹목록 출력
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
                        res = re.match('^((https?:\\/\\/)?scoresaber\\.com\\/u\\/)?[0-9]+$', msg[2])
                        if res:
                            async with message.channel.typing():
                                rankid = res.group(3)
                                saveProfile(message.author.id, rankid)
                            await message.channel.send('내정보 등록이 완료되었습니다.')
                        else:
                            async with message.channel.typing():
                                search = ' '.join(msg[2:])
                                req = urllib.request.Request("http://saber.tarcle.kr/api/search/"+search, headers={'api': 'beatsaber'})
                                text = urllib.request.urlopen(req).read().decode('utf-8')
                                players = json.loads(text)

                                sel = -1
                                #검색목록 출력
                            if len(players) > 0:
                                if len(players) == 1:
                                    sel = 0
                                else:
                                    content = '```json\n'
                                    for i in range(min(5, len(players))):
                                        name = players[i]['name']
                                        rank = players[i]['rank']
                                        pp = players[i]['pp']
                                        content += '{} : {} ( {} ) - {}\n'.format(i+1, name, pp, rank)
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
                            rankid = players[sel]['url']
                            saveProfile(message.author.id, rankid)
                            await clearReaction(searchlist)
                            await message.channel.send('내정보 등록이 완료되었습니다.')
                    else:
                        return await message.channel.send('닉네임 또는 스코어세이버 URL을 입력해주세요.')
                else:
                    async with message.channel.typing():
                        rows = mysql.select('quicks', '*', 'where uid='+str(message.author.id))

                    if len(rows) > 0:
                        href = 'http://saber.tarcle.kr/api/profile/'+rows[0]['rankid']
                        req = urllib.request.Request(href, headers={'api': 'beatsaber'})
                        text = urllib.request.urlopen(req).read().decode('utf-8')
                        player = json.loads(text)

                        embed = createProfile(player, href)
                        await message.channel.send(embed=embed)
                    else:
                        await message.channel.send('등록된 계정이 없습니다. [{}내정보 등록]을 먼저 실행해주세요.'.format(prefix))
            
            elif command in ['전적', '기록', 'history', 'record', '-h', '-ㅗ']:
                def records_sql(id, page):
                    return mysql.select(
                        '(SELECT b.rankid, min(c.date) - interval 1 day date, min(c.rank_global)rank_global, min(c.rank_country)rank_country, c.pp FROM supporters AS a '+
                        'LEFT JOIN quicks AS b ON a.uid = b.uid '+
                        'LEFT JOIN rank_records AS c ON b.rankid = c.rankid '+
                        'WHERE a.uid={} '.format(id)+
                        'GROUP BY c.pp)t',
                        '*', 'order by date desc limit 11 offset {}'.format(max(page*10-1, 0))
                    )
                def records_all_sql(id, page):
                    return mysql.select(
                        'supporters as a', 'b.rankid, c.date - interval 1 day as date, c.rank_global, c.rank_country, c.pp',
                        'LEFT JOIN quicks AS b ON a.uid = b.uid ' +
                        'LEFT JOIN rank_records AS c ON b.rankid = c.rankid ' +
                        'WHERE a.uid={} '.format(id)+
                        'order by date desc limit 11 offset {}'.format(max(page*10-1, 0))
                    )
                
                rall = len(msg)>1 and msg[1] in ['모두', '전체', 'all', 'a']
                async with message.channel.typing():
                    if rall:
                        count = mysql.select(
                            'supporters as a', 'count(*) as count',
                            'LEFT JOIN quicks AS b ON a.uid = b.uid ' +
                            'LEFT JOIN rank_records AS c ON b.rankid = c.rankid ' +
                            'WHERE a.uid=' + str(message.author.id)
                        )[0]['count']
                    else:
                        count = len(mysql.select(
                            'supporters as a', 'count(*) as count',
                            'LEFT JOIN quicks AS b ON a.uid = b.uid '+
                            'LEFT JOIN rank_records AS c ON b.rankid = c.rankid '+
                            'WHERE a.uid={} '.format(message.author.id)+
                            'group by c.pp'
                        ))
                if count == 0:
                    return await message.channel.send("```\n후원자를 위한 기능입니다.\n```")
                if rall:
                    records = records_all_sql(message.author.id, 0)
                else:
                    records = records_sql(message.author.id, 0)
                if not records[0]['rankid']:
                    return await message.channel.send("```\n내정보를 먼저 등록해주세요.\n```")
                if not records[0]['date']:
                    return await message.channel.send("```\n아직 데이터가 존재하지 않습니다.\n내일 다시 시도해주세요.```")
                
                href = 'http://saber.tarcle.kr/api/profile/'+records[0]['rankid']
                req = urllib.request.Request(href, headers={'api': 'beatsaber'})
                text = urllib.request.urlopen(req).read().decode('utf-8')
                player = json.loads(text)

                total_page = int(math.ceil((count+1) / 10))

                now = {'date': date.today(), 'rank_global': player['rank_global'], 'rank_country': player['rank_country'], 'pp': player['pp']}
                records.insert(0, now)
                recordlist = await message.channel.send(embed=createRecordlist(message.author, records, 0, total_page))
                
                if count > 10:
                    #페이징
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
                            
                            records = records_all_sql(message.author.id, curr_page) if rall else records_sql(message.author.id, curr_page)
                            if curr_page == 0:
                                records.insert(0, now)
                            if(getPerms(message).manage_messages):
                                await recordlist.remove_reaction(res[0].emoji, message.author)
                            await recordlist.edit(embed=createRecordlist(message.author, records, curr_page, total_page))
            
            elif command in ['점수', '성과', 'score', '-c', '-ㅊ']:
                if len(msg)>1:
                    if msg[1] in ['최고', 'top', 't', 'ㅅ']:
                        param = 'topscore'
                    elif msg[1] in ['최근', 'recent', 'r', 'ㄱ']:
                        param = 'recentscore'
                    else:
                        return await message.channel.send('명령어(최고, 최근)를 정확히 입력해주세요.')
                else:
                    param = 'topscore'

                async with message.channel.typing():
                    if len(msg)>2:
                        search = ' '.join(msg[2:])
                        req = urllib.request.Request("http://saber.tarcle.kr/api/search/"+search, headers={'api': 'beatsaber'})
                        text = urllib.request.urlopen(req).read().decode('utf-8')
                        players = json.loads(text)

                        sel = -1
                        #검색목록 출력
                        if len(players) > 0:
                            if len(players) == 1:
                                sel = 0
                            else:
                                content = createSearchlist(players)
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

                        rankid = players[sel]['url']
                    else:
                        rows = mysql.select('quicks', '*', 'where uid='+str(message.author.id))
                        if len(rows) > 0:
                            rankid = rows[0]['rankid']

                # 페이지 이동
                # 플레이어 정보
                req = urllib.request.Request('http://saber.tarcle.kr/api/profile/'+rankid, headers={'api': 'beatsaber'})
                text = urllib.request.urlopen(req).read().decode('utf-8')
                player = json.loads(text)
                
                # 점수 정보
                req = urllib.request.Request('http://saber.tarcle.kr/api/'+param+'/'+rankid, headers={'api': 'beatsaber'})
                text = urllib.request.urlopen(req).read().decode('utf-8')
                scores = json.loads(text)

                embed = createScorelist(player, scores, rankid)
                if 'searchlist' in locals():
                    await clearReaction(searchlist)
                    await searchlist.edit(content="", embed=embed)
                else:
                    searchlist = await message.channel.send(embed=embed)
                    
                #페이징
                total_page = int(scores[0])
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
                        page_start = curr_page*8

                        # 점수 정보
                        req = urllib.request.Request('http://saber.tarcle.kr/api/%s/%s/%d'%(param, rankid, (curr_page+1)), headers={'api': 'beatsaber'})
                        text = urllib.request.urlopen(req).read().decode('utf-8')
                        scores = json.loads(text)

                        embed = createScorelist(player, scores, rankid)
                        if(getPerms(message).manage_messages):
                            await searchlist.remove_reaction(res[0].emoji, message.author)
                        await searchlist.edit(embed=embed)
            
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

def getPerms(msg):
    if msg.guild:
        return msg.channel.permissions_for(msg.guild.me)
    else:
        return msg.channel.permissions_for(msg.channel.me)

async def clearReaction(msg):
    if msg.guild and getPerms(msg).manage_messages:
        return await msg.clear_reactions()

def saveProfile(uid, rankid):
    if mysql.select('quicks', 'count(*) as count', 'where uid="'+str(uid)+'"')[0]['count'] > 0:
        mysql.update('quicks', 'uid='+str(uid), 'rankid='+rankid)
    else:
        mysql.insert('quicks', ['uid', 'rankid'], (uid, rankid))
    return True

def createSearchlist(players):
    content = '```json\n'
    for i in range(min(5, len(players))):
        content += '{} : {} ( {} ) - {}\n'.format(i+1, players[i]['name'], players[i]['pp'], players[i]['rank'])
    content += '```'

    return content

def createProfile(player, href):
    country = 'https://scoresaber.com/imports/images/flags/'+player['country']+'.png'
    link_global = "https://scoresaber.com/global"
    link_country = link_global + "?country=" + player['country']

    embed = discord.Embed(title="자세히 보려면 여기를 클릭하세요.", description="Player Ranking: [#{}]({} '글로벌 랭킹') - ( [{} #{}]({} '국내 랭킹') )".format(player['rank_global'], link_global, player['country'].upper(), player['rank_country'], link_country), url=href, color=embed_color)
    embed.set_thumbnail(url=player['avatar'])
    embed.set_author(name=player['name'], icon_url=country)
    embed.add_field(name='Perfomance Points', value=player['pp'], inline=False)
    embed.add_field(name='Play Count', value=player['playcount'], inline=False)
    embed.add_field(name='Total Score', value=player['totalscore'], inline=False)
    embed.add_field(name='Replays Watched by Others', value=player['replays'], inline=False)

    return embed

def createRanklist(players, country, page_start=0):
    embed = discord.Embed(title="자세히 보려면 여기를 클릭하세요.", description="", url="https://scoresaber.com/global?country="+country, color=embed_color)
    embed.set_author(name=("글로벌" if country=="" else country.upper())+" 랭킹", icon_url="https://scoresaber.com/imports/images/flags/"+country+".png")

    page_end = page_start + min(10, len(players)-curr_page*10)
    for player in players[page_start:page_end]:
        embed.add_field(name="{}: [{}]".format(str(player['rank']).zfill(2), country.upper()), value="[{}](https://scoresaber.com/u/{}) ({}pp) [{}]".format(player['name'], player['url'], player['pp'], ("+" if player['weekly_change']>0 else "")+str(player['weekly_change'])), inline=False)

    return embed

def createScorelist(player, scores, rankid):
    embed = discord.Embed(title="자세히 보려면 여기를 클릭하세요.", description="Perfomance Points : %.2f" % player['pp'], url="https://scoresaber.com/u/"+rankid, color=embed_color)
    embed.set_thumbnail(url=player['avatar'])
    embed.set_author(name=player['name'], icon_url='https://scoresaber.com/imports/images/flags/'+player['country']+'.png')

    for score in scores:
        if isinstance(score, str): continue
        accuracy = (score['accuracy'] if 'accuracy' in score.keys() else score['score']+"점")
        embed.add_field(name=score['name']+" "+score['difficult']+" ["+score['mapper']+"]", value="%.2f ( %.2f ) | %s | #%s" % (score['pp'], score['pp_weight'], accuracy, score['rank']), inline=False)

    return embed

def createRecordlist(author, records, curr_page, total_page):
    embed = discord.Embed(title="", description="", url="", color=embed_color)
    embed.set_author(name="{}님의 전적 ({} / {})".format(author.name, curr_page+1, total_page))
    embed.set_thumbnail(url=author.avatar_url)

    i = 1
    for record in records[:min(len(records), 10)]:
        value = "#{} (#{}) {}pp".format(record['rank_global'], record['rank_country'], record['pp'])
        if record != records[-1]:
            change_pp = '%.2f' % (record['pp']-records[i]['pp'])
            if not change_pp.startswith('-'): change_pp = '+'+change_pp
            value += ' [%s]' % change_pp
        embed.add_field(name="{}년 {}월 {}일".format(record['date'].year, str(record['date'].month).zfill(2), str(record['date'].day).zfill(2)),
            value=value, inline=False)
        i += 1

    return embed

bot = App()
bot.run(token)
