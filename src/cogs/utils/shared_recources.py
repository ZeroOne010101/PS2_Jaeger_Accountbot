import json
import pathlib
import asyncpg
import gspread

# This files purpose is to define shared recources that submodules (cogs) need access to.
# This design pattern is made possible due to python only initializing the module on the first import.

# TODO Location of the python module, only needed on windows,TODO remove later
path = pathlib.Path('d:/Dateien/Programmieren/Python/PS2 Jaeger Accountbot')

# Load settings from json file
with open(path / 'data' / 'settings.json', mode='r') as settingsFile:
    botSettings = json.load(settingsFile)

# Setup database connection pool
dbSettings = botSettings['postgres']

dbPool = None
async def initialize_pool():
    """Initializes db connection pool, to be called once the bot is ready."""
    global dbPool
    dbPool = await asyncpg.create_pool(host=dbSettings['pgHost'],
                                       user=dbSettings['pgUser'],
                                       password=dbSettings['pgPassword'],
                                       database=dbSettings['pgDatabase'])

gspread_service_account = None
def initialize_gspread_service_account():
    """Service Account for google sheets"""
    global gspread_service_account
    gspread_service_account = gspread.service_account(filename=botSettings['google_service_account'])
