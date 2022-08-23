from discord.ext import commands

def is_mod():
    def predicate(ctx):
        perms = dict(ctx.author.guild_permissions)
        return perms['manage_guild']
    return commands.check(predicate)

def is_admin():
    def predicate(ctx):
        perms = dict(ctx.author.guild_permissions)
        return perms['administrator']
    return commands.check(predicate)
