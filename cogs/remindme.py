import discord
from discord.ext import commands
from .utils.dataIO import fileIO
import os
import asyncio
import time
import logging

class RemindMe:
    """Never forget anything anymore."""

    def __init__(self, bot):
        self.bot = bot
        self.reminders = fileIO("data/remindme/reminders.json", "load")
        self.units = {"minuty" : 60, "godziny" : 3600, "dni" : 86400, "tygodnie": 604800, "miesiące": 2592000}

    @commands.command(pass_context=True)
    async def przypomnij(self, ctx,  ilosc : int, jednostka : str, *, wiadomosc : str):
        """Wysyła Ci <wiadomość> kiedy czas minie.

        Przyjmuje: minuty, godziny, dni, tygodnie, miesiące
        Przykład:
        [p]przypomnij 3 dni Napisać post na grupie."""
        jednostka = jednostka.lower()
        author = ctx.message.author
        s = ""
        if jednostka.endswith("s"):
            jednostka = jednostka[:-1]
            s = "s"
        if not jednostka in self.units:
            await self.bot.say("Zła jednostka czasu. Wybierz: minuty/godziny/dni/tygodnie/miesiące")
            return
        if ilosc < 1:
            await self.bot.say("Ilość nie może być zerowa, lub mniejsza.")
            return
        if len(wiadomosc) > 1960:
            await self.bot.say("Tekst jest za długi")
            return
        seconds = self.units[jednostka] * ilosc
        future = int(time.time()+seconds)
        self.reminders.append({"ID" : author.id, "FUTURE" : future, "TEXT" : wiadomosc})
        logger.info("{} ({}) set a reminder.".format(author.name, author.id))
        await self.bot.say("Przypomnę Ci o tym za: {} {}.".format(str(ilosc), jednostka))
        fileIO("data/remindme/reminders.json", "save", self.reminders)

    @commands.command(pass_context=True)
    async def zapomnij(self, ctx):
        """Usuwa wszystkie Twoje przypomnienia"""
        author = ctx.message.author
        to_remove = []
        for reminder in self.reminders:
            if reminder["ID"] == author.id:
                to_remove.append(reminder)

        if not to_remove == []:
            for reminder in to_remove:
                self.reminders.remove(reminder)
            fileIO("data/remindme/reminders.json", "save", self.reminders)
            await self.bot.say("Wszystkie Twoje przypomnienia zostały usunięte.")
        else:
            await self.bot.say("Nie masz ustawionych żadnych przypomnień.")

    async def sprawdz_przypomnienia(self):
        while self is self.bot.get_cog("RemindMe"):
            to_remove = []
            for reminder in self.reminders:
                if reminder["FUTURE"] <= int(time.time()):
                    try:
                        await self.bot.send_message(discord.User(id=reminder["ID"]), "Miałem Ci o tym przypomnieć:\n{}".format(reminder["TEXT"]))
                    except (discord.errors.Forbidden, discord.errors.NotFound):
                        to_remove.append(reminder)
                    except discord.errors.HTTPException:
                        pass
                    else:
                        to_remove.append(reminder)
            for reminder in to_remove:
                self.reminders.remove(reminder)
            if to_remove:
                fileIO("data/remindme/reminders.json", "save", self.reminders)
            await asyncio.sleep(5)

def check_folders():
    if not os.path.exists("data/remindme"):
        print("Creating data/remindme folder...")
        os.makedirs("data/remindme")

def check_files():
    f = "data/remindme/reminders.json"
    if not fileIO(f, "check"):
        print("Creating empty reminders.json...")
        fileIO(f, "save", [])

def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("remindme")
    if logger.level == 0: # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='data/remindme/reminders.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    n = RemindMe(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.sprawdz_przypomnienia())
    bot.add_cog(n)
