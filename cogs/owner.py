import discord
from discord.ext import commands
from cogs.utils import checks
from __main__ import set_cog
from .utils.dataIO import dataIO
from .utils.chat_formatting import pagify, box

import importlib
import traceback
import logging
import asyncio
import threading
import datetime
import glob
import os
import aiohttp

log = logging.getLogger("red.owner")


class CogNotFoundError(Exception):
    pass


class CogLoadError(Exception):
    pass


class NoSetupError(CogLoadError):
    pass


class CogUnloadError(Exception):
    pass


class OwnerUnloadWithoutReloadError(CogUnloadError):
    pass


class Owner:
    """Komendy dla właściciela do debugowania bota."""

    def __init__(self, bot):
        self.bot = bot
        self.setowner_lock = False
        self.disabled_commands = dataIO.load_json("data/red/disabled_commands.json")
        self.global_ignores = dataIO.load_json("data/red/global_ignores.json")
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    def __unload(self):
        self.session.close()

    @commands.command()
    @checks.is_owner()
    async def load(self, *, cog_name: str):
        """Ładuje moduł

        Przykład: load mod"""
        module = cog_name.strip()
        if "cogs." not in module:
            module = "cogs." + module
        try:
            self._load_cog(module)
        except CogNotFoundError:
            await self.bot.say("Ten moduł nie istnieje.")
        except CogLoadError as e:
            log.exception(e)
            traceback.print_exc()
            await self.bot.say("Był problem z wczytaywaniem modułu. Sprawdź"
                               " konsole albo logi.")
        except Exception as e:
            log.exception(e)
            traceback.print_exc()
            await self.bot.say('Moduł został znaleziony i może załadowany, ale '
                               'coś poszło nie tak, sprawdź logi albo konsole ')
        else:
            set_cog(module, True)
            await self.disable_commands()
            await self.bot.say("Moduł został załadowany.")

    @commands.group(invoke_without_command=True)
    @checks.is_owner()
    async def unload(self, *, cog_name: str):
        """Rozładowuje moduł

        Przykład: unload mod"""
        module = cog_name.strip()
        if "cogs." not in module:
            module = "cogs." + module
        if not self._does_cogfile_exist(module):
            await self.bot.say("Ten moduł nie istnieje, wyłączę autoładowanie"
                               " jakby co.")
        else:
            set_cog(module, False)
        try:  # No matter what we should try to unload it
            self._unload_cog(module)
        except OwnerUnloadWithoutReloadError:
            await self.bot.say("Nie chcesz tego robić.")
        except CogUnloadError as e:
            log.exception(e)
            traceback.print_exc()
            await self.bot.say('Nie udało się bezpiecznie rozładować.')
        else:
            await self.bot.say("Moduł rozładowany.")

    @unload.command(name="all")
    @checks.is_owner()
    async def unload_all(self):
        """Rozładowuje wszystkie moduły"""
        cogs = self._list_cogs()
        still_loaded = []
        for cog in cogs:
            set_cog(cog, False)
            try:
                self._unload_cog(cog)
            except OwnerUnloadWithoutReloadError:
                pass
            except CogUnloadError as e:
                log.exception(e)
                traceback.print_exc()
                still_loaded.append(cog)
        if still_loaded:
            still_loaded = ", ".join(still_loaded)
            await self.bot.say("Nie udało się rozładować kilku modułów: "
                "{}".format(still_loaded))
        else:
            await self.bot.say("Wszystkie moduły rozładowane.")

    @checks.is_owner()
    @commands.command(name="reload")
    async def _reload(self, *, cog_name: str):
        """Przeładowuje moduł

        przykład: reload audio"""
        module = cog_name.strip()
        if "cogs." not in module:
            module = "cogs." + module

        try:
            self._unload_cog(module, reloading=True)
        except:
            pass

        try:
            self._load_cog(module)
        except CogNotFoundError:
            await self.bot.say("Nie znalazłem modułu.")
        except NoSetupError:
            await self.bot.say("Ten moduł nie ma funkcji startowej.")
        except CogLoadError as e:
            log.exception(e)
            traceback.print_exc()
            await self.bot.say("Był problem z wczytaywaniem modułu. Sprawdź"
                               " Konsole.")
        else:
            set_cog(module, True)
            await self.disable_commands()
            await self.bot.say("Przeładowano moduł.")

    @commands.command(name="cogs")
    @checks.is_owner()
    async def _show_cogs(self):
        """Pokazuje załadowane i niezaładowane moduły"""
        # This function assumes that all cogs are in the cogs folder,
        # which is currently true.

        # Extracting filename from __module__ Example: cogs.owner
        loaded = [c.__module__.split(".")[1] for c in self.bot.cogs.values()]
        # What's in the folder but not loaded is unloaded
        unloaded = [c.split(".")[1] for c in self._list_cogs()
                    if c.split(".")[1] not in loaded]

        if not unloaded:
            unloaded = ["None"]

        msg = ("+ Załadowane\n"
               "{}\n\n"
               "- Nie załadowane\n"
               "{}"
               "".format(", ".join(sorted(loaded)),
                         ", ".join(sorted(unloaded)))
               )
        for page in pagify(msg, [" "], shorten_by=16):
            await self.bot.say(box(page.lstrip(" "), lang="diff"))

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def debug(self, ctx, *, code):
        """Ewaluuje kod"""
        def check(m):
            if m.content.strip().lower() == "more":
                return True

        author = ctx.message.author
        channel = ctx.message.channel

        code = code.strip('` ')
        result = None

        global_vars = globals().copy()
        global_vars['bot'] = self.bot
        global_vars['ctx'] = ctx
        global_vars['message'] = ctx.message
        global_vars['author'] = ctx.message.author
        global_vars['channel'] = ctx.message.channel
        global_vars['server'] = ctx.message.server

        try:
            result = eval(code, global_vars, locals())
        except Exception as e:
            await self.bot.say(box('{}: {}'.format(type(e).__name__, str(e)),
                                   lang="py"))
            return

        if asyncio.iscoroutine(result):
            result = await result

        result = str(result)

        if not ctx.message.channel.is_private:
            censor = (self.bot.settings.email,
                      self.bot.settings.password,
                      self.bot.settings.token)
            r = "[EXPUNGED]"
            for w in censor:
                if w is None or w == "":
                    continue
                result = result.replace(w, r)
                result = result.replace(w.lower(), r)
                result = result.replace(w.upper(), r)

        result = list(pagify(result, shorten_by=16))

        for i, page in enumerate(result):
            if i != 0 and i % 4 == 0:
                last = await self.bot.say("Nadal są {} wiadomości. "
                                          "Napisz `more` aby kontynuować."
                                          "".format(len(result) - (i+1)))
                msg = await self.bot.wait_for_message(author=author,
                                                      channel=channel,
                                                      check=check,
                                                      timeout=10)
                if msg is None:
                    try:
                        await self.bot.delete_message(last)
                    except:
                        pass
                    finally:
                        break
            await self.bot.say(box(page, lang="py"))

    @commands.group(name="set", pass_context=True)
    async def _set(self, ctx):
        """Zmienia ustawienia bota"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)
            return

    @_set.command(pass_context=True)
    async def owner(self, ctx):
        """Ustala właściciela"""
        if self.bot.settings.no_prompt is True:
            await self.bot.say("Interakcja z konsolą jest wyłączona, użyj rozruchu "
                               "bez parametru `--no-prompt`.")
            return
        if self.setowner_lock:
            await self.bot.say("Komenda już jest w stanie oczekuje.")
            return

        if self.bot.settings.owner is not None:
            await self.bot.say(
            "Właściciel już istnieje i jego zmiana jest niebezpieczna. Potwierdzenie wymagane"
            )
            await asyncio.sleep(3)

        await self.bot.say("Potwierdź w konsoli bycie właścicielem.")
        self.setowner_lock = True
        t = threading.Thread(target=self._wait_for_answer,
                             args=(ctx.message.author,))
        t.start()

    @_set.command()
    @checks.is_owner()
    async def defaultmodrole(self, *, role_name: str):
        """Ustala rolę, którą bot uznaje za moda"""
        self.bot.settings.default_mod = role_name
        self.bot.settings.save_settings()
        await self.bot.say("Ustawiono.")

    @_set.command()
    @checks.is_owner()
    async def defaultadminrole(self, *, role_name: str):
        """Ustala rolę, którą bot uważa za admina"""
        self.bot.settings.default_admin = role_name
        self.bot.settings.save_settings()
        await self.bot.say("Ustawiono.")

    @_set.command(pass_context=True)
    @checks.is_owner()
    async def prefix(self, ctx, *prefixes):
        """ustawia globalny prefix bota

        Akceptuje dowolną ilośc oddzialoną spacjami, prefixy ze spacją w nawiasy
        Przykład: set prefix ! $ ? "lol lol" """
        if prefixes == ():
            await self.bot.send_cmd_help(ctx)
            return

        self.bot.settings.prefixes = sorted(prefixes, reverse=True)
        self.bot.settings.save_settings()
        log.debug("Nowe globalne prefixy to to:\n\t{}"
                  "".format(self.bot.settings.prefixes))

        p = "prefixes" if len(prefixes) > 1 else "prefix"
        await self.bot.say("Globalny {} ustawiony".format(p))

    @_set.command(pass_context=True, no_pm=True)
    @checks.serverowner_or_permissions(administrator=True)
    async def serverprefix(self, ctx, *prefixes):
        """Ustala serwerowy prefix bota

        Akceptuje dowolną ilośc oddzialoną spacjami, prefixy ze spacją w nawiasy
        Przykład: set prefix ! $ ? "lol lol"

        Uruchomienie komendy bez parametrów zresetuje prefixy do globalnych."""
        server = ctx.message.server

        if prefixes == ():
            self.bot.settings.set_server_prefixes(server, [])
            self.bot.settings.save_settings()
            current_p = ", ".join(self.bot.settings.prefixes)
            await self.bot.say("Server prefixes reset. Current prefixes: "
                               "`{}`".format(current_p))
            return

        prefixes = sorted(prefixes, reverse=True)
        self.bot.settings.set_server_prefixes(server, prefixes)
        self.bot.settings.save_settings()
        log.debug("Setting server's {} prefixes to:\n\t{}"
                  "".format(server.id, self.bot.settings.prefixes))

        p = "Prefixes" if len(prefixes) > 1 else "Prefix"
        await self.bot.say("{} ustawiony dla tego servera.\n"
                           "Aby wrócić do globalnego użyj"
                           " `{}set serverprefix` "
                           "".format(p, prefixes[0]))

    @_set.command(pass_context=True)
    @checks.is_owner()
    async def name(self, ctx, *, name):
        """Ustala nazwę bota"""
        name = name.strip()
        if name != "":
            try:
                await self.bot.edit_profile(self.bot.settings.password,
                                            username=name)
            except:
                await self.bot.say("Coś nie pykło"
                                   " nazwa może być zmienion dwa razy na godzinę."
                                   "Nicki można zmieniać bez limitu"
                                   ". {}set nickname"
                                   "".format(ctx.prefix))
            else:
                await self.bot.say("Zrobione.")
        else:
            await self.bot.send_cmd_help(ctx)

    @_set.command(pass_context=True, no_pm=True)
    @checks.is_owner()
    async def nickname(self, ctx, *, nickname=""):
        """Ustala nick bota

        pusty argument zresetuje nick."""
        nickname = nickname.strip()
        if nickname == "":
            nickname = None
        try:
            await self.bot.change_nickname(ctx.message.server.me, nickname)
            await self.bot.say("Zrobione.")
        except discord.Forbidden:
            await self.bot.say("Nie mogę tego zrobić, brakuje "
                "\"Change Nickname\" permisji.")

    @_set.command(pass_context=True)
    @checks.is_owner()
    async def game(self, ctx, *, game=None):
        """Ustala w co gra bot

        Brak argumentu wyczyści."""

        server = ctx.message.server

        current_status = server.me.status if server is not None else None

        if game:
            game = game.strip()
            await self.bot.change_presence(game=discord.Game(name=game),
                                           status=current_status)
            log.debug('Status zmieniony na "{}" przez właściciela'.format(game))
        else:
            await self.bot.change_presence(game=None, status=current_status)
            log.debug('statusz wyczyszczony')
        await self.bot.say("DZrobione.")

    @_set.command(pass_context=True)
    @checks.is_owner()
    async def status(self, ctx, *, status=None):
        """Ustala status bota

        Statusy:
            online
            idle
            dnd
            invisible"""

        statuses = {
                    "online"    : discord.Status.online,
                    "idle"      : discord.Status.idle,
                    "dnd"       : discord.Status.dnd,
                    "invisible" : discord.Status.invisible
                   }

        server = ctx.message.server

        current_game = server.me.game if server is not None else None

        if status is None:
            await self.bot.change_presence(status=discord.Status.online,
                                           game=current_game)
            await self.bot.say("Zresetowano status.")
        else:
            status = statuses.get(status.lower(), None)
            if status:
                await self.bot.change_presence(status=status,
                                               game=current_game)
                await self.bot.say("Status zmieniony.")
            else:
                await self.bot.send_cmd_help(ctx)

    @_set.command(pass_context=True)
    @checks.is_owner()
    async def stream(self, ctx, streamer=None, *, stream_title=None):
        """Ustala status streamowania

        Brak argumentów wyczyści status."""

        server = ctx.message.server

        current_status = server.me.status if server is not None else None

        if stream_title:
            stream_title = stream_title.strip()
            if "twitch.tv/" not in streamer:
                streamer = "https://www.twitch.tv/" + streamer
            game = discord.Game(type=1, url=streamer, name=stream_title)
            await self.bot.change_presence(game=game, status=current_status)
            log.debug('Owner has set streaming status and url to "{}" and {}'.format(stream_title, streamer))
        elif streamer is not None:
            await self.bot.send_cmd_help(ctx)
            return
        else:
            await self.bot.change_presence(game=None, status=current_status)
            log.debug('stream cleared by owner')
        await self.bot.say("Done.")

    @_set.command()
    @checks.is_owner()
    async def avatar(self, url):
        """Ustala avatar bota"""
        try:
            async with self.session.get(url) as r:
                data = await r.read()
            await self.bot.edit_profile(self.bot.settings.password, avatar=data)
            await self.bot.say("Zrobione.")
            log.debug("zmieniono avatar")
        except Exception as e:
            await self.bot.say("Błąd "
                               "sprawdź konsole.")
            log.exception(e)
            traceback.print_exc()

    @_set.command(name="token")
    @checks.is_owner()
    async def _token(self, token):
        """Sets Red's login token"""
        if len(token) < 50:
            await self.bot.say("Niewłaściwy token.")
        else:
            self.bot.settings.token = token
            self.bot.settings.save_settings()
            await self.bot.say("Token ustawiony. R-restart me senpai.")
            log.debug("Token zmieniony.")

    @_set.command(name="adminrole", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _server_adminrole(self, ctx, *, role: discord.Role):
        """Ustala role admina dla servera"""
        server = ctx.message.server
        if server.id not in self.bot.settings.servers:
            await self.bot.say("Ustaw tez role moda.")
        self.bot.settings.set_server_admin(server, role.name)
        await self.bot.say("Rola admina zmieniona na '{}'".format(role.name))

    @_set.command(name="modrole", pass_context=True, no_pm=True)
    @checks.serverowner()
    async def _server_modrole(self, ctx, *, role: discord.Role):
        """Ustala role mode dla servera"""
        server = ctx.message.server
        if server.id not in self.bot.settings.servers:
            await self.bot.say("Ustaw tez role admina.")
        self.bot.settings.set_server_mod(server, role.name)
        await self.bot.say("Rola moda zmieniona na '{}'".format(role.name))

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def blacklist(self, ctx):
        """Zarządzanie czarną listą

        Urzytkownicy na czarnej liście nie mogą używać komend"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @blacklist.command(name="add")
    async def _blacklist_add(self, user: discord.Member):
        """Dodaje na czarną listę"""
        if user.id not in self.global_ignores["blacklist"]:
            self.global_ignores["blacklist"].append(user.id)
            self.save_global_ignores()
            await self.bot.say("Dodano.")
        else:
            await self.bot.say("Użytkownik już jest na tej liście.")

    @blacklist.command(name="remove")
    async def _blacklist_remove(self, user: discord.Member):
        """Usuwa z czarnej listy"""
        if user.id in self.global_ignores["blacklist"]:
            self.global_ignores["blacklist"].remove(user.id)
            self.save_global_ignores()
            await self.bot.say("Usunięto.")
        else:
            await self.bot.say("Użytkownika nie ma na czarnej liście.")

    @blacklist.command(name="list")
    async def _blacklist_list(self):
        """Wypisuje członków czarnej listy"""
        blacklist = self._populate_list(self.global_ignores["blacklist"])

        if blacklist:
            for page in blacklist:
                await self.bot.say(box(page))
        else:
            await self.bot.say("Czarna lista jest pusta.")

    @blacklist.command(name="clear")
    async def _blacklist_clear(self):
        """Czyści czarną listę"""
        self.global_ignores["blacklist"] = []
        self.save_global_ignores()
        await self.bot.say("Czarna lista jest teraz pusta.")

    @commands.command()
    @checks.is_owner()
    async def shutdown(self, silently : bool=False):
        """Wyłącza bota"""
        wave = "\N{WAVING HAND SIGN}"
        skin = "\N{EMOJI MODIFIER FITZPATRICK TYPE-3}"
        try: # We don't want missing perms to stop our shutdown
            if not silently:
                await self.bot.say("SOLONGGAYBOWSER... " + wave + skin)
        except:
            pass
        await self.bot.shutdown()

    @commands.command()
    @checks.is_owner()
    async def restart(self, silently : bool=False):
        """Próbuje restartować bota

        Nie gwarantuję, że działa"""
        try:
            if not silently:
                await self.bot.say("*Insert restarting sound here*...")
        except:
            pass
        await self.bot.shutdown(restart=True)

    @commands.group(name="command", pass_context=True)
    @checks.is_owner()
    async def command_disabler(self, ctx):
        """Blokuje/Odblokowuje komendy

        bez argumentu wypisuje zablokowane komendy"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)
            if self.disabled_commands:
                msg = "Zablokowane komendy:\n```xl\n"
                for cmd in self.disabled_commands:
                    msg += "{}, ".format(cmd)
                msg = msg.strip(", ")
                await self.bot.whisper("{}```".format(msg))

    @command_disabler.command()
    async def disable(self, *, command):
        """Blokuje komendy"""
        comm_obj = await self.get_command(command)
        if comm_obj is KeyError:
            await self.bot.say("Ta komenda nie istnieje.")
        elif comm_obj is False:
            await self.bot.say("Tej komendy nie mozna zablokować.")
        else:
            comm_obj.enabled = False
            comm_obj.hidden = True
            self.disabled_commands.append(command)
            self.save_disabled_commands()
            await self.bot.say("Komenda zablokowana.")

    @command_disabler.command()
    async def enable(self, *, command):
        """Enables commands/subcommands"""
        if command in self.disabled_commands:
            self.disabled_commands.remove(command)
            self.save_disabled_commands()
            await self.bot.say("Komenda odblokowana.")
        else:
            await self.bot.say("Ta komenda nie jest zablokowana.")
            return
        try:
            comm_obj = await self.get_command(command)
            comm_obj.enabled = True
            comm_obj.hidden = False
        except:  # In case it was in the disabled list but not currently loaded
            pass # No point in even checking what returns

    async def get_command(self, command):
        command = command.split()
        try:
            comm_obj = self.bot.commands[command[0]]
            if len(command) > 1:
                command.pop(0)
                for cmd in command:
                    comm_obj = comm_obj.commands[cmd]
        except KeyError:
            return KeyError
        for check in comm_obj.checks:
            if hasattr(check, "__name__") and check.__name__ == "is_owner_check":
                return False
        return comm_obj

    async def disable_commands(self): # runs at boot
        for cmd in self.disabled_commands:
            cmd_obj = await self.get_command(cmd)
            try:
                cmd_obj.enabled = False
                cmd_obj.hidden = True
            except:
                pass

    async def leave_confirmation(self, server, owner, ctx):
        await self.bot.say("Are you sure you want me "
                    "to leave {}? (yes/no)".format(server.name))

        msg = await self.bot.wait_for_message(author=owner, timeout=15)

        if msg is None:
            await self.bot.say("I guess not.")
        elif msg.content.lower().strip() in ("yes", "y"):
            await self.bot.leave_server(server)
            if server != ctx.message.server:
                await self.bot.say("Done.")
        else:
            await self.bot.say("Alright then.")

    @commands.command(pass_context=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def contact(self, ctx, *, message : str):
        """Pozwala na kontakt z właścicielem"""
        if self.bot.settings.owner is None:
            await self.bot.say("I have no owner set.")
            return
        server = ctx.message.server
        owner = discord.utils.get(self.bot.get_all_members(),
                                  id=self.bot.settings.owner)
        author = ctx.message.author
        footer = "ID użytkownika: " + author.id

        if ctx.message.server is None:
            source = "przez priv"
        else:
            source = "od {}".format(server) 
            footer += " | ID servera: " + server.id

        if isinstance(author, discord.Member):
            colour = author.colour
        else:
            colour = discord.Colour.red()

        description = "Wysłane przez {} {}".format(author, source)

        e = discord.Embed(colour=colour, description=message)
        if author.avatar_url:
            e.set_author(name=description, icon_url=author.avatar_url)
        else:
            e.set_author(name=description)
        e.set_footer(text=footer)

        try:
            await self.bot.send_message(owner, embed=e)
        except discord.InvalidArgument:
            await self.bot.say("Nie mogę wysłać twojej wiadomości, nie mogę znaleźć"
                               " mojego właściciela... *cichy płacz*")
        except discord.HTTPException:
            await self.bot.say("Twoja wiadomość jest zbyt długa.")
        except:
            await self.bot.say("Coś poszło nie tak.")
        else:
            await self.bot.say("Wiadomość wysłana.")

    @commands.command()
    async def info(self):
        """Informacje o źródle bota"""
        author_repo = "https://github.com/Twentysix26"
        red_repo = author_repo + "/Red-DiscordBot"
        server_url = "https://discord.gg/red"
        dpy_repo = "https://github.com/Rapptz/discord.py"
        python_url = "https://www.python.org/"
        since = datetime.datetime(2016, 1, 2, 0, 0)
        days_since = (datetime.datetime.utcnow() - since).days
        dpy_version = "[{}]({})".format(discord.__version__, dpy_repo)
        py_version = "[{}.{}.{}]({})".format(*os.sys.version_info[:3],
                                             python_url)

        owner_set = self.bot.settings.owner is not None
        owner = self.bot.settings.owner if owner_set else None
        if owner:
            owner = discord.utils.get(self.bot.get_all_members(), id=owner)
            if not owner:
                try:
                    owner = await self.bot.get_user_info(self.bot.settings.owner)
                except:
                    owner = None
        if not owner:
            owner = "Unknown"

        about = (
            "To jest instancja bota [Red, an open source Discord bot]({}) "
            "stworzonego przez [Twentysix]({}) i ulepszana przez wielu.\n\n"
            "".format(red_repo, author_repo))

        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Właściciel instancji", value=str(owner))
        embed.add_field(name="Python", value=py_version)
        embed.add_field(name="discord.py", value=dpy_version)
        embed.add_field(name="O RED", value=about, inline=False)
        embed.set_footer(text="Przynoszenie uśmiechu od 02 Stycznia 2016 (ponad "
                         "{} dni temu!)".format(days_since))

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("Nie mam pozwolenia")

    @commands.command()
    async def uptime(self):
        """Pokazuje od jakiego czasu bot jest online"""
        since = self.bot.uptime.strftime("%Y-%m-%d %H:%M:%S")
        passed = self.get_bot_uptime()
        await self.bot.say("Żyję od: **{}** (od {} UTC)"
                           "".format(passed, since))

    @commands.command()
    async def wersja(self):
        """Pokazuje wersję bota"""
        response = self.bot.loop.run_in_executor(None, self._get_version)
        result = await asyncio.wait_for(response, timeout=10)
        try:
            await self.bot.say(embed=result)
        except discord.HTTPException:
            await self.bot.say("Nie mam pozwolenia")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def traceback(self, ctx, public: bool=False):
        """Wysyła ostatni błąd komendy na priv

        Argument public wyśle na czat"""
        if not public:
            destination = ctx.message.author
        else:
            destination = ctx.message.channel

        if self.bot._last_exception:
            for page in pagify(self.bot._last_exception):
                await self.bot.send_message(destination, box(page, lang="py"))
        else:
            await self.bot.say("Jakimś cudem jeszcze nie było błędów :thonk:")

    def _populate_list(self, _list):
        """Used for both whitelist / blacklist

        Returns a paginated list"""
        users = []
        total = len(_list)

        for user_id in _list:
            user = discord.utils.get(self.bot.get_all_members(), id=user_id)
            if user:
                users.append(str(user))

        if users:
            not_found = total - len(users)
            users = ", ".join(users)
            if not_found:
                users += "\n\n ... i {} użytkowników, których nie znalazłem".format(not_found)
            return list(pagify(users, delims=[" ", "\n"]))

        return []

    def _load_cog(self, cogname):
        if not self._does_cogfile_exist(cogname):
            raise CogNotFoundError(cogname)
        try:
            mod_obj = importlib.import_module(cogname)
            importlib.reload(mod_obj)
            self.bot.load_extension(mod_obj.__name__)
        except SyntaxError as e:
            raise CogLoadError(*e.args)
        except:
            raise

    def _unload_cog(self, cogname, reloading=False):
        if not reloading and cogname == "cogs.owner":
            raise OwnerUnloadWithoutReloadError(
                "Can't unload the owner plugin :P")
        try:
            self.bot.unload_extension(cogname)
        except:
            raise CogUnloadError

    def _list_cogs(self):
        cogs = [os.path.basename(f) for f in glob.glob("cogs/*.py")]
        return ["cogs." + os.path.splitext(f)[0] for f in cogs]

    def _does_cogfile_exist(self, module):
        if "cogs." not in module:
            module = "cogs." + module
        if module not in self._list_cogs():
            return False
        return True

    def _wait_for_answer(self, author):
        print(author.name + " requested to be set as owner. If this is you, "
              "type 'yes'. Otherwise press enter.")
        print()
        print("*DO NOT* set anyone else as owner. This has security "
              "repercussions.")

        choice = "None"
        while choice.lower() != "yes" and choice == "None":
            choice = input("> ")

        if choice == "yes":
            self.bot.settings.owner = author.id
            self.bot.settings.save_settings()
            print(author.name + " has been set as owner.")
            self.setowner_lock = False
            self.owner.hidden = True
        else:
            print("The set owner request has been ignored.")
            self.setowner_lock = False

    def _get_version(self):
        if not os.path.isdir(".git"):
            msg = "This instance of Red hasn't been installed with git."
            e = discord.Embed(title=msg,
                              colour=discord.Colour.red())
            return e

        commands = " && ".join((
            r'git config --get remote.origin.url',         # Remote URL
            r'git rev-list --count HEAD',                  # Number of commits
            r'git rev-parse --abbrev-ref HEAD',            # Branch name
            r'git show -s -n 3 HEAD --format="%cr|%s|%H"'  # Last 3 commits
        ))
        result = os.popen(commands).read()
        url, ncommits, branch, commits = result.split("\n", 3)
        if url.endswith(".git"):
            url = url[:-4]
        if url.startswith("git@"):
            domain, _, resource = url[4:].partition(':')
            url = 'https://{}/{}'.format(domain, resource)
        repo_name = url.split("/")[-1]

        embed = discord.Embed(title="Updates of " + repo_name,
                              description="Last three updates",
                              colour=discord.Colour.red(),
                              url="{}/tree/{}".format(url, branch))

        for line in commits.split('\n'):
            if not line:
                continue
            when, commit, chash = line.split("|")
            commit_url = url + "/commit/" + chash
            content = "[{}]({}) - {} ".format(chash[:6], commit_url, commit)
            embed.add_field(name=when, value=content, inline=False)

        embed.set_footer(text="Total commits: " + ncommits)

        return embed

    def get_bot_uptime(self, *, brief=False):
        # Courtesy of Danny
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not brief:
            if days:
                fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
            else:
                fmt = '{h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h}h {m}m {s}s'
            if days:
                fmt = '{d}d ' + fmt

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    def save_global_ignores(self):
        dataIO.save_json("data/red/global_ignores.json", self.global_ignores)

    def save_disabled_commands(self):
        dataIO.save_json("data/red/disabled_commands.json", self.disabled_commands)


def _import_old_data(data):
    """Migration from mod.py"""
    try:
        data["blacklist"] = dataIO.load_json("data/mod/blacklist.json")
    except FileNotFoundError:
        pass

    try:
        data["whitelist"] = dataIO.load_json("data/mod/whitelist.json")
    except FileNotFoundError:
        pass

    return data


def check_files():
    if not os.path.isfile("data/red/disabled_commands.json"):
        print("Creating empty disabled_commands.json...")
        dataIO.save_json("data/red/disabled_commands.json", [])

    if not os.path.isfile("data/red/global_ignores.json"):
        print("Creating empty global_ignores.json...")
        data = {"blacklist": [], "whitelist": []}
        try:
            data = _import_old_data(data)
        except Exception as e:
            log.error("Failed to migrate blacklist / whitelist data from "
                      "mod.py: {}".format(e))

        dataIO.save_json("data/red/global_ignores.json", data)


def setup(bot):
    check_files()
    n = Owner(bot)
    bot.add_cog(n)
