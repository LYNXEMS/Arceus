import discord
from discord.ext import commands
from discord.ext.commands import cooldown
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
        await self.simple_embed("1. Na czatach obowiązuje atmosfera wspólnego szanowania. Jeśli masz z kimś problem, załatw go na kanale prywatnym. Nie psuj dnia i krwi innym.", title="Zasada 1")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z2(self):
        """Displays rule 2."""
        await self.simple_embed("Zabronione jest obrażanie kogokolwiek i czegokolwiek. Można dyskutować, ale argumenty które mogą być obraźliwe należy formułować z szacunkiem i na temat dyskusji.", title="Zasada 2")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z3(self):
        """Displays rule 3."""
        await self.simple_embed("Nie spamuj i staraj się zachować wypowiedzi w dobrej jakości bez wywoływania i kontynuacji dram, nadmiaru emotek itp. Dla dłuższych tekstów używaj stron jak https://hastebin.com/.", title="Zasada 3")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z4(self):
        """Displays rule 4."""
        await self.simple_embed("4. Na czatach nie należy wkraczać do tematów innych czatów. Spam, materiały NSFW i długie wiadomości (Które nie są na Hastebinie itp.) są zakazane, chyba że powiedziane jest inaczej.", title="Zasada 4")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z5(self):
        """Displays rule 5."""
        await self.simple_embed("Jedno konto na użytkownika. Boty na kontach użytkowników dostępne na cały server są zakazane. Jeśli chcesz zmienić konto, najpierw wyjdź starym.", title="Zasada 5")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z6(self):
        """Displays rule 6."""
        await self.simple_embed("Zasada o piractwie... Nie pytaj się jak piracić gry. Nie dziel się materiałem objętym prawami autorskimi. Nie wspominaj o narzędziach stworzonych tylko do piracenia.", title="Zasada 6")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z7(self):
        """Displays rule 7."""
        await self.simple_embed("W przypadku drastycznych naruszeń administracja może bezzwłocznie usunąć użytkownika łamiącego regulamin.", title="Zasada 7")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z8(self):
        """Displays rule 8."""
        await self.simple_embed("Nie wysyłaj informacji osobistych (także prywatnych konwersacji) bez zgody.", title="Zasada 8")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z9(self):
        """Displays rule 7."""
        await self.simple_embed("Zapytaj się Administracji przed reklamowaniem czegokolwiek i zaczekaj na zgodę. Dotyczy to także ofert handlowych. Publikacja własnego OC (original content) jest natomiast mile widziana.", title="Zasada 9")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z10(self):
        """Displays rule 8."""
        await self.simple_embed("Odpowiednie tematy powinny pojawiać się na odpowiednich kanałach. Każdy kanał ma swój temat w opisie kanału i nazwie. Inne tematy lecą na #off-topy lub #off-topy-dwa .", title="Zasada 10")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z11(self):
        """Displays rule 8."""
        await self.simple_embed("Próba unikania zasad będzie uznawana za łamanie ich.", title="Zasada 11")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z12(self):
        """Zasada 12."""
        await self.simple_embed("Dyskusje o Friend Code i dodawaniu się do znajomych powinny być obsługiwane przez bota. W plikach grupy na Facebooku istnieje też Lista FC do której można się dodać.", title="Zasada 12")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z13(self):
        """Zasada 13."""
        await self.simple_embed("Ujawnianie ważnych szczegółów fabuły gier, filmów, książek i innych tekstów kultury młodszych niż siedem lat bez ostrzeżenia i zgody współrozmówców jest zabronione. Szczególnie karane będzie celowe wyjawianie szczegółów fabuły tekstów kultury osobie, która jest w trackie przechodzenia, oglądania, czytania itp. Dotyczy to wtedy również starszych dzieł. Punkt ten nie obowiązuje na kanale #spoilery.", title="Zasada 13")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z14(self):
        """Zasada 14."""
        await self.simple_embed("Pierwszy i ostatni punkt pełnią rolę punktu zdrowego rozsądku. Jeżeli coś nie jest ujęte w regulaminie, a według administracji zasługuje na potępienie, to osoba funkcyjna ma prawo ukarać użytkownika za dany czyn. Ma to na celu opanowanie bezprecedensowych sytuacji.", title="Zasada 14")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def z15(self):
        """Zasada 14."""
        await self.simple_embed("Ponownie. Szanujmy siebie nawzajem, nie ma absolutnie żadnej potrzeby niszczenia milej atmosfery. Głaskanie administracji nie jest zabronione, ale nie jesteśmy odpowiedzialni za ugryzienia i oparzenia (szczególnie te spowodowane przez smoki).", title="Zasada 15")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def nickiavatary(self):
        """Zasada 14."""
        await self.simple_embed("Nicki powinny składać się ze znaków dostępnych na klawiaturze dla tagowania. Administracja może nadać nick nie do zmiany jeśli to zostanie spełnione. Avatary i nicki nie mogą zawierać nic NSFW lub obraźliwego. Nick można zmieniać raz na tydzień komendą `.zmiennick`", title="O Nickach i Avatarach")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def interwencje(self):
        """Interwencje Administracji."""
        await self.simple_embed("Łamanie zasad spowoduje interwencję administracji i kary: Warny, Kicki, Bany, Grzywny w walucie serwerowej lub inne kary.", title="Interwenja Administracji")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def zaproszenie(self):
        """Link zaproszeniowy."""
        await self.simple_embed("To jest permanentny link do servera! Śmiało zapraszaj znajomych. https://discord.gg/hyeeahd", title="Zaproszenie")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def kody(self):
        """Kody."""
        await self.simple_embed("Widoczność niektórych czaty można w pelni włączyc lub wyłączyć, ta komenda będzie także używana do eventów. Komenda ta to `!kod <kod>`. A wiec kody ktore zostaja upublicznione to: `botcommands` dla kanału #bot dla testowania bota i `spoiler` dla kanału #spoilery gdzie dozwolone sa spoilery", title="Kody")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def pokespecial(self):
        """Dzięki Nid, za partnerstwo :3."""
        await self.simple_embed("Jeżeli chcecie dowiedzieć się czegoś więcej na temat mangi i doujinów związanej z pokemonami, zapraszamy na stronę http://pokespecial.com.pl", title="Pokespecial")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def sklep(self):
        """Sklep."""
        await self.simple_embed("Sklep Serwerowy:\n"
            "Dodanie mema do bota - 5000EV\n"
            "Dodanie mema do gotowej komendy, aby była na niego szansa przy wpisywaniu - 3000EV\n"
            "Dodanie emoji na serwer - 10000EV max. 1 na osobę\n"
            "Dodanie własnej odznaki (możesz ją rozdawać innym) - 3000EV\n"
            "Dodanie koloru do listy kolorów tak długo, jak nie przypomina inne - 15000EV\n"
            "Dodanie tła do !profile - 5000EV\n"
            "Dodanie tła do !rank - 4000EV\n"
            "Dodanie tła do level up - 5000EV\n"
            "Wymuszona zmiana nicku - 2000EV\n"
            "Pokemon BR - 3000EV, przy 6 Pokemonach 12000EV\n"
            "Itemy w Pokemonach - 1000EV za sztukę", title="Kody")

def setup(bot):
    bot.add_cog(Zasady(bot))
