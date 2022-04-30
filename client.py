import json
import os
import platform
import random
import sys

import servus

import discord
from discord.ext import tasks, commands
from discord.utils import get
from discord.ext.commands import Bot
from discord.ext.commands import Context

from db.api import add_guild, connect, get_guild, remove_guild


if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


intents = discord.Intents.default()
intents.members = True
intents.reactions = True

prefix = config.get("prefix", "&")
client = Bot(command_prefix=commands.when_mentioned_or(prefix), intents=intents)


@client.event
async def on_ready() -> None:
    """
    The code in this even is executed when the client is ready
    """
    print(f"Logged in as {client.user.name}")
    print(f"Discord API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    status_task.start()


@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """
    Setup the game status task of the client
    """

    statuses = ["YOU SHALL NOT PASS!"]
    await client.change_presence(activity=discord.Game(random.choice(statuses)))


# Removes the default help command of discord.py to be able to create our custom help command.
client.remove_command("help")


def load_commands(command_type: str) -> None:
    for file in os.listdir(f"./cogs/{command_type}"):
        if file.endswith(".py") and not file.startswith("__"):
            extension = file[:-3]
            try:
                client.load_extension(f"cogs.{command_type}.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


if __name__ == "__main__":
    """
    This will automatically load slash commands and normal commands located in their respective folder.

    If you want to remove slash commands, which is not recommended due to the Message Intent being a privileged intent, you can remove the loading of slash commands below.
    """

    # load_commands("slash") uncomment if slash commands are added to the bot
    # load_commands("accounts")
    load_commands("normal")


@client.event
async def on_message(message: discord.Message) -> None:
    """
    The code in this event is executed every time someone sends a message, with or without the prefix
    :param message: The message that was sent.
    """

    if message.author == client.user or message.author.bot:
        return
    await client.process_commands(message)


@client.event
async def on_command_error(ctx: Context, error) -> None:
    """
    The code in this event is executed every time a normal valid command catches an error
    :param ctx: The normal command that failed executing.
    :param error: The error that has been faced.
    """

    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            title="Hey, please slow down!",
            description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=0xE02B2B,
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="You are missing the permission(s) `"
            + ", ".join(error.missing_permissions)
            + "` to execute this command!",
            color=0xE02B2B,
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error!",
            description=str(error).capitalize(),
            # We need to capitalize because the command arguments have no capital letter in the code.
            color=0xE02B2B,
        )
        await ctx.send(embed=embed)
    raise error


@client.event
async def on_guild_join(guild) -> None:
    """
    The code in this event is executed every time the bot joins a guild
    """

    conn = connect()
    col = conn["db"].guilds
    guildData = {"guildId": guild.id, "enabled": False, "extensions": {}}

    add_guild(col, guildData)


@client.event
async def on_guild_remove(guild) -> None:
    """
    The code in this event is executed every time the leaves a guild
    """

    conn = connect()
    col = conn["db"].guilds

    remove_guild(col, guild.id)


@client.event
async def on_member_join(member) -> None:
    """
    The code in this event is executed every time a member joins a guild
    """
    conn = connect()
    col = conn["db"].guilds

    guildData = get_guild(col, member.guild.id)

    if "enabled" in guildData.keys() and guildData["enabled"]:
        rolesIds = []
        [rolesIds.append(role.id) for role in member.guild.roles]

        # Give unchecked role to the user
        if (
            "uncheckedRoleId" in guildData.keys()
            and guildData["uncheckedRoleId"] in rolesIds
        ):
            uncheckedRole = get(member.guild.roles, id=guildData["uncheckedRoleId"])
            await member.add_roles(uncheckedRole)


@client.command()
async def ping(ctx: Context):
    await ctx.send("Hello Beautiful World! 🚌")


# Add the createRequestClient coroutine to `client` async loop
client.loop.create_task(servus.discord_utils.createRequestsClient(client))

# Run the bot with the token
client.run(config["token"])
