from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def test(self, ctx):
        for i in ctx.guild.members:
            print(i)

        print(list(ctx.guild.members))

async def setup(bot):
    await bot.add_cog(Test(bot))
