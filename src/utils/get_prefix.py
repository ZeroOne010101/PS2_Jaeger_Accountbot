import utils.shared_resources as shared_resources
from discord.ext import commands

# Gets prefixes from db
async def get_prefix(bot, ctx):
    """
    Function that is used by the bot to determine the custom prefix of the guild.
    Defaults to '!' if no custom prefix has been set.
    """
    async with shared_resources.dbPool.acquire() as conn:
        db_records = await conn.fetch('SELECT prefix FROM prefixes WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);', ctx.guild.id)
        if db_records:
            if len(db_records) > 1:
                prefixes = [record['prefix'] for record in db_records]
            else:
                prefixes = [db_records[0]['prefix']]
        else:
            prefixes = ['!']
    return commands.when_mentioned_or(*prefixes)(bot, ctx)
