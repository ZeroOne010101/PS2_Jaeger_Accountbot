from discord.ext import commands
import discord
from urllib.parse import quote
import aiohttp
from .utils.shared_resources import dbPool, botSettings
from .utils.errors import NoOutfitNameError, InvalidOutfitNameError, FailedCensusRequest

class Paritycheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.cooldown(rate=1, per=300, type=commands.BucketType.guild)  # Cooldown blocks command everytime its used for 300sec for the guild that called it
    @commands.command()
    async def paritycheck(self, ctx):
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
            matched_member = None

            if guild_member.nick is not None:
                display_name = guild_member.nick
            else:
                display_name = guild_member.name

            # Match member and character object by discord username
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

def setup(bot):
    bot.add_cog(Paritycheck(bot))
