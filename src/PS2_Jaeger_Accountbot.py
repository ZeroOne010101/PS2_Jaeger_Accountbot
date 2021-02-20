from discord.ext import commands
import discord
import logging
import os
import cogs.utils.shared_recources as shared_recources

# Ensuring working directory is correct
os.chdir(shared_recources.path)

# Setting up basic logging
logging.basicConfig(format="[%(asctime)s] %(levelname)s:%(message)s", level=logging.INFO, datefmt="%d.%m.%Y %H:%M:%S", filename="data/logfile.log")

# Gets prefixes from db
async def _get_prefix(bot, ctx):
    """
    Function that is used by the bot to determine the custom prefix of the guild.
    Defaults to '!' if no custom prefix has been set.
    """
    async with shared_recources.dbPool.acquire() as conn:
        db_records = await conn.fetch('SELECT prefix FROM prefixes WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);', ctx.guild.id)
        if db_records:
            if len(db_records) > 1:
                prefixes = [record['prefix'] for record in db_records]
            else:
                prefixes = [db_records[0]['prefix']]
        else:
            prefixes = ['!']
    return commands.when_mentioned_or(*prefixes)(bot, ctx)

# Define gateway intents
intents = discord.Intents.default()
intents.members = True  # Privileged intent, needs Verification at 100+ Guilds
# Disable spammy intents
intents.typing = False
intents.presences = False

# Define bot
bot = commands.Bot(
    command_prefix=_get_prefix, owner_id=shared_recources.botSettings['owner_id'],
    intents=intents, help_command=commands.MinimalHelpCommand()
)

# Checks if the bot is ready. Nothing executes boefore the check has passed.
@bot.event
async def on_ready():
    logging.info('The bot is now ready!')
    logging.info(f'Logged in as {bot.user}')

    # Initialize database pool
    await shared_recources.initialize_pool()
    await bot.loop.run_in_executor(None, shared_recources.initialize_gspread_service_account)

    # Load cogs from settings file
    for cog_str in shared_recources.botSettings['cogs']:
        bot.load_extension(cog_str)

    # Add guilds that the bot is part of to db if not already in there
    async with shared_recources.dbPool.acquire() as conn:
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

@bot.command()
async def ping(ctx):
    """Reports the bots latency."""
    await ctx.reply(f'Pong! :ping_pong:\n```The bot has {bot.latency}s latency.```')

@bot.command(aliases=["about"])
async def info(ctx):
    info_embed = discord.Embed(title="Info", description="A discord bot that assigns temporary jaeger accounts.")
    info_embed.add_field(name="Code & Documentation", value="[Github](https://github.com/ZeroOne010101/PS2_Jaeger_Accountbot)", inline=False)
    info_embed.add_field(name="Help", value="`!help`\n[Discord](https://discord.com/invite/yvnRZjJ)\n[Github](https://github.com/ZeroOne010101/PS2_Jaeger_Accountbot/issues)", inline=False)
    await ctx.reply(embed=info_embed)

# Add guild to db if it gets invited
@bot.event
async def on_guild_join(guild):
    async with shared_recources.dbPool.acquire() as conn:
        async with conn.transaction():
            await conn.execute('INSERT INTO guilds(guild_id) VALUES($1);', guild.id)

# Remove guild from db if it gets kicked
@bot.event
async def on_guild_remove(guild):
    async with shared_recources.dbPool.acquire() as conn:
        async with conn.transaction():
            await conn.execute('DELETE FROM guilds WHERE guild_id = $1;', guild.id)

##### Cog load/unload/reload commands #####
# These commands are not to be placed in cogs,
# as their purpose is to load/unload them.

@commands.is_owner()
@bot.command(hidden=True)
async def load(ctx, *, module):
    """Loads a module."""
    try:
        bot.load_extension(f'cogs.{module}')
    except commands.ExtensionError as e:
        logging.error(f'{e.__class__.__name__}: {e}')
        await ctx.reply(f'{e.__class__.__name__}: {e}')
    else:
        logging.info(f'module cogs.{module} was loaded successfully')
        await ctx.reply(':thumbsup:')

@commands.is_owner()
@bot.command(hidden=True)
async def unload(ctx, *, module):
    """Unloads a module."""
    try:
        bot.unload_extension(f'cogs.{module}')
    except commands.ExtensionError as e:
        logging.error(f'{e.__class__.__name__}: {e}')
        await ctx.reply(f'{e.__class__.__name__}: {e}')
    else:
        logging.info(f'module cogs.{module} was unloaded successfully')
        await ctx.reply(':thumbsup:')

@commands.is_owner()
@bot.command(hidden=True)
async def reload(ctx, *, module):
    """Reloads a module."""
    try:
        bot.reload_extension(f'cogs.{module}')
    except commands.ExtensionError as e:
        logging.error(f'{e.__class__.__name__}: {e}')
        await ctx.reply(f'{e.__class__.__name__}: {e}')
    else:
        logging.info(f'module cogs.{module} was reloaded successfully')
        await ctx.reply(':thumbsup:')

@commands.is_owner()
@bot.command(hidden=True)
async def loaded(ctx):
    """Reports all loded modules."""
    await ctx.reply(f'```{bot.extensions}```')

bot.run(shared_recources.botSettings['token'])
