from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks


class Add(commands.Cog, name="add"):
    def __init__(self, client):
        self.client = client

    @commands.command(
        name="add",
        description="Adds an extension to the bot.",
    )
    @checks.is_owner()
    async def add(self, ctx: Context, extension) -> None:
        await ctx.send(f"Added {extension} extension!")


def setup(client):
    client.add_cog(Add(client))
