import asyncio
import discord
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

app = discord.Client()
token = 'NTIwOTgwNDg0NDQ5MzcwMTQz.D2d7vQ.oK2Z-RnxV4u7CNcyAT7lx-K8P3U'

command_head = '.'
embed_color = 0x880015

@app.event
async def on_ready():
    print('다음으로 로그인합니다: ')
    print(app.user.name)
    print(app.user.id)
    print('===============')
    await app.change_presence(game=discord.Game(name='{ch}?, {ch}도움말'.format(ch=command_head), type=1))

@app.event
async def on_message(message):
    if message.author.bot:
        return None
    if message.content.startswith(command_head):
        msg = message.content.split(' ')
        command = msg[0][len(command_head):]
        if command in ['도움말', '?']:await bot_help(message)
        elif command in ['검색']:await search_destiny2(message)
        elif command in ['미세먼지']:
            await app.send_typing(message.channel)
            if len(msg)>=2:
                search = msg[1:]
                search_ = urllib.parse.quote(' '.join(search)+'+미세먼지')
                req = urllib.request.Request("https://search.naver.com/search.naver?query={}".format(search_), headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(req).read().decode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')
                area = soup.select('#main_pack .main_select_tab .select_text')
                air = soup.select('#main_pack .main_box.expand .state_info .main_figure')
                if len(air)>0:
                    await app.send_message(message.channel, '```md\n#{} 미세먼지\n>  {}㎍/㎥ ```'.format(area[0].text.strip(), air[0].text.strip()))
                else:
                    await app.send_message(message.channel, '``` 네이버가 이 지역을 찾을 수 없어요! ```')
            # else:
                #main_pack > div.content_search.section._atmospheric_environment > div > div.contents03_sub > div > div:nth-child(3) > div.main_box > div.detail_box > div.tb_scroll > table > tbody > tr:nth-child(1)

async def bot_help(message):
    await app.send_typing(message.channel)
    content = '```md\n'+\
        '# {ch}?, {ch}도움말\n'+\
        '>   이 봇이 가진 명령어를 확인합니다.\n'+\
        '# {ch}검색 [장비 또는 속성 이름] : 장비 또는 속성 설명 검색\n'+\
        '>   1. 구글 검색으로 나오는 결과 5개 출력\n'+\
        '>   2. 5개 중 원하는 내용 선택 (반응 클릭)\n'+\
        '>   3. 내용 확인!\n'+\
        '```'
    await app.send_message(message.channel, content.format(ch=command_head))
async def search_destiny2(message):
    msg = message.content.split(' ')
    if len(msg)>=2:
        await app.send_typing(message.channel)
        perms = message.channel.permissions_for(message.channel.server.me)
        if(not perms.add_reactions):
            await app.send_message(message.channel, '관리자 권한 또는 반응 추가 권한이 있어야 가능합니다.')
            return False
        search = msg[1:]
        search_ = urllib.parse.quote(' '.join(search))
        req = urllib.request.Request("https://www.google.com/search?q=light.gg+"+search_, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        emoji = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣']

        #검색목록 출력
        links = soup.select('div.g .r a')
        content = '```'
        i=0
        for link in links[:5]:
            content += '{} : '.format(emoji[i])+'-'.join(link.text.strip().split('-')[:2])+'\n'
            i+=1
        content += '```'
        searchlist = await app.send_message(message.channel, content)

        for e in emoji: await app.add_reaction(searchlist, e)
        res = await app.wait_for_reaction(emoji, user=message.author, message=searchlist, timeout=30)
        if res != None:
            sel = emoji.index(res.reaction.emoji)
        else: #시간초과
            await app.send_message(message.channel, '시간이 초과되었습니다. 다시 시도해주세요.')
            if(perms.administrator or perms.manage_emojis): await app.clear_reactions(searchlist)
            else:
                for e in emoji: await app.remove_reaction(searchlist, e, app.user)
            return False

        await app.send_typing(message.channel)
        link = links[sel]
        title = link.text.strip()
        href = urllib.parse.unquote(link.get('href').split('/url?q=')[1].split('&')[0])

        # 페이지 이동
        req = urllib.request.Request(href, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        if len(soup.select('.item-header'))>0: #검색 성공
            title = soup.select('.item-header .item-name h2')[0].text.strip()
            weapon_type = soup.select('.item-header .weapon-type')[0].text.strip()
            is_exotic = weapon_type.startswith('경이')
            is_legend = weapon_type.startswith('전설')
            img = soup.select('.item-header .bump img')[0].get('src')
            flavor = soup.select('.item-header .flavor-text > h4')[0].text.strip()
            source_line = soup.select('.item-header .source-line')
            if len(source_line)>0: source_line = source_line[0].text.strip()
            else: source_line = ''
            embed = discord.Embed(title='더 자세히 보려면 여기를 클릭하세요.', description=weapon_type+'\n\n'+flavor, url=href, color=embed_color)
            embed.set_author(name=title, icon_url=img, url=href)
            embed.set_footer(text=source_line)

            frames = soup.select('#socket-container .perks>.sockets')
            if len(frames)>0:
                if is_exotic: frame_title = '경이 본질'
                else: frame_title = '프레임'
                alts = frames[0].select('img')
                frame = ''
                if len(alts)>0:
                    for alt in alts: frame += alt.get('alt')+'\n'
                else:
                    alts = frames[1].select('img')
                    for alt in alts: frame += alt.get('alt')+'\n'
                embed.add_field(name=frame_title, value=frame, inline=True)

                perks = soup.select('#socket-container .perks>.sockets+.sockets')
                if len(perks)>0: #장비 속성 검색
                    if is_exotic: field_name = '속성'
                    elif is_legend: field_name = '걸작 속성'
                    else: field_name = '고정 속성'
                    fixed_value = []
                    if len(soup.select('.sockets .item.random'))>0: tmp = int(len(perks)/2)
                    else: tmp = len(perks)
                    for perk in perks[:tmp]:
                        li = perk.select('.item.show-hover:not(.random)')
                        if len(li)>0:
                            alts = ''
                            for img in li:
                                alt = img.select('img')[0].get('alt')
                                if alt!=frame: alts += alt+' / '
                            if len(alts)>0: fixed_value.append(alts[:-3])
                    embed.add_field(name=field_name, value='\n'.join(fixed_value), inline=False)

                    perks = soup.select('#socket-container .perks>.sockets li.random')
                    # embed = discord.Embed(title='', color=embed_color)
                    if len(perks)>0:
                        i = 0
                        for perk in perks:
                            field_name = '랜덤 속성 '+str(i+1)
                            field_value = ''
                            li = perk.select('.item.show-hover.random')
                            if len(li)>0:
                                for img in li:
                                    alt = img.select('img')[0].get('alt')
                                    if alt!=frame:
                                        field_value += alt+'\n'
                                i+=1
                                embed.add_field(name=field_name, value=field_value)
            else: #속성 설명 검색
                embed.title = weapon_type
                embed.description = flavor
            await app.delete_message(searchlist)
            await app.send_message(message.channel, embed=embed)
        else:
            await app.delete_message(searchlist)
            await app.send_message(message.channel, '검색에 실패했습니다. 자세하게 입력해주세요.')
    else:
        await app.send_message(message.channel, '명령어는 {}도움말 로 확인해주세요'.format(command_head))

app.run(token)