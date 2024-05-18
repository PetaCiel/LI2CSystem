#timeとthreading,asyncioは標準ライブラリ(のはず)
#discordとsmbusが拡張ライブラリ
import time
import smbus
import discord
import asyncio
import threading

#I2C宣言
bus=smbus.SMBus(1)
addr=0x2a #今回はS-11059を使用する為,標準の2aを使用.もしそれ以外を使用する場合は要注意,i2cdetectでSlaveAddressを検索する事
param=[0x0b,0x0a,0x09,0x08,0x03,0x02,0x01,0x00] #コピペした為用途不明,要検証
bus.write_byte_data(addr,0x00,0x80)
bus.write_byte_data(addr,0x00,param[0])

#discord.pyのintents,client宣言
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

#discord.pyのDiscordに表示されるステータス,鑑賞中にする為'watching'
state0 = discord.Activity(name='🟥🟥|施錠|🟥🟥', type=discord.ActivityType.watching)
state1 = discord.Activity(name='🟩🟩|開錠|🟩🟩', type=discord.ActivityType.watching)
state2 = discord.Activity(name='🛑🛑|メンテ中だお|🛑🛑', type=discord.ActivityType.watching)



#GPIOの入力をint(0,1)に変換しSetActiveを起動する関数GP
def gp():
    ipr=4#I2C-Previous
    ibi=0#I2C-Bit
    print("testtesttest")#デバッグ用仮設置、頃合いを見て削除
    while True:
        data=bus.read_i2c_block_data(addr,0x03,8)
        act=data[0]*256+data[1]#元コードに倣って*256だが、有効な方法あれば修正可能
        if (act<600):#このコードでは閾値を600にして二値化を図っているが、もし閾値が異なる場合は都度修正必須かも
            ibi=0
        else:
            ibi=1
        if ibi!=ipr:
            if (ibi==0):
                ipr=ibi
                print("d0")#デバッグ用設置、頃合いを見て削除,以下同文
            elif (ibi==1):
                ipr=ibi
                print("d1")
            elif (ibi==2):
                ipr=ibi
                print("d2")
            elif (ibi==3):
                ipr=ibi
                print("d3")
            asyncio.run(setactive(ibi))
            time.sleep(0.25)#要らないかも？

#async関数、ibiを貰ってDiscordの状態のフラグに使用
async def setactive(ans):
    if ans==0:
        await client.change_presence(status=discord.Status.online, activity=state0)
    if ans==1:
        await client.change_presence(status=discord.Status.online, activity=state1)
    if ans==2:
        await client.change_presence(status=discord.Status.online, activity=state2)

#サブスレッドの構築、ターゲットはGP
thread1 = threading.Thread(target=gp)

#Discordのデコレータ関数,on_readyにサブスレッド起動の構築,改善必須
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    thread1.start()
@client.event
async def on_message(message):
    if message.author == client.user:
        return

#Discord.pyのrun,譲渡する際はTokenを'token'に変更
#('token')にトークンを''で入力
client.run('token')
