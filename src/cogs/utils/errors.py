from discord.ext import commands

class AccountsBaseException(commands.CommandError):
    """Base exception for all exceptions in thie jaegeraccounts Cog"""
    pass

class NoSheetsUrlException(AccountsBaseException):
    """Exception to be raised when the guild has not set a google sheets url"""
    pass

class InvalidSheetsValue(AccountsBaseException):
    """Exception to be raised when the formatting of the sheets document is nonstandard"""
    pass

class BookingDurationLimitExceededError(AccountsBaseException):
    """Exception to be raised when user tries to book account for duration longer than allowed limit"""
    pass

class ParityBaseException(commands.CommandError):
    """Base exception for all exceptions in the paritycheck Cog"""
    pass

class NoOutfitNameError(ParityBaseException):
    """Exception to be raised when the guild has not set an outfit name"""
    pass

class InvalidOutfitNameError(ParityBaseException):
    """Exception to be raised when the guild has not set an outfit name"""
    pass
