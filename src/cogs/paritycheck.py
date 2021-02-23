from discord.ext import commands
import discord
import auraxium
from auraxium import ps2
from .utils.shared_recources import dbPool, botSettings
from .utils.errors import NoOutfitNameError, InvalidOutfitNameError

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

        # Inform user of delay
        await ctx.reply("`Getting data, this may take some time...`")

        # Get census api data
        async with auraxium.Client(service_id=botSettings['censusToken']) as client:
            outfit = await client.get_by_name(ps2.Outfit, outfit_name)
            if outfit is None:
                raise InvalidOutfitNameError("The outfit name you have specified does not seem to be valid")

            outfit_member_list = await outfit.members()
            outfit_character_list = [await i.character() for i in outfit_member_list]

        outliers_list = []

        # Compare guild layout to outfit layout
        for guild_member in ctx.guild.members:
            matched_member = None
            matched_character = None
            # Leaving this in in case determining the role is ever necessary
            # matched_role = None

            if guild_member.nick is not None:
                display_name = guild_member.nick
            else:
                display_name = guild_member.name

            # Match member and character object by discord username
            for outfit_member, outfit_character in zip(outfit_member_list, outfit_character_list):
                if outfit_character.name() in (guild_member.name, guild_member.nick):
                    matched_character = outfit_character
                    matched_member = outfit_member
                    break

            if matched_character is None:
                outliers_list.append((display_name, "Name does not match any outfit member."))
                continue

            for role in guild_member.roles:
                if role.name == matched_member.data.rank:
                    # Leaving this in in case determining the role is ever necessary
                    # matched_role = role
                    continue

            outliers_list.append((display_name, "No Role matching outfit rank."))

        embed_list = []
        embed = discord.Embed(title="Checkresults")
        for name, reason in outliers_list:
            # If embed with new items too big, add old embed to list and create new one
            if (len(embed) + len(name) + len(reason)) > 6000:
                embed_list.append(embed)
                embed = discord.Embed(title="Checkresults")
            embed.add_field(name=name, value=reason, inline=False)

        for embed in embed_list:
            await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Paritycheck(bot))
