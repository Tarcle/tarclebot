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
    await app.change_presence(game=discord.Game(name=command_head+'?', type=1))

searching = list
@app.event
async def on_message(message):
    if message.author.bot:
        return None
    if message.content.startswith(command_head):
        msg = message.content.split(' ')
        command = msg[0][len(command_head):]
        if command in ['도움말', '?']:
            await app.send_typing(message.channel)
            content = '{ch}검색 [장비 또는 속성 이름] : 장비 또는 속성 설명 검색\n'
            await app.send_message(message.channel, content.format(ch=command_head))
        if command in ['검색']:
            if len(msg)>=2:
                await app.send_typing(message.channel)
                search = msg[1:]
                search_ = urllib.parse.quote(' '.join(search))
                req = urllib.request.Request("https://www.google.com/search?q=light.gg+"+search_, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(req).read().decode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')

                link = soup.select('div.g .r a')[0]
                title = link.text.strip()
                href = urllib.parse.unquote(link.get('href').split('/url?q=')[1].split('&')[0])

                # 페이지 이동
                req = urllib.request.Request(href, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(req).read().decode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')
                if len(soup.select('.item-header'))>0: #검색 성공
                    title = soup.select('.item-header .item-name h2')[0].text.strip()
                    weapon_type = soup.select('.item-header .weapon-type')[0].text.strip()
                    img = soup.select('.item-header .bump img')[0].get('src')
                    flavor = soup.select('.item-header .flavor-text > h4')[0].text
                    embed = discord.Embed(title='', color=embed_color)
                    embed.set_author(name=title, icon_url=img, url=href)

                    perks = soup.select('#socket-container .perks .sockets')
                    if len(perks)>0: #장비 속성 검색
                        is_exotic = weapon_type.startswith('경이')
                        is_legend = weapon_type.startswith('전설')
                        embed.set_footer(text=flavor)
                        for alt in perks:
                            alts = alt.select('img')
                            if len(alts)>0:
                                frame = ''
                                for alt in alts: frame += alt.get('alt')+' / '
                                frame = frame[:-3]
                                break
                        if is_exotic: embed.title = weapon_type+'\n\n경이 본질'
                        else: embed.title = weapon_type+'\n\n프레임'
                        embed.description = frame
                        fixed_value = []
                        for perk in perks[:4]:
                            li = perk.select('.item.show-hover:not(.random)')
                            if len(li)>0:
                                alts = ''
                                for img in li:
                                    alt = img.select('img')[0].get('alt')
                                    if alt!=frame: alts += alt+' / '
                                if len(alts)>0: fixed_value.append(alts[:-3])
                        if is_exotic: field_name = '속성'
                        elif is_legend: field_name = '걸작 속성'
                        else: field_name = '고정 속성'
                        embed.add_field(name=field_name, value='\n'.join(fixed_value), inline=False)

                        perks = soup.select('#socket-container .perks .sockets li.random')
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
                                            field_value += alt+' / '
                                    field_value = field_value[:-3]
                                    i+=1
                                    embed.add_field(name=field_name, value=field_value)
                    else: #속성 설명 검색
                        embed.title = weapon_type
                        embed.description = flavor
                    await app.send_message(message.channel, embed=embed)
                else:
                    await app.send_message(message.channel, '검색에 실패했습니다. 자세하게 입력해주세요.')
            else:
                await app.send_message(message.channel, '명령어는 {}도움말 로 확인해주세요'.format(command_head))

app.run(token)