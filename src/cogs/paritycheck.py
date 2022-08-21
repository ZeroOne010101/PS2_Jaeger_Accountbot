from discord.ext import commands
import discord
from urllib.parse import quote
import aiohttp
from utils.shared_resources import dbPool, botSettings
from utils.errors import NoOutfitNameError, InvalidOutfitNameError, FailedCensusRequest

class Paritycheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.cooldown(rate=1, per=120, type=commands.BucketType.guild)  # Cooldown blocks command everytime its used for 300sec for the guild that called it
    @commands.hybrid_group(name="planetside-parity", fallback="check")
    async def ps2parity(self, ctx):
        """Compares all server members discord users to their ingame characters"""
        # Signal the server that the bot takes a while (timeout 15min instead of seconds)
        await ctx.defer()

        # Get outfit name from db
        async with dbPool.acquire() as conn:
            outfit_name = await conn.fetchval("SELECT outfit_name FROM guilds WHERE guild_id = $1;", ctx.guild.id)
        if outfit_name is None:
            raise NoOutfitNameError("No outfit name set")

        url_outfit_name = quote(outfit_name, safe="")
        url = f"https://census.daybreakgames.com/{botSettings['census_token']}/get/ps2:v2/outfit?name={url_outfit_name}&c:join=outfit_member^inject_at:members^list:1(character^inject_at:character)"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    raw_data = await response.json()
                    if len(raw_data['outfit_list']) < 1 or raw_data['returned'] == 0:
                        raise InvalidOutfitNameError("The outfit name you have specified does not seem to be valid")
                    members = raw_data['outfit_list'][0]['members']
                else:
                    raise FailedCensusRequest("Something went wrong when contacting the Planetside 2 API, please try again later.")

        outliers_list = []

        # Compare guild layout to outfit layout
        for guild_member in ctx.guild.members:

            # Exclude excempt members
            async with dbPool.acquire() as conn:
                exempt_member_id = await conn.fetchval("SELECT user_id FROM parity_exempt WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1) AND user_id = $2;", ctx.guild.id, guild_member.id)

            if exempt_member_id:
                continue

            matched_member = None

            if guild_member.nick:
                display_name = guild_member.nick
            else:
                display_name = guild_member.name

            # Match census member and character object to discord username
            for member in members:
                character = member['character']
                if character['name']['first'] in (guild_member.name, guild_member.nick):
                    matched_member = member
                    break

            if matched_member is None:
                outliers_list.append((display_name, "Name does not match any outfit member."))
                continue

            role_matches = False
            for role in guild_member.roles:
                if role.name == matched_member['rank']:
                    role_matches = True
                    break

            if role_matches:
                continue

            outliers_list.append((display_name, "No Role matching outfit rank."))

        if len(outliers_list) <= 0:
            outliers_list = [["None", "No deviations from the ingame outfit were found"]]

        embed_list = []
        embed = discord.Embed(title="Checkresults")

        for i in range(len(outliers_list)):
            name = outliers_list[i][0]
            reason = outliers_list[i][1]

            # If embed with new items too big, add old embed to list and create new one
            if (len(embed) + len(name) + len(reason)) > 6000:
                embed_list.append(embed)
                embed = discord.Embed(title="Checkresults")
            embed.add_field(name=name, value=reason, inline=False)

            # Ensures the last embed always gets added
            if i >= (len(outliers_list) - 1):
                embed_list.append(embed)

        for embed in embed_list:
            await ctx.reply(embed=embed)

    @commands.guild_only()
    @ps2parity.command(name="show_excluded")
    async def show_excluded(self, ctx):
        """Lists users excluded from the parity check"""
        async with dbPool.acquire() as conn:
            excluded_records = await conn.fetch("SELECT user_id FROM parity_exempt WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)

        userstrings = []

        for record in excluded_records:
            member = await ctx.guild.fetch_member(record['user_id'])
            if member is not None:
                if member.nick is not None:
                    display_name = member.nick
                else:
                    display_name = member.name

                userstrings.append(display_name)

        if len(userstrings) <= 0:
            userstrings = ["None"]
        printstring = "\n".join(userstrings)
        await ctx.reply(f"Here are the currently excluded users:\n`{printstring}`")

    @commands.guild_only()
    @ps2parity.command()
    async def exclude(self, ctx, user: discord.Member):  # Validation is handled by discord.ext via typing
        """Exclude a user from the parity check"""
        async with dbPool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("INSERT INTO parity_exempt(fk, user_id) VALUES((SELECT id FROM guilds WHERE guild_id = $1), $2);", ctx.guild.id, user.id)
        await ctx.reply(f"User {user.mention} has been excluded from the parity check")

    @commands.guild_only()
    @ps2parity.command(name="unexclude")
    async def include(self, ctx, user: discord.Member):  # Validation is handled by discord.ext via typing
        """Removes a user from the exclusion list"""
        async with dbPool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM parity_exempt WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1) AND user_id = $2;", ctx.guild.id, user.id)
        await ctx.reply(f"User {user.mention} has been unexcluded from the parity check")

async def setup(bot):
    await bot.add_cog(Paritycheck(bot))
