from discord.ext import commands
import discord

class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Basic ping command to enable connection Troubleshooting
    @commands.command()
    async def ping(self, ctx):
        """Reports the bots latency."""
        await ctx.reply(f'Pong! :ping_pong:\n```The bot has {self.bot.latency:.2}s latency.```')

    # Info command to display basic information
    @commands.command(aliases=["about"])
    async def info(self, ctx):
        info_embed = discord.Embed(title="Info", description="A discord bot that assigns temporary jaeger accounts.")
        info_embed.add_field(name="Code & Documentation", value="[Github](https://github.com/ZeroOne010101/PS2_Jaeger_Accountbot)", inline=False)
        info_embed.add_field(name="Help", value="`!help`\n[Discord](https://discord.com/invite/yvnRZjJ)\n[Github](https://github.com/ZeroOne010101/PS2_Jaeger_Accountbot/issues)", inline=False)
        await ctx.reply(embed=info_embed)
