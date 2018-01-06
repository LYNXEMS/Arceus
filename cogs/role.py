import discord
from discord.ext import commands
from sys import argv

class Nsfw:
    """
    God why.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    
    @commands.has_permissions(change_nickname=True)
    @commands.command(hidden=True, pass_context=True)
    async def nsfw(self, ctx):
        """Zdobądź, lub zabierz sobie dostęp do #nsfw."""
        server = ctx.message.server
        author = ctx.message.author
        await self.bot.delete_message(ctx.message)
        if discord.utils.get(server.roles, name="NSFW") in author.roles:
            await self.bot.add_roles(author, discord.utils.get(server.roles, name="NSFW"))
            await self.bot.send_message(author, "Dostęp zabrany")
        else:
            await self.bot.send_message(author, "Zamierzasz dołączyć do kanału NSFW. Wpisując 'tak' oznajmiasz, że wg. obowiązujących praw możesz oglądać treści zezwolone na tym kanale (Wszystko co jest zgodne z zasadami Discorda), oraz nie obwiniasz administracji za złe użycie komendy.")
            answer = await self.bot.wait_for_message(timeout=120, author=author)
            try:
                answ = answer.content
                if answ == "Tak":
                    await self.bot.add_roles(author, discord.utils.get(server.roles, name="NSFW"))
                    await self.bot.send_message(author, "Dostęp przyznany")
                elif answ == "tak":
                    await self.bot.add_roles(author, discord.utils.get(server.roles, name="NSFW"))
                    await self.bot.send_message(author, "Dostęp przyznany")
                else:
                    await self.bot.say("Brak odpowiedzi lub niepoprawna odpowiedź, jeśli chcesz ponownie spróbować uzyskać dostęp, ponownie wpiszk komendę.")
                    return
            except:
                await self.bot.say("Brak odpowiedzi lub niepoprawna odpowiedź, jeśli chcesz ponownie spróbować uzyskać dostęp, ponownie wpiszk komendę.")
                return
				

    @commands.command(pass_context=True)
    async def kod(self, ctx, kod):
        """Zdobądź, lub zabierz sobie dostęp do niektórych kanałów."""
        server = ctx.message.server
        author = ctx.message.author
        await self.bot.delete_message(ctx.message)
        if kod == "fireemblemspoiler":
            if discord.utils.get(server.roles, name="FESPOILER") in author.roles:
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="FESPOILER"))
                await self.bot.send_message(author, "Dostep Odebrany")
            else:
                await self.bot.add_roles(author, discord.utils.get(server.roles, name="FESPOILER"))
                await self.bot.send_message(author, "Dostep Przyznany")
        if kod == "botcommands":
            if discord.utils.get(server.roles, name="BOTCOM") in author.roles:
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="BOTCOM"))
                await self.bot.send_message(author, "Dostep Odebrany")
            else:
                await self.bot.add_roles(author, discord.utils.get(server.roles, name="BOTCOM"))
                await self.bot.send_message(author, "Dostep Przyznany")
        if kod == "spoiler":
            if discord.utils.get(server.roles, name="SPOILER") in author.roles:
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="SPOILER"))
                await self.bot.send_message(author, "Dostep Odebrany")
            else:
                await self.bot.add_roles(author, discord.utils.get(server.roles, name="SPOILER"))
                await self.bot.send_message(author, "Dostep Przyznany")
        else:
            await self.bot.send_message(author, "{} kod nie jest wlasciwy.".format(kod))

    @commands.command(pass_context=True)
    async def kolor(self, ctx, kolor):
        """Zmienia kolor twojego nicku. Tylko znani. Dostępne kolory to czerwony, zielony, żółty, różowy i niebieski."""
        server = ctx.message.server
        author = ctx.message.author
        if discord.utils.get(server.roles, name="Znany") in author.roles:
            if kolor == "czerwony":
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤Z"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤N"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤Ż"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤R"))
                await self.bot.add_roles(author, discord.utils.get(server.roles, name="❤C"))
                await self.bot.sau("Kolor Zmieniony")
            if kolor == "zielony":
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤C"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤N"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤Ż"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤R"))
                await self.bot.add_roles(author, discord.utils.get(server.roles, name="❤Z"))
                await self.bot.say("Kolor Zmieniony")
            if kolor == "żółty":
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤C"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤N"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤Z"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤R"))
                await self.bot.add_roles(author, discord.utils.get(server.roles, name="❤Ż"))
                await self.bot.say("Kolor Zmieniony")
            if kolor == "różowy":
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤C"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤N"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤Z"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤Ż"))
                await self.bot.add_roles(author, discord.utils.get(server.roles, name="❤R"))
                await self.bot.say("Kolor Zmieniony")
            if kolor == "niebieski":
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤C"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤R"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤Z"))
                await self.bot.remove_roles(author, discord.utils.get(server.roles, name="❤Ż"))
                await self.bot.add_roles(author, discord.utils.get(server.roles, name="❤N"))
                await self.bot.say("Kolor Zmieniony")
            else:
                return
        else:
            await self.bot.say("Nie posiadasz rangi Znany.")

def setup(bot):
    bot.add_cog(Nsfw(bot))
