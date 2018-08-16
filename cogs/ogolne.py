import discord
from discord.ext import commands
from .utils.chat_formatting import escape_mass_mentions, italics, pagify
from random import randint
from random import choice
from enum import Enum
from urllib.parse import quote_plus
import datetime
import time
import aiohttp
import asyncio

settings = {"POLL_DURATION" : 60}


class RPS(Enum):
    rock     = "\N{MOYAI}"
    paper    = "\N{PAGE FACING UP}"
    scissors = "\N{BLACK SCISSORS}"


class RPSParser:
    def __init__(self, argument):
        argument = argument.lower()
        if argument == "kamien":
            self.choice = RPS.rock
        elif argument == "papier":
            self.choice = RPS.paper
        elif argument == "nozyce":
            self.choice = RPS.scissors
        else:
            raise


class Ogolne:
    """Komendy ogólne, do wszystkiego i niczego."""

    def __init__(self, bot):
        self.bot = bot
        self.stopwatches = {}
        self.ball = ["Z tego co widzę, to tak.", "Na pewno.", "Zdecydowanie tak.", "Prawdopodobnie tak.", "Bardzo możliwe.", "Wygląda na to, że tak.",
                     "Zapytaj Fluffa.", "Zapytaj Guzmy.", "Zapytaj Aloesa.", "Gwiazdy wskazują, że tak.", "Gwiazdy wskazują, że nie.", "Nie jestem pewny.", "Nie mam pojęcia lol",
					 "Myślę, że tak.", "Bez wątpienia.", "Yep.", "Tak.", "Nie.", "Nope.", "Tak. Nie. Może?", "Tak, na sto procent tak.",
					 "Nie wydaje mi się.", "Jestem pewny, że nie.", "Możesz na to liczyć.", "Odpowiedź jest niejasna, spróbuj ponownie.",
                     "Ukradli mi kulę, spróbuj ponownie później.", "Sam/a sobie odpowiedz na to pytanie.", "Nie powiem ci, hihi.", "NOSZ KURWA SOWE", "Majke popsuła mi system, spróbuj jeszcze raz.",
					 "Kula czasowo niedostępna, spróbuj później.", "Nie jestem pewny, nie widzę odpowiedzi...", "Skup się i zadaj to pytanie jeszcze raz.",
                     "Eeeee... nie.", "Nie liczyłbym na to.", "Tak, jeżeli oddasz mi cześć.", "Moja odpowiedź brzmi - nie.", "Moje źródła mówią mi, że nie.",
					 "Moja odpowiedź brzmi - tak.", "Oczywiście.", "Nie ma szans.", "Raczej tak.", "Raczej nie.", "Wygląda na to, że nie.", "Wątpię.", "You don't have enough badges to train me.", 
					 "Giratina mnie trolluje, spróbuj ponownie później", "Jeden Pokébreeder powie tak, inny Pokébreeder powie nie...", "Szybciej Zekrom zbieleje.", "Zapomnij o tym."]
        self.poll_sessions = []

    @commands.command(hidden=True)
    async def ping(self):
        """Pong."""
        await self.bot.say("Pong.")

    @commands.command()
    async def wybierz(self, *choices):
        """Wybiera między paroma opcjami.

        Aby zaznaczyć opcję z kilku słów, należy wpisać ją w cudzysłów.
        """
        choices = [escape_mass_mentions(c) for c in choices]
        if len(choices) < 2:
            await self.bot.say('Co to, Fire Emblem Awakening? Daj mi więcej niż jedną opcję, z której mogę wybrać!')
        else:
            await self.bot.say(choice(choices))

    @commands.command(pass_context=True)
    async def rzutkostka(self, ctx, number : int = 100):
        """Wyrzuca losowy numer pomiędzy 1 a określoną, wybraną przez użytkownika liczbą.

        Domyślna liczba to 100.
        """
        author = ctx.message.author
        if number > 1:
            n = randint(1, number)
            await self.bot.say("{} :game_die: {} :game_die:".format(author.mention, n))
        else:
            await self.bot.say("{} Rzuć jednościenną kostką. I dare you. I double dare you, dragonfu**er. ;P".format(author.mention))

    @commands.command(pass_context=True)
    async def rzutmoneta(self, ctx, user : discord.Member=None):
        """Rzuca monetą... lub użytkownikiem.

        Domyślnie rzuca monetą.
        """
        if user != None:
            msg = ""
            if user.id == self.bot.user.id:
                user = ctx.message.author
                msg = "Hah, powodzenia z tym. Myślisz, że jesteś zabawny/a? Zobaczymy, co powiesz po *TYM*:\n\n"
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.display_name.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            await self.bot.say(msg + "(╯°□°）╯︵ " + name[::-1])
        else:
            await self.bot.say("*rzuca monetą, wynik to... " + choice(["ORZEŁ!*", "RESZKA!*"]))

    @commands.command(pass_context=True)
    async def rps(self, ctx, your_choice : RPSParser):
        """Zagraj w kamień, papier, nożyce!"""
        author = ctx.message.author
        player_choice = your_choice.choice
        red_choice = choice((RPS.rock, RPS.paper, RPS.scissors))
        cond = {
                (RPS.rock,     RPS.paper)    : False,
                (RPS.rock,     RPS.scissors) : True,
                (RPS.paper,    RPS.rock)     : True,
                (RPS.paper,    RPS.scissors) : False,
                (RPS.scissors, RPS.rock)     : False,
                (RPS.scissors, RPS.paper)    : True
               }

        if red_choice == player_choice:
            outcome = None # Tie
        else:
            outcome = cond[(player_choice, red_choice)]

        if outcome is True:
            await self.bot.say("{} Argh, Przegrałem {}!"
                               "".format(red_choice.value, author.mention))
        elif outcome is False:
            await self.bot.say("{} Ha, Wygrałem {}!"
                               "".format(red_choice.value, author.mention))
        else:
            await self.bot.say("{} Remis {}!"
                               "".format(red_choice.value, author.mention))

    @commands.command(name="8", aliases=["8ball"])
    async def _8ball(self, *, question : str):
        """Zadaj 8ball pytanie.

        Pytania muszą kończyć się znakiem zapytania.
        """
        if question.endswith("?") and question != "?":
            await self.bot.say("`" + choice(self.ball) + "`")
        else:
            await self.bot.say("To nie wygląda jak pytanie - pamiętaj o znaku zapytania.")

    @commands.command(aliases=["sw"], pass_context=True)
    async def stoper(self, ctx):
        """Włącza/Wyłącza stoper."""
        author = ctx.message.author
        if not author.id in self.stopwatches:
            self.stopwatches[author.id] = int(time.perf_counter())
            await self.bot.say(author.mention + " Stoper włączony!")
        else:
            tmp = abs(self.stopwatches[author.id] - int(time.perf_counter()))
            tmp = str(datetime.timedelta(seconds=tmp))
            await self.bot.say(author.mention + " Stoper wyłączony! Time: **" + tmp + "**")
            self.stopwatches.pop(author.id, None)

    @commands.command()
    async def lmgtfy(self, *, search_terms : str):
        """Tworzy link do lmgtfy na wskazany temat."""
        search_terms = escape_mass_mentions(search_terms.replace(" ", "+"))
        await self.bot.say("https://lmgtfy.com/?q={}".format(search_terms))

    @commands.command(no_pm=True, hidden=True)
    async def tul(self, user : discord.Member, intensity : int=1):
        """Bo każdy, nawet smoki, uwielbiają przytulasy!

        Do 10 poziomów intensywności przytuleń."""
        name = italics(user.display_name)
        if intensity <= 0:
            msg = "(っ˘̩╭╮˘̩)っ" + name
        elif intensity <= 3:
            msg = "(っ´▽｀)っ" + name
        elif intensity <= 6:
            msg = "╰(*´︶`*)╯" + name
        elif intensity <= 9:
            msg = "(つ≧▽≦)つ" + name
        elif intensity >= 10:
            msg = "(づ￣ ³￣)づ{} ⊂(´・ω・｀⊂)".format(name)
        await self.bot.say(msg)

    @commands.command(pass_context=True, no_pm=True)
    async def infouzytkownik(self, ctx, *, user: discord.Member=None):
        """Pokazuje informacje o użytkowniku."""
        author = ctx.message.author
        server = ctx.message.server

        if not user:
            user = author

        roles = [x.name for x in user.roles if x.name != "@everyone"]

        joined_at = self.fetch_joined_at(user, server)
        since_created = (ctx.message.timestamp - user.created_at).days
        since_joined = (ctx.message.timestamp - joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        member_number = sorted(server.members,
                               key=lambda m: m.joined_at).index(user) + 1

        created_on = "{}\n({} dni temu)".format(user_created, since_created)
        joined_on = "{}\n({} dni temu)".format(user_joined, since_joined)

        game = "Chilluje będąc {}".format(user.status)

        if user.game is None:
            pass
        elif user.game.url is None:
            game = "Gra w {}".format(user.game)
        else:
            game = "Streamuje: [{}]({})".format(user.game, user.game.url)

        if roles:
            roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                       if x.name != "@everyone"].index)
            roles = ", ".join(roles)
        else:
            roles = "None"

        data = discord.Embed(description=game, colour=user.colour)
        data.add_field(name="Dołączył do Discorda", value=created_on)
        data.add_field(name="Dołączył do tego serwera", value=joined_on)
        data.add_field(name="Role", value=roles, inline=False)
        data.set_footer(text="Członek #{} | User ID:{}"
                             "".format(member_number, user.id))

        name = str(user)
        name = " ~ ".join((name, user.nick)) if user.nick else name

        if user.avatar_url:
            data.set_author(name=name, url=user.avatar_url)
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(name=name)

        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            await self.bot.say("Potrzebuje zezwolenia `Embed links` "
                               "aby to wysłać.")

    @commands.command(pass_context=True, no_pm=True)
    async def serwerinfo(self, ctx):
        """Pokazuje informacje o serwerze."""
        server = ctx.message.server
        online = len([m.status for m in server.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])
        total_users = len(server.members)
        text_channels = len([x for x in server.channels
                             if x.type == discord.ChannelType.text])
        voice_channels = len(server.channels) - text_channels
        passed = (ctx.message.timestamp - server.created_at).days
        created_at = ("Od {}. To już {} dni temu!"
                      "".format(server.created_at.strftime("%d %b %Y %H:%M"),
                                passed))

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)

        data = discord.Embed(
            description=created_at,
            colour=discord.Colour(value=colour))
        data.add_field(name="Region", value=str(server.region))
        data.add_field(name="Użytkownicy", value="{}/{}".format(online, total_users))
        data.add_field(name="Kanały tekstowe", value=text_channels)
        data.add_field(name="Kanały głosowe", value=voice_channels)
        data.add_field(name="Role", value=len(server.roles))
        data.add_field(name="Właściciel", value=str(server.owner))
        data.set_footer(text="ID serwera: " + server.id)

        if server.icon_url:
            data.set_author(name=server.name, url=server.icon_url)
            data.set_thumbnail(url=server.icon_url)
        else:
            data.set_author(name=server.name)

        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            await self.bot.say("Potrzebuje zezwolenia `Embed links` "
                               "aby to wysłać.")

    @commands.command()
    async def urban(self, *, search_terms : str, definition_number : int=1):
        """Urban Dictionary search

        Definition number must be between 1 and 10"""
        def encode(s):
            return quote_plus(s, encoding='utf-8', errors='replace')

        # definition_number is just there to show up in the help
        # all this mess is to avoid forcing double quotes on the user

        search_terms = search_terms.split(" ")
        try:
            if len(search_terms) > 1:
                pos = int(search_terms[-1]) - 1
                search_terms = search_terms[:-1]
            else:
                pos = 0
            if pos not in range(0, 11): # API only provides the
                pos = 0                 # top 10 definitions
        except ValueError:
            pos = 0

        search_terms = "+".join([encode(s) for s in search_terms])
        url = "http://api.urbandictionary.com/v0/define?term=" + search_terms
        try:
            async with aiohttp.get(url) as r:
                result = await r.json()
            if result["list"]:
                definition = result['list'][pos]['definition']
                example = result['list'][pos]['example']
                defs = len(result['list'])
                msg = ("**Definicja #{} z {}:\n**{}\n\n"
                       "**Przykład:\n**{}".format(pos+1, defs, definition,
                                                 example))
                msg = pagify(msg, ["\n"])
                for page in msg:
                    await self.bot.say(page)
            else:
                await self.bot.say("Nie znalazłam żadnych wyników co do tego, czego wyszukiwaleś/aś.")
        except IndexError:
            await self.bot.say("Nie ma definicji na #{}".format(pos+1))
        except:
            await self.bot.say("I am error. Coś poszło nie tak. :< ")

    @commands.command(pass_context=True, no_pm=True)
    async def oankieta(self, ctx, *text):
        """Otwiera/zamyka ankietę

        Przykład użycia:
        ankieta Czy to jest ankieta?;Tak;Nie;Może
        ankieta stop"""
        message = ctx.message
        if len(text) == 1:
            if text[0].lower() == "stop":
                await self.endpoll(message)
                return
        if not self.getPollByChannel(message):
            check = " ".join(text).lower()
            if "@everyone" in check or "@here" in check:
                await self.bot.say("Nie jesteś omnipotentny, niezła próba.")
                return
            p = NewPoll(message, " ".join(text), self)
            if p.valid:
                self.poll_sessions.append(p)
                await p.start()
            else:
                await self.bot.say("ankieta pytanie;odpowiedz1;odpowiedz2 (...)")
        else:
            await self.bot.say("Na tym kanale już trwa jakaś ankieta.")

    async def endpoll(self, message):
        if self.getPollByChannel(message):
            p = self.getPollByChannel(message)
            if p.author == message.author.id: # or isMemberAdmin(message)
                await self.getPollByChannel(message).endPoll()
            else:
                await self.bot.say("Tylko autor ankiety i admini mogą zastopować zbieranie głosów.")
        else:
            await self.bot.say("Na tym kanale nie trwa żadna ankieta. Może spróbuj zrobić jakąś?")

    def getPollByChannel(self, message):
        for poll in self.poll_sessions:
            if poll.channel == message.channel:
                return poll
        return False

    async def check_poll_votes(self, message):
        if message.author.id != self.bot.user.id:
            if self.getPollByChannel(message):
                    self.getPollByChannel(message).checkAnswer(message)

    def fetch_joined_at(self, user, server):
        """Na specjalne wypadki, dla kogoś specjalnego :^)"""
        if user.id == "96130341705637888" and server.id == "133049272517001216":
            return datetime.datetime(2016, 1, 10, 6, 8, 4, 443000)
        else:
            return user.joined_at

class NewPoll():
    def __init__(self, message, text, main):
        self.channel = message.channel
        self.author = message.author.id
        self.client = main.bot
        self.poll_sessions = main.poll_sessions
        msg = [ans.strip() for ans in text.split(";")]
        if len(msg) < 2: # Needs at least one question and 2 choices
            self.valid = False
            return None
        else:
            self.valid = True
        self.already_voted = []
        self.question = msg[0]
        msg.remove(self.question)
        self.answers = {}
        i = 1
        for answer in msg: # {id : {answer, votes}}
            self.answers[i] = {"ANSWER" : answer, "VOTES" : 0}
            i += 1

    async def start(self):
        msg = "**ANKIETA ROZPOCZĘTA!**\n\n{}\n\n".format(self.question)
        for id, data in self.answers.items():
            msg += "{}. *{}*\n".format(id, data["ANSWER"])
        msg += "\nWpisz numer obok odpowiedzi, aby na nią zagłosować!"
        await self.client.send_message(self.channel, msg)
        await asyncio.sleep(settings["POLL_DURATION"])
        if self.valid:
            await self.endPoll()

    async def endPoll(self):
        self.valid = False
        msg = "**ANKIETA ZAKOŃCZONA!**\n\n{}\n\n".format(self.question)
        for data in self.answers.values():
            msg += "*{}* - {} głosów\n".format(data["ANSWER"], str(data["VOTES"]))
        await self.client.send_message(self.channel, msg)
        self.poll_sessions.remove(self)

    def checkAnswer(self, message):
        try:
            i = int(message.content)
            if i in self.answers.keys():
                if message.author.id not in self.already_voted:
                    data = self.answers[i]
                    data["VOTES"] += 1
                    self.answers[i] = data
                    self.already_voted.append(message.author.id)
        except ValueError:
            pass

def setup(bot):
    n = Ogolne(bot)
    bot.add_listener(n.check_poll_votes, "on_message")
    bot.add_cog(n)
