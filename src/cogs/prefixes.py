from discord.ext import commands
from .utils.shared_recources import dbPool
import logging
from asyncpg import PostgresError, StringDataRightTruncationError

class Prefixes(commands.Cog):
    """Cog that contains prefix settings for server admins"""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx):
        """Add, remove or view prefixes.
        Lists all active prefixes if no argumants are given."""
        prefix_str = ""
        try:
            async with dbPool.acquire() as conn:
                async with conn.transaction():
                    db_records = await conn.fetch("SELECT prefix FROM prefixes WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)
                    for db_record in db_records:
                        prefix_str += f"{db_record['prefix']} "
            if prefix_str != "":
                await ctx.send(f"```{prefix_str[:-1]}```")
            else:
                await ctx.send("```No prefix set, default is ! or @ZeroBot```")
        except PostgresError as error:
            logging.error(f'{error.__class__.__name__}: {error}')
            raise error
        except Exception as error:
            logging.error(f'{error.__class__.__name__}: {error}')
            raise error

    @prefix.command()
    async def add(self, ctx, prefix):
        """Adds a prefix.
        If this is the first prefix added for a server, it overrides the default prefix."""
        try:
            async with dbPool.acquire() as conn:
                async with conn.transaction():
                    guild_id = await conn.fetchval("SELECT id FROM guilds WHERE guild_id = $1;", ctx.guild.id)
                    await conn.execute("INSERT INTO prefixes VALUES ($1, $2);", guild_id, prefix)
        except StringDataRightTruncationError as e:
            limit = e.message.replace("value too long for type character varying(", "")
            limit = limit.replace(")", "")
            await ctx.send(f"```Error: this prefix exceeds the limit of {limit} characters```")
        except PostgresError as error:
            logging.error(f'PostgresError: {error.__class__.__name__}: {error}')
            raise error
        except Exception as error:
            logging.error(f'{error.__class__.__name__}: {error}')
            raise error

    @prefix.command()
    async def remove(self, ctx, prefix):
        """Removes a prefix.
        If all prefixes are removed, the prefix reverts to the default."""
        try:
            async with dbPool.acquire() as conn:
                async with conn.transaction():
                    guild_id = await conn.fetchval("SELECT id FROM guilds WHERE guild_id = $1;", ctx.guild.id)
                    await conn.execute("DELETE FROM prefixes WHERE fk=$1 AND prefix=$2;", guild_id, prefix)
        except PostgresError as error:
            logging.error(f'{error.__class__.__name__}: {error}')
            raise error
        except Exception as error:
            logging.error(f'{error.__class__.__name__}: {error}')
            raise error

def setup(bot):
    bot.add_cog(Prefixes(bot))
