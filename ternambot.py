# NTgxMDA3NjYwMDI4MjY0NDU5.XOZBLQ.yXtwYxk9Mk3-zXbBbAVKu4hKb2g

import asyncio
import discord
import urllib
from bs4 import BeautifulSoup

import random
import math

prefix = '털남아'
embed_color = 0x880015
emoji_num = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣']

class App(discord.Client):
    async def on_ready(self):
        print('다음으로 로그인합니다: {0}'.format(self.user))
        print('===============')
        await self.change_presence(activity=discord.Game(name='{ch} 도움말, {ch} 명령어'.format(ch=prefix), type=1))
    async def on_message(self, message):
        if message.author.bot:
            return None
        if message.content.startswith(prefix):
            msg = message.content.split(' ')
            if len(msg) == 1:
                if len(msg)>1 and msg[1] in ['헤어지자','헤어져']:
                    if message.author.id == 337499428560699392: #미니누나
                        await message.channel.send("털은 영어로 hair")
                elif len(msg)==1:
                    if message.author.id == 361018280569470986: #나
                        await message.channel.send("네 주인님!")
                    elif message.author.id == 343569224700264448: #홍누나
                        await message.channel.send("미니야 헤어지자")
                    else:
                        chat = ["응?","왜?","왜불러!","뀨?","빵사올까?","얼마면돼","아잉~ 부끄러웡","뭐야 넌 주인님이 아니잖아?","누구세요?","아뇨~ 뚱인데요!"]
                        await message.channel.send(chat[int(random.random()*len(chat))])
            else:
                command = msg[1]
                if command in ['도움말', '명령어']:
                    content = '```md\n'+\
                        '# {ch} 도움말, {ch} 명령어\n'+\
                        '>   내가 할 줄 아는 걸 알려줘!\n\n'+\
                        '# {ch} 스크림 멤버는 a b c d e f ...\n'+\
                        '>   에이펙스 스크림을 할 때 팀을 나눠줄거야.\n\n'+\
                        '# {ch} 주사위\n'+\
                        '>   주사위가 없는 너희를 위해 내가 대신 굴려줄게! (1~100)'+\
                        '```'
                    await message.channel.send(content.format(ch=prefix))
                elif command == '스크림':
                    if len(msg) < 3:
                        await message.channel.send('멤버도 말해줘! (명령어 : 털남아 스크림 멤버는 a b c d e f ...')
                        return False
                    elif msg[2] == '멤버는':
                        members = msg[3:]
                        # 총 멤버수 입력
                        mem_len = len(members)
                        # 나누기를 위해 3의배수로 맞춰준다
                        mem_len += (3 - mem_len % 3) % 3
                        # 팀 나누기
                        team = []
                        # 1부터 배열수만큼
                        for i in range(int(mem_len / 3)):
                            # 사람 부족한만큼 팀원 수 조정
                            if i <= mem_len/3 - (3 - len(members)%3) % 3: team += [i,i,i]
                            else: team += [i,i]
                        random.shuffle(team)

                        res = []
                        j = 0
                        for i in range(max(team)+1): res.append([])
                        for i in team:
                            if j >= len(members): break
                            res[i].append(members[j])
                            j += 1
                        embed = discord.Embed(title='팀을 나눠달라는 말씀이시군요!', color=embed_color)
                        for i in range(len(res)):
                            embed.add_field(name='{}팀'.format(i+1), value='\n'.join(res[i]))
                        await message.channel.send(embed=embed)
                elif command == '주사위':
                    await message.channel.send('```\n내가 주사위를 대신 굴려줄게!\n두구두구두구두구x100\n\n짜잔! {}의 주사위는 {}!!!\n```'.format(message.author, random.randrange(1, 101)))

bot = App()
bot.run('NTgxMDA3NjYwMDI4MjY0NDU5.XOZBLQ.yXtwYxk9Mk3-zXbBbAVKu4hKb2g')