from discord.ext import commands
import discord
from cogs.utils.shared_recources import dbPool, gspread_service_account
import datetime
import re
from typing import Union
from cogs.utils.errors import InvalidSheetsValue, NoSheetsUrlException
import logging


class Account:
    def __init__(self, name: str, password: str, last_user: Union[str, None], last_booked_from: Union[datetime.datetime, None], last_booked_to: Union[datetime.datetime, None], account_row: Union[int, None]):
        self.name = name
        self.password = password
        self.last_user = last_user
        self.last_booked_from = last_booked_from
        self.last_booked_to = last_booked_to
        self.account_row = account_row

    def __repr__(self):
        return f"<Account Name: {self.name}, PW: {self.password}, last_user: {self.last_user}, last_boked_from: {self.last_booked_from}, last booked_to: {self.last_booked_to}>"

    @property
    def embed(self):
        terms_of_service = "\u2022 You may only use the account for this occation.\n\u2022 You are not allowed create, delete, or add characters to the account.\n\u2022 You are not allowed to ASP the charakter.\n" \
                           "\u2022 You are expected to follow the [Jaeger Code of Conduct](https://docs.google.com/document/d/1zlx6BgZKHyKvt2d04d1jnyjvNZLgeLgsPANg38ANRS4/edit) and not disturb any of the [currently ongoing events](https://docs.google.com/spreadsheets/d/1eA4ybkAiz-nv_mPxu_laL504nwTDmc-9GnsojnTiSRE/edit) on the server.\n" \
                           "\u2022 Failure to follow these rules may result in repercussions, both for you personally and for your outfit."

        embed = discord.Embed(title="Account Assignment")
        embed.add_field(name="Account", value=self.name, inline=True)
        embed.add_field(name="Password", value=self.password, inline=True)
        embed.add_field(name="Terms of Service",
                        value=terms_of_service, inline=False)

        return embed

    @property
    def is_booked(self):
        if self.last_booked_to and self.last_booked_to >= datetime.datetime.now(tz=self.last_booked_to.tzinfo):
            return True
        else:
            return False


class SheetData:
    def __init__(self):
        self.raw_data = None
        self.accounts = None
        self.ctx = None

    def _get_sheet_data(self, url: str):
        """Fetches all relevant data from the spreadsheet"""

        sheet1 = gspread_service_account.open_by_url(url).get_worksheet(0)
        sheet_data = sheet1.get("1:13")
        return sheet_data

    def _write_sheet_data(self, url: str, row: int, col: int, data: str):
        """Writes $data to cell specified by $row and $col Note: row and col in gspread start at index 1"""

        sheet = gspread_service_account.open_by_url(url).get_worksheet(0)
        update_info = sheet.update_cell(row, col, data)
        logging.info(f"Updated: `{update_info['updatedRange']}` with data: `{data}`")
        return

    async def _get_accounts(self):
        """Parses accounts out of the raw data"""

        async with dbPool.acquire() as conn:
            utcoffset = await conn.fetchval("SELECT utcoffset FROM guilds WHERE guild_id = $1;", self.ctx.guild.id)

        accounts = []
        # This is for writing to sheet later. Don't need to iterate over accounts again, if just save row index of account
        account_row = 2
        for row in self.raw_data[1:]:
            name, password = row[0:2]

            indexed_row = enumerate(row)
            last_user = None
            for index, entry in reversed(list(indexed_row)):
                if index > 1:
                    if entry != "":
                        match = re.match(
                            r"(.+)\((\d?\d:\d\d[AP]M)(?:-(\d?\d:\d\d[AP]M))?\)", entry)
                        if match:
                            last_user = match.group(1)
                            from_time_str = match.group(2)
                            to_time_str = match.group(3)
                        else:
                            raise InvalidSheetsValue(
                                "There seems to be a time (username) formatting error in the google sheets document.")

                        date_str = self.raw_data[:1][0][index]
                        from_datetime_str = date_str + "_" + from_time_str

                        try:
                            last_booked_from = datetime.datetime.strptime(
                                from_datetime_str, '%m/%d/%Y_%I:%M%p')
                            last_booked_from = last_booked_from.replace(tzinfo=datetime.timezone(
                                datetime.timedelta(hours=utcoffset)))  # Makes datetime object timezone aware

                            last_booked_to = None
                            if to_time_str:
                                to_datetime_str = date_str + "_" + to_time_str
                                last_booked_to = datetime.datetime.strptime(
                                    to_datetime_str, "%m/%d/%Y_%I:%M%p")
                                last_booked_to = last_booked_to.replace(tzinfo=datetime.timezone(
                                    datetime.timedelta(hours=utcoffset)))  # Makes datetime object timezone aware
                                # Handle booking across days
                                if last_booked_from > last_booked_to:
                                    last_booked_to += datetime.timedelta(
                                        hours=24)
                            break
                        except ValueError:
                            raise InvalidSheetsValue(
                                "There seems to be a date (top row) or time (username) formatting error in the google sheets document.")
                else:
                    last_user = None
                    last_booked_from = None
                    last_booked_to = None

            accounts.append(Account(name, password, last_user,
                                    last_booked_from, last_booked_to, account_row))
            account_row += 1
        return accounts

    async def user_has_account(self):
        """Returns the users currently booked account or None"""
        # Necessary because author.nick is None if the user has not changed his name on the server
        name = self.ctx.author.name
        if self.ctx.author.nick is not None:
            name = self.ctx.author.nick

        for account in self.accounts:
            if account.last_user == name:
                if account.is_booked:
                    return account
        return None

    @classmethod
    async def from_url(cls, bot: commands.Bot, ctx: commands.Context, url: str):
        """Creates a SheetData object from the arguments given"""
        cls = cls()
        cls.ctx = ctx
        cls.raw_data = await bot.loop.run_in_executor(None, cls._get_sheet_data, url)
        cls.accounts = await cls._get_accounts()
        return cls

    async def insert_booking(self, bot: commands.Bot, ctx: commands.Context, url: str, account: Account):
        # Will need to compare dates
        async with dbPool.acquire() as conn:
            utcoffset = await conn.fetchval("SELECT utcoffset FROM guilds WHERE guild_id = $1;", ctx.guild.id)
        
        raw_dates = self.raw_data[0]
        indexed_dates = enumerate(raw_dates)
        last_date = None
        last_index = len(raw_dates) - 1
        for index, date in reversed(list(indexed_dates)):
            try:
                last_date = datetime.datetime.strptime(date, "%m/%d/%Y")
                last_index = index
                break
            except ValueError:
                logging.info(f"`{date}` could not be parsed when when inserting booking")

        # Compare last date, so can write to same column
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=utcoffset)))
        today = now.date()

        create_new_column = False
        # If last date in sheet is before today, create new row
        if last_date is None or today > last_date.date():
            last_date = today
            last_index = len(raw_dates) + 1
            create_new_column = True
        # if last day in sheet is today, but account was already booked for today, create new date column
        elif account.last_booked_to and account.last_booked_to.date() == today:
            last_date = today
            last_index = len(raw_dates) + 1
            create_new_column = True
        
        # Add new date column if needed
        if create_new_column:
            await bot.loop.run_in_executor(None, self._write_sheet_data, url, 1, last_index, last_date.strftime("%m/%d/%Y"))

        # Prepare data to write
        # TODO later will allow to book for more than 1 hour, need to figure out how
        # TODO figure out case when account booked for today and tmr

        name = ctx.author.name
        if ctx.author.nick is not None:
            name = ctx.author.nick

        
        hrs_now = now.strftime("%I:%M%p")
        hrs_after_x = (now + datetime.timedelta(hours=1)).strftime("%I:%M%p")
        write_data = f"{name}({hrs_now}-{hrs_after_x})"
        write_row = account.account_row
        write_col = last_index

        await bot.loop.run_in_executor(None, self._write_sheet_data, url, write_row, write_col, write_data)

class AccountDistrubution(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _account_to_sheet(self, url, account):
        gspread_service_account.open_by_url(url).sheet1

    @commands.guild_only()
    @commands.group(invoke_without_command=True)
    async def account(self, ctx):
        async with dbPool.acquire() as conn:
            url = await conn.fetchval("SELECT url FROM sheet_urls WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)
        if url is None:
            raise NoSheetsUrlException(
                "There is no google sheets url associated with this guild.")

        sheet_data = await SheetData.from_url(self.bot, ctx, url)
        account = await sheet_data.user_has_account()

        if account is not None:
            await ctx.reply(f"Your currently assigned account is: `{account.name}`.\n"
                            "Please check your PMs for the login details.")
        else:
            await ctx.reply(f"{ctx.author.mention}\nYou have not been assigned any accounts for today.\n"
                            "Please use the `!account book` command or ask your OVO rep for account assignment.")

    @commands.guild_only()
    @account.command()
    async def book(self, ctx):
        async with dbPool.acquire() as conn:
            url = await conn.fetchval("SELECT url FROM sheet_urls WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)
        if url is None:
            raise NoSheetsUrlException(
                "There is no google sheets url associated with this guild.")

        sheet_data = await SheetData.from_url(self.bot, ctx, url)

        # Necessary because author.nick is None if the user has not changed his name on the server
        name = ctx.author.name
        if ctx.author.nick is not None:
            name = ctx.author.nick

        # Try to assign accounts to the person that last had it as often as possible.
        for account in sheet_data.accounts:
            if account.last_user == name:
                if account.is_booked:
                    await ctx.reply(f"You have already been assigned: `{account.name}`.\n"
                                    "Please check your PMs for the login details.")
                    return
                else:
                    await sheet_data.insert_booking(self.bot, ctx, url, account)
                    await ctx.author.send(embed=account.embed)
                    return

        # If the user does not have any prior accounts, assign the first free one
        for account in sheet_data.accounts:
            if account.is_booked:
                continue
            else:
                await sheet_data.insert_booking(self.bot, ctx, url, account)
                await ctx.author.send(embed=account.embed)
                return

        # If the function made it this far, there are no free accounts available
        await ctx.author.send("```There are currently no free accounts.\nIf you need one urgently, talk to your OVO rep.```")

    @commands.guild_only()
    @commands.command()
    async def distribute_accounts(self, ctx: commands.Context):
        """
        Distributes accounts to all mentioned users.

        Arguments:
        force       Distributes accounts regardless of prior allocation
        """
        async with dbPool.acquire() as conn:
            async with conn.transaction():
                url = await conn.fetch('SELECT url FROM jaeger_urls WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);', ctx.guild.id)

        accounts = await self._get_accounts(url)

        if len(accounts) >= len(ctx.message.mentions):
            for member in ctx.message.mentions:
                # Making sure account usage is evenly spread
                random.shuffle(accounts)
                account = accounts.pop()
                await member.send(str(account))
                await ctx.author.send(f"Member {member.nick} has been assigned account {account.name}.")

        else:
            raise NotImplementedError("MAKE OWN EXCEPTION HERE")


# from discord.ext import commands
# import discord
# from .utils.shared_recources import dbPool
# import gspread
# import datetime
# import random
# import logging
# from asyncpg import PostgresError

# class Account:
#     def __init__(self, name:str, password: str, last_user: str, last_booked: datetime.datetime):
#         self.name = name
#         self.password = password
#         self.last_user = last_user
#         self.last_booked = last_booked

#     def embed(self):
#         terms_of_service = "\u2022 You may only use the account for this occation.\n\u2022 You are not allowed create, delete, or add characters to the account.\n\u2022 You are not allowed to ASP the charakter.\n" \
#                            "\u2022 You are expected to follow the [Jaeger Code of Conduct](https://docs.google.com/document/d/1zlx6BgZKHyKvt2d04d1jnyjvNZLgeLgsPANg38ANRS4/edit) and not disturb any of the [currently ongoing events](https://docs.google.com/spreadsheets/d/1eA4ybkAiz-nv_mPxu_laL504nwTDmc-9GnsojnTiSRE/edit) on the server.\n" \
#                            "\u2022 Failure to follow these rules may result in repercussions, both for you personally and for your outfit."

#         embed = discord.Embed(title="Account Assignment")
#         embed.add_field(name="Account", value=self.name, inline=True)
#         embed.add_field(name="Password", value=self.password, inline=True)
#         embed.add_field(name="Terms of Service", value=terms_of_service, inline=False)

#         return embed

#     def is_booked(self):
#         now = datetime.datetime.now(self.last_booked.tzinfo)

#         formatstring = "%m/%d/%Y"
#         now = now.strftime(formatstring)
#         last_booked = self.last_booked.strftime(formatstring)

#         if now == last_booked:
#             return True
#         else:
#             return False

# class AccountDistrubutor(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.serviceAccount = gspread.service_account(filename=r"D:\Dateien\Programmieren\Python\PS2 Jaeger Accountbot\data\ps2jaegeraccountbot-8fd42185680c.json")

# # TODO
# # Outline:
# # !account - gets currently assigned account if there is any
# # !account get - gets an account if user doesnt have one yet
# # !account distrubute - distribute accounts to mentions if accounts are free, skip those mentioned that already have one for the day
# # !account forcedistribute - distributes accounts to mentions regardless of prior allocation

#     def _get_sheet_data(self, url: str):
#         """Fetches all relevant data from the spreadsheet"""

#         sheet1 = shared_recources.gspread_service_account.open_by_url(url).sheet1
#         sheet_data = sheet1.get("1:13")
#         return sheet_data

#     async def _get_accounts(self, ctx: commands.Context, sheet_data: list):
#         """Parses accounts out of the raw data"""
#         async with dbPool.acquire() as conn:
#                 async with conn.transaction():
#                     utcoffset = await conn.fetchval("SELECT utcoffset FROM guilds WHERE guild_id = $1;", ctx.guild.id)

#         accounts = []

#         for row in sheet_data[1:]:
#             name, password = row[0:2]

#             indexed_row = enumerate(row)
#             last_user = None
#             for index, entry in reversed(list(indexed_row)):
#                 if entry != "":
#                     last_user = entry
#                     last_booked_str = sheet_data[:1][0][index]
#                     try:
#                         last_booked = datetime.datetime.strptime(last_booked_str, "%m/%d/%Y")
#                         last_booked = last_booked.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=utcoffset))) # Makes datetime object timezone aware
#                         break
#                     except ValueError:
#                         await ctx.reply("```Error: There seems to be a date formatting error in the google sheets document.```")
#                         raise NotImplementedError("TODO: Make custom errorhandler-compatible exception for invalid google-sheet values") #TODO: Make custom errorhandler-compatible exception for invalid google-sheet values to outsource this

#             accounts.append(Account(name, password, last_user, last_booked))
#         return accounts

#     async def _user_has_account(self, ctx, accounts):
#         for account in accounts:
#             # Necessary because author.nick is None if the user has not changed his name on the server
#             if not ctx.author.nick is None:
#                 name = ctx.author.nick
#             else:
#                 name = ctx.author.name

#             if account.last_user == name:
#                 if account.is_booked:
#                     return account
#         return None

# ##### Command Section #####
#     @commands.guild_only()
#     @commands.group(invoke_without_command=True)
#     async def account(self, ctx):
#         async with dbPool.acquire() as conn:
#                 async with conn.transaction():
#                     url = await conn.fetchval("SELECT url FROM sheet_urls WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)
#         if url is None:
#             await ctx.send(f"{ctx.author.mention}\nThere is no google sheets url associated with this guild.\n"\
#                             "Please use the `!jaeger_url` command to to set a url.")
#             return
#         sheet_data = await self.bot.loop.run_in_executor(None, self._get_sheet_data, url)
#         accounts = await self._get_accounts(ctx, sheet_data)

#         account = await self._user_has_account(ctx, accounts)
#         if not account is None:
#             await ctx.send(f"Your currently assigned account is: `{account.name}`.\n"\
#                             "Please check your PMs for the login details.")
#         else:
#             await ctx.send(f"{ctx.author.mention}\nYou have not been assigned any accounts for today.\n"\
#                             "Please use the `!account book` command or ask your OVO rep for account assignment.")

#     @commands.guild_only()
#     @account.command()
#     async def book(self, ctx):
#         async with dbPool.acquire() as conn:
#                 async with conn.transaction():
#                     url = await conn.fetchval("SELECT url FROM sheet_urls WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)
#         if url is None:
#             await ctx.send(f"{ctx.author.mention}\nThere is no google sheets url associated with this guild.\n"\
#                             "Please use the `!jaeger_url` command to to set a url.")
#             return

#         sheet_data = await self.bot.loop.run_in_executor(None, self._get_sheet_data, url)
#         accounts = await self._get_accounts(ctx, sheet_data)

#         # Try to assign accounts to the person that last had it as often as possible
#         for account in accounts:
#             # Necessary because author.nick is None if the user has not changed his name on the server
#             if not ctx.author.nick is None:
#                 name = ctx.author.nick
#             else:
#                 name = ctx.author.name

#             if account.last_user == name:
#                 if account.is_booked:
#                     await ctx.send(f"You have already been assigned: `{account.name}`.\n"\
#                                     "Please check your PMs for the login details.")
#                     return
#                 else:
#                     await ctx.author.send(embed=account.embed())
#                     return
#         #TODO actually enter this into the google sheet
#         # If the user does not have any prior accounts, assign the first free one
#         for account in accounts:
#             if account.is_booked:
#                 continue
#             else:
#                 await ctx.author.send(embed=account.embed())
#                 return

#         # If the function made it this far, there are no free accounts available
#         await ctx.author.send("````There are currently no free accounts.\nIf you really need one, talk to your OVO rep.```")

#     @commands.guild_only()
#     @commands.command()
#     async def distribute_accounts(self, ctx: commands.Context):
#         """
#         Distributes accounts to all mentioned users.

#         Arguments:
#         force       Distributes accounts regardless of prior allocation
#         """
#         async with dbPool.acquire() as conn:
#             async with conn.transaction():
#                 url = await conn.fetch('SELECT url FROM jaeger_urls WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);', ctx.guild.id)

#         accounts = await self._get_accounts(url)

#         if len(accounts) >= len(ctx.message.mentions):
#             for member in ctx.message.mentions:
#                 random.shuffle(accounts)
#                 account = accounts.pop()
#                 await member.send(str(account))
#                 await ctx.author.send(f"Member {member.nick} has been assigned account {account.name}.")

#         else:
#             raise NotImplementedError("MAKE OWN EXCEPTION HERE")


def setup(bot):
    bot.add_cog(AccountDistrubution(bot))


"""
from __future__ import print_function
import gspread
from discord.ext import commands
import datetime

class Account:
    def __init__(self, accountName, accountPassword):
        self.name = accountName
        self.password = accountPassword
        self.available = True

    def setAvailability(self, val: bool):
        self.available = val

class AccountDistrubutor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.serviceAccount = gspread.service_account(filename=r"D:\Dateien\Programmieren\Python\PS2 Jaeger Accountbot\data\ps2jaegeraccountbot-8fd42185680c.json")

    async def _getAccounts(self):
        "
        def _getWorksheet(url):

            try:
                worksheet = serviceAccount.open_by_url(string(url)).sheet1 # get the first worksheet of the spreadsheet returned by open_by_url
                return worksheet
            except Exception as e:
                print(e) #TODO make bot exception to be caught by errorhandler
                return None

        worksheet = None
        async with dbPool.acquire() as conn:
            async with conn.transaction():
                sheetsAddress = conn.fetchval("SELECT sheets_url FROM sheets_urls WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)
                if not sheetsAddress is None:
                    worksheet = self.bot.loop.run_in_executor(None, _getWorksheet, sheetsAddress)
                else:
                    #TODO make bot exception to be caught by errorhandler
                    raise Exception("SheetsAddress is none, NOT IMPLEMENTED")

        # Get everything in columns A & B
        columnA = self.bot.loop.run_in_executor(None, worksheet.col_values, 1)
        columnB = self.bot.loop.run_in_executor(None, worksheet.col_values, 2)

        # Remove Header from list (e.g. Account Name)
        if columnA[0] != "Account Name" or columnB[0] != "Password":
            #TODO make bot exception to be caught by errorhandler
            raise Exception("Something is terribly wrong, contact administrator and check spreadsheet for integrity")
        del columnA[0]
        del columnB[0]

        # Create a list of availablable Account objects, and filter example accounts
        accounts = []
        for accountName, password in columnA, columnB:
            if accountName == "" or password == "":
                break
            accounts.append(Account(accountName,password))

        datetime.datetime.now() # TODO get discord server's timezone and validate account availability



    def _isAvailable()

    def _getAccount()






    @commands.group()
    @commands.check(isOutfitRep())
    def accounts(self, ctx):
        sheetsAddress = None
        async with dbPool.acquire() as conn:
            async with conn.transaction():
                sheetsAddress = conn.fetchval("SELECT sheets_url FROM sheets_urls WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)
        if not sheetsAddress is None:
            try:
                worksheet = serviceAccount.open_by_url("https://docs.google.com/spreadsheets/d/1Kad_6iSXRfFeiJFX3Qub-e6QApgNeCCc5rhTFCAjPB4/edit#gid=0").sheet1 # get the first worksheet of the spreadsheet returned by open_by_url
            except Exception as e:
                print(e)


    @accounts.command()
    @commands.check(isOutfitRep())
    def distribute(self, ctx):
        pass

    @commands.command


serviceAccount = gspread.service_account(filename=r"D:\Dateien\Programmieren\Python\PS2 Jaeger Accountbot\data\ps2jaegeraccountbot-8fd42185680c.json")
worksheet = serviceAccount.open_by_url("https://docs.google.com/spreadsheets/d/1Kad_6iSXRfFeiJFX3Qub-e6QApgNeCCc5rhTFCAjPB4/edit#gid=0").sheet1 # get the first worksheet of the spreadsheet returned by open_by_url

# Get everything in columns A & B
columnA = worksheet.col_values(1)
columnB = worksheet.col_values(2)

# Remove Header (e.g. Account Name)
if columnA[0] != "Account Name" or columnB[0] != "Password":
    raise Exception("Something is terribly wrong, contact administrator and check spreadsheet for integrity")
del columnA[0]
del columnB[0]

# Create a list of availablable Account objects, and filter example accounts
accounts = []
for accountName, password in columnA, columnB:
    if accountName == "" or password == "":
        break
    accounts.append(Account(accountName,password))




# accountNames =
# accountPasswords =

# print(vals)
"""
