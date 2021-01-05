from discord.ext import commands

class AccountsBaseException(commands.CommandError):
    """Base exception for all exceptions in this Cog"""
    pass

class NoSheetsUrlException(AccountsBaseException):
    """Exception to be raised when the guild has not set a google sheets url"""
    pass

class InvalidSheetsValue(AccountsBaseException):
    """Exception to be raised when the formatting of the sheets document is nonstandard"""
    pass
