import discord
from discord.ext import commands
# from discord.ext.commands import cooldown
from sys import argv

class Zasady:
    """
    Przestudiuj zasady grupy!
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def simple_embed(self, text, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = text
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def yarr(self):
        """Ej! Nie kradnij Pokemonów innym trenerom!"""
        await self.bot.say("Prosimy o nie pomaganie i nie dyskutowanie o piractwie.")

    @commands.command()
    async def zasady(self):
        """Linki do listy zasad."""
        await self.bot.say("Prosze sprawdz #regulamin dla listy zasad")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z1(self):
        """Displays rule 1."""
        await self.simple_embed("Na czatach obowiązuje atmosfera wspólnego szanowania. Jeśli masz z kimś problem, załatw go na kanale prywatnym. Nie psuj dnia i krwi innym.", title="Zasada 1")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z2(self):
        """Displays rule 2."""
        await self.simple_embed("Zabronione jest obrażanie kogokolwiek i czegokolwiek. Można dyskutować, ale argumenty które mogą być obraźliwe należy formułować z szacunkiem i na temat dyskusji.", title="Zasada 2")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z3(self):
        """Displays rule 3."""
        await self.simple_embed("Na czatach nie nalezy wkraczac do tematow innych czatow. Spam, materialy NSFW i dlugie wiadomosci (Ktore nie sa na Hastebinie itp.) sa zakazane chyba ze powiedziane jest inaczej.", title="Zasada 3")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z4(self):
        """Displays rule 4."""
        await self.simple_embed("Dodatkowe zasady kazdego czatu i ich tematy sa w przypietych wiadmosciach danych czatow.", title="Zasada 4")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z5(self):
        """Displays rule 5."""
        await self.simple_embed("Dyskusje o Friend Code i Dodawaniu się do znajomych powinny byc obslugiwane przez komendy `!fcdodaj3ds` i `!fcznajdz3ds`. Najlepiej uzywac ich na czatach #walki-i-trading albo #hacking. W plikach grupy na Fecebooku istnieje tez Lista FC do ktorej mozna sie dodac.", title="Zasada 5")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z6(self):
        """Displays rule 6."""
        await self.simple_embed("W przypadku naruszenia regulaminu administracja może ukarać użytkownika łamiącego regulamin ostrzeżeniem. Trzy ostrzeżenia oznaczają usuniecie z czatu na czas w zaleznosci od wykroczen.", title="Zasada 6")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z7(self):
        """Displays rule 7."""
        await self.simple_embed("W przypadku drastycznych naruszeń administracja może bezzwłocznie usunąć użytkownika łamiącego regulamin.", title="Zasada 7")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z8(self):
        """Displays rule 8."""
        await self.simple_embed("Jakiekolwiek przyznawanie się do piractwa, postowanie nielegalnie zawartości objętej prawami autorskimi (pliki CIA, CCX, 3DS, WUD, WBFS, ISO, GCN, Titlekeye) lub stron zawierających takie rzeczy są SUROWO ZAKAZANE.", title="Zasada 8")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z9(self):
        """Displays rule 7."""
        await self.simple_embed("Jakakolwiek próba reklamowania (m. in. innych grup i fanpage) bez zgody administracji jest zakazana. Dotyczy to takze ofert handlowych. Publikacja **własnego OC** (original content) jest natomiast mile widziana", title="Zasada 9")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z10(self):
        """Displays rule 8."""
        await self.simple_embed("Samobójstwo i samookaleczenie nie są tematem do żartów, bo uniemożliwiają naprawdę potrzebującym dostęp do odpowiedniej pomocy. Jeśli myślisz, że masz problem skontaktuj się ze specjalistą lub uzyskaj pomoc pod tym adresem: www.telefonzaufania.org.pl", title="Zasada 10")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z11(self):
        """Displays rule 8."""
        await self.simple_embed("Ujawnianie ważnych szczegółów fabuły gier, filmów, książek i innych tekstów kultury młodszych niż siedem lat bez ostrzeżenia i zgody współrozmówców jest zabronione. Szczególnie karane będzie celowe wyjawianie szczegółów fabuły tekstów kultury osobie, która jest w trackie przechodzenia, oglądania, czytania itp. Dotyczy to wtedy również starszych dzieł.", title="Zasada 11")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z12(self):
        """Displays rule 8."""
        await self.simple_embed("Pierwszy i ostatni punkt pełnią rolę punktu zdrowego rozsądku. Jeżeli coś nie jest ujęte w regulaminie, a według administracji zasługuje na potępienie, to osoba funkcyjna ma prawo ukarać użytkownika za dany czyn. Ma to na celu opanowanie bezprecedensowych sytuacji.", title="Zasada 12")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z13(self):
        """Displays rule 8."""
        await self.simple_embed("Ponownie. Szanujmy siebie nawzajem, nie ma absolutnie żadnej potrzeby niszczenia milej atmosfery. Glaskanie adminisracje nie jest zabronione, ale nie jestesmy odpowiedzialni za ugryzienia i oparzenia (szczegolnie te spowodowane przez smoki)", title="Zasada 13")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def newb(self):
        """Displays rule 8."""
        await self.simple_embed("Sugerujemy zweryfikowanie się, żeby uzyskać uprawnienia do wysyłania załączników i rozmawiania na naszych czatach głosowych. Aby to zrobić, należy dołączyć do jednej z naszych zapartnerowanych grup (Polska Społeczność Pokemon, lub Fire Emblem Polska) oraz podać swoją nazwę użytkownika z Facebooka w prywatnej wiadomości członkowi administracji (zielony, niebieski lub różowy kolor nicku). Zapoznaj się z naszym regulaminem i życzymy miłego pobytu na naszym serwerze!", title="Witaj na serwerze Polskiej Społeczności Nintendo!")
		
def setup(bot):
    bot.add_cog(Zasady(bot))
