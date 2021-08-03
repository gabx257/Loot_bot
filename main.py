import asyncio
from ping import keep_alive
import discord
from discord.ext import commands

import event
import suport_functions
import wallet

token = "ODU3OTM4NDkxOTAzNTc0MDI2.YNW3fA.BZRjvufi2QwDbLciFI6RqHGK8oA"
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='%', intents=intents)


# @bot.event
# async def on_message(ctx):
#     async for i in ctx.channel.history(limit=10):
#         print(i.embeds)

async def walleting(channel):
    await channel.send("Choose the roles that should have a wallet", delete_after=20)
    try:
        msg = await bot.wait_for("message", check=suport_functions.checkchannel, timeout=60)
    except asyncio.TimeoutError:
        await msg.channel.send("error, waited to long for a response", delete_after=5)
        raise
    try:
        for r in msg.role_mentions:
            for p in r.members:
                wallet.create_wallet(p.display_name)
    except TypeError:
        await msg.channel.send("error,roles not found", delete_after=5)
        walleting(channel)
        raise

class Admin(commands.Cog):

    @commands.command(Help=" ")
    async def setup(self, ctx):
        category = discord.utils.get(ctx.guild.categories, name="Gank")
        event_creator = discord.utils.get(ctx.guild.channels, name="create-your-event")
        if category is None:
            category = await ctx.guild.create_category("Gank")
        relatorios = discord.utils.get(category.channels, name="relatorios")
        if relatorios is None:
            await category.create_text_channel("relatorios")
        if event_creator is None:
            event_creator = await ctx.guild.create_text_channel("create-your-event")
            embed = discord.Embed(title="Create your event")
            msg = await event_creator.send(embed=embed)
            await suport_functions.add_reactions(msg, ["Gank", "PvE"], [":axe:", ":wheelchair:"])
        await walleting(event_creator)

    @commands.command(
        help=
        "clear the chat of msgs")
    async def clear(self, ctx, arg=100):
        if ctx.channel.permissions_for(ctx.author).manage_messages or ctx.author.id == 289922186247012364:
            await ctx.channel.purge(limit=int(arg), check=lambda x: x.author != bot.user)
        else:
            await ctx.channel.send("you dont have permission to do that", delete_after=5)


class Loot(commands.Cog):

    @commands.command()
    async def ip(self, ctx, n):
        try:
            if n.isdigit():
                async for m in ctx.channel.history(limit=20, oldest_first= True):
                    if len(m.embeds) != 0 and m.embeds[0].title == str(ctx.channel.name):
                        msg = m
                        break
                t = msg.embeds[0].description.split("\n")[1].split()[-1]
                msg.embeds[0].description = msg.embeds[0].description.replace(t, n)
                await msg.edit(embed=msg.embeds[0])
        except (RuntimeError, NameError):
            await ctx.channel.send("channel msg not found, try using %clear"
                                   " to remove some of the junk msgs from the channel")

    @commands.command()
    async def content(self, ctx, n):
        async for m in ctx.channel.history(limit=20, oldest_first=True):
            if len(m.embeds) != 0 and m.embeds[0].title == str(ctx.channel.name):
                msg = m
                break
        try:
            t = msg.embeds[0].description.split("\n")[0].split()[-1]
            msg.embeds[0].description = msg.embeds[0].description.replace(t, n)
            await msg.edit(embed=msg.embeds[0])
        except (RuntimeError, NameError):
            await ctx.channel.send("channel msg not found, try using %clear"
                                   " to remove some of the junk msgs from the channel")

    @commands.command(Help=" ")
    async def add(self, ctx, id, amount):
        try:
            ctx_event = event.Event.load_to_memory(id)
            ctx_event.amount += int(amount)
            msg = await ctx.channel.fetch_message(ctx_event.summary)
            t = msg.embeds[0].description.split("\n")[0].split()[-1]
            edit = str(ctx_event.amount)
            total = sum([i["participation"] for i in ctx_event.participants.values()])
            loot_per_time = int(amount) / total
            for i, p in enumerate(ctx_event.participants):
                wallet.add_money(p, round(ctx_event.participants[p]["participation"] * loot_per_time))
                money = int(msg.embeds[0].fields[i].value) + ctx_event.participants[p]["participation"] * loot_per_time
                msg.embeds[0].set_field_at(i, name=msg.embeds[0].fields[i].name, value=round(money))
            msg.embeds[0].description = msg.embeds[0].description.replace(t, edit, 1)
            await msg.edit(embed=msg.embeds[0])
            await ctx.channel.send("done", delete_after=5)
            ctx_event.save()
        except KeyError:
            await ctx.channel.send("error, Person does not have a wallet", delete_after=10)
            raise

    @commands.command(help=" ")
    async def pay(self, ctx, person, amount):
        if wallet.check_funds(person) < int(amount):
            await ctx.channel.send(
                "you are about to pay {0} to {1} and he/she doesn't have the funds"
                " are you sure?(y/n)".format(int(amount) - wallet.check_funds(person), person), delete_after=10)
            msg = await bot.wait_for("message", check=suport_functions.checkchannel,timeout=60)
            if msg.content == "y":
                try:
                    wallet.sub_money(person, int(amount))
                    await ctx.channel.send("done", delete_after=5)
                except KeyError:
                    await ctx.channel.send("error, Person does not have a wallet", delete_after=10)
                    raise
                except asyncio.TimeoutError:
                    await ctx.channel.send("error, took to long to respond", delete_after=10)
                    raise
            else:
                await ctx.channel.send("canceled", delete_after=5)
        else:
            try:
                wallet.sub_money(person, int(amount))
                await ctx.channel.send("done", delete_after=5)
            except KeyError:
                await ctx.channel.send("error, Person does not have a wallet", delete_after=10)
                raise

    @commands.command(help=" ")
    async def raw_add(self, ctx, amount, person):
        try:
            wallet.add_money(person, amount)
            await ctx.channel.send("done", delete_after=5)
        except KeyError:
            await ctx.channel.send("error, Person does not have a wallet", delete_after=10)
            raise

    @commands.command(help=" ")
    async def raw_sub(self, ctx, amount, person):
        try:
            wallet.sub_money(person, amount)
            await ctx.channel.send("done", delete_after=5)
        except KeyError:
            await ctx.channel.send("error, Person does not have a wallet", delete_after=10)
            raise

    @commands.command(Help=" ")
    async def where(self, ctx, id, where):
        try:
            ctx_event = event.Event.load_to_memory(id)
            ctx_event.where = where
            msg2 = await ctx.channel.fetch_message(ctx_event.summary)
            t = msg2.embeds[0].description.split("\n")[1].split()[-1]
            edit = str(ctx_event.where)
            msg2.embeds[0].description = msg2.embeds[0].description.replace(t, edit)
            await msg2.edit(embed=msg2.embeds[0])
            ctx_event.save()
            await ctx.channel.send("done", delete_after=5)
        except:
            await ctx.channel.send("error", delete_after=5)
            raise


@bot.event
async def on_voice_state_update(member, before, after):
    category = discord.utils.get(member.guild.categories, name="Gank")
    nick = member.display_name
    if before.channel.category == category:
        ctx_event = event.Event.load_to_memory(str(before.channel.name))
        chnl = discord.utils.get(category.channels, name=str(before.channel.name))
        async for m in chnl.history(limit=20, oldest_first=True):
            if len(m.embeds) != 0 and m.embeds[0].title == str(before.channel.name):
                msg = m
                break
        if nick in ctx_event.participants:
            await ctx_event.updateMembers(msg, nick)
            await msg.reactions[0].remove(member)


@bot.event
async def on_raw_reaction_add(payload):
    await bot.wait_until_ready()
    info = await suport_functions.get_reaction_info(payload, bot)
    msg = info[0]
    user = info[1]
    member = await msg.guild.fetch_member(user.id)
    reactions = [i.emoji for i in msg.reactions]
    category = discord.utils.get(msg.guild.categories, name="Gank")
    nick = member.display_name
    if bot.user != user and msg.author == bot.user:
        embed = msg.embeds[0]
        if embed.title == "Create your event":  # config msg------------
            if reactions[0] == str(payload.emoji):  # gank--------
                if category is None:
                    return
                new_event = event.Event(leader=nick)
                chnl = await msg.guild.create_text_channel("loading", category=category)
                msg2 = await new_event.createmsg(chnl)
                await chnl.edit(name=str(msg2.id)[13:])
                new_event.save()
                await msg.reactions[0].remove(user)
                await msg.guild.create_voice_channel(str(msg2.id)[13:], category=category)
            elif reactions[1] == str(payload.emoji):  # presence list---------------
                pass

        elif embed.title.isdigit():  # gank-----------
            ctx_event = event.Event.load_to_memory(str(msg.id)[13:])
            chlid = discord.utils.get(msg.guild.voice_channels, name=ctx_event.ID)
            chlid2 = discord.utils.get(msg.guild.text_channels, name=ctx_event.ID)
            if str(payload.emoji) == reactions[0]:  # join-------------
                if member.voice is not None:
                    if member.voice.channel.name != ctx_event.ID:
                        await member.move_to(chlid)
                    await ctx_event.updateMembers(msg, nick)
                else:
                    await msg.reactions[0].remove(user)

            elif str(payload.emoji) == msg.reactions[1].emoji:  # start------------
                if "Event is running" not in embed.description and "Event is over" not in embed.description \
                        and nick == ctx_event.leader and ctx_event.participants:
                    ctx_event.event_start()
                    embed.description += "\nEvent is running"
                    await msg.edit(embed=embed)
                else:
                    await msg.reactions[1].remove(user)

            elif str(payload.emoji) == msg.reactions[2].emoji:
                if "Event is over" not in embed.description \
                        and nick == ctx_event.leader:  # stop--------------
                    try:
                        info = ctx_event.end_event()
                    except TypeError:
                        await msg.reactions[2].remove(user)
                        raise
                        return
                    print(info)
                    embed.description = embed.description.replace("Event is running", "Event is over")
                    await msg.edit(embed=embed)
                    embed = discord.Embed(title=embed.title, description="total loot: 0\n" + "chest: None\n"
                                                                         + "date: " + info[0] + "\n" +
                                                                         "duration: " + info[1] + "min\n")
                    names = list(info[2].keys())
                    amount = list(info[2].values())
                    for i in range(len(names)):
                        embed.add_field(name=names[i],
                                        value=amount[i],
                                        inline=False)
                    channel = discord.utils.get(category.text_channels, name="relatorios")
                    msg2 = await channel.send(embed=embed)
                    ctx_event.summary = msg2.id
                    ctx_event.save()
                    for m in chlid.members:
                        await m.move_to(None)
                    await chlid.delete()
                    await chlid2.delete()
                else:
                    await msg.reactions[2].remove(user)

        elif "Loot split is disabled" in embed.description:  # presence list------------

            if reactions[-1] == str(payload.emoji):
                if nick in embed.description:
                    await msg.delete()
                else:
                    await msg.reactions[-1].remove(user)
            else:
                await suport_functions.updateMembers(payload, reactions, msg, nick, user)


@bot.event
async def on_raw_reaction_remove(payload):
    await bot.wait_until_ready()
    info = await suport_functions.get_reaction_info(payload, bot)
    msg = info[0]
    user = info[1]
    embed = msg.embeds[0]
    member = await msg.guild.fetch_member(user.id)
    reactions = [i.emoji for i in msg.reactions]
    i = reactions.index(str(payload.emoji))
    nick = member.display_name
    if msg.author == bot.user:
        embed = embed
        fields = embed.fields
        if "Event is over" not in msg.embeds[0].description:  # gank--------------
            ctx_event = event.Event.load_to_memory(str(msg.id)[13:])
            if str(payload.emoji) == reactions[0]:  # join--------------------------
                await ctx_event.updateMembers(msg, nick)
            if str(payload.emoji) == reactions[1]:
                pass
            if str(payload.emoji) == reactions[2]:
                pass
        elif "Loot split is disabled" in embed.description and str(payload.emoji) != reactions[-1]:  # presence list
            if nick in fields[i].value:
                name = fields[i].name
                value = fields[i].value.replace(nick, "---")
                embed.set_field_at(i, name=name, value=value)
            else:
                pass

        await msg.edit(embed=embed)


bot.add_cog(Loot())
bot.add_cog(Admin())
bot.check(suport_functions.checkServer)
bot.check(suport_functions.checkEvent)

keep_alive()
bot.run(token)
