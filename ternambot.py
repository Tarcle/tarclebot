# NTgxMDA3NjYwMDI4MjY0NDU5.XOZBLQ.yXtwYxk9Mk3-zXbBbAVKu4hKb2g

import asyncio
import discord
import urllib
from bs4 import BeautifulSoup

import random

prefix = '털남아'
embed_color = 0x880015
emoji_num = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣']

class App(discord.Client):
    async def on_ready(self):
        print('다음으로 로그인합니다: {0}'.format(self.user))
        print('===============')
        await self.change_presence(activity=discord.Game(name='{ch}?, {ch}도움말, {ch}help'.format(ch=prefix), type=1))
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
                    '```'
                await message.channel.send(content.format(ch=prefix))
            elif command == '':
                if len(msg)>1 and msg[1] in ['헤어지자','헤어져']:
                    if message.author.id == 337499428560699392: #미니누나
                        await message.channel.send("털은 영어로 hair")
                elif len(msg)==1:
                    if message.author.id == 361018280569470986: #나
                        await message.channel.send("네 주인님!")
                    elif message.author.id == 343569224700264448: #홍님
                        await message.channel.send("미니야 헤어지자")
                    else:
                        chat = ["응?","왜?","왜불러!","뀨?","빵사올까?","얼마면돼","아잉~ 부끄러웡","뭐야 넌 주인님이 아니잖아?","누구세요?","아뇨~ 뚱인데요!"]
                        await message.channel.send(chat[int(random.random()*len(chat))])

bot = App()
bot.run('NTgxMDA3NjYwMDI4MjY0NDU5.XOZBLQ.yXtwYxk9Mk3-zXbBbAVKu4hKb2g')