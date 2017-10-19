from discord.ext import commands
from cogs.utils.dataIO import dataIO
from cogs.utils import checks
from cogs.utils.chat_formatting import pagify, box
from __main__ import send_cmd_help, set_cog
import os
from subprocess import run as sp_run, PIPE
import shutil
from asyncio import as_completed
from setuptools import distutils
import discord
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from time import time
from importlib.util import find_spec
from copy import deepcopy

NUM_THREADS = 4
REPO_NONEX = 0x1
REPO_CLONE = 0x2
REPO_SAME = 0x4
REPOS_LIST = "https://twentysix26.github.io/Red-Docs/red_cog_approved_repos/"

DISCLAIMER = ("Zamierzasz dodać repozytorium niezatwierdzone przez twórców bota"
              " Robisz to na własną odpowiedzialność "
              "napisz `tak` jesli podejmujesz to ryzyko")


class UpdateError(Exception):
    pass


class CloningError(UpdateError):
    pass


class RequirementFail(UpdateError):
    pass


class Pobieraczek:
    """Instalator i deinstalator modułów."""

    def __init__(self, bot):
        self.bot = bot
        self.disclaimer_accepted = False
        self.path = os.path.join("data", "downloader")
        self.file_path = os.path.join(self.path, "repos.json")
        # {name:{url,cog1:{installed},cog1:{installed}}}
        self.repos = dataIO.load_json(self.file_path)
        self.executor = ThreadPoolExecutor(NUM_THREADS)
        self._do_first_run()

    def save_repos(self):
        dataIO.save_json(self.file_path, self.repos)

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def cog(self, ctx):
        """Dodatkowe zarządzanie modułami"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @cog.group(pass_context=True)
    async def repo(self, ctx):
        """Zarządzanie repozytoriami"""
        if ctx.invoked_subcommand is None or \
                isinstance(ctx.invoked_subcommand, commands.Group):
            await send_cmd_help(ctx)
            return

    @repo.command(name="add", pass_context=True)
    async def _repo_add(self, ctx, repo_name: str, repo_url: str):
        """Dodaje repozytorium do listy"""
        if not self.disclaimer_accepted:
            await self.bot.say(DISCLAIMER)
            answer = await self.bot.wait_for_message(timeout=30,
                                                     author=ctx.message.author)
            if answer is None:
                await self.bot.say('Nie dodano repozytorium.')
                return
            elif "tak" not in answer.content.lower():
                await self.bot.say('Nie dodano repozytorium.')
                return
            else:
                self.disclaimer_accepted = True
        self.repos[repo_name] = {}
        self.repos[repo_name]['url'] = repo_url
        try:
            self.update_repo(repo_name)
        except CloningError:
            await self.bot.say("To repozytorium nie wydaje się "
                               "właściwe.")
            del self.repos[repo_name]
            return
        self.populate_list(repo_name)
        self.save_repos()
        data = self.get_info_data(repo_name)
        if data:
            msg = data.get("INSTALL_MSG")
            if msg:
                await self.bot.say(msg[:2000])
        await self.bot.say("Repozytorium '{}' dodane.".format(repo_name))

    @repo.command(name="remove")
    async def _repo_del(self, repo_name: str):
        """Usuwa repozytorium bez modułów z listy."""
        def remove_readonly(func, path, excinfo):
            os.chmod(path, 0o755)
            func(path)

        if repo_name not in self.repos:
            await self.bot.say("To repozytorium nie istnieje.")
            return
        del self.repos[repo_name]
        try:
            shutil.rmtree(os.path.join(self.path, repo_name), onerror=remove_readonly)
        except FileNotFoundError:
            pass
        self.save_repos()
        await self.bot.say("Repozytorium '{}' usunięte.".format(repo_name))

    @cog.command(name="list")
    async def _send_list(self, repo_name=None):
        """Daje listę modułów możliwych do dodania

        Lista repozytoriów:
        https://twentysix26.github.io/Red-Docs/red_cog_approved_repos/"""
        retlist = []
        if repo_name and repo_name in self.repos:
            msg = "Dostępne moduły:\n"
            for cog in sorted(self.repos[repo_name].keys()):
                if 'url' == cog:
                    continue
                data = self.get_info_data(repo_name, cog)
                if data and data.get("HIDDEN") is True:
                    continue
                if data:
                    retlist.append([cog, data.get("SHORT", "")])
                else:
                    retlist.append([cog, ''])
        else:
            if self.repos:
                msg = "Available repos:\n"
                for repo_name in sorted(self.repos.keys()):
                    data = self.get_info_data(repo_name)
                    if data:
                        retlist.append([repo_name, data.get("SHORT", "")])
                    else:
                        retlist.append([repo_name, ""])
            else:
                await self.bot.say("Jeszcze nie dodałeś repozytorium.\n"
                                   "Zacznij teraz! {}".format(REPOS_LIST))
                return

        col_width = max(len(row[0]) for row in retlist) + 2
        for row in retlist:
            msg += "\t" + "".join(word.ljust(col_width) for word in row) + "\n"
        msg += "\nLista repozytoriów: {}".format(REPOS_LIST)
        for page in pagify(msg, delims=['\n'], shorten_by=8):
            await self.bot.say(box(page))

    @cog.command()
    async def info(self, repo_name: str, cog: str=None):
        """Pokazuje informacje o module"""
        if cog is not None:
            cogs = self.list_cogs(repo_name)
            if cog in cogs:
                data = self.get_info_data(repo_name, cog)
                if data:
                    msg = "{} by {}\n\n".format(cog, data["AUTHOR"])
                    msg += data["NAME"] + "\n\n" + data["DESCRIPTION"]
                    await self.bot.say(box(msg))
                else:
                    await self.bot.say("Ten moduł nie ma pliku informacji.")
            else:
                await self.bot.say("Ten moduł nie istnieje."
                                   " Użyj cog lista.")
        else:
            data = self.get_info_data(repo_name)
            if data is None:
                await self.bot.say("To repozytorium nie istnieje, lub"
                                   " nie ma w nim pliku z informacjami"
                                   ".")
                return
            name = data.get("NAME", None)
            name = repo_name if name is None else name
            author = data.get("AUTHOR", "Nieznany")
            desc = data.get("DESCRIPTION", "")
            msg = ("```{} by {}```\n\n{}".format(name, author, desc))
            await self.bot.say(msg)

    @cog.command(pass_context=True)
    async def uninstall(self, ctx, repo_name, cog):
        """Deinstaluje moduł"""
        if repo_name not in self.repos:
            await self.bot.say("That repo doesn't exist.")
            return
        if cog not in self.repos[repo_name]:
            await self.bot.say("That cog isn't available from that repo.")
            return
        set_cog("cogs." + cog, False)
        self.repos[repo_name][cog]['INSTALLED'] = False
        self.save_repos()
        os.remove(os.path.join("cogs", cog + ".py"))
        owner = self.bot.get_cog('Owner')
        await owner.unload.callback(owner, cog_name=cog)
        await self.bot.say("Cog successfully uninstalled.")

    @cog.command(name="install", pass_context=True)
    async def _install(self, ctx, repo_name: str, cog: str):
        """Instaluje wybrany moduł"""
        if repo_name not in self.repos:
            await self.bot.say("To repozytorium nie istnieje.")
            return
        if cog not in self.repos[repo_name]:
            await self.bot.say("To repozytorium nie ma takiego modułu.")
            return
        data = self.get_info_data(repo_name, cog)
        try:
            install_cog = await self.install(repo_name, cog, notify_reqs=True)
        except RequirementFail:
            await self.bot.say("Ten moduł ma wymagania których nie mogę "
                               "zainstalować. Sprawdź konsolę.")
            return
        if data is not None:
            install_msg = data.get("INSTALL_MSG", None)
            if install_msg:
                await self.bot.say(install_msg[:2000])
        if install_cog:
            await self.bot.say("Zainstalowano. Załadować? (yes/no)")
            answer = await self.bot.wait_for_message(timeout=15,
                                                     author=ctx.message.author)
            if answer is None:
                await self.bot.say("Jasne, możesz go zawsze załadować"
                                   " `{}load {}`".format(ctx.prefix, cog))
            elif answer.content.lower().strip() == "yes":
                set_cog("cogs." + cog, True)
                owner = self.bot.get_cog('Owner')
                await owner.load.callback(owner, cog_name=cog)
            else:
                await self.bot.say("Jasne, możesz go zawsze załadować"
                                   " `{}load {}`".format(ctx.prefix, cog))
        elif install_cog is False:
            await self.bot.say("Invalid cog. Installation aborted.")
        else:
            await self.bot.say("Ten moduł nie istnieje, użyj cog list"
                               " dla pełnej listy.")

    async def install(self, repo_name, cog, *, notify_reqs=False,
                      no_install_on_reqs_fail=True):
        # 'no_install_on_reqs_fail' will make the cog get installed anyway
        # on requirements installation fail. This is necessary because due to
        # how 'cog update' works right now, the user would have no way to
        # reupdate the cog if the update fails, since 'cog update' only
        # updates the cogs that get a new commit.
        # This is not a great way to deal with the problem and a cog update
        # rework would probably be the best course of action.
        reqs_failed = False
        if cog.endswith('.py'):
            cog = cog[:-3]

        path = self.repos[repo_name][cog]['file']
        cog_folder_path = self.repos[repo_name][cog]['folder']
        cog_data_path = os.path.join(cog_folder_path, 'data')
        data = self.get_info_data(repo_name, cog)
        if data is not None:
            requirements = data.get("REQUIREMENTS", [])

            requirements = [r for r in requirements
                            if not self.is_lib_installed(r)]

            if requirements and notify_reqs:
                await self.bot.say("Instalowanie wymagań...")

            for requirement in requirements:
                if not self.is_lib_installed(requirement):
                    success = await self.bot.pip_install(requirement)
                    if not success:
                        if no_install_on_reqs_fail:
                            raise RequirementFail()
                        else:
                            reqs_failed = True

        to_path = os.path.join("cogs", cog + ".py")

        print("Kopiowanie {}...".format(cog))
        shutil.copy(path, to_path)

        if os.path.exists(cog_data_path):
            print("Kopiowanie foleru danych {} ...".format(cog))
            distutils.dir_util.copy_tree(cog_data_path,
                                         os.path.join('data', cog))
        self.repos[repo_name][cog]['INSTALLED'] = True
        self.save_repos()
        if not reqs_failed:
            return True
        else:
            raise RequirementFail()

    def get_info_data(self, repo_name, cog=None):
        if cog is not None:
            cogs = self.list_cogs(repo_name)
            if cog in cogs:
                info_file = os.path.join(cogs[cog].get('folder'), "info.json")
                if os.path.isfile(info_file):
                    try:
                        data = dataIO.load_json(info_file)
                    except:
                        return None
                    return data
        else:
            repo_info = os.path.join(self.path, repo_name, 'info.json')
            if os.path.isfile(repo_info):
                try:
                    data = dataIO.load_json(repo_info)
                    return data
                except:
                    return None
        return None

    def list_cogs(self, repo_name):
        valid_cogs = {}

        repo_path = os.path.join(self.path, repo_name)
        folders = [f for f in os.listdir(repo_path)
                   if os.path.isdir(os.path.join(repo_path, f))]
        legacy_path = os.path.join(repo_path, "cogs")
        legacy_folders = []
        if os.path.exists(legacy_path):
            for f in os.listdir(legacy_path):
                if os.path.isdir(os.path.join(legacy_path, f)):
                    legacy_folders.append(os.path.join("cogs", f))

        folders = folders + legacy_folders

        for f in folders:
            cog_folder_path = os.path.join(self.path, repo_name, f)
            cog_folder = os.path.basename(cog_folder_path)
            for cog in os.listdir(cog_folder_path):
                cog_path = os.path.join(cog_folder_path, cog)
                if os.path.isfile(cog_path) and cog_folder == cog[:-3]:
                    valid_cogs[cog[:-3]] = {'folder': cog_folder_path,
                                            'file': cog_path}
        return valid_cogs

    def get_dir_name(self, url):
        splitted = url.split("/")
        git_name = splitted[-1]
        return git_name[:-4]

    def is_lib_installed(self, name):
        return bool(find_spec(name))

    def _do_first_run(self):
        save = False
        repos_copy = deepcopy(self.repos)

        # Issue 725
        for repo in repos_copy:
            for cog in repos_copy[repo]:
                cog_data = repos_copy[repo][cog]
                if isinstance(cog_data, str):  # ... url field
                    continue
                for k, v in cog_data.items():
                    if k in ("file", "folder"):
                        repos_copy[repo][cog][k] = os.path.normpath(cog_data[k])

        if self.repos != repos_copy:
            self.repos = repos_copy
            save = True

        invalid = []

        for repo in self.repos:
            broken = 'url' in self.repos[repo] and len(self.repos[repo]) == 1
            if broken:
                save = True
                try:
                    self.update_repo(repo)
                    self.populate_list(repo)
                except CloningError:
                    invalid.append(repo)
                    continue
                except Exception as e:
                    print(e) # TODO: Proper logging
                    continue

        for repo in invalid:
            del self.repos[repo]

        if save:
            self.save_repos()

    def populate_list(self, name):
        valid_cogs = self.list_cogs(name)
        new = set(valid_cogs.keys())
        old = set(self.repos[name].keys())
        for cog in new - old:
            self.repos[name][cog] = valid_cogs.get(cog, {})
            self.repos[name][cog]['INSTALLED'] = False
        for cog in new & old:
            self.repos[name][cog].update(valid_cogs[cog])
        for cog in old - new:
            if cog != 'url':
                del self.repos[name][cog]

    def update_repo(self, name):

        def run(*args, **kwargs):
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'
            kwargs['env'] = env
            return sp_run(*args, **kwargs)

        try:
            dd = self.path
            if name not in self.repos:
                raise UpdateError("Repo does not exist in data, wtf")
            folder = os.path.join(dd, name)
            # Make sure we don't git reset the Red folder on accident
            if not os.path.exists(os.path.join(folder, '.git')):
                #if os.path.exists(folder):
                    #shutil.rmtree(folder)
                url = self.repos[name].get('url')
                if not url:
                    raise UpdateError("Need to clone but no URL set")
                branch = None
                if "@" in url: # Specific branch
                    url, branch = url.rsplit("@", maxsplit=1)
                if branch is None:
                    p = run(["git", "clone", url, folder])
                else:
                    p = run(["git", "clone", "-b", branch, url, folder])
                if p.returncode != 0:
                    raise CloningError()
                self.populate_list(name)
                return name, REPO_CLONE, None
            else:
                rpbcmd = ["git", "-C", folder, "rev-parse", "--abbrev-ref", "HEAD"]
                p = run(rpbcmd, stdout=PIPE)
                branch = p.stdout.decode().strip()

                rpcmd = ["git", "-C", folder, "rev-parse", branch]
                p = run(["git", "-C", folder, "reset", "--hard",
                        "origin/%s" % branch, "-q"])
                if p.returncode != 0:
                    raise UpdateError("Error resetting to origin/%s" % branch)
                p = run(rpcmd, stdout=PIPE)
                if p.returncode != 0:
                    raise UpdateError("Unable to determine old commit hash")
                oldhash = p.stdout.decode().strip()
                p = run(["git", "-C", folder, "pull", "-q", "--ff-only"])
                if p.returncode != 0:
                    raise UpdateError("Error pulling updates")
                p = run(rpcmd, stdout=PIPE)
                if p.returncode != 0:
                    raise UpdateError("Unable to determine new commit hash")
                newhash = p.stdout.decode().strip()
                if oldhash == newhash:
                    return name, REPO_SAME, None
                else:
                    self.populate_list(name)
                    self.save_repos()
                    ret = {}
                    cmd = ['git', '-C', folder, 'diff', '--no-commit-id',
                           '--name-status', oldhash, newhash]
                    p = run(cmd, stdout=PIPE)

                    if p.returncode != 0:
                        raise UpdateError("Error in git diff")

                    changed = p.stdout.strip().decode().split('\n')

                    for f in changed:
                        if not f.endswith('.py'):
                            continue

                        status, _, cogpath = f.partition('\t')
                        cogname = os.path.split(cogpath)[-1][:-3]  # strip .py
                        if status not in ret:
                            ret[status] = []
                        ret[status].append(cogname)

                    return name, ret, oldhash

        except CloningError as e:
            raise CloningError(name, *e.args) from None
        except UpdateError as e:
            raise UpdateError(name, *e.args) from None

    async def _robust_edit(self, msg, text):
        try:
            msg = await self.bot.edit_message(msg, text)
        except discord.errors.NotFound:
            msg = await self.bot.send_message(msg.channel, text)
        except:
            raise
        return msg

    @staticmethod
    def format_patch(repo, cog, log):
        header = "Patch Notes for %s/%s" % (repo, cog)
        line = "=" * len(header)
        if log:
            return '\n'.join((header, line, log))


def check_folders():
    if not os.path.exists(os.path.join("data", "downloader")):
        print('Making repo downloads folder...')
        os.mkdir(os.path.join("data", "downloader"))


def check_files():
    f = os.path.join("data", "downloader", "repos.json")
    if not dataIO.is_valid_json(f):
        print("Creating default data/downloader/repos.json")
        dataIO.save_json(f, {})


def setup(bot):
    check_folders()
    check_files()
    n = Pobieraczek(bot)
    bot.add_cog(n)
