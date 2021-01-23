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
    @commands.cooldown(rate=1, per=300, type=commands.BucketType.guild)  # Cooldown blocks command -everytime its used -for 300sec -for the guild that called it
    @commands.command()
    async def paritycheck(self, ctx):
        async with dbPool.acquire() as conn:
            outfit_name = await conn.fetchval("SELECT outfit_name FROM guilds WHERE guild_id = $1;", ctx.guild.id)
        if outfit_name is None:
            raise NoOutfitNameError("No outfit name set")

        embed = discord.Embed(title="Checkresults")

        async with auraxium.Client(service_id=botSettings['censusToken']) as client:

            outfit = await client.get_by_name(ps2.Outfit, outfit_name)
            if outfit is None:
                raise InvalidOutfitNameError("The outfit name you have specified does not seem to be valid")
            outfit_members = await outfit.members()

            await ctx.reply("```Starting comparison...\nThis tends to take a while...```")

            guild_members = ctx.guild.members
            for member in guild_members:
                # First check if the discord members name matches any character name
                outfit_member = None

                for _outfit_member in outfit_members:
                    character = await _outfit_member.character()
                    if character.name() == member.name or character.name() == member.nick:
                        outfit_member = _outfit_member
                        break

                # Dont check roles if its not an outfit member
                if outfit_member is None:
                    embed.add_field(name=member.name, value="Name does not match any outfit member.", inline=False)
                    continue

                matching_role = False
                for role in member.roles:
                    if role.name == outfit_member.data.rank:
                        matching_role = True

                if not matching_role:
                    embed.add_field(name=member.name, value="No Role matching outfit rank.", inline=False)

        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Paritycheck(bot))
