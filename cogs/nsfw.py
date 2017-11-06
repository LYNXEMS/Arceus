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

def setup(bot):
    bot.add_cog(Nsfw(bot))
