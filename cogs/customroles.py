from .utils import checks
from discord.ext import commands
from cogs.utils.dataIO import dataIO
from __main__ import send_cmd_help
import discord
import re
import os


class CustomRoles:
    def __init__(self, bot):
        self.bot = bot
        self.roles_file = 'data/customroles/data.json'
        self.roles = dataIO.load_json(self.roles_file)

    async def server_has_role(self, server, role):
        if role in [role.name for role in server.roles]:
            return True
        return False

    async def bot_has_role(self, server, role):
        if server.id in self.roles:
            if role in self.roles[server.id]:
                return True
        return False

    async def server_get_role(self, server, role):
        if await self.server_has_role(server, role):
            return [r for r in server.roles if r.name == role][0]
        return False

    async def save_role_data(self):
        dataIO.save_json(self.roles_file, self.roles)

    async def server_add_role(self, server, role, color):
        if re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', color):
            color = discord.Color(int(color, 16))
            try:
                if not await self.server_has_role(server, role):
                    await self.bot.create_role(server, name=role, color=color, permissions=discord.Permissions(permissions=0), hoist=False)
                    if server.id not in self.roles:
                        self.roles[server.id] = {}
                    self.roles[server.id][role] = {}
                    await self.save_role_data()
                    return 0
                else:
                    return 3
            except discord.Forbidden:
                return 2
        else:
            return 1

    async def server_remove_role(self, server, role):
        if await self.bot_has_role(server, role) and await self.server_has_role(server, role):
            try:
                role = await self.server_get_role(server, role)
                await self.bot.delete_role(server, role)
                if server.id not in self.roles:
                    self.roles[server.id] = {}
                if role.name in self.roles[server.id]:
                    del self.roles[server.id][role.name]
                await self.save_role_data()
                return 0
            except discord.Forbidden:
                return 2
        else:
            return 1

    async def member_apply_role(self, server, member, role):
        if await self.bot_has_role(server, role) and await self.server_has_role(server, role):
            try:
                role = await self.server_get_role(server, role)
                await self.bot.add_roles(member, role)
                return 0
            except discord.Forbidden:
                return 2
        else:
            return 1

    async def member_remove_role(self, server, member, role):
        if await self.bot_has_role(server, role) and await self.server_has_role(server, role):
            try:
                role = await self.server_get_role(server, role)
                await self.bot.remove_roles(member, role)
                return 0
            except discord.Forbidden:
                return 2
        else:
            return 1

    @commands.group(pass_context=True, no_pm=True, name='rola', aliases=['cr'])
    async def _rola(self, context):
        """Własne role."""
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @_rola.command(pass_context=True, no_pm=True, name='dodaj', aliases=['new'])
    @checks.mod_or_permissions(manage_roles=True)
    async def _add(self, context, color, *, name):
        """Dodaje role
        Przykład: role dodaj ff0000 Czerwona Rola"""
        message = name, color
        server = context.message.server
        check = await self.server_add_role(server, name, color)
        if check == 0:
            message = 'Rola stworzona'
        elif check == 1:
            message = '`{}` niewłaściwy kolor'.format(color)
        elif check == 2:
            message = 'Nie mam uprawnień.'
        elif check == 3:
            message = '`{}` już istnieje'.format(name)
        else:
            message = 'Nani?'
        await self.bot.say(message)

    @_rola.command(pass_context=True, no_pm=True, name='skasuj', aliases=['delete'])
    @checks.mod_or_permissions(manage_roles=True)
    async def _remove(self, context, *, name):
        """Usuwa rolę"""
        server = context.message.server
        check = await self.server_remove_role(server, name)
        if check == 0:
            message = 'Rola usunięta'
        elif check == 1:
            message = 'Rola nie istnieje na tym serwerze'
        elif check == 2:
            message = 'Błąd uprawnień.'
        await self.bot.say(message)

    @_rola.command(pass_context=True, no_pm=True, name='dołącz')
    async def _apply(self, context, *, role):
        """Dołącza do roli"""
        server = context.message.server
        author = context.message.author
        check = await self.member_apply_role(server, author, role)
        if check == 0:
            message = 'Rola przyznana!'
        elif check == 1:
            message = 'Rola nie istnieje na tym serwerze'
        elif check == 2:
            message = 'Błąd uprawnień.'
        await self.bot.say(message)

    @_rola.command(pass_context=True, no_pm=True, name='opuść')
    async def _relieve(self, context, *, role):
        """Opuszcza rolę"""
        server = context.message.server
        author = context.message.author
        check = await self.member_remove_role(server, author, role)
        if check == 0:
            message = 'Rola odebrana!'
        elif check == 1:
            message = 'Taka rola nie istnieje'
        elif check == 2:
            message = 'Błąd uprawnień.'
        await self.bot.say(message)

    @_rola.command(pass_context=True, no_pm=True, name='lista')
    async def _list(self, context):
        """Lista roli"""
        server = context.message.server
        message = '```Wszystkie dostępne role na {}\n\n'.format(server.name)
        if server.id in self.roles:
            for role in self.roles[server.id]:
                message += '{}\n'.format(role)
        message += '```'
        await self.bot.say(message)


def check_folder():
    if not os.path.exists('data/customroles'):
        print('Creating data/customroles folder...')
        os.makedirs('data/customroles')


def check_file():
    data_file = 'data/customroles/data.json'
    if not dataIO.is_valid_json(data_file):
        print('Creating default data.json...')
        dataIO.save_json(data_file, {})


def setup(bot):
    check_folder()
    check_file()
    n = CustomRoles(bot)
    bot.add_cog(n)
