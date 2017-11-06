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
    async def mejlej(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i3.kym-cdn.com/photos/images/original/000/811/792/400.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def disgusting(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/7udMrNU.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def wat(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/uyoovgR.png")

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
    async def groodon(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/WO7P2bd.png")

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
    async def k(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/LfNSnnA.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def yas(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/XaJ5nWE.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def dance(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/jD99J8b.gif")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def robotnik(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/dV59VNs.gif")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def sowe(self, ctx):
        """Memes."""
        await self._meme(ctx, "NOSZ KURWA SOWE")		

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def dataintfalco(self, ctx):
        """Memes."""
        await self._meme(ctx, "Dat ain't Falcooo...WOMBO COMBO")		

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def lenny(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/Fui9MPX.png")		

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def wincyjmemow(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i0.kym-cdn.com/photos/images/newsfeed/001/144/795/b08.jpg")		

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def cudzyslow(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://imgflip.com/s/meme/Dr-Evil-Laser.jpg")		
        
    @commands.command(pass_context=True, hidden=True)
    async def rusure(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/dqh3fNi.png")

    @commands.command(pass_context=True, hidden=True)
    async def rip(self, ctx):
        """Memes."""
        await self._meme(ctx, "Press F to pay respects.")

    @commands.command(pass_context=True, hidden=True)
    async def angerattata(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://cdn.discordapp.com/attachments/338350771907067905/340148350760517633/20170725_125057.png")

    @commands.command(pass_context=True, hidden=True)
    async def fuggered(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/15D2bOV.gif")

    @commands.command(pass_context=True, hidden=True)
    async def helpful(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/TaBjzQa.jpg")

    @commands.command(pass_context=True, hidden=True)
    async def scaredgays(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/nRp1Nkk.png")

    @commands.command(pass_context=True, hidden=True)
    async def lucina(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/tnWSXf7.png")

    @commands.command(pass_context=True, hidden=True)
    async def sigh(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://media.discordapp.net/attachments/338350771907067905/340146231458136075/Waga_331942_5854657.jpg?width=655&height=506")

    @commands.command(pass_context=True, hidden=True)
    async def charly(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://media.discordapp.net/attachments/338350771907067905/340145138204672011/FB_IMG_1500837553617.jpg")

    @commands.command(pass_context=True, hidden=True)
    async def bait(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i0.kym-cdn.com/photos/images/original/001/167/898/67c.png")

    @commands.command(pass_context=True, hidden=True)
    async def gottagofat(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://cdn.discordapp.com/attachments/338350771907067905/340143683414261772/received_1304525799664741.gif")

    @commands.command(pass_context=True, hidden=True)
    async def niko(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://s-media-cache-ak0.pinimg.com/236x/87/eb/fa/87ebfa00352db446917d8654cbe505cd--one-shot-game-niko-niko-oneshot.jpg")
        await self._meme(ctx, "**=**")
        await self._meme(ctx, "https://static.pexels.com/photos/126407/pexels-photo-126407.jpeg")

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
    async def hairdresser(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/nkF7thj.jpg")

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
    async def birbd(self, ctx):
        """Memes."""
        await self._meme(ctx, "YOU'VE JUST :b:EEN :b:IR:b:ED")
        await self._meme(ctx, "https://cdn.discordapp.com/attachments/327785258194042890/336964104906342400/obraz.png")

    @commands.command(pass_context=True, hidden=True)
    async def gejm(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://ih1.redbubble.net/image.332791515.7996/flat,800x800,075,f.jpg")

    @commands.command(pass_context=True, hidden=True)
    async def lordandsavior(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i0.kym-cdn.com/photos/images/newsfeed/000/787/435/b9d.jpg")

    @commands.command(pass_context=True, hidden=True)
    async def fite1v1(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i0.kym-cdn.com/photos/images/facebook/000/786/936/d2b.jpg")

    @commands.command(pass_context=True, hidden=True)
    async def lucena(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://img.ifcdn.com/images/0672f32ed83c8d75eaeff9af5bc4ace0d3e81ba1e49639bf82771ae5beec0b5c_1.jpg")

    @commands.command(pass_context=True, hidden=True)
    async def clap(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/UYbIZYs.gifv")

    @commands.command(pass_context=True, hidden=True)
    async def thumbsup(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/hki1IIs.gifv")

    @commands.command(pass_context=True, hidden=True)
    async def bigsmoke(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/vo5l6Fo.jpg\nALL YOU HAD TO DO WAS FOLLOW THE DAMN TRAIN CJ!")

    @commands.command(pass_context=True, hidden=True)
    async def badadmin(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://cdn.discordapp.com/attachments/327794230091186177/339117290350051330/dzg.jpg")

    @commands.command(pass_context=True, hidden=True)
    async def bullshitvisor(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://cdn.discordapp.com/attachments/327787386715242497/339117116907323392/DFcRkdOWsAAXUiA.gif")

    @commands.command(pass_context=True, hidden=True)
    async def itsexplodingtime(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/yrjpXRm.png")

    @commands.command(pass_context=True, hidden=True)
    async def notstableenough(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://33.media.tumblr.com/4bc31d157f42b59e048bec33d975ec49/tumblr_nmr1ddSLp01rw42iio1_1280.gif")

    @commands.command(pass_context=True, hidden=True)
    async def soontm(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://cdn.discordapp.com/attachments/336597031604715521/339061186681110528/soon.gif")

    @commands.command(pass_context=True, hidden=True)
    async def bigorder(self, ctx):
        """Memes."""
        await self._meme(ctx, "I’ll have two number 9s, a number 9 large, a number 6 with extra dip, a number 7, two number 45s, one with cheese, and a large soda.")
		
    @commands.command(pass_context=True, hidden=True)
    async def ninjad(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://cdn.meme.am/cache/instances/folder689/35454689.jpg")		
		
    @commands.command(pass_context=True, hidden=True)
    async def fug(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i.imgur.com/yWSOK98.jpg")		

    @commands.command(pass_context=True, hidden=True)		
    async def thiccbricc(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://lh5.ggpht.com/-HpiQO1VzJ9I/UKqFah7EB8I/AAAAAAAABFU/TS8PpaF_IVE/image_thumb%25255B2%25255D.png?imgmax=800")

    @commands.command(pass_context=True, hidden=True)		
    async def przestraszmajke(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://pm1.narvii.com/6409/ba4e6a9d8361d2aa00ea393fb2d50952d2e4dc4b_hq.jpg")

    @commands.command(pass_context=True, hidden=True)
    async def smolbricc(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://cdn2.ubergizmo.com/wp-content/uploads/2011/03/nintendo-bricked-3DS.jpg")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def switchhax(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://cdn.discordapp.com/attachments/246739894511206410/290463418748633088/IbBzwiv.jpg")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def ripcorn(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://images.discordapp.net/attachments/327787267533963274/328995710253006850/corrin_girl_gyate_by_kirbmaster-dao7u3g.png?width=703&height=491")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def soweintensifies(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://images.discordapp.net/attachments/327787267533963274/328998469463310359/bloggif_595171832f466.gif")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def soweintensifiesintensifies(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://images.discordapp.net/attachments/327787267533963274/328999369892167680/bloggif_59517269b9afa.gif")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def memepolice(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/pExXSAr.jpg")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def dealwithit(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/E64y5HT.mp4")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def imcorny(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/6a5XNau.jpg")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def przestraszraidena(self, ctx):
        """Memes."""
        await self._meme(ctx, "Nic nie może przestraszyć Raidena")
        await self._meme(ctx, "3x !warn Raiden")
        await self._meme(ctx, "Cofam, tylko jedna rzecz moze przestraszyc Raidena")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def targetacquired(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/WTejTJD.jpg")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def kekromalert(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/z1ouj5Y.png")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def prawdziweobliczesowe(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/VrKGY0y.png")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def brrrt(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://i0.wp.com/mi-24.com/wp-content/uploads/2015/02/1414082247_8.jpg?fit=900%2C568")		
 		
    @commands.command(pass_context=True, hidden=True)
    async def whattheraiden(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://cdn.discordapp.com/attachments/327787267533963274/329351954558091264/raiden.png")		
          
    @commands.command(pass_context=True, hidden=True)
    async def killstreak25(self, ctx):
        """Memes."""
        await self._meme(ctx, "http://i.imgur.com/cFhn4jL.png")
          
    @commands.command(pass_context=True, hidden=True)
    async def majke(self, ctx):
        """Memes."""
        await self._meme(ctx, "Nigdy nie bedzie mema na majke")
          
    @commands.command(pass_context=True, hidden=True)
    async def paradoks(self, ctx):
        """Memes."""
        await self._meme(ctx, "To zdanie jest falszywe")
        
    @commands.command(pass_context=True, hidden=True)
    async def ravioboi(self, ctx):
        """Memes."""
        await self._meme(ctx, "*breathes in*")
        await self._meme(ctx, "BOI")
        await self._meme(ctx, "http://cdn.nintendonews.com/wp-content/uploads/2016/10/ravio_yuga_hyrule_warriors_legends_dlc-700x394.jpg")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.channel)
    async def pepe(self, ctx):
        """Memes."""
        await self._meme(ctx, "https://lh3.googleusercontent.com/j5fD3m5qXRNtGYDuajhEtS_etFvU8FE5PogmqTY2hrshDG0_urf_UBeVAyJljoCxdf4=w300")		

# Load the extension
def setup(bot):
    bot.add_cog(Memy(bot))
