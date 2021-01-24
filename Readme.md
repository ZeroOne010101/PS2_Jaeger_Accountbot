# PS2 Jaeger Accountbot  ![build](https://github.com/ZeroOne010101/PS2_Jaeger_Accountbot/workflows/build/badge.svg?branch=master)
## About
The bot is written in discord.py and is currently being developed in cooperation with the RITE Outfit.
Its primary purpose is the distribution of temporary accounts for the Jaeger Server of the MMOFPS Planetside 2.

## Running the Bot
While you are welcome to run your own instance of the bot, we recommend inviting the instance currently maintained by us.  
Invite link and Instructions Coming Soon<sup>TM</sup>

## Setup
- Set the UTC-Offset of your timezone using the `!utc_offset set <value>` command.  
  This is necessary to make sure the bot enters the correct date and time in your google sheets.
- Set the google sheets url using the `!jaeger_url set <url>` command.  
  The bot's service account needs to have read and write access, so you may need to add it to the sheet.  
  The service account's address is ps2jaegeraccountbotsa@ps2jaegeraccountbot.iam.gserviceaccount.com.
- Please keep in mind, that the Settings commands are restricted to users with mod or admin privileges.

## Features

<sup>1</sup> This command is only usable by users with mod or admin privileges.

| Command | Description |
| --- | --- |
| **Miscellaneous** | |
| !help (command)| Lists commands and displays help for the command specified. |
| !ping | Displays the Bot's latency. |
| **Settings** | |
| !utc_offset (set)<sup>1</sup> | Displays/Sets the utc offset used for the google sheet. |
| !jaeger_url (set\|delete)<sup>1</sup> | Displays/Sets/Deletes the google sheets url the bot will try to provision accounts from. |
| !outfit_name (set\|delete)<sup>1</sup> | Displays/Sets/Deletes the outfit name the bot will try to use. |
| **Account Distribution** | |
| !account | Displays the the name of the users currently provisioned account. |
| !account book \| return | Book/Return an account if there are any available. |
| !account (force)distribute \<mentions><sup>1</sup>| Distribute accounts to all mentioned members. If the distribution is forced, prior allocation is ignored. |
| **Parity Check** | |
| !paritycheck | Compares the Name and Role structure of your Discord to your Planetside 2 Outfit and points out the outliers. |

## Special Thanks

To Asorr for providing the resources neccesary to host the bot instance.

To TheJerry for helping me code this bot.
