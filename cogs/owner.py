from discord.ext import commands
import discord
import textwrap
import io
from contextlib import redirect_stdout
import traceback
import mysql.connector as mariadb
from credentials import mysql_username, mysql_dbname_dev, mysql_password

class OwnerCog:
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self._cogs_folder = 'cogs.' # check likely location of cogs to be added
        self.dbconn = mariadb.connect(user=mysql_username, password='test1111', host='localhost', port='8008', database=mysql_dbname_dev)
        self.cur = self.dbconn.cursor()

    @commands.command(hidden=True, name='echo')
    @commands.is_owner()
    async def _echo(self, ctx, *, to_echo : str):
        await ctx.send(to_echo)

    @commands.command(hidden=True, name='sqlexec')
    @commands.is_owner()
    async def _sql_exec(self, ctx, *, query: str):
        try:
            self.cur.execute(query)
            if self.cur.rowcount <= 10:
                strout = self.cur.fetchall()
                await ctx.send(f"```{strout}```")
            else:
                strout = self.cur.fetchmany(size=10)
                await ctx.send(f"```Only first 10 results shown!\n{strout}")
        except mariadb.Error as e:
            await ctx.send(f"```ERROR: {e}```")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog_name: str):
        try:
            self.bot.load_extension(cog_name)
        except Exception as e1:
            try:
                self.bot.load_extension(self._cogs_folder + cog_name)
            except Exception as e2:
                await ctx.send(f'`Error loading cog {cog_name}: {type(e1).__name__} - {e1} \n {type(e2).__name__} - {e2}`')
            else:
                await ctx.send(f'`Successfully loaded cog {cog_name} from defaults cogs folder {self._cogs_folder}.`')
        else:
            await ctx.send(f'`Successfully loaded cog {cog_name}.`')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog_name: str):
        try:
            self.bot.unload_extension(cog_name)
            # unload doesn't throw error if not found, so no nested try block
            self.bot.unload_extension(self._cogs_folder + cog_name)
        except Exception as e:
            await ctx.send(f'`Error unloading cog {cog_name}: {type(e).__name__} - {e}`')
        else:
            await ctx.send(f'`Successfully unloaded cog {cog_name}.`')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog_name: str):
        try:
            await ctx.invoke(self.unload, cog_name=cog_name)
            await ctx.invoke(self.load, cog_name=cog_name)
        except Exception as e:
            await ctx.send(f'`Error reloading cog {cog_name}: {type(e).__name__} - {e}`')
        else:
            await ctx.send(f'`Successfully reloaded cog {cog_name}.`')

    @commands.command(pass_context=True, hidden=True, name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """Stolen from RoboDanny: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py#L72"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

def setup(bot):
    bot.add_cog(OwnerCog(bot))