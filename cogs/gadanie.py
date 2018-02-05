import discord
from discord.ext import commands
from sys import argv

class Gadanie:
    """
    Moduł do wysyłania wiadomości jako bot.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.has_permissions(ban_members=True)
    @commands.command(hidden=True, pass_context=True)
    async def oglos(self, ctx, *, inp):
        server = ctx.message.server
        await self.bot.send_message(discord.utils.get(server.channels, name='ogloszenia-serwerowe'), inp)

    @commands.has_permissions(ban_members=True)
    @commands.command(hidden=True, pass_context=True)
    async def mow(self, ctx, channel_destination: str, *, inp):
        channel = ctx.message.channel_mentions[0]
        await self.bot.send_message(channel, inp)

    @commands.has_permissions(ban_members=True)
    @commands.command(hidden=True, pass_context=True)
    async def botpisze(self, ctx, channel_destination: str):
        channel = ctx.message.channel_mentions[0]
        await self.bot.send_typing(channel)

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True, pass_context=True)
    async def priv(self, ctx, channel_destination: str, *, inp):
        dest = ctx.message.mentions[0]
        await self.bot.send_message(dest, inp)
		
    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True, pass_context=True)
    async def priv(self, ctx, channel_destination: str, *, inp):
        dest = ctx.message.mentions[0]
        await self.bot.send_message(dest, inp)
		
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.command(hidden=True, pass_context=True)
    async def zaproponuj(self, ctx, *, inp):
        server = ctx.message.server
        em = discord.Embed(description=inp)
        await self.bot.send_message(discord.utils.get(server.channels, name='propozycje'), "Propozycja użytkownika " + ctx.message.author.mention, embed = em)

def setup(bot):
    bot.add_cog(Gadanie(bot))
