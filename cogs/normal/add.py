import sys
import os
import json

import discord
from discord.ext import commands
from discord.ext.commands import Context
from db.api import connect, get_guild, update_guild

from helpers import checks
from helpers.embed import custom_embed
from helpers.api import is_endpoint_ok


class Add(commands.Cog, name="add"):
    def __init__(self, client):
        if not os.path.isfile("config.json"):
            sys.exit("'config.json' not found! Please add it and try again.")
        else:
            with open("config.json") as file:
                config = json.load(file)

        self.client = client
        self.config = config

    @commands.command(
        name="add",
        description="Adds an extension to the bot.",
    )
    @checks.is_owner()
    async def add(self, ctx: Context, extension) -> None:
        AVAILABLE_EXTENSIONS = self.config["availableExtensions"]

        conn = connect()
        col = conn["db"].guilds

        guildData = get_guild(col, ctx.guild.id)
        extensions = guildData["extensions"]

        # Check if extension isn't already enabled
        if extension not in extensions and extension in AVAILABLE_EXTENSIONS:
            if extension == "email-check":
                await custom_embed(
                    self.client,
                    "🖥️ What is the endpoint to check if the user email is in your db?\n\n[How to create the endpoint?](https://google.com)",
                    ctx.channel.id,
                    None,
                )

                endpoint = await self.client.wait_for(
                    "message", check=checks.is_author(ctx.author), timeout=60 * 10
                )

                # Check is the endpoint is up / exists
                if endpoint.author != self.client.user and is_endpoint_ok(
                    endpoint.content
                ):
                    extensions[extension] = endpoint.content
                else:
                    await custom_embed(
                        self.client,
                        "The endpoint is not valid!\n\n[How to create the endpoint?](https://google.com)",
                        ctx.channel.id,
                        False,
                    )
                    return

            updatedGuildData = {**guildData, "extensions": extensions}

            update_guild(col, updatedGuildData)

            await custom_embed(
                self.client,
                f"Extension **{extension}** added!",
                ctx.channel.id,
                True,
            )
        elif extension in AVAILABLE_EXTENSIONS:
            await custom_embed(
                self.client,
                f"Extension **{extension}** has already been added!",
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
    client.add_cog(Add(client))
