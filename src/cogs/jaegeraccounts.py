from discord.ext import commands
import discord
from cogs.utils.shared_recources import dbPool, gspread_service_account
import datetime
import re
from typing import Union
from cogs.utils.errors import InvalidSheetsValue, NoSheetsUrlException, BookingDurationLimitExceededError
import logging
import random

# Allow to book acounts for 12 hours max
BOOKING_DURATION_LIMIT = 12

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

        sheet1 = gspread_service_account.open_by_url(url).get_worksheet(1)
        sheet_data = sheet1.get("1:13")
        return sheet_data

    def _write_sheet_data(self, url: str, row: int, col: int, data: str):
        """Writes $data to cell specified by $row and $col Note: row and col in gspread start at index 1"""

        sheet = gspread_service_account.open_by_url(url).get_worksheet(1)
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
                                from_datetime_str, "%-m/%-d/%Y_%-I:%-M%p")
                            last_booked_from = last_booked_from.replace(tzinfo=datetime.timezone(
                                datetime.timedelta(hours=utcoffset)))  # Makes datetime object timezone aware

                            last_booked_to = None
                            if to_time_str:
                                to_datetime_str = date_str + "_" + to_time_str
                                last_booked_to = datetime.datetime.strptime(
                                    to_datetime_str, "%-m/%-d/%Y_%-I:%-M%p")
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

    async def insert_bookings(self, bot: commands.Bot, ctx: commands.Context, url: str, accounts_to_write: list([Account]), book_duration: int):
        # Will need to compare dates
        async with dbPool.acquire() as conn:
            utcoffset = await conn.fetchval("SELECT utcoffset FROM guilds WHERE guild_id = $1;", ctx.guild.id)
        
        raw_dates = self.raw_data[0]
        indexed_dates = enumerate(raw_dates)
        last_date = None
        last_index = len(raw_dates)
        for index, date in reversed(list(indexed_dates)):
            try:
                last_date = datetime.datetime.strptime(date, "%m/%d/%Y")
                last_index = index + 1
                break
            except ValueError:
                logging.info(f"`{date}` could not be parsed when when inserting booking")

        # Compare last date, so can write to same column
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=utcoffset)))
        today = now.date()

        last_account_booked_date = None
        for account in accounts_to_write:
            if account.last_booked_to is None:
                continue
            if last_account_booked_date is None:
                last_account_booked_date = account.last_booked_to.date()
                continue

            if account.last_booked_to.date() > last_account_booked_date:
                last_account_booked_date = account.last_booked_to.date()

        create_new_column = False
        # If last date in sheet is before today, create new row
        if last_date is None or today > last_date.date():
            last_date = today
            last_index = len(raw_dates) + 1
            create_new_column = True
        # if last day in sheet is today, but account was already booked for today, create new date column
        elif last_account_booked_date and last_account_booked_date == today:
            last_date = today
            last_index = len(raw_dates) + 1
            create_new_column = True
        
        # Add new date column if needed
        if create_new_column:
            await bot.loop.run_in_executor(None, self._write_sheet_data, url, 1, last_index, last_date.strftime("%m/%d/%Y"))

        # Prepare data to write
        hrs_now = now.strftime("%-I:%-M%p")
        hrs_after_x = (now + datetime.timedelta(hours=book_duration)).strftime("%-I:%-M%p")        

        for account in accounts_to_write:
            write_data = f"{account.last_user}({hrs_now}-{hrs_after_x})"
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
            await ctx.reply("You have not been assigned any accounts for today.\n"
                            "Please use the `!account book` command or ask your OVO rep for account assignment.")

    @commands.guild_only()
    @account.command()
    async def book(self, ctx, duration='1'):

        book_duration = 1
        if duration.isnumeric() and int(duration) > 0:
            book_duration = int(duration)
            if book_duration > BOOKING_DURATION_LIMIT:
                raise BookingDurationLimitExceededError(f"Can not book a account for longer than 12 hours. ({duration} > 12 By the way :stuck_out_tongue_winking_eye:)")

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
                    await sheet_data.insert_bookings(self.bot, ctx, url, [account], book_duration)
                    await ctx.author.send(embed=account.embed)
                    return

        # If the user does not have any prior accounts, assign the first free one
        for account in sheet_data.accounts:
            if account.is_booked:
                continue
            else:
                account.last_user = name
                await sheet_data.insert_bookings(self.bot, ctx, url, [account], book_duration)
                await ctx.author.send(embed=account.embed)
                return

        # If the function made it this far, there are no free accounts available
        await ctx.author.send("```There are currently no free accounts.\nIf you need one urgently, talk to your OVO rep.```")

    @commands.guild_only()
    @commands.command()
    async def distribute_accounts(self, ctx: commands.Context, force="False"):
        """
        Distributes accounts to all mentioned users.

        Arguments:
        force       Distributes accounts regardless of prior allocation
        """
        async with dbPool.acquire() as conn:
            url = await conn.fetchval("SELECT url FROM sheet_urls WHERE fk = (SELECT id FROM guilds WHERE guild_id = $1);", ctx.guild.id)
        if url is None:
            raise NoSheetsUrlException(
                "There is no google sheets url associated with this guild.")

        sheet_data = await SheetData.from_url(self.bot, ctx, url)
        available_accounts = []

        # Find accounts that are not booked or assign all if force flag is set
        for account in sheet_data.accounts:
            if force == "force" or not account.is_booked:
                available_accounts.append(account)

        # TODO Need to figure out how to handle situations when one of mentioned users already has an account
        if len(available_accounts) >= len(ctx.message.mentions):
            accounts_to_assign = []
            for member in ctx.message.mentions:
                # Making sure account usage is evenly spread
                random.shuffle(available_accounts)
                account = available_accounts.pop()
                name = member.nick if member.nick is not None else member.name
                account.last_user = name
                accounts_to_assign.append(account)
                await member.send(embed=account.embed)
                await ctx.author.send(f"Member {name} has been assigned account {account.name}.")
            await sheet_data.insert_bookings(self.bot, ctx, url, accounts_to_assign, 1)
        else:
            raise NotImplementedError("MAKE OWN EXCEPTION HERE")

def setup(bot):
    bot.add_cog(AccountDistrubution(bot))