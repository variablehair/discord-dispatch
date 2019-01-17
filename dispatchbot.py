from discord.ext import commands
import discord
from credentials import dispatch_token

import traceback

description = '''Dispatch bot'''

default_extensions = (
	'cogs.owner',
	'cogs.dispatch'
)

def _prefix_callable():
	return '-'

class DispatchBot(commands.AutoShardedBot):
	def __init__(self):
		super().__init__(command_prefix='-', description=description)

		for extension in default_extensions:
			try:
				self.load_extension(extension)
			except Exception:
				print(f'Extension {extension} failed to load.')
				traceback.print_exc()

	def run(self):
		super().run(dispatch_token, reconnect=True)

	async def on_ready(self):
		print('Logged in as')
		print(self.user.name)
		print(self.user.id)
		print('------')

bot = DispatchBot()
bot.run()