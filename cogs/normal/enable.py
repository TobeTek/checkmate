from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks


class Enable(commands.Cog, name="enable"):
    def __init__(self, client):
        self.client = client

    @commands.command(
        name="enable",
        description="Enables the mail authentification on the server.",
    )
    @checks.is_owner()
    async def enable(self, ctx: Context) -> None:
        await ctx.send("Enabled!")


def setup(client):
    client.add_cog(Enable(client))
