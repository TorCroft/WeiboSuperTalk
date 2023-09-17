from . import bark
from . import custom
from . import gocqhttp
from . import dingtalk
from . import discord
from . import pushdeer
from . import pushplus
from . import qmsg
from . import serverchan
from . import serverchanturbo
from . import telegram
from . import wechatworkapp
from . import wechatworkbot

_all_providers = {
    bark.Bark.name: bark.Bark,
    custom.Custom.name: custom.Custom,
    gocqhttp.Gocqhttp.name: gocqhttp.Gocqhttp,
    dingtalk.DingTalk.name: dingtalk.DingTalk,
    discord.Discord.name: discord.Discord,
    pushdeer.Pushdeer.name: pushdeer.Pushdeer,
    pushplus.PushPlus.name: pushplus.PushPlus,
    qmsg.Qmsg.name: qmsg.Qmsg,
    serverchan.ServerChan.name: serverchan.ServerChan,
    serverchanturbo.ServerChanTurbo.name: serverchanturbo.ServerChanTurbo,
    telegram.Telegram.name: telegram.Telegram,
    wechatworkapp.WechatWorkApp.name: wechatworkapp.WechatWorkApp,
    wechatworkbot.WechatWorkBot.name: wechatworkbot.WechatWorkBot
}
