# This Project has been deprecated - i do not recommend further production use

# PS2 Jaeger Accountbot
<a href="https://discordapp.com/oauth2/authorize?client_id=751830501639323718&scope=bot&permissions=19456"><img src="https://img.shields.io/badge/invite-PS2JaegerAccountBot-677BC4"></a>
<a href="https://discord.com/invite/yvnRZjJ"><img src="https://img.shields.io/badge/ask-anything-677BC4"></a>
<a href="https://github.com/ZeroOne010101/PS2_Jaeger_Accountbot/blob/master/LICENSE"><img src="https://img.shields.io/github/license/ZeroOne010101/PS2_Jaeger_Accountbot"></a>
![master](https://github.com/ZeroOne010101/PS2_Jaeger_Accountbot/workflows/master/badge.svg?branch=master)

## About
The bot is written in discord.py and is currently being developed in cooperation with the RITE Outfit.
Its primary purpose is the distribution of temporary accounts for the Jaeger Server of the MMOFPS Planetside 2.

## Setup
- Set the UTC-Offset of your timezone using the `!utc-offset set <value>` command.  
  This is necessary to make sure the bot enters the correct date and time in your google sheets.
- Set the google sheets url using the `!jaeger-url set <url>` command.  
  The bot's service account needs to have read and write access, so you may need to add it to the sheet.  
  The service account's address is ps2jaegeraccountbotsa@ps2jaegeraccountbot.iam.gserviceaccount.com.
- Set the outfit name using `!outfit-name set <name>`.
- Please keep in mind, that some Settings commands are restricted to users with mod or admin privileges.

## Features
All commands marked by an <sup><b>A</b></sup> are only usable by users with mod or admin privileges.  
All commands can also be called without the hyphen for convenience. (e.g. `!utc-offset`->`!utcoffset`)
Most commands are available as Slash Commands. Due to Discord limitations the syntax may differ slightly.

() = optional, <> = argument
| Command | Description |
| --- | --- |
| **Miscellaneous** |
| `!help (command)` | Lists commands and displays help for the command specified |
| `!ping` | Displays the Bot's latency |
| `!info` | Shows some information about the bot |
| `!invite` | Shows the bots invite link |
| **Settings** |
| `!utc-offset (set) <hours>`<sup><b>A</b></sup> | Displays/Sets the utc offset used for the google sheet |
| `!jaeger-url (set\|delete) <url>`<sup><b>A</b></sup> | Displays/Sets/Deletes the google sheets url the bot will try to provision accounts from. |
| `!outfit-name (set\|delete) <name>`<sup><b>A</b></sup> | Displays/Sets/Deletes the outfit name the bot will try to use. |
| **Prefixes** |
| `!prefix` | Lists all active prefixes |
| `!prefix add <prefix>`<sup><b>A</b></sup> | Adds a new prefix |
| `!prefix delete <prefix>`<sup><b>A</b></sup> | Delete a prefix |
| **Account Distribution** |
| `!account` | Displays the the name of the users currently provisioned account |
| `!account book <hours>` | Book an account for the specified time if there are any available. |
| `!account distribute (force) <hours> <mentions>`<sup><b>A</b></sup> | Distribute accounts to all mentioned members. If the distribution is forced, prior allocation is ignored. |
| **Parity Check** |
| `!paritycheck` | Compares the Name and Role structure of your Discord to your Planetside 2 Outfit and points out the outliers |
| `!paritycheck show_excluded` | Lists users excluded from the parity check |
| `!paritycheck exclude <mention>`<sup><b>A</b></sup> | Exclude a user from the parity check |
| `!paritycheck unexclude <mention>`<sup><b>A</b></sup> | Removes a user from the exclusion list |

## Selfhosting
There are many ways to host a python program. Here i will describe my approach.
### Environment
OS: Debian 11 bullseye (stable at the time of writing)

Python: Version 3.10
### Setup
#### Ensure you are in the home directory
`cd ~`
#### Get master
Since we dont do any real releases, we treat the stable branch as the production branch.
Not that this may not be the best approach for other repositories.

`git clone "https://github.com/ZeroOne010101/PS2_Jaeger_Accountbot"`
#### cd to Repository
`cd PS2_Jaeger_Accountbot`
#### Install python
At the time of writing only python 3.9 was available for bullseye. So i followed this guide to install 3.10:

https://tecadmin.net/how-to-install-python-3-10-on-debian-11/
#### Install dependencies
All the dependencies of the bot are listed in this txt file.

`pip3.10 -r requirements.txt`
#### Install postgresql
`sudo apt install postgresql`
#### Create sql user and set password
Change PG_PASS in DB_user.sql to the password your bot should use for sql communications.

`sudo -u postgres psql -U postgres -f DB_user.sql`
#### Create Database
`sudo -u postgres psql -U postgres -f DB_schema.sql`
#### Change bot settings
Populate `data/settings.json` with your credentials
#### Copy, enable and start service
`sudo cp ps2jaegeraccountbot.service /etc/systemd/system/ps2jaegeraccountbot.service`

`sudo systemctl enable ps2jaegeraccountbot.service`

`sudo systemctl start ps2jaegeraccountbot.service`

## Special Thanks

To Asorr for providing the resources neccesary to host the bot instance.  
To [TheJerry/vilgovskiy](https://github.com/vilgovskiy) for helping me code this bot.
