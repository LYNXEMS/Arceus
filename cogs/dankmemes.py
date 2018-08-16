import time
import os 
import os.path
import random
import shutil
from typing import List

import aiohttp
import discord
from discord.ext import commands

from .utils.dataIO import dataIO
from .utils import checks, chat_formatting as cf


default_settings = {
    "next_ids": {}
}


class RandImage:

    """Create categories and add images to the categories, then fetch a random
    one from a category.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.base = "data/randimage/"
        self.settings_path = "data/randimage/settings.json"
        self.settings = dataIO.load_json(self.settings_path)

    def _list_image_dirs(self, server_id: str) -> List[str]:
        ret = []
        for thing in os.listdir(os.path.join(self.base, server_id)):
            if os.path.isdir(os.path.join(self.base, server_id, thing)):
                ret.append(thing)
        return ret

    @commands.command(pass_context=True, no_pm=True, name="mem")
    async def _mem(self, ctx: commands.Context, category: str):
        """Wysyła mema"""

        await self.bot.type()

        server = ctx.message.server

        if server.id not in os.listdir(self.base):
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)
            os.makedirs(os.path.join(self.base, server.id))

        if category not in self._list_image_dirs(server.id):
            await self.bot.reply(cf.error("Kategoria nie znaleziona."))
            return

        direc = os.path.join(self.base, server.id, category)
        
        ls = os.listdir(os.path.join(self.base, server.id, category))

        if not ls:
            await self.bot.reply(
                cf.warning("W tej kategorii nie ma memów."))
            return
        x=1
        while x==1:
            img = os.path.join(direc, random.choice(ls))
            
            if img.endswith('.ini'):
                pass
            else:
                x=0

        await self.bot.upload(img)   

    @commands.command(pass_context=True, no_pm=True, name="dodajkategorie")
    @checks.mod_or_permissions(kick_members=True)
    async def _dodajkategorie(self, ctx: commands.Context, new_category: str):
        """Dodaje nową ktegorię."""

        await self.bot.type()

        server = ctx.message.server

        if server.id not in os.listdir(self.base):
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)
            os.makedirs(os.path.join(self.base, server.id))

        if new_category in self._list_image_dirs(server.id):
            await self.bot.reply(cf.error("Kategoria już istnieje."))
            return

        self.settings[server.id]["next_ids"][new_category] = 1
        dataIO.save_json(self.settings_path, self.settings)
        os.makedirs(os.path.join(self.base, server.id, new_category))

        await self.bot.reply(cf.info("Kategoria stworzona."))

    @commands.command(pass_context=True, no_pm=True, name="usunkategorie")
    @checks.mod_or_permissions(kick_members=True)
    async def _usunkategorie(self, ctx: commands.Context, category: str):
        """Usuwa kategorię z obrazkami."""

        await self.bot.type()

        server = ctx.message.server

        if server.id not in os.listdir(self.base):
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)
            os.makedirs(os.path.join(self.base, server.id))

        if category not in self._list_image_dirs(server.id):
            await self.bot.reply(cf.error("Category not found."))
            return

        num_imgs = len(os.listdir(os.path.join(self.base, server.id,
                                               category)))

        await self.bot.reply(cf.question(
            "Chcesz usunąć kategorię."
            " Na pewno? (yes/no)"))

        answer = await self.bot.wait_for_message(timeout=15,
                                                 author=ctx.message.author)

        await self.bot.type()

        if answer is None or answer.content.lower().strip() != "yes":
            await self.bot.reply("Kategoria nie usunięta.")
            return

        del self.settings[server.id]["next_ids"][category]
        dataIO.save_json(self.settings_path, self.settings)
        shutil.rmtree(os.path.join(self.base, server.id, category))

        await self.bot.reply(cf.info("Kategoria usunięta."))

    @commands.command(pass_context=True, no_pm=True, name="memy")
    async def _memy(self, ctx: commands.Context):
        """Wysyła wszystkie kategorie."""

        await self.bot.type()

        server = ctx.message.server

        if server.id not in os.listdir(self.base):
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)
            os.makedirs(os.path.join(self.base, server.id))

        categories = self._list_image_dirs(server.id)

        if len(categories) == 0:
            await self.bot.reply(cf.warning("Nie ma kategorii."))
            return

        strbuffer = []
        for cat in categories:
            imgs_in_cat = len(os.listdir(os.path.join(self.base, server.id,
                                                      cat)))
            strbuffer.append("{} - {} image{}".format(
                cat, imgs_in_cat, "" if imgs_in_cat == 1 else "s"))

        mess = "```"
        for line in strbuffer:
            if len(mess) + len(line) + 4 < 2000:
                mess += "\n" + line
            else:
                mess += "```"
                await self.bot.whisper(mess)
                mess = "```" + line
        if mess != "":
            mess += "```"
            await self.bot.whisper(mess)

        await self.bot.reply("Sprawdź DM!")

    @commands.command(pass_context=True, no_pm=True, name="dodajmema")
    @checks.mod_or_permissions(kick_members=True)
    async def _dodajmema(self, ctx: commands.Context, category: str,
                        image_url: str=None):
        """Dodaje mema do kategorii."""

        await self.bot.type()

        server = ctx.message.server

        if server.id not in os.listdir(self.base):
            self.settings[server.id] = default_settings
            dataIO.save_json(self.settings_path, self.settings)
            os.makedirs(os.path.join(self.base, server.id))

        if category not in self._list_image_dirs(server.id):
            await self.bot.reply(cf.error("Nie znaleziono kategorii."))
            return

        attach = ctx.message.attachments
        if len(attach) > 1 or (attach and image_url):
            await self.bot.reply(cf.error("Jeden plik naraz."))
            return

        url = ""
        filename = ""
        if attach:
            a = attach[0]
            url = a["url"]
            filename = a["filename"]
        elif image_url:
            url = image_url
            filename = os.path.basename(
                "_".join(url.split()).replace("%20", "_"))
        else:
            await self.bot.reply(cf.error(
                "Załącz obrazek, albo"
                " daj bezpośredni do niego link."))
            return

        new_id = str(self.settings[server.id]["next_ids"][category])
        self.settings[server.id]["next_ids"][category] += 1
        dataIO.save_json(self.settings_path, self.settings)

        ext = os.path.splitext(filename)[1]
        filepath = os.path.join(
            self.base, server.id, category, "{}_{}.{}".format(
                category, new_id, ext))

        async with aiohttp.get(url) as new_sound:
            f = open(filepath, "wb")
            f.write(await new_sound.read())
            f.close()

        await self.bot.reply(cf.info("Dodano mema."))


def check_folders():
    if not os.path.exists("data/randimage"):
        print("Creating data/randimage directory...")
        os.makedirs("data/randimage")


def check_files():
    f = "data/randimage/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating data/randimage/settings.json...")
        dataIO.save_json(f, {})


def setup(bot: commands.Bot):
    check_folders()
    check_files()
    bot.add_cog(RandImage(bot))
