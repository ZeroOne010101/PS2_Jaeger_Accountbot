from discord.ext import commands
import discord
import utils.shared_resources as shared_resources

class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Info command to display basic information
    @commands.hybrid_command(aliases=["about"])
    async def info(self, ctx):
        info_embed = discord.Embed(title="Info", description="A discord bot that assigns temporary jaeger accounts.")
        info_embed.add_field(name="Code & Documentation", value="[Github](https://github.com/ZeroOne010101/PS2_Jaeger_Accountbot)", inline=False)
        info_embed.add_field(name="Help", value="`!help`\n[Discord](https://discord.com/invite/yvnRZjJ)\n[Github](https://github.com/ZeroOne010101/PS2_Jaeger_Accountbot/issues)", inline=False)
        await ctx.reply(embed=info_embed)

    # Prints the Invite url inside an embed
    @commands.hybrid_command()
    async def invite(self, ctx):
        embed = discord.Embed(title="Invite me!", url=shared_resources.botSettings['inviteLink'])
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
