#https://public-api.tracker.gg/apex/v1/standard/profile/5/Tarcle
#1e913677-7f9e-491d-b16b-fb097d0456ac

#Tvtf3hsW0468tDq8n1b6D3RQrNTvjnMbDgAF1Wso
import discord
from discord.ext import commands
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

bot = commands.Bot(command_prefix='.')
@bot.event
async def on_ready():
    print('다음으로 로그인합니다: {0}'.format(bot.user))
    print('===============')
    await bot.change_presence(activity=discord.Game(name='{ch}?, {ch}도움말'.format(ch='.'), type=1))
@bot.command()
async def 검색(channel, arg):
    await channel.send(arg)
# bot = Client()
bot.run('NTU1OTI1NzgxNjcxMzEzNDA4.D2yR3g._AMmQVmG0XmatsX0-bYQhmFlnIk')