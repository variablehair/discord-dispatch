from discord.ext import commands
import discord
import asyncio
from .classes.mission import Mission

# TODO: delete these test objects

test_mission = Mission(title='Herb Picking', description='Perb Hicking', duration=5)

# TODO: move this somewhere else

def _mission_complete_callback(mission : Mission):
    return f'{mission.title} complete after {mission.duration}!'      

class GameCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def get_missions(self, ctx):
        missions_embed = discord.Embed(title='Missions')
        missions_embed.add_field(name='1', value='empty', inline=True)
        missions_embed.add_field(name=test_mission.title, value=test_mission.description, inline=True)
        missions_embed.add_field(name="Duration", value=test_mission.duration)
        await ctx.send(embed=missions_embed)

    @commands.command()
    async def send_mission(self, ctx, to_send):
        await ctx.send("Mission 1 started!")
        await asyncio.sleep(test_mission.duration)
        await ctx.send(_mission_complete_callback(test_mission))

def setup(bot):
    bot.add_cog(GameCog(bot))