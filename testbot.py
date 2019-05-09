#https://public-api.tracker.gg/apex/v1/standard/profile/5/Tarcle
#1e913677-7f9e-491d-b16b-fb097d0456ac

#Tvtf3hsW0468tDq8n1b6D3RQrNTvjnMbDgAF1Wso
import asyncio
import discord
import urllib
from bs4 import BeautifulSoup

prefix = '.'
embed_color = 0x880015
emoji_num = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣']

class App(discord.Client):
    async def on_ready(self):
        print('다음으로 로그인합니다: {0}'.format(self.user))
        print('===============')
        await self.change_presence(activity=discord.Game(name='{ch}?, {ch}도움말, {ch}help'.format(ch='.'), type=1))
    async def on_message(self, message):
        if message.author.bot:
            return None
        if message.content.startswith(prefix):
            msg = message.content.split(' ')
            command = msg[0][len(prefix):]
            if command in ['?', '도움말', 'help']:
                content = '```md\n'+\
                    '# {ch}?, {ch}도움말, {ch}help\n'+\
                    '>   이 봇이 가진 명령어를 확인합니다.\n'+\
                    '# {ch}검색 [장비 또는 속성 이름]'+\
                    '>장비 또는 속성 설명 검색\n'+\
                    '>   1. 검색 목록 5개 출력\n'+\
                    '>   2. 봇이 번호 추가하기 기다리기\n'+\
                    '>   3. 5개 중 원하는 내용 선택 (반응 클릭)\n'+\
                    '>   4. 내용 확인!\n'+\
                    '```'
                await message.channel.send(content.format(ch=prefix))
            elif command in ['검색']:
                async with message.channel.typing():
                    perms = message.channel.permissions_for(message.channel.guild.me)
                    if(not perms.add_reactions):
                        await message.channel.send('관리자 권한 또는 반응 추가 권한이 있어야 가능합니다.')
                        return None
                    search = urllib.parse.quote(' '.join(msg[1:]))
                    req = urllib.request.Request("https://www.google.com/search?q=light.gg+"+search, headers={'User-Agent': 'Mozilla/5.0'})
                    html = urllib.request.urlopen(req).read().decode('utf-8')
                    soup = BeautifulSoup(html, 'html.parser')

                    #검색목록 출력
                    links = soup.select('div.g .r a')
                    content = '```'
                    for i in range(5):
                        content += '{} : '.format(emoji_num[i])+'-'.join(links[i].text.strip().split('-')[:2])+'\n'
                    content += '```'
                    searchlist = await message.channel.send(content)

                for e in emoji_num: await searchlist.add_reaction(e)
                def check(reaction, user): return user == message.author and str(reaction.emoji) in emoji_num
                try:
                    res = await self.wait_for('reaction_add', timeout=30, check=check)
                except asyncio.TimeoutError: #시간초과
                    await message.channel.send('시간이 초과되었습니다. 다시 시도해주세요.')
                    if(perms.manage_emojis):
                        await searchlist.clear_reactions()
                    else:
                        for e in emoji_num: await searchlist.remove_reaction(e, self.user)
                    return False
                else:
                    sel = emoji_num.index(res[0].emoji)

                async with message.channel.typing():
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
                        await searchlist.delete()
                        await message.channel.send(embed=embed)
                    else:
                        await searchlist.delete()
                        await message.channel.send('검색에 실패했습니다. 자세하게 입력해주세요.')

bot = App()
bot.run('NTU1OTI1NzgxNjcxMzEzNDA4.D2yR3g._AMmQVmG0XmatsX0-bYQhmFlnIk')