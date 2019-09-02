# NjExNzkxNjY5NTQ4ODEwMjYx.XVY-aQ.ybFurqgvEOz66djiibWhgk0E3Uw <-- 스코어세이버 Bot
# NjExODgxNzkxMDc4NTMxMDkz.XV3gKw.nX_ZEFo08o5IIorxqAED77S677o <-- Test Bot

import asyncio
import discord
import urllib
from bs4 import BeautifulSoup
import pymysql

import random
import math

token = 'NjExNzkxNjY5NTQ4ODEwMjYx.XVY-aQ.ybFurqgvEOz66djiibWhgk0E3Uw'
prefix = '-'
embed_color = 0x880015
emoji_num = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣']

mysql_host = '172.105.241.159'
mysql_user = 'root'
mysql_password = 'cjc!40812848'
mysql_database = 'scoresaber'
mysql_charset = 'utf8'

class App(discord.Client):
    async def on_ready(self):
        print('다음으로 로그인합니다: {0}'.format(self.user))
        print('===============')
        # await self.change_presence(activity=discord.Game(name='{ch} 검색 [닉네임]'.format(ch=prefix), type=1))
    async def on_message(self, message):
        if message.author.bot:
            return None
        if message.content.startswith(prefix):
            msg = message.content.split(' ')
            command = msg[0][len(prefix):]
            if command in ['검색', '전적', 'search']:
                try: perms = message.channel.permissions_for(message.channel.guild.me)
                except: None
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
                        content = '```py\n'
                        for i in range(min(5, len(players))):
                            player = players[i].select('.player>a>.pp')[0]
                            rank = players[i].select('.rank')[0]
                            pp = players[i].select('.ppValue')[0]
                            content += '{} : {} ( {} ) - {}\n'.format(i+1, player.text.strip(), pp.text.strip(), rank.text.strip())
                        content += '```'
                        searchlist = await message.channel.send(content)
                else:
                    await message.channel.send('검색한 닉네임이 존재하지 않습니다. 다시 확인해주세요.')
                    return False

                #이모지 추가
                if sel < 0:
                    for e in emoji_num[:min(5, len(players))]: await searchlist.add_reaction(e)
                    def check(reaction, user): return user == message.author and str(reaction.emoji) in emoji_num
                    try:
                        res = await self.wait_for('reaction_add', timeout=30, check=check)
                    except asyncio.TimeoutError: #시간초과
                        await message.channel.send('시간이 초과되었습니다. 다시 시도해주세요.')
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
                await message.channel.send(embed=embed)
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

                    #검색목록 출력
                    players = soup.select('.ranking>.ranking>tbody>tr')
                if len(players) > 0:
                    content = '```py\n'
                    for i in range(min(10, len(players))):
                        player = players[i].select('.player>a')[0]
                        rank = players[i].select('.rank')[0]
                        pp = players[i].select('.ppValue')[0]
                        content += '{} : {} ( {} )\n'.format(i+1, player.text.strip(), pp.text.strip())
                    content += '```'
                    searchlist = await message.channel.send(content)
                else:
                    await message.channel.send('입력하신 국가코드는 존재하지 않습니다. 다시 확인해주세요.')
                    return False
                return False

                #이모지 추가
                buttons = ['⬅', '➡']
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
                    async with message.channel.typing():
                        if len(msg) > 2:
                            uid = str(message.author.id)
                            rankid = msg[2]
                            db_delete('quicks', 'uid = %s', uid)
                            db_insert('quicks', 'uid, rankid', (uid, rankid))

                    await message.channel.send('내정보 등록이 완료되었습니다.')
                else:
                    async with message.channel.typing():
                        conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_database, charset=mysql_charset)
                        curs = conn.cursor(pymysql.cursors.DictCursor)
                        
                        sql = "SELECT * FROM quicks WHERE uid={}".format(message.author.id)
                        curs.execute(sql)
                        rows = curs.fetchall()
                        
                        conn.close()

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
            elif command in ['dm']:
                dm = await message.author.create_dm()
                await dm.send('test')

def db_insert(table, columns, values):
    conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_database, charset=mysql_charset)
    curs = conn.cursor()

    tmp = "%s"
    for i in values[1:]:
        tmp += ", %s"
    curs.execute("insert into {}({}) values ({})".format(table, columns, tmp), values)
    conn.commit()

    conn.close()

def db_update(table, wheres, sets):
    conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_database, charset=mysql_charset)
    curs = conn.cursor()

    curs.execute("update {} set {} where {}".format(table, sets, wheres))
    conn.commit()

    conn.close()

def db_delete(table, where, values):
    conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_database, charset=mysql_charset)
    curs = conn.cursor()

    curs.execute("delete from {} where {}".format(table, where), values)
    conn.commit()

    conn.close()

def db_select(query):
    conn = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_database, charset=mysql_charset)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    
    curs.execute(query)
    rows = curs.fetchall()
    
    conn.close()

    return rows

def createProfile(soup, href):
    avatar = soup.select('.avatar>img')[0].get('src')
    country = 'https://scoresaber.com'+soup.select('.title>img')[0].get('src')
    name = soup.select('.title')[0].text.strip()
    info = soup.select('.column>ul>li')
    if len(soup.select('.avatar>center>img'))>0: del info[0]

    rank_global = info[0].select('a')[0].text.strip()
    rank_country = info[0].select('a')[1].text.strip()
    columns = []
    columns.append(info[1].text.split(':'))
    columns.append(info[2].text.split(':'))
    columns.append(info[3].text.split(':'))
    columns.append(info[4].text.split(':'))

    embed = discord.Embed(title='더 자세히 보려면 여기를 클릭하세요.', description='Player Ranking: {} - ( 국내 {} )'.format(rank_global, rank_country), url=href, color=embed_color)
    embed.set_thumbnail(url=avatar)
    embed.set_author(name=name, icon_url=country)
    for column in columns:
        embed.add_field(name=column[0].strip(), value=column[1].strip(), inline=False)
    return embed

bot = App()
bot.run(token)
