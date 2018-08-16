import discord
from discord.ext import commands
from sys import argv

class Memy:
    """
    Memiczne komendy zagłady i sponiewierania mentalnego.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def _meme(self, ctx, msg):
        author = ctx.message.author
        await self.bot.say(msg)

    # list memes
    @commands.command(name="listamemow", pass_context=True)
    async def _listamemow(self, ctx):
        """Lista komend wyświetlających memy."""
        # this feels wrong...
        funcs = dir(self)
        msg = "```\n"
        msg += ", ".join(func for func in funcs if func != "bot" and func[0] != "_")
        msg += "```"
        await self._meme(ctx, msg)

    # 3dshacks memes

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def disgusting(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/7udMrNU.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def ammy(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://imgur.com/a/6ZbzT")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def wrongway(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://imgur.com/a/C8LyR")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def heh(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://imgur.com/ZSXWcCv")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def bonerback(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/JouuaJX.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def gay(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/wXxXoq3.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def pissedblanc(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/vHFkNgT.gif")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def guzmangery(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/Ru5g0M7.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def delet(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/oUIjmIB.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def sebe(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/mk2oVTD.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def derpsebe(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://orig00.deviantart.net/d19e/f/2009/198/a/c/buizel_teeter_dance_by_lucario375.gif")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def stopman(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/B3ZPiaX.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def ship(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/hSRIhgF.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def lenny(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/Fui9MPX.png")

    @commands.command(pass_context=True, hidden=True)
    async def rip(self, ctx):
        """Memes."""
        await self._meme(ctx, "Press F to pay respects.")

    @commands.command(pass_context=True, hidden=True)
    async def fuggered(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/15D2bOV.gif")

    @commands.command(pass_context=True, hidden=True)
    async def lucina(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/tnWSXf7.png")

    @commands.command(pass_context=True, hidden=True)
    async def bait(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i0.kym-cdn.com/photos/images/original/001/167/898/67c.png")

    @commands.command(pass_context=True, hidden=True)
    async def abaitening(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/MCiWx7e.png")

    @commands.command(pass_context=True, hidden=True)
    async def perhaps(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://images.discordapp.net/attachments/327787267533963274/337620665287049216/perhaps.PNG?width=454&height=362")

    @commands.command(pass_context=True, hidden=True)
    async def delicje(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i0.kym-cdn.com/photos/images/newsfeed/001/072/505/b98.png")

    @commands.command(pass_context=True, hidden=True)
    async def yos(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/6U45W6F.jpg")

    @commands.command(pass_context=True, hidden=True)
    async def itsbanningtime(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/Xevncee.png")
        await self._meme(ctx, "https://i.imgur.com/nCVaZXB.jpg")

    @commands.command(pass_context=True, hidden=True)
    async def failure(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://vignette3.wikia.nocookie.net/ssb/images/5/54/Failure.png/revision/latest?cb=20131211220605")

    @commands.command(pass_context=True, hidden=True)
    async def gejm(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://ih1.redbubble.net/image.332791515.7996/flat,800x800,075,f.jpg")

    @commands.command(pass_context=True, hidden=True)
    async def clap(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/UYbIZYs.gifv")

    @commands.command(pass_context=True, hidden=True)
    async def soontm(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://cdn.discordapp.com/attachments/336597031604715521/339061186681110528/soon.gif")
		
    @commands.command(pass_context=True, hidden=True)
    async def ninjad(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://cdn.meme.am/cache/instances/folder689/35454689.jpg")		
		
    @commands.command(pass_context=True, hidden=True)
    async def fug(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/yWSOK98.jpg")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def targetacquired(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/WTejTJD.jpg")
 		
    @commands.command(pass_context=True, hidden=True)
    async def whattheraiden(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://cdn.discordapp.com/attachments/327787267533963274/329351954558091264/raiden.png")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def boner(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://imgur.com/fa39o6o")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def ship2(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://imgur.com/5JZJqte")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def derpcopter(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://78.media.tumblr.com/2e45535e0e318bd217db408a662bac5e/tumblr_msdn5wKNQf1sgrojoo1_500.gif")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def urus(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://imgur.com/2dyPgLj")
    	
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def money(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://imgur.com/bvhk33y")
    	
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def pastmoney(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://imgur.com/ym2X6p6")
    	
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def shipisreal(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://imgur.com/fhx6J2J")	



# Load the extension
def setup(bot):
    bot.add_cog(Memy(bot))
