import discord
import emoji
import datetime
from datetime import datetime
import json


async def checkEvent(ctx):
    channel = discord.utils.get(ctx.guild.channels, name="relatorios")
    msgs = []
    async for i in channel.history(limit=50):
        if i.embeds:
            msgs.append(i.embeds[0].title)

    with open("events.json", "r") as file:
        events = json.load(file)
    temp = events.copy()
    for event in temp:
        if str(event) not in msgs:
            events.pop(event)
    with open("events.json", "w") as file:
        json.dump(events, file, indent=4)
    return True

def checkServer(ctx):
    with open("whitelist.json", "r") as file:
        guilds = json.load(file)
    return ctx.guild.id in guilds


def checkUser(ctx):
    return ctx.author.id == 289922186247012364


def checkchannel(ctx):
    return ctx.channel.name == "relatorios"

def get_time():
    time = datetime.utcnow()
    return [time.hour, time.minute, time.second, time.day, time.month]


def time_passed(t):
    t2 = get_time()
    time = list(map(lambda x, y: (x - y), t2, t))
    return sum([time[0] * 3600 + time[1] * 60 + time[2], time[3]*24*3600, time[4]*30*24*3600])


async def foot_notes_format(clas, emotes):
    end_string = ""
    for em, cl in zip(emotes, clas):
        e = emoji.emojize(em, use_aliases=True)
        line = "  " + cl + " = " + e
        end_string += line
    return end_string


async def add_reactions(msg, cls, reactions):
    for reaction in reactions:
        await msg.add_reaction(emoji.emojize(reaction, use_aliases=True))
    s = await foot_notes_format(cls, reactions)  # here
    msg.embeds[0].set_footer(text=s)
    await msg.edit(embed=msg.embeds[0])


async def get_reaction_info(payload, bot):
    chl = bot.get_channel(payload.channel_id)
    msg = await chl.fetch_message(payload.message_id)
    await bot.wait_until_ready()
    user = bot.get_user(payload.user_id)
    return [msg, user]


async def updateMembers(payload, reactions, msg, nick, user):
    i = reactions.index(str(payload.emoji))
    embed = msg.embeds[0]
    fields = embed.fields
    names = [i.name for i in fields]
    values = [i.value for i in fields]
    for value in values:
        if nick in value:
            await msg.reactions[i].remove(user)
            return
    if str(payload.emoji) in reactions:
        v = values[i].replace("---", nick, 1)
        if v == values[i]:
            await msg.reactions[i].remove(user)
            return
        embed.set_field_at(i, name=names[i], value=v)
        await msg.edit(embed=embed)

