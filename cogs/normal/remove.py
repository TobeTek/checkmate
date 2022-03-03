import sys
import os
import json

import discord
from discord.ext import commands
from discord.ext.commands import Context
from db.api import connect, get_guild, update_guild

from helpers import checks
from helpers.embed import custom_embed


class Remove(commands.Cog, name="remove"):
    def __init__(self, client):
        if not os.path.isfile("config.json"):
            sys.exit("'config.json' not found! Please add it and try again.")
        else:
            with open("config.json") as file:
                config = json.load(file)

        self.client = client
        self.config = config

    @commands.command(
        name="remove",
        description="Removes an extension already added to the bot.",
    )
    @checks.is_owner()
    async def remove(self, ctx: Context, extension) -> None:
        AVAILABLE_EXTENSIONS = self.config["availableExtensions"]

        conn = connect()
        col = conn["db"].guilds

        guildData = get_guild(col, ctx.guild.id)
        extensions = guildData["extensions"]

        # Check if extension is enabled
        if extension in extensions:
            del extensions[extension]
            updatedGuildData = {**guildData, "extensions": extensions}

            update_guild(col, updatedGuildData)

            await custom_embed(
                self.client,
                f"Extension {extension} removed!",
                ctx.channel.id,
                True,
            )
        elif extension in AVAILABLE_EXTENSIONS:
            await custom_embed(
                self.client,
                f"Extension {extension} hasn't already been added!",
                ctx.channel.id,
                False,
            )
        else:
            await custom_embed(
                self.client,
                f"Extension **{extension}** doesn't exist!\n\n[Check all available extensions](https://google.com)",
                ctx.channel.id,
                False,
            )


def setup(client):
    client.add_cog(Remove(client))
