import discord
from discord.ext import commands
from cogs.utils.dataIO import dataIO
from collections import namedtuple, defaultdict, deque
from datetime import datetime
from copy import deepcopy
from .utils import checks
from cogs.utils.chat_formatting import pagify, box
from enum import Enum
from __main__ import send_cmd_help
import os
import time
import logging
import random

default_settings = {"PAYDAY_TIME": 72000, "PAYDAY_CREDITS": 50,
                    "SLOT_MIN": 20, "SLOT_MAX": 1000, "SLOT_TIME": 0,
                    "REGISTER_CREDITS": 0, "ELITE_CREDITS": 200, 
					"REGISTERED_CREDITS": 100, "LEADER_CREDITS": 300}


class EconomyError(Exception):
    pass


class OnCooldown(EconomyError):
    pass


class InvalidBid(EconomyError):
    pass


class BankError(Exception):
    pass


class AccountAlreadyExists(BankError):
    pass


class NoAccount(BankError):
    pass


class InsufficientBalance(BankError):
    pass


class NegativeValue(BankError):
    pass


class SameSenderAndReceiver(BankError):
    pass


NUM_ENC = "\N{COMBINING ENCLOSING KEYCAP}"


class SMReel(Enum):
    yanma     = "<:yanmega:328463769053167618>"
    buizl     = "<:lasicawodna:331790325766946816>"
    harold    = "<:harold:339062212515594240>"
    reshiram  = "<:fluff:327790685191143435>"
    sowe      = "<:sowe:327793049625296896>"
    angery    = "<:angery:327792177554128897>"
    thonk     = "<:thonk:353860033190035457>"
    bricc     = "<:gateway:327911155421151234>"
    myoo      = "<:myoo:327870437235097601>"
    wimpod    = "<:wimpod:327911408153001995>"
    catto     = "<:catto:328286102177841155>"
    ban       = "<:ban:330115327553830912>"
    flajgon   = "<:smolflajgon:329513435907883018>"

PAYOUTS = {
    (SMReel.reshiram, SMReel.reshiram, SMReel.reshiram) : {
        "payout" : lambda x: x * 1000 + x,
        "phrase" : "JACKPOT! STAY FLUFFY! Stawka * 1000!"
    },
    (SMReel.yanma, SMReel.yanma, SMReel.yanma) : {
        "payout" : lambda x: x + 1000,
        "phrase" : "Trzy Yanmegi! +1000!"
    },
    (SMReel.buizl, SMReel.buizl, SMReel.buizl) : {
        "payout" : lambda x: x + 800,
        "phrase" : "3 🅱uizle! +800!"
    },
    (SMReel.reshiram, SMReel.reshiram) : {
        "payout" : lambda x: x * 4 + x,
        "phrase" : "Preeeaah! Stawka * 4!"
    },
    (SMReel.buizl, SMReel.buizl) : {
        "payout" : lambda x: x * 3 + x,
        "phrase" : "Dwa 🅱uizle, stawka * 3!"
    },
    (SMReel.harold, SMReel.harold, SMReel.harold) : {
        "payout" : lambda x: x + 1,
        "phrase" : "Hide your pain! +1!"
    },
    "3 symbols" : {
        "payout" : lambda x: x + 500,
        "phrase" : "Trzy symbole! +500!"
    },
    "2 symbols" : {
        "payout" : lambda x: x * 2 + x,
        "phrase" : "Dwa symbole! stawka * 2!"
    },
}

SLOT_PAYOUTS_MSG = ("Wyplaty:\n"
                    "{reshiram.value} {reshiram.value} {reshiram.value} Stawka * 500\n"
                    "{yanma.value} {yanma.value} {yanma.value} +1000\n"
                    "{buizl.value} {buizl.value} {buizl.value} +800\n"
                    "{reshiram.value} {reshiram.value} stawka * 4\n"
                    "{buizl.value} {buizl.value} stawka * 3\n\n"
                    "Three symbols: +500\n"
                    "Two symbols: stawka * 2".format(**SMReel.__dict__))


class Bank:

    def __init__(self, bot, file_path):
        self.accounts = dataIO.load_json(file_path)
        self.bot = bot

    def create_account(self, user, *, initial_balance=0):
        server = user.server
        if not self.account_exists(user):
            if server.id not in self.accounts:
                self.accounts[server.id] = {}
            if user.id in self.accounts:  # Legacy account
                balance = self.accounts[user.id]["balance"]
            else:
                balance = initial_balance
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            account = {"name": user.name,
                       "balance": balance,
                       "created_at": timestamp
                       }
            self.accounts[server.id][user.id] = account
            self._save_bank()
            return self.get_account(user)
        else:
            raise AccountAlreadyExists()

    def account_exists(self, user):
        try:
            self._get_account(user)
        except NoAccount:
            return False
        return True

    def withdraw_credits(self, user, amount):
        server = user.server

        if amount < 0:
            raise NegativeValue()

        account = self._get_account(user)
        if account["balance"] >= amount:
            account["balance"] -= amount
            self.accounts[server.id][user.id] = account
            self._save_bank()
        else:
            raise InsufficientBalance()

    def deposit_credits(self, user, amount):
        server = user.server
        if amount < 0:
            raise NegativeValue()
        account = self._get_account(user)
        account["balance"] += amount
        self.accounts[server.id][user.id] = account
        self._save_bank()

    def set_credits(self, user, amount):
        server = user.server
        if amount < 0:
            raise NegativeValue()
        account = self._get_account(user)
        account["balance"] = amount
        self.accounts[server.id][user.id] = account
        self._save_bank()

    def transfer_credits(self, sender, receiver, amount):
        if amount < 0:
            raise NegativeValue()
        if sender is receiver:
            raise SameSenderAndReceiver()
        if self.account_exists(sender) and self.account_exists(receiver):
            sender_acc = self._get_account(sender)
            if sender_acc["balance"] < amount:
                raise InsufficientBalance()
            self.withdraw_credits(sender, amount)
            self.deposit_credits(receiver, amount)
        else:
            raise NoAccount()

    def can_spend(self, user, amount):
        account = self._get_account(user)
        if account["balance"] >= amount:
            return True
        else:
            return False

    def wipe_bank(self, server):
        self.accounts[server.id] = {}
        self._save_bank()

    def get_server_accounts(self, server):
        if server.id in self.accounts:
            raw_server_accounts = deepcopy(self.accounts[server.id])
            accounts = []
            for k, v in raw_server_accounts.items():
                v["id"] = k
                v["server"] = server
                acc = self._create_account_obj(v)
                accounts.append(acc)
            return accounts
        else:
            return []

    def get_all_accounts(self):
        accounts = []
        for server_id, v in self.accounts.items():
            server = self.bot.get_server(server_id)
            if server is None:
                # Servers that have since been left will be ignored
                # Same for users_id from the old bank format
                continue
            raw_server_accounts = deepcopy(self.accounts[server.id])
            for k, v in raw_server_accounts.items():
                v["id"] = k
                v["server"] = server
                acc = self._create_account_obj(v)
                accounts.append(acc)
        return accounts

    def get_balance(self, user):
        account = self._get_account(user)
        return account["balance"]

    def get_account(self, user):
        acc = self._get_account(user)
        acc["id"] = user.id
        acc["server"] = user.server
        return self._create_account_obj(acc)

    def _create_account_obj(self, account):
        account["member"] = account["server"].get_member(account["id"])
        account["created_at"] = datetime.strptime(account["created_at"],
                                                  "%Y-%m-%d %H:%M:%S")
        Account = namedtuple("Account", "id name balance "
                             "created_at server member")
        return Account(**account)

    def _save_bank(self):
        dataIO.save_json("data/economy/bank.json", self.accounts)

    def _get_account(self, user):
        server = user.server
        try:
            return deepcopy(self.accounts[server.id][user.id])
        except KeyError:
            raise NoAccount()


class SetParser:
    def __init__(self, argument):
        allowed = ("+", "-")
        if argument and argument[0] in allowed:
            try:
                self.sum = int(argument)
            except:
                raise
            if self.sum < 0:
                self.operation = "withdraw"
            elif self.sum > 0:
                self.operation = "deposit"
            else:
                raise
            self.sum = abs(self.sum)
        elif argument.isdigit():
            self.sum = int(argument)
            self.operation = "set"
        else:
            raise


class Economy:
    """Ekonomia

    Stań się bogaty i udawaj, że udalo ci się w życiu z naszą zmyśloną walutą!"""

    def __init__(self, bot):
        global default_settings
        self.bot = bot
        self.bank = Bank(bot, "data/economy/bank.json")
        self.file_path = "data/economy/settings.json"
        self.settings = dataIO.load_json(self.file_path)
        if "PAYDAY_TIME" in self.settings:  # old format
            default_settings = self.settings
            self.settings = {}
        self.settings = defaultdict(lambda: default_settings, self.settings)
        self.payday_register = defaultdict(dict)
        self.slot_register = defaultdict(dict)

    @commands.group(name="bank", pass_context=True)
    async def _bank(self, ctx):
        """Komendy odnoszące się do banku"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @_bank.command(pass_context=True, no_pm=True)
    async def zarejestruj(self, ctx):
        """Rejestruje konto w banku PSP"""
        settings = self.settings[ctx.message.server.id]
        author = ctx.message.author
        credits = 0
        if ctx.message.server.id in self.settings:
            credits = settings.get("REGISTER_CREDITS", 0)
        try:
            account = self.bank.create_account(author, initial_balance=credits)
            await self.bot.say("{} Konto otwarte. Balans: {}"
                               "".format(author.mention, account.balance))
        except AccountAlreadyExists:
            await self.bot.say("{} Już masz konto w"
                               " banku PSP.".format(author.mention))

    @_bank.command(pass_context=True)
    async def srodki(self, ctx, user: discord.Member=None):
        """Pokazuje saldo użytkownika.

        Domyślnie pokazuje twoje."""
        if not user:
            user = ctx.message.author
            try:
                await self.bot.say("{} Twoje saldo to: {}".format(
                    user.mention, self.bank.get_balance(user)))
            except NoAccount:
                await self.bot.say("{} Nie masz konta w"
                                   " banku PSP. Uzyj `{}bank zarejestruj`"
                                   " aby otworzyć.".format(user.mention,
                                                          ctx.prefix))
        else:
            try:
                await self.bot.say("Saldo {} to {}".format(
                    user.name, self.bank.get_balance(user)))
            except NoAccount:
                await self.bot.say("Ten użytkownik nie ma konta.")

    @_bank.command(pass_context=True)
    async def transfer(self, ctx, user: discord.Member, sum: int):
        """Przenosi walutę do innych użytkowników."""
        author = ctx.message.author
        try:
            self.bank.transfer_credits(author, user, sum)
            logger.info("{}({}) przelał {} EV {}({})".format(
                author.name, author.id, sum, user.name, user.id))
            await self.bot.say("{} EV zostało przelane {}"
                               ".".format(sum, user.name))
        except NegativeValue:
            await self.bot.say("Minimalna suma przelewu to 1.")
        except SameSenderAndReceiver:
            await self.bot.say("Nie możesz przelać EV sobie.")
        except InsufficientBalance:
            await self.bot.say("Nie masz wystarczających środków aby zrealizować operacje.")
        except NoAccount:
            await self.bot.say("Ten użytkownik nie ma konta.")

    @_bank.command(name="set", pass_context=True)
    @checks.admin_or_permissions(ban_members=True)
    async def _set(self, ctx, user: discord.Member, credits: SetParser):
        """Ustala saldo konta bankowego wskazanego użytkownika. Wpisz help dla listy komend.

        Dodanie plusa/minusa dodaje/odejmuje walutę z konta, zamiast ustalać określoną sumę.

        Examples:
            bank set @Twentysix 26 - Ustala, że konto @Twentysix będzie mialo 26 EV
            bank set @Twentysix +2 - Dodaje 2 EV
            bank set @Twentysix -6 - Odejmuje 6 EV"""
        author = ctx.message.author
        try:
            if credits.operation == "deposit":
                self.bank.deposit_credits(user, credits.sum)
                logger.info("{}({}) dał {} EV {} ({})".format(
                    author.name, author.id, credits.sum, user.name, user.id))
                await self.bot.say("{} EV zostało dodane {}"
                                   "".format(credits.sum, user.name))
            elif credits.operation == "withdraw":
                self.bank.withdraw_credits(user, credits.sum)
                logger.info("{}({}) zabrał {} EV {} ({})".format(
                    author.name, author.id, credits.sum, user.name, user.id))
                await self.bot.say("{} EV zostało zabrane {}"
                                   "".format(credits.sum, user.name))
            elif credits.operation == "set":
                self.bank.set_credits(user, credits.sum)
                logger.info("{}({}) ustawił {} EV na koncie {} ({})"
                            "".format(author.name, author.id, credits.sum,
                                      user.name, user.id))
                await self.bot.say("EV {} zostało ustawione na {}".format(
                    user.name, credits.sum))
        except InsufficientBalance:
            await self.bot.say("Użytkownik nie ma wystarczających środków.")
        except NoAccount:
            await self.bot.say("Użytkowanik nie ma konta.")

    @_bank.command(pass_context=True, no_pm=True)
    @checks.serverowner_or_permissions(administrator=True)
    async def reset(self, ctx, confirmation: bool=False):
        """Usuwa WSZYSTKIE konta bankowe na serwerze!"""
        if confirmation is False:
            await self.bot.say("To Usunie wszystkie konta bankowe! "
                               "Jeśli jesteś pewny wpisz "
                               "{}bank reset yes".format(ctx.prefix))
        else:
            self.bank.wipe_bank(ctx.message.server)
            await self.bot.say("Wszystkie konta zostały usunięte.")

    @commands.command(pass_context=True, no_pm=True)
    async def wyplata(self, ctx):  # TODO
        """izi maneeeey - Otrzymaj nieco darmowych monet."""
        rolepay = "PAYDAY_CREDITS"
        author = ctx.message.author
        server = author.server
        id = author.id
        if self.bank.account_exists(author):
            if discord.utils.get(server.roles, name="Gym Leader") in author.roles:
                rolepay = "LEADER_CREDITS"
            elif discord.utils.get(server.roles, name="Elit3") in author.roles:
                rolepay = "ELITE_CREDITS"
            elif discord.utils.get(server.roles, name="Zweryfikowany") in author.roles:
                rolepay = "REGISTERED_CREDITS"
            else:
                rolepay = "PAYDAY_CREDITS"
            if id in self.payday_register[server.id]:
                seconds = abs(self.payday_register[server.id][
                              id] - int(time.perf_counter()))
                if seconds >= self.settings[server.id]["PAYDAY_TIME"]:
                    self.bank.deposit_credits(author, self.settings[
                                              server.id][rolepay])
                    self.payday_register[server.id][
                        id] = int(time.perf_counter())
                    await self.bot.say(
                        "{} ~~Masz, poczęstuj się~~ Hej, oto twoja dzienna wypłata. Powodzenia! (+{}"
                        " EV!)".format(
                            author.mention,
                            str(self.settings[server.id][rolepay])))
                else:
                    dtime = self.display_time(
                        self.settings[server.id]["PAYDAY_TIME"] - seconds)
                    await self.bot.say(
                        "{} Za wcześnie na kolejną wypłatę - musisz jeszcze"
                        " poczekać {}.".format(author.mention, dtime))
            else:
                self.payday_register[server.id][id] = int(time.perf_counter())
                self.bank.deposit_credits(author, self.settings[
                                          server.id][rolepay])
                await self.bot.say(
                    "{} ~~Masz, poczęstuj się~~ Hej, oto twoja dzienna wypłata. Powodzenia! (+{} EV!)".format(
                        author.mention,
                        str(self.settings[server.id][rolepay])))
        else:
            await self.bot.say("{} Potrzebujesz konta bankowego, żeby otrzymać EV."
                               " Wpisz `{}bank zarejestruj`,aby je założyć!.".format(
                                   author.mention, ctx.prefix))

    @commands.group(pass_context=True)
    async def najbogatsi(self, ctx):
        """Server / global leaderboard

        Defaults to server"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self._server_leaderboard)

    @najbogatsi.command(name="server", pass_context=True)
    async def _server_leaderboard(self, ctx, top: int=10):
        """Prints out the server's leaderboard

        Defaults to top 10"""
        # Originally coded by Airenkun - edited by irdumb
        server = ctx.message.server
        if top < 1:
            top = 10
        bank_sorted = sorted(self.bank.get_server_accounts(server),
                             key=lambda x: x.balance, reverse=True)
        bank_sorted = [a for a in bank_sorted if a.member] #  exclude users who left
        if len(bank_sorted) < top:
            top = len(bank_sorted)
        topten = bank_sorted[:top]
        highscore = ""
        place = 1
        for acc in topten:
            highscore += str(place).ljust(len(str(top)) + 1)
            highscore += (str(acc.member.display_name) + " ").ljust(23 - len(str(acc.balance)))
            highscore += str(acc.balance) + "\n"
            place += 1
        if highscore != "":
            for page in pagify(highscore, shorten_by=12):
                await self.bot.say(box(page, lang="py"))
        else:
            await self.bot.say("There are no accounts in the bank.")

    @commands.cooldown(rate=1, per=1.0, type=commands.BucketType.channel)
    @commands.command(pass_context=True, no_pm=True)
    async def slot(self, ctx, bid: int):
        """Play the slot machine"""
        author = ctx.message.author
        server = author.server
        settings = self.settings[server.id]
        valid_bid = settings["SLOT_MIN"] <= bid and bid <= settings["SLOT_MAX"]
        slot_time = settings["SLOT_TIME"]
        last_slot = self.slot_register.get(author.id)
        now = datetime.utcnow()
        try:
            if last_slot:
                if (now - last_slot).seconds < slot_time:
                    raise OnCooldown()
            if not valid_bid:
                raise InvalidBid()
            if not self.bank.can_spend(author, bid):
                raise InsufficientBalance
            await self.slot_machine(author, bid)
        except NoAccount:
            await self.bot.say("{} Potrzebujesz konta bankowego, żeby zagrać na jednorękim "
                               "bandycie. Wpisz `{}bank rejestracja` aby takie założyć."
                               "".format(author.mention, ctx.prefix))
        except InsufficientBalance:
            await self.bot.say("{} Musisz mieć wystarczającą ilość EV na koncie, żeby "
                               "zagrać w jednorękiego bandytę.".format(author.mention))
        except OnCooldown:
            await self.bot.say("Zaraz oderwiesz drugą rękę temu bandycie! Poczekaj jeszcze {} "
                               "sekund, żeby zagrać znowu.".format(slot_time))
        except InvalidBid:
            await self.bot.say("Bid must be between {} and {}."
                               "".format(settings["SLOT_MIN"],
                                         settings["SLOT_MAX"]))

    async def slot_machine(self, author, bid):
        default_reel = deque(SMReel)
        reels = []
        self.slot_register[author.id] = datetime.utcnow()
        for i in range(3):
            default_reel.rotate(random.randint(-999, 999)) # weeeeee
            new_reel = deque(default_reel, maxlen=3) # we need only 3 symbols
            reels.append(new_reel)                   # for each reel
        rows = ((reels[0][0], reels[1][0], reels[2][0]),
                (reels[0][1], reels[1][1], reels[2][1]),
                (reels[0][2], reels[1][2], reels[2][2]))

        slot = "~~\n~~" # Mobile friendly
        for i, row in enumerate(rows): # Let's build the slot to show
            sign = "  "
            if i == 1:
                sign = ">"
            slot += "{}{} {} {}\n".format(sign, *[c.value for c in row])

        payout = PAYOUTS.get(rows[1])
        if not payout:
            # Checks for two-consecutive-symbols special rewards
            payout = PAYOUTS.get((rows[1][0], rows[1][1]),
                     PAYOUTS.get((rows[1][1], rows[1][2]))
                                )
        if not payout:
            # Still nothing. Let's check for 3 generic same symbols
            # or 2 consecutive symbols
            has_three = rows[1][0] == rows[1][1] == rows[1][2]
            has_two = (rows[1][0] == rows[1][1]) or (rows[1][1] == rows[1][2])
            if has_three:
                payout = PAYOUTS["3 symbols"]
            elif has_two:
                payout = PAYOUTS["2 symbols"]

        if payout:
            then = self.bank.get_balance(author)
            pay = payout["payout"](bid)
            now = then - bid + pay
            self.bank.set_credits(author, now)
            await self.bot.say("{}\n{} {}\n\nTwoja Stawka: {}\n{} → {}!"
                               "".format(slot, author.mention,
                                         payout["phrase"], bid, then, now))
        else:
            then = self.bank.get_balance(author)
            self.bank.withdraw_credits(author, bid)
            now = then - bid
            await self.bot.say("{}\n{} Nic!\nTwoja Stawka: {}\n{} → {}!"
                               "".format(slot, author.mention, bid, then, now))

    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def economyset(self, ctx):
        """Zmienia ustawienia modułu ekonomii"""
        server = ctx.message.server
        settings = self.settings[server.id]
        if ctx.invoked_subcommand is None:
            msg = "```"
            for k, v in settings.items():
                msg += "{}: {}\n".format(k, v)
            msg += "```"
            await send_cmd_help(ctx)
            await self.bot.say(msg)

    @economyset.command(pass_context=True)
    async def slotmin(self, ctx, bid: int):
        """Minimalna stawka do zagrania w jednorękiego bandytę"""
        server = ctx.message.server
        self.settings[server.id]["SLOT_MIN"] = bid
        await self.bot.say("Minimalna stawka dla jednorękiego bandyty wynosi teraz {} EV.".format(bid))
        dataIO.save_json(self.file_path, self.settings)

    @economyset.command(pass_context=True)
    async def slotmax(self, ctx, bid: int):
        """Maksymalna stawka do zagrania w jednorękiego bandytę"""
        server = ctx.message.server
        self.settings[server.id]["SLOT_MAX"] = bid
        await self.bot.say("Maksymalna stawka dla jednorękiego bandyty wynosi teraz {} EV.".format(bid))
        dataIO.save_json(self.file_path, self.settings)

    @economyset.command(pass_context=True)
    async def slottime(self, ctx, seconds: int):
        """Okres oczekiwania pomiędzy grami w jednorękiego bandytę w sekundach"""
        server = ctx.message.server
        self.settings[server.id]["SLOT_TIME"] = seconds
        await self.bot.say("Czas oczekiwania na kolejną grę w jednorękiego bandytę wynosi teraz {} sekund.".format(seconds))
        dataIO.save_json(self.file_path, self.settings)

    @economyset.command(pass_context=True)
    async def paydaytime(self, ctx, seconds: int):
        """Okres oczekiwania pomiędzy wypłatami w sekundach"""
        server = ctx.message.server
        self.settings[server.id]["PAYDAY_TIME"] = seconds
        await self.bot.say("Wartość została zmieniona. Co najmniej {} sekund musi minąć "
                           "pomiędzy wypłatami.".format(seconds))
        dataIO.save_json(self.file_path, self.settings)

    @economyset.command(pass_context=True)
    async def paydaycredits(self, ctx, credits: int):
        """Ilość waluty wydawanej przy wypłacie"""
        server = ctx.message.server
        self.settings[server.id]["PAYDAY_CREDITS"] = credits
        await self.bot.say("Każda wypłata teraz będzie dawać {} EV."
                           "".format(credits))
        dataIO.save_json(self.file_path, self.settings)

    @economyset.command(pass_context=True)
    async def registercredits(self, ctx, credits: int):
        """Ilość waluty wydawanej przy rejestracji nowego konta"""
        server = ctx.message.server
        if credits < 0:
            credits = 0
        self.settings[server.id]["REGISTER_CREDITS"] = credits
        await self.bot.say("Rejestracja nowego konta przyznawać teraz będzie {} EV."
                           "".format(credits))
        dataIO.save_json(self.file_path, self.settings)

    # What would I ever do without stackoverflow?
    def display_time(self, seconds, granularity=2):
        intervals = (  # Source: http://stackoverflow.com/a/24542445
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),    # 60 * 60 * 24
            ('hours', 3600),    # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )

        result = []

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        return ', '.join(result[:granularity])


def check_folders():
    if not os.path.exists("data/economy"):
        print("Creating data/economy folder...")
        os.makedirs("data/economy")


def check_files():

    f = "data/economy/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default economy's settings.json...")
        dataIO.save_json(f, {})

    f = "data/economy/bank.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty bank.json...")
        dataIO.save_json(f, {})


def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("red.economy")
    if logger.level == 0:
        # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(
            filename='data/economy/economy.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    bot.add_cog(Economy(bot))
