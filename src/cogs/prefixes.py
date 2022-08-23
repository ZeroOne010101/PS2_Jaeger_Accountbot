from discord.ext import commands
from utils.shared_resources import dbPool
import logging
from asyncpg import PostgresError, StringDataRightTruncationError
from utils.checks import is_admin, is_mod

class Prefixes(commands.Cog):
    """Cog that contains prefix settings for admins and mods"""
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(invoke_without_command=True, fallback="show")
    async def prefix(self, ctx):
        """Lists all active prefixes"""
        prefix_str = ""
        try:
            async with dbPool.acquire() as conn:
                db_records = await conn.fetch("SELECT prefix FROM prefixes WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)
                for db_record in db_records:
                    prefix_str += f"{db_record['prefix']}\n"
            if prefix_str != "":
                await ctx.reply(f"```{prefix_str[:-1]}```")
            else:
                await ctx.reply("```No prefix set, default is ! or @ZeroBot```")
        except PostgresError as error:
            logging.error(f'{error.__class__.__name__}: {error}')
            raise error
        except Exception as error:
            logging.error(f'{error.__class__.__name__}: {error}')
            raise error

    @commands.guild_only()
    @commands.check_any(is_admin(), is_mod())
    @prefix.command()
    async def add(self, ctx, prefix):
        """Adds a new prefix"""
        try:
            async with dbPool.acquire() as conn:
                async with conn.transaction():
                    guild_id = await conn.fetchval("SELECT id FROM guilds WHERE guild_id = $1;", ctx.guild.id)
                    await conn.execute("INSERT INTO prefixes VALUES ($1, $2);", guild_id, prefix)
        except StringDataRightTruncationError as e:
            limit = e.message.replace("value too long for type character varying(", "")
            limit = limit.replace(")", "")
            await ctx.reply(f"```Error: this prefix exceeds the limit of {limit} characters```")
        except PostgresError as error:
            logging.error(f'PostgresError: {error.__class__.__name__}: {error}')
            raise error
        except Exception as error:
            logging.error(f'{error.__class__.__name__}: {error}')
            raise error

    @commands.guild_only()
    @commands.check_any(is_admin(), is_mod())
    @prefix.command()
    async def delete(self, ctx, prefix):
        """Delete a prefix"""
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

async def setup(bot):
    await bot.add_cog(Prefixes(bot))
