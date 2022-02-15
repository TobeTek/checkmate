from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks


class Disable(commands.Cog, name="disable"):
    def __init__(self, client):
        self.client = client

    @commands.command(
        name="disable",
        description="Disables the mail authentification on the server.",
    )
    @checks.is_owner()
    async def disable(self, ctx: Context) -> None:
        await ctx.send("Disabled!")


def setup(client):
    client.add_cog(Disable(client))
