import json
from datetime import datetime

import discord

import suport_functions


class Event:

    def load_to_memory(ID:str):
        with open("events.json", "r") as file:
            lst = json.load(file)
            ctx = lst[ID]
            return Event(ID, ctx["leader"], ctx["ip"], ctx["date"], ctx["where"], ctx["time"], ctx["participants"],
                         ctx["amount"], ctx["status"], ctx["summary"])

    def __init__(self, ID=None, leader=None, ip="*",
                 date=str(datetime.utcnow().day) + "-" + str(datetime.utcnow().month),
                 where=None, time=None, participants={}, amount=0, status="stopped", summary=None):
        self.ID = ID
        self.ip = ip
        self.date = date
        self.leader = leader
        self.where = where
        self.amount = amount
        self.participants = participants
        self.status = status
        self.time = time
        self.summary = summary

    async def createmsg(self, channel):
        cls = ["join", "start", "stop"]
        reactions = [":wheelchair:", ":white_check_mark:", ":no_entry:"]
        message_1 = discord.Embed(title="loading", description="content: -\n"+"IP: "+str(self.ip)+"\n")
        message_1.add_field(name="Participants", value="-")
        msg2 = await channel.send(embed=message_1)
        self.ID = str(msg2.id)[13:]
        message_1.title = self.ID
        await msg2.edit(embed=message_1)
        await suport_functions.add_reactions(msg2, cls, reactions)
        self.save()
        return msg2

    async def updateMembers(self, msg, nick):
        embed = msg.embeds[0]
        field = embed.fields[0]
        t = [i.display_name async for i in msg.reactions[0].users()]
        if field.value == "-":
            field.value = ""
        if nick not in field.value and nick in t:
            v = field.value + "\n" + nick
            embed.set_field_at(0, name=field.name, value=v)
            self.participants[nick] = {"start": suport_functions.get_time(), "spent": 0, "participation": 0}
        elif nick in self.participants.keys():
            v = field.value.replace(nick, "")
            if v == "":
                v = "-"
            embed.set_field_at(0, name=field.name, value=v)
            self.participants[nick]["spent"] = suport_functions.time_passed(self.participants[nick]["start"])
        self.save()
        await msg.edit(embed=embed)


    def event_start(self):
        self.time = suport_functions.get_time()
        self.amount = 0
        self.status = "running"
        for person in self.participants.keys():
            self.participants[person] = {"start": suport_functions.get_time(), "spent": 0, "participation": 0}
        self.save()

    def save(self):
        with open("events.json", "r") as file:
            lst = json.load(file)
        if self.ID not in lst.keys():
            lst[self.ID] = {}
        lst[self.ID]["ip"] = self.ip
        lst[self.ID]["date"] = self.date
        lst[self.ID]["leader"] = self.leader
        lst[self.ID]["where"] = self.where
        lst[self.ID]["status"] = self.status
        lst[self.ID]["amount"] = self.amount
        lst[self.ID]["time"] = self.time
        lst[self.ID]["participants"] = self.participants
        lst[self.ID]["summary"] = self.summary
        with open("events.json", "w") as file:
            json.dump(lst, file, indent=4)

    def end_event(self):
        self.time = suport_functions.time_passed(self.time)
        for person in self.participants.values():
            person["spent"] = suport_functions.time_passed(person["start"])
            person["participation"] = round(person["spent"]/self.time, 2)
            lst = {n: p["participation"] for p, n in zip(self.participants.values(), self.participants.keys())}
        self.save()
        return [self.date, str(self.time/60), lst]
