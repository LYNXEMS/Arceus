import asyncio
import os
import sys
sys.path.insert(0, "lib")
import logging
import logging.handlers
import traceback
import datetime
import subprocess

try:
    from discord.ext import commands
    import discord
except ImportError:
    print("Discord.py nie jest zainstalowany. Jeśli to czytasz znaczy że nie powinieneś używać tego bota.")
    sys.exit(1)

from cogs.utils.settings import Settings
from cogs.utils.dataIO import dataIO
from cogs.utils.chat_formatting import inline
from collections import Counter
from io import TextIOWrapper

# Bot Arceus, zrobiony przez fluffa

description = "Arceus - wielofunkcyjny bot stworzony przez Fluffa"


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):

        def prefix_manager(bot, message):
            """
            Zwraca prefixy serverowe, a jeśli nie istnieją, globalne

            wymaga instancji bota i wiadomości
            """
            return bot.settings.get_prefixes(message.server)

        self.counter = Counter()
        self.uptime = datetime.datetime.utcnow()  # Odświerzane przed logowaniem
        self._message_modifiers = []
        self.settings = Settings()
        self._intro_displayed = False
        self._shutdown_mode = None
        self.logger = set_logger(self)
        self._last_exception = None
        self.oauth_url = ""
        if 'self_bot' in kwargs:
            self.settings.self_bot = kwargs['self_bot']
        else:
            kwargs['self_bot'] = self.settings.self_bot
            if self.settings.self_bot:
                kwargs['pm_help'] = False
        super().__init__(*args, command_prefix=prefix_manager, **kwargs)

    async def send_message(self, *args, **kwargs):
        if self._message_modifiers:
            if "content" in kwargs:
                pass
            elif len(args) == 2:
                args = list(args)
                kwargs["content"] = args.pop()
            else:
                return await super().send_message(*args, **kwargs)

            content = kwargs['content']
            for m in self._message_modifiers:
                try:
                    content = str(m(content))
                except:   # złe modyfikatory
                    pass  # nie zepsują wiadomości
            kwargs['content'] = content

        return await super().send_message(*args, **kwargs)

    async def shutdown(self, *, restart=False):
        """wyłącza bota z kodem 1

        jeśli restart=true bot spróbuje się zrestartować z kodem 26"""
        self._shutdown_mode = not restart
        await self.logout()

    def add_message_modifier(self, func):
        """
        Dodaje modyfikator do wiadomości

        Można wywołać coś zawartością wiadomości
        przed wysłaniem wiadmości funkcja zostanie zawołana z treścią jako argumentem
        Excepcje wyrzucone zostaną wyciszone
        """
        if not callable(func):
            raise TypeError("Funkcja modyfikatora wiadmości "
                            "musi bć zdolna do bycia wywołaną.")

        self._message_modifiers.append(func)

    def remove_message_modifier(self, func):
        """Usuwa modyfikator wiadomości"""
        if func not in self._message_modifiers:
            raise RuntimeError("Funkcja nie istnieje w modyfikatorach wiadomości")

        self._message_modifiers.remove(func)

    def clear_message_modifiers(self):
        """Usuwa wszystkie modyfikatory wiadmości"""
        self._message_modifiers.clear()

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = self.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await self.send_message(ctx.message.channel, page)
        else:
            pages = self.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await self.send_message(ctx.message.channel, page)

    def user_allowed(self, message):
        author = message.author

        if author.bot:
            return False

        if author == self.user:
            return self.settings.self_bot

        mod_cog = self.get_cog('Mod')
        global_ignores = self.get_cog('Owner').global_ignores

        if self.settings.owner == author.id:
            return True

        if author.id in global_ignores["blacklist"]:
            return False

        if global_ignores["whitelist"]:
            if author.id not in global_ignores["whitelist"]:
                return False

        if not message.channel.is_private:
            server = message.server
            names = (self.settings.get_server_admin(
                server), self.settings.get_server_mod(server))
            results = map(
                lambda name: discord.utils.get(author.roles, name=name),
                names)
            for r in results:
                if r is not None:
                    return True

        if mod_cog is not None:
            if not message.channel.is_private:
                if message.server.id in mod_cog.ignore_list["SERVERS"]:
                    return False

                if message.channel.id in mod_cog.ignore_list["CHANNELS"]:
                    return False

        return True

    async def pip_install(self, name, *, timeout=None):
        """
        Bezpiecznie instaluje pakiet pip w folderze lib

        Zwraca boolean jeśli się powiodło
        """

        IS_MAC = sys.platform == "darwin"
        interpreter = sys.executable

        if interpreter is None:
            raise RuntimeError("Nie moge znaleźć interpretatora Pythona")

        args = [
            interpreter, "-m",
            "pip", "install",
            "--upgrade",
            "--target", "lib",
            name
        ]

        if IS_MAC: # --target is a problem on Homebrew. See PR #552
            args.remove("--target")
            args.remove("lib")

        def install():
            code = subprocess.call(args)
            sys.path_importer_cache = {}
            return not bool(code)

        response = self.loop.run_in_executor(None, install)
        return await asyncio.wait_for(response, timeout=timeout)


class Formatter(commands.HelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _add_subcommands_to_page(self, max_width, commands):
        for name, command in sorted(commands, key=lambda t: t[0]):
            if name in command.aliases:
                # pomiń aliasy
                continue

            entry = '  {0:<{width}} {1}'.format(name, command.short_doc,
                                                width=max_width)
            shortened = self.shorten(entry)
            self._paginator.add_line(shortened)


def initialize(bot_class=Bot, formatter_class=Formatter):
    formatter = formatter_class(show_check_failure=False)

    bot = bot_class(formatter=formatter, description=description, pm_help=None)

    import __main__
    __main__.send_cmd_help = bot.send_cmd_help  # Wsteczna
    __main__.user_allowed = bot.user_allowed    # kompatybilność
    __main__.settings = bot.settings            # ssie

    async def get_oauth_url():
        try:
            data = await bot.application_info()
        except Exception as e:
            return "Nie mogłem znaleźć linka z zaproszeniem.Error: {}".format(e)
        return discord.utils.oauth_url(data.id)

    async def set_bot_owner():
        if bot.settings.self_bot:
            bot.settings.owner = bot.user.id
            return "[Selfbot mode]"

        if bot.settings.owner:
            owner = discord.utils.get(bot.get_all_members(),
                                      id=bot.settings.owner)
            if not owner:
                try:
                    owner = await bot.get_user_info(bot.settings.owner)
                except:
                    owner = None
                if not owner:
                    owner = bot.settings.owner  # Tylko ID
            return owner

        how_to = "Do `[p]set owner` in chat to set it"

        if bot.user.bot:  # Dorwiemy właściciela
            try:
                data = await bot.application_info()
                bot.settings.owner = data.owner.id
                bot.settings.save_settings()
                return data.owner
            except:
                return "Nie znalazłem właściciela. " + how_to
        else:
            return "Nie ma właściciela. " + how_to

    @bot.event
    async def on_ready():
        if bot._intro_displayed:
            return
        bot._intro_displayed = True

        owner_cog = bot.get_cog('Owner')
        total_cogs = len(owner_cog._list_cogs())
        users = len(set(bot.get_all_members()))
        servers = len(bot.servers)
        channels = len([c for c in bot.get_all_channels()])

        login_time = datetime.datetime.utcnow() - bot.uptime
        login_time = login_time.seconds + login_time.microseconds/1E6

        print("Login pomyślny. ({}ms)\n".format(login_time))

        owner = await set_bot_owner()

        print("-----------------")
        print("Arceus - Discord Bot")
        print("-----------------")
        print(str(bot.user))
        print("\nPołączony z:")
        print("{} serwerami".format(servers))
        print("{} kanałami".format(channels))
        print("{} użytkownikami\n".format(users))
        prefix_label = 'Prefix'
        if len(bot.settings.prefixes) > 1:
            prefix_label += 'es'
        print("{}: {}".format(prefix_label, " ".join(bot.settings.prefixes)))
        print("Owner: " + str(owner))
        print("{}/{} aktywnych modułów z {} komendami".format(
            len(bot.cogs), total_cogs, len(bot.commands)))
        print("-----------------")

        if bot.settings.token and not bot.settings.self_bot:
            print("\nLink zapraszający:")
            url = await get_oauth_url()
            bot.oauth_url = url
            print(url)

        await bot.get_cog('Owner').disable_commands()

    @bot.event
    async def on_resumed():
        bot.counter["session_resumed"] += 1

    @bot.event
    async def on_command(command, ctx):
        bot.counter["processed_commands"] += 1

    @bot.event
    async def on_message(message):
        bot.counter["messages_read"] += 1
        if bot.user_allowed(message):
            await bot.process_commands(message)

    @bot.event
    async def on_command_error(error, ctx):
        channel = ctx.message.channel
        if isinstance(error, commands.MissingRequiredArgument):
            await bot.send_cmd_help(ctx)
        elif isinstance(error, commands.BadArgument):
            await bot.send_cmd_help(ctx)
        elif isinstance(error, commands.DisabledCommand):
            await bot.send_message(channel, "Ta komenda jest wyłączona z użytku.")
        elif isinstance(error, commands.CommandInvokeError):
            # Znajdź mi lepszy sposób
            no_dms = "Cannot send messages to this user"
            is_help_cmd = ctx.command.qualified_name == "help"
            is_forbidden = isinstance(error.original, discord.Forbidden)
            if is_help_cmd and is_forbidden and error.original.text == no_dms:
                msg = ("Nie mogłem ci wysłać priva"
                       " zablokowałeś mnie :(, lub coś posżło nie tak.")
                await bot.send_message(channel, msg)
                return

            bot.logger.exception("Błąd w komendzie '{}'".format(
                ctx.command.qualified_name), exc_info=error.original)
            message = ("Błąd w komendzie '{}'. Sprawdź konsole, albo "
                       "log dla detali."
                       "".format(ctx.command.qualified_name))
            log = ("Błąd w komendzie '{}'\n"
                   "".format(ctx.command.qualified_name))
            log += "".join(traceback.format_exception(type(error), error,
                                                      error.__traceback__))
            bot._last_exception = log
            await ctx.bot.send_message(channel, inline(message))
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            await bot.send_message(channel, "Ta komenda nie "
                                            "działa na priv.")
        elif isinstance(error, commands.CommandOnCooldown):
            await bot.send_message(channel, "Woah, zwolnij trochę. "
                                            "Spróbuj za {:.2f}s"
                                            "".format(error.retry_after))
        else:
            bot.logger.exception(type(error).__name__, exc_info=error)

    return bot


def check_folders():
    folders = ("data", "data/red", "cogs", "cogs/utils")
    for folder in folders:
        if not os.path.exists(folder):
            print("Tworzenie folderu " + folder + " ...")
            os.makedirs(folder)


def interactive_setup(settings):
    first_run = settings.bot_settings == settings.default_settings

    if first_run:
        print("Pierwsza konfiguracja\n")

    if not settings.login_credentials:
        print("\nWstaw token bota:")
        while settings.token is None and settings.email is None:
            choice = input("> ")
            if "@" not in choice and len(choice) >= 50:  # Bierem ten token
                settings.token = choice
            elif "@" in choice:
                settings.email = choice
                settings.password = input("\nHasło> ")
            else:
                print("To nie wygląda mi na token.")
        settings.save_settings()

    if not settings.prefixes:
        print("\nWybierz prefix do rozpoznawania komend."
              "\nNa przykład wykrzyknik.\n"
              "Może być kilka znaków. Będziesz mógł zmienić "
              "to później, lub dodać więcej.\nWybierz prefix:")
        confirmation = False
        while confirmation is False:
            new_prefix = ensure_reply("\nPrefix> ").strip()
            print("\nCzy chcesz {0} jako prefix?\nBędziesz "
                  "pisał komendy mniej więcej tak: {0}pomoc"
                  "\nWpisz tak lub nie".format(
                      new_prefix))
            confirmation = get_answer()
        settings.prefixes = [new_prefix]
        settings.save_settings()

    if first_run:
        print("\nWpisz nazwę roli Administratora")
        print("Puste oznacza domyślną rolę (Administrator)")
        settings.default_admin = input("\nRola admina> ")
        if settings.default_admin == "":
            settings.default_admin = "Administrator"
        settings.save_settings()

        print("\nWpisz nazwę roli Moderatora")
        print("Puste oznacza domyślną rolę (Mod)")
        settings.default_mod = input("\nRola moderatora> ")
        if settings.default_mod == "":
            settings.default_mod = "Mod"
        settings.save_settings()

        print("\nKonfiguracja zakończona\n"
              "Wciśnij enter")
        input("\n")


def set_logger(bot):
    logger = logging.getLogger("red")
    logger.setLevel(logging.INFO)

    red_format = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
        '%(message)s',
        datefmt="[%d/%m/%Y %H:%M]")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(red_format)
    if bot.settings.debug:
        stdout_handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        stdout_handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)

    fhandler = logging.handlers.RotatingFileHandler(
        filename='data/red/red.log', encoding='utf-8', mode='a',
        maxBytes=10**7, backupCount=5)
    fhandler.setFormatter(red_format)

    logger.addHandler(fhandler)
    logger.addHandler(stdout_handler)

    dpy_logger = logging.getLogger("discord")
    if bot.settings.debug:
        dpy_logger.setLevel(logging.DEBUG)
    else:
        dpy_logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(
        filename='data/red/discord.log', encoding='utf-8', mode='a')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
        '%(message)s',
        datefmt="[%d/%m/%Y %H:%M]"))
    dpy_logger.addHandler(handler)

    return logger


def ensure_reply(msg):
    choice = ""
    while choice == "":
        choice = input(msg)
    return choice


def get_answer():
    choices = ("yes", "y", "no", "n")
    c = ""
    while c not in choices:
        c = input(">").lower()
    if c.startswith("y"):
        return True
    else:
        return False


def set_cog(cog, value):  # Trza by to zabrać
    data = dataIO.load_json("data/red/cogs.json")
    data[cog] = value
    dataIO.save_json("data/red/cogs.json", data)


def load_cogs(bot):
    defaults = ("alias", "audio", "customcom", "downloader", "economy",
                "general", "image", "mod", "streams", "trivia")

    try:
        registry = dataIO.load_json("data/red/cogs.json")
    except:
        registry = {}

    bot.load_extension('cogs.owner')
    owner_cog = bot.get_cog('Owner')
    if owner_cog is None:
        print("Zniknął ważny moduł Owner #oddej. Wyłączanie....")
        exit(1)

    if bot.settings._no_cogs:
        bot.logger.debug("Skipping initial cogs loading (--no-cogs)")
        if not os.path.isfile("data/red/cogs.json"):
            dataIO.save_json("data/red/cogs.json", {})
        return

    failed = []
    extensions = owner_cog._list_cogs()

    if not registry:  # All default cogs enabled by default
        for ext in defaults:
            registry["cogs." + ext] = True

    for extension in extensions:
        if extension.lower() == "cogs.owner":
            continue
        to_load = registry.get(extension, False)
        if to_load:
            try:
                owner_cog._load_cog(extension)
            except Exception as e:
                print("{}: {}".format(e.__class__.__name__, str(e)))
                bot.logger.exception(e)
                failed.append(extension)
                registry[extension] = False

    dataIO.save_json("data/red/cogs.json", registry)

    if failed:
        print("\nNie załadowano: {}\n".format(" ".join(failed)))


def main(bot):
    check_folders()
    if not bot.settings.no_prompt:
        interactive_setup(bot.settings)
    load_cogs(bot)

    if bot.settings._dry_run:
        print("Wyłącznie, suche odpalenie")
        bot._shutdown_mode = True
        exit(0)

    print("Logowanie...")
    bot.uptime = datetime.datetime.utcnow()

    if bot.settings.login_credentials:
        yield from bot.login(*bot.settings.login_credentials,
                             bot=not bot.settings.self_bot)
    else:
        print("Brak danych loginu.")
        raise RuntimeError()
    yield from bot.connect()


if __name__ == '__main__':
    sys.stdout = TextIOWrapper(sys.stdout.detach(),
                               encoding=sys.stdout.encoding,
                               errors="replace",
                               line_buffering=True)
    bot = initialize()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(bot))
    except discord.LoginFailure:
        bot.logger.error(traceback.format_exc())
        if not bot.settings.no_prompt:
            choice = input("Zły login. Może to być wina discorda. Wciśnij enter aby spróbować ponownie, lub wpisz reset aby zmienić.\n> ")
            if choice.lower().strip() == "reset":
                bot.settings.token = None
                bot.settings.email = None
                bot.settings.password = None
                bot.settings.save_settings()
                print("Zresetowano login.")
    except KeyboardInterrupt:
        loop.run_until_complete(bot.logout())
    except Exception as e:
        bot.logger.exception("Error. Houston, memy problem, próbujemy zrestartować się z gracją",
                             exc_info=e)
        loop.run_until_complete(bot.logout())
    finally:
        loop.close()
        if bot._shutdown_mode is True:
            exit(0)
        elif bot._shutdown_mode is False:
            exit(26) # restart
        else:
            exit(1)
