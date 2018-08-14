from discord.ext import commands
import discord
import textwrap
import io
from contextlib import redirect_stdout
import traceback
from elasticsearch import Elasticsearch

class OwnerCog:
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.es = Elasticsearch([{'host':'localhost', 'port':9200}])

    @commands.command(hidden=True, name='echo')
    @commands.is_owner()
    async def _echo(self, ctx, *, to_echo : str):
        await ctx.send(to_echo)

    @commands.command(hidden=True, name='esget')
    @commands.is_owner()
    async def _esget(self, ctx, index, doc_type, id):
        "Usage: esget [index] [doc_type] [id]"
        await ctx.send(self.es.get(index, doc_type, id))

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