"""
 * db_mod.py
 * PSP database cog for Red
 * by PikaPi and Fluff

                                                                                                                    .---.
_________   _...._      .--.     .                                                          _________   _...._      |   |
\        |.'      '-.   |__|   .'|                                                          \        |.'      '-.   |   |
 \        .'```'.    '. .--. .'  |                                                           \        .'```'.    '. |   |
  \      |       \     \|  |<    |            __        __        __        __                \      |       \     \|   |
   |     |        |    ||  | |   | ____    .:--.'.   .:--.'.   .:--.'.   .:--.'.               |     |        |    ||   |.--------.
   |      \      /    . |  | |   | \ .'   / |   \ | / |   \ | / |   \ | / |   \ |              |      \      /    . |   ||____    |
   |     |\`'-.-'   .'  |  | |   |/  .    `" __ | | `" __ | | `" __ | | `" __ | |              |     |\`'-.-'   .'  |   |    /   /
   |     | '-....-'`    |__| |    /\  \    .'.''| |  .'.''| |  .'.''| |  .'.''| |              |     | '-....-'`    |   |  .'   /
  .'     '.                  |   |  \  \  / /   | |_/ /   | |_/ /   | |_/ /   | |_            .'     '.             '---' /    /___
'-----------'                '    \  \  \ \ \._,\ '/\ \._,\ '/\ \._,\ '/\ \._,\ '/          '-----------'                |         |
                            '------'  '---'`--'  `"  `--'  `"  `--'  `"  `--'  `"                                        |_________|
"""
import discord
from discord.ext import commands
import sys
import sqlite3
from .utils.dataIO import dataIO
from .utils import checks

class db_cog:

	def __init__(self, bot):
		self.bot = bot
		self.db  = sqlite3.connect('acc.db')

	@commands.group(no_pm=True)
	@checks.is_owner()
	async def psp_initdb(self):
		self.db.execute("DROP TABLE IF EXISTS accounts")
		self.db.execute("DROP TABLE IF EXISTS platforms")
		self.db.execute("CREATE TABLE accounts (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
							   DTAG TEXT NOT NULL);")
		self.db.execute("CREATE TABLE platforms (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
							   NAME TEXT NOT NULL,\
							   SPECIAL TEXT NOT NULL);")
		self.db.commit()
		await self.bot.say("DB initialized successfully.")

	@commands.group(pass_context=True, no_pm=True)
	async def konta(self, ctx):
		"""Manage accounts"""
		if ctx.invoked_subcommand is None:
			return

	@konta.command(name="zarejestruj", pass_context=True, no_pm=True)
	async def ac_register(self, ctx):
		"""Rejestruje w systemie"""
		author   = ctx.message.author
		nickname = ctx.message.author.id
		self.db.execute("INSERT INTO accounts (DTAG) VALUES (\"%s\")" % (nickname))
		self.db.commit()
		await self.bot.say("Zarejestrowano pomyślnie jako %s!" % (nickname))

	@konta.command(name="dane", pass_context=True, no_pm=True)
	async def ac_dane(self, ctx, user : discord.Member):
		"""Wyświetla dane z bazy"""
		uid 			= user.id
		db_check 		= self.db.execute("SELECT ID FROM accounts WHERE DTAG=\"%s\"" % (uid))
		db_c			= db_check.fetchone()
		data			= []

		if db_c is None:
			await self.bot.say("Podałeś użytkownika niezarejestrowanego w bazie.")
			return

		db_query 		= "SELECT {platf} FROM accounts WHERE DTAG=\"{uidd}\""
		db_platforms 	= self.db.execute("SELECT * FROM platforms")

		for var in db_platforms:
			db_q_scope = self.db.execute(db_query.format(platf=var[1], uidd=uid))
			data.append([var[1], db_q_scope.fetchone()[0]])

		msg = "\n{rest}"

		for arr in data:
			tmp = "- {a}: \"{b}\"\n%s".format(a=arr[0], b=arr[1]) % ("{rest}")
			msg = msg.format(rest=tmp)
		msg = msg.format(rest="")
		em = discord.Embed(description=msg)

		await self.bot.say(ctx.message.author.mention, embed=em)

	@konta.command(name="addplatform", no_pm=True)
	@checks.admin_or_permissions(kick_members=True)
	async def ac_addplatform(self, platform : str):
		"""Dodaje nową platforme (owner)"""
		db_check = self.db.execute("SELECT * FROM platforms WHERE NAME=\"%s\"" % (platform))
		db_c     = db_check.fetchone()
		if db_c is not None:
			await self.bot.say("Taka platforma jest już zarejestrowana w bazie.")
			return
		self.db.execute("INSERT INTO platforms (NAME, SPECIAL) VALUES (\"%s\", \"\")" % (platform))
		self.db.execute("ALTER TABLE accounts ADD %s TEXT" % (platform))
		self.db.commit()
		await self.bot.say("Dodano!")

	@konta.command(name="dodaj", pass_context=True, no_pm=True)
	async def ac_add(self, ctx, platforma : str, wartosc : str):
		"""Dodaje lub aktualizuje dane w bazie"""
		author   = ctx.message.author
		nickname = ctx.message.author.id
		db_check = self.db.execute("SELECT ID FROM accounts WHERE DTAG=\"%s\"" % (nickname))
		db_c     = db_check.fetchone()
		if db_c is None:
			await self.bot.say("Najpierw zarejestruj sie w bazie!")
			return
		self.db.execute("UPDATE accounts SET {platform}=\"{value}\" WHERE DTAG=\"{dtag}\"".format(platform=platforma, value=wartosc, dtag=nickname))
		self.db.commit()
		await self.bot.say("Zrobione!")

	@konta.command(name="platformy", no_pm=True)
	async def ac_listplatforms(self):
		"""Wyświetla liste platform"""
		platforms = self.db.execute("SELECT * FROM platforms")
		msg       = "Dostępne platformy: \n{rest}"
		for row in platforms:
			rst = "- {plat}\n%s".format(plat=row[1]) % ("{rest}")
			msg = msg.format(rest=rst)
		msg = msg.format(rest="")
		await self.bot.say(msg)

def setup(bot):
	bot.add_cog(db_cog(bot))
