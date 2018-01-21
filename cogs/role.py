import discord
from discord.ext import commands
import sys

class Nsfw:
    """
    God why.
    """
    def __init__(self, bot):
        self.bot = bot

        self.get_colors = True
        self.colors = [["❤Z","zielony"],["❤N","niebieski"],["❤Ż","żółty"],["❤R","różowy"],["❤C","czerwony"]]

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

    async def clear_colors(self, usr):
        r = [item[0] for item in self.colors]
        await self.bot.remove_roles(usr, *r)

    async def update_color(self, usr, color):
        await self.clear_colors(usr)
        await self.bot.add_roles(usr, self.get_color(color))

    def get_color(self, color):
        a = [item[0] for item in self.colors if item[1] == color]
        return a[0]

    @commands.command(pass_context=True)
    async def kolor(self, ctx, kolor):
        """Zmienia kolor twojego nicku. Tylko znani. Dostępne kolory to czerwony, zielony, żółty, różowy i niebieski."""
        server = ctx.message.server
        author = ctx.message.author
        debug  = False
        if self.get_colors:
            for i, color in enumerate(self.colors):
                self.colors[i][0] = discord.utils.get(server.roles, name=color[0])
            self.get_colors = False

        if discord.utils.get(server.roles, name="Znany") in author.roles:
            try:
                await self.update_color(author, kolor)
                await self.bot.say("Kolor zmieniony.")
            except BaseException as e:
                await self.bot.say("Podany kolor jest nieprawidłowy.")
                if debug:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    await self.bot.say("EXCEPTION: {} on line {}".format(str(e), exc_tb.tb_lineno))
                pass

            else:
                return
        else:
            await self.bot.say("Nie posiadasz rangi Znany.")

def setup(bot):
    bot.add_cog(Nsfw(bot))
