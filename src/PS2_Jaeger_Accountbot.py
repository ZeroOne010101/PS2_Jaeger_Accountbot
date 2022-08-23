import discord
from discord.ext import commands
import os
import utils.shared_resources as shared_resources
from utils.get_prefix import get_prefix
import logging

##### Initialisation #####
# Ensure working directory is correct
os.chdir(shared_resources.path)

# Setting up basic logging
logging.basicConfig(format="[%(asctime)s] %(levelname)s:%(message)s", level=logging.INFO, datefmt="%d.%m.%Y %H:%M:%S", filename="data/logfile.log")


class JaegerBot(commands.Bot):
    # Things to do before the bot connects
    async def setup_hook(self):
        # Initialize database pool
        await shared_resources.initialize_pool()
        await bot.loop.run_in_executor(None, shared_resources.initialize_gspread_service_account)

        # Load cogs from settings file
        for cog_str in shared_resources.botSettings['cogs']:
            await self.load_extension(cog_str)


# Define Intents and instanciate JaegerBot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = JaegerBot(
    command_prefix=get_prefix,
    intents=intents,
    owner_id=shared_resources.botSettings['owner_id'],
    help_command=commands.MinimalHelpCommand()
)

# Things that execute once after the bot has connected
@bot.event
async def on_ready():
    logging.info('The bot is now ready!')
    logging.info(f'Logged in as {bot.user}')

    # Add guilds that the bot is part of to db if not already in there, and trims nonexistent guilds
    async with shared_resources.dbPool.acquire() as conn:
        # Get records from db
        guild_id_list = []
        guild_id_records = await conn.fetch('SELECT guild_id FROM guilds;')
        for record in guild_id_records:
            guild_id_list.append(record['guild_id'])

        # Compare list from db with list from discord and add missing
        for guild in bot.guilds:
            if guild.id not in guild_id_list:
                async with conn.transaction():
                    await conn.execute('INSERT INTO guilds(guild_id) VALUES($1);', guild.id)

        # Compare list from discord with list from db and remove missing
        for id in guild_id_list:
            if id not in [guild.id for guild in bot.guilds]:
                async with conn.transaction():
                    await conn.execute('DELETE FROM guilds WHERE guild_id = $1;', id)

    # Synchronize App-Commands with discord
    await bot.tree.sync()


##### Database syncronisation #####
# Add guild to db if it gets invited
@bot.event
async def on_guild_join(guild):
    async with shared_resources.dbPool.acquire() as conn:
        async with conn.transaction():
            await conn.execute('INSERT INTO guilds(guild_id) VALUES($1);', guild.id)

# Remove guild from db if it gets kicked
@bot.event
async def on_guild_remove(guild):
    async with shared_resources.dbPool.acquire() as conn:
        async with conn.transaction():
            await conn.execute('DELETE FROM guilds WHERE guild_id = $1;', guild.id)


##### Maintainance and Troubleshooting #####
# Basic ping command to enable troubleshooting
@bot.hybrid_command()
async def ping(ctx):
    """Reports the bots latency."""
    await ctx.reply(f'Pong! :ping_pong:\n```The bot has {bot.latency:.2}s latency.```')

# Command for loading new cog
@commands.is_owner()
@bot.command(hidden=True)
async def load(ctx, *, module):
    """Loads a module."""
    try:
        await bot.load_extension(f'cogs.{module}')
        await bot.tree.sync()
    except commands.ExtensionError as e:
        logging.error(f'{e.__class__.__name__}: {e}')
        await ctx.reply(f'{e.__class__.__name__}: {e}')
    else:
        logging.info(f'module cogs.{module} was loaded successfully')
        await ctx.reply(':thumbsup:')

# Command for unloading cogs
@commands.is_owner()
@bot.command(hidden=True)
async def unload(ctx, *, module):
    """Unloads a module."""
    try:
        await bot.unload_extension(f'cogs.{module}')
        await bot.tree.sync()
    except commands.ExtensionError as e:
        logging.error(f'{e.__class__.__name__}: {e}')
        await ctx.reply(f'{e.__class__.__name__}: {e}')
    else:
        logging.info(f'module cogs.{module} was unloaded successfully')
        await ctx.reply(':thumbsup:')

# Command for reloading cogs
@commands.is_owner()
@bot.command(hidden=True)
async def reload(ctx, *, module):
    """Reloads a module."""
    try:
        await bot.reload_extension(f'cogs.{module}')
        await bot.tree.sync()
    except commands.ExtensionError as e:
        logging.error(f'{e.__class__.__name__}: {e}')
        await ctx.reply(f'{e.__class__.__name__}: {e}')
    else:
        logging.info(f'module cogs.{module} was reloaded successfully')
        await ctx.reply(':thumbsup:')

# Print currently loaded cogs
@commands.is_owner()
@bot.command(hidden=True)
async def loaded(ctx):
    """Reports all loded modules."""
    await ctx.reply(f'```{bot.extensions}```')

bot.run(shared_resources.botSettings['token'])
