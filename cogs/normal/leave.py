from discord.ext import commands
from discord.utils import get
from discord.ext.commands import Context
from db.api import connect, get_guild, remove_guild

from helpers import checks


class Leave(commands.Cog, name="leave"):
    def __init__(self, client):
        self.client = client

    @commands.command(
        name="leave",
        description="Proper way to kick the bot.",
    )
    @checks.is_owner()
    async def leave(self, ctx: Context) -> None:
        conn = connect()
        col = conn["db"].guilds

        guildData = get_guild(col, ctx.guild.id)

        # Delete check-infos channel
        checkInfosChannel = get(ctx.guild.channels, id=guildData["checkInfosChannelId"])
        await checkInfosChannel.delete() if checkInfosChannel else None

        uncheckedRole = get(ctx.guild.roles, id=guildData["uncheckedRoleId"])
        checkedRole = get(ctx.guild.roles, id=guildData["checkedRoleId"])

        # Delete checked & unchecked roles
        await uncheckedRole.delete() if uncheckedRole else None
        await checkedRole.delete() if checkedRole else None

        remove_guild(col, ctx.guild.id)

        await ctx.guild.leave()


def setup(client):
    client.add_cog(Leave(client))
