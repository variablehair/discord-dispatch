from discord.ext import commands
import discord

class OwnerCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def echo(self, ctx, *, to_echo : str):
        await ctx.send(to_echo)

def setup(bot):
    bot.add_cog(OwnerCog(bot))