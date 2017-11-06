from cogs.utils.dataIO import dataIO
from aiohttp import web
import datetime
import asyncio
import os

try:
    import ipgetter
    has_ipgetter = True
except:
    has_ipgetter = False

web_template = """<html><header> <link href="https://fonts.googleapis.com/css?family=Assistant:300,400,600,700" rel="stylesheet"> <style type="text/css"> body{{background-color: rgb(16%, 18%, 20%); color: rgb(58%, 59%, 60%); font-family: 'Assistant', sans-serif; font-weight: 300; font-size: 18px;}}.avatar{{box-shadow: rgba(255, 255, 255, 0.2) 0px 0px 5px 0px; height: 80px; width: 80px; border-radius: 50% 50% 50% 50%; padding: 4px;}}.avatar img{{height: 80px; width: 80px; border-radius: 50% 50% 50% 50%; border: none; outline: none; background-color: #7289DA;}}.big-thing{{background-color: rgb(21%, 22%, 24%); width: 1080px; margin: 0 auto; margin-top: 15px; padding: 30px; border-radius: 5px 5px 5px 5px; box-shadow: rgba(0, 0, 0, 0.1) 0px 1px 10px 0px;}}.title-thing{{padding-top: 15px; margin: 0 auto; width: 1110px;}}.title-thing h4{{color: #fff; font-weight: 600; font-size: 32px; line-height: 34px;}}.title-thing-two h4{{color: #fff; font-size: 18px; padding: 0 0 0 0; font-weight: 300;}}.servers{{width: 1140px; margin: 0 auto; padding-top: 15px; display: grid; grid-gap: 10px; grid-template-columns: repeat(3, 373px);}}.server{{background-color: rgb(21%, 22%, 24%); border-radius: 5px 5px 5px 5px; box-shadow: rgba(0, 0, 0, 0.1) 0px 1px 10px 0px; padding: 15px; padding-bottom: 0; height: 105px;}}.server .title{{position: relative; left: 35%; top: -50%; font-size: 18px; letter-spacing: 0.8px; font-weight: 400; color: #ddd; line-height: 20px; width: 220px; height: 80x;}}.bot-information{{display: grid; grid-gap: 10px; grid-template-columns: repeat(2, 400px);}}footer{{text-align: center; padding: 40px 0 40px; font-size: 11px;}}.other-thing{{width: 600px;}}.system-information{{display: grid; grid-gap: 10px; grid-template-columns: repeat(3, 363px);}}p{{color: hsla(0,0%,100%,.5); font-size: 18px; font-weight: 400; text-indent: 4px;}}.bold{{font-weight: 600;}}.white{{color: #ddd;}}</style> <title>{name}- Web Statistics</title></header><body> <div class="title-thing"> <h4>Web Statistics Status Page</h4> </div><div class="big-thing bot-information"> <div class="other-thing"> <div class="avatar"> <img src="{bot_avatar_icon_url}" alt=''/> </div></div><div class="other-thing"> <p> <span class="white bold">Name: </span>{name}<p> <p> <span class="white bold">Owner: </span>{owner}</p><p> <span class="white bold">Created: </span>{created}</p><p> <span class="white bold">Uptime: </span>{uptime}</p></div></div><div class="title-thing"> <h4>Bot Information</h4> </div><div class="big-thing system-information"> <div class="other-thing"> <div class="title-thing-two"> <h4>Servers</h4> </div><p>{total_servers}</p><div class="title-thing-two"> <h4>Users</h4> </div><p>{user_count}</p><div class="title-thing-two"> <h4>Active Cogs</h4> </div><p>{active_cogs}</p><div class="title-thing-two"> <h4>Commands</h4> </div><p>{total_commands}</p></div><div class="other-thing"> <div class="title-thing-two"> <h4>Channels</h4> </div><p>{total_channels}</p><div class="title-thing-two"> <h4>Text</h4> </div><p>{text_channels}</p><div class="title-thing-two"> <h4>Voice</h4> </div><p>{voice_channels}</p><div class="title-thing-two"> <h4>Messages Received</h4> </div><p>{messages_received}</p><div class="title-thing-two"> <h4>Commands Run</h4> </div><p>{commands_run}</p></div><div class="other-thing"> <div class="title-thing-two"> <h4>CPU</h4> </div><p>{cpu_usage:.1f}%</p><div class="title-thing-two"> <h4>Memory</h4> </div><p>{memory_usage_mb:.0f}MB ({memory_usage:.1f}%)</p><div class="title-thing-two"> <h4>Threads</h4> </div><p>{threads}</p><div class="title-thing-two"> <h4>I/O</h4> </div><p><span class="white">Total reads: </span>{io_reads}</p><p><span class="white ">Total writes: </span>{io_writes}</p></div></div><div class="title-thing"> <h4>Loaded Cogs</h4> </div><div class="big-thing system-information">{loaded_cogs}</div><div class="title-thing"> <h4>Available Commands</h4> </div><div class="big-thing system-information">{all_commands}</div><div class="title-thing"> <h4>Servers</h4> </div><div class="servers">{servers}</div><footer>{date_now}</footer></body></html>"""


class WebStatistics:
    def __init__(self, bot):
        self.bot = bot
        self.server = None
        self.app = web.Application()
        self.handler = None
        self.dispatcher = {}
        self.settings = dataIO.load_json('data/webstatistics/settings.json')
        self.ip = ipgetter.myip()
        self.port = self.settings['server_port']
        self.bot.loop.create_task(self.make_webserver())

    async def get_owner(self):
        return await self.bot.get_user_info(self.bot.settings.owner)

    async def get_bot(self):
        return self.bot.user

    async def _get_servers_html(self, data):
        template = """
        <div class="server">
          <div class="avatar">
            <img src="{icon_url}" alt='' />
          </div>
          <div class="title">
            {name} ({members})
          </div>
        </div>"""
        tmp = ''
        for server in data['servers']:
            if server['icon_url']:
                icon_url = server['icon_url']
            else:
                icon_url = 'data:image/gif;base64,R0lGODlhAQABAPcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAP8ALAAAAAABAAEAAAgEAP8FBAA7'
            tmp += template.format(icon_url=icon_url, name=server['name'], members=server['members'])
        return tmp

    async def _get_cogs_html(self, data):
        template = """
        <div class="other-thing">
            {cog}
        </div>"""
        tmp = ''
        for cog in data['loaded_cogs']:
            tmp += template.format(cog=cog)
        return tmp

    async def _get_commands_html(self, data):
        template = """
        <div class="other-thing">
            {command}
        </div>"""
        tmp = ''
        for command in data:
            tmp += template.format(command=command)
        return tmp

    async def generate_body(self):
        data = self.bot.get_cog('Statistics').redapi_hook()
        bot_avatar_icon_url = data['avatar']
        name = '{0.name}#{0.discriminator}'.format(await self.get_bot())
        owner = '{0.name}#{0.discriminator}'.format(await self.get_owner())
        uptime = data['uptime']
        created = data['created_at']
        total_servers = data['total_servers']
        user_count = data['users']
        active_cogs = data['cogs']
        all_commands = await self._get_commands_html([command for command in self.bot.commands])
        total_commands = data['total_commands']
        total_channels = data['channels']
        text_channels = data['text_channels']
        voice_channels = data['voice_channels']
        messages_received = data['read_messages']
        commands_run = data['commands_run']
        cpu_usage = data['cpu_usage']
        memory_usage = data['mem_v']
        memory_usage_mb = int(data['mem_v_mb']) / 1024 / 1024
        threads = data['threads']
        io_reads = data['io_reads']
        io_writes = data['io_writes']
        date_now = 'Page generated on {}'.format(datetime.datetime.utcnow())
        servers = await self._get_servers_html(data)
        loaded_cogs = await self._get_cogs_html(data)
        body = web_template.format(
                servers=servers, bot_avatar_icon_url=bot_avatar_icon_url, name=name,
                owner=owner, uptime=uptime, total_servers=total_servers, user_count=user_count,
                active_cogs=active_cogs, total_commands=total_commands, total_channels=total_channels,
                text_channels=text_channels, voice_channels=voice_channels, messages_received=messages_received,
                commands_run=commands_run, cpu_usage=cpu_usage, memory_usage=memory_usage,
                memory_usage_mb=memory_usage_mb, created=created, date_now=date_now, loaded_cogs=loaded_cogs,
                all_commands=all_commands, threads=threads, io_reads=io_reads, io_writes=io_writes)
        return body

    async def make_webserver(self):
        async def page(request):
            body = await self.generate_body()
            return web.Response(text=body, content_type='text/html')

        await asyncio.sleep(10)

        self.app.router.add_get('/', page)
        self.handler = self.app.make_handler()

        self.server = await self.bot.loop.create_server(self.handler, '0.0.0.0', self.port)

        print('webstatistics.py: Serving on http://{}:{}'.format(self.ip, self.port))
        message = 'Serving Web Statistics on http://{}:{}'.format(self.ip, self.port)

        await self.bot.send_message(await self.get_owner(), message)

    def __unload(self):
        self.server.close()
        self.server.wait_closed()
        print('webstatistics.py: Stopping server')


def check_folder():
    if not os.path.exists('data/webstatistics'):
        print('Creating data/webstatistics folder...')
        os.makedirs('data/webstatistics')


def check_file():
    data = {}
    data['server_port'] = 4545
    if not dataIO.is_valid_json('data/webstatistics/settings.json'):
        print('Creating settings.json...')
        dataIO.save_json('data/webstatistics/settings.json', data)


def setup(bot):
    if not has_ipgetter:
        raise RuntimeError('ipgetter is not installed. Run `pip3 install ipgetter --upgrade` to use this cog.')
    elif not bot.get_cog('Statistics'):
        raise RuntimeError('To run this cog, you need the Statistics cog')
    else:
        check_folder()
        check_file()
        cog = WebStatistics(bot)
        bot.add_cog(cog)
