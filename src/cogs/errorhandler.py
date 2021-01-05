from discord.ext import commands
import logging
import traceback
from .utils.errors import AccountsBaseException
import gspread

class Errorhandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _log_trace_then_raise(self, ctx, error):
        logging.info(f"Ignoring exception {error.__class__.__name__} in command {ctx.command.name} with message: {error}")
        with open("data/logfile.log", "a") as logfile:
            traceback.print_tb(error.__traceback__, file=logfile)
        await ctx.send(f"```Error: An unexpected error has occured in the command \"{ctx.command}\".\nPlease contact the Administrator.```")
        raise error

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Prevents any commands with local handlers from being handled here.
        if hasattr(ctx.command, 'on_error'):
            return

        # Prevents any cogs with an overwritten cog_command_error from being handled here.
        if ctx.cog:
            if ctx.cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
                return

        # Do nothing if the error is ignored
        ignored = (commands.CommandNotFound, )
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(f"```Error: {ctx.command} is currently disabled```")

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"```Error: Missing argument: {error.param}```")

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(f"```Error: {ctx.command} can not be used in private messages```")

        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"```{error}```")

        elif isinstance(error, AccountsBaseException):
            await ctx.send(f"```{error}```")

        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, gspread.exceptions.APIError):
                if error.original.response.status_code == 403:
                    await ctx.send("```Error: the bot does not have permission to access the sheet you have specified.```")
                else:
                    await self._log_trace_then_raise(ctx, error)
            else:
                await self._log_trace_then_raise(ctx, error)

        else:
            await self._log_trace_then_raise(ctx, error)

def setup(bot):
    bot.add_cog(Errorhandler(bot))
