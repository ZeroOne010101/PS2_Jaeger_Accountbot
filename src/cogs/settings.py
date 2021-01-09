from discord.ext import commands
from .utils.shared_recources import dbPool, gspread_service_account
import gspread

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ##### Jaeger Accounts #####
    @commands.guild_only()
    @commands.group(invoke_without_command=True, aliases=["utcoffset"])
    async def utc_offset(self, ctx, offset=None):
        async with dbPool.acquire() as conn:
            async with conn.transaction():
                db_offset = await conn.fetchval("SELECT utcoffset FROM guilds WHERE guild_id = $1;", ctx.guild.id)
        await ctx.reply(f"The UTC Offset for this Guild is currently set to `{db_offset} hours`.")

    @commands.guild_only()
    @utc_offset.command(name="set")  # Collides with builtin set
    async def set_utc_offset(self, ctx, offset):
        try:
            offset = int(offset)
        except ValueError:
            raise commands.BadArgument("Error: Please only enter numbers between -23 and 23")

        if offset >= -23 and offset <= 23:
            async with dbPool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute("UPDATE guilds SET utcoffset = $1 WHERE guild_id = $2;", offset, ctx.guild.id)
        else:
            raise commands.BadArgument("Error: Please only enter numbers between -23 and 23")

    @commands.guild_only()
    @commands.group(invoke_without_command=True, aliases=["jaegerurl"])
    async def jaeger_url(self, ctx):
        async with dbPool.acquire() as conn:
            async with conn.transaction():
                db_url = await conn.fetchval("SELECT url FROM sheet_urls WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)
                if db_url is None:
                    db_url = "not set"
        await ctx.reply(f"The account url for this guild is currently `{db_url}`.")

    @commands.guild_only()
    @jaeger_url.command(name="set")  # Collides with builtin set
    async def set_jaeger_url(self, ctx, url):
        try:
            await self.bot.loop.run_in_executor(None, gspread_service_account.open_by_url, url)
            async with dbPool.acquire() as conn:
                async with conn.transaction():
                    db_guild_id = await conn.fetchval("SELECT id FROM guilds WHERE guild_id = $1;", ctx.guild.id)
                    await conn.execute("INSERT INTO sheet_urls(fk, url) VALUES($1, $2);", db_guild_id, url)  # BUG @TheJerry This could be one for you, it should update if it already exists. This'd do it, but i dont get it: https://www.postgresql.org/docs/current/sql-insert.html#SQL-ON-CONFLICT
        except (gspread.SpreadsheetNotFound,
                gspread.exceptions.NoValidUrlKeyFound,
                gspread.exceptions.WorksheetNotFound,
                gspread.exceptions.APIError):
            raise commands.BadArgument("Error: The Spreadsheet that you have specified could not be found")

    @commands.guild_only()
    @jaeger_url.command()
    async def delete(self, ctx):
        async with dbPool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM sheet_urls WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)

def setup(bot):
    bot.add_cog(Settings(bot))
