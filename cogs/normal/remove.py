from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks


class Remove(commands.Cog, name="remove"):
    def __init__(self, client):
        self.client = client

    @commands.command(
        name="remove",
        description="Removes an extension already added to the bot.",
    )
    @checks.is_owner()
    async def remove(self, ctx: Context, extension) -> None:
        await ctx.send(f"Removed {extension} extension!")


def setup(client):
    client.add_cog(Remove(client))
