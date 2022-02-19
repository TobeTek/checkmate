import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import Context
from db.api import connect, get_guild, update_guild

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
        conn = connect()
        col = conn["db"].guilds

        guildData = get_guild(col, ctx.guild.id)

        # Check if the bot is already disabled
        if guildData["enabled"]:
            # List all roles ids of the guild
            rolesIds = []
            [rolesIds.append(role.id) for role in ctx.guild.roles]

            uncheckedRole = get(ctx.guild.roles, id=guildData["uncheckedRoleId"])

            perms = discord.Permissions()
            perms.update(
                read_messages=True,
                read_message_history=True,
                connect=True,
                speak=True,
                send_messages=True,
                change_nickname=False,
                view_channel=True,
            )

            # Give all perms to unchecked role
            await uncheckedRole.edit(reason=None, permissions=perms) if uncheckedRole and guildData[
                "uncheckedRoleId"
            ] in rolesIds else None

            # Delete check-infos channel
            checkInfosChannel = get(ctx.guild.channels, id=guildData["checkInfosChannelId"])
            await checkInfosChannel.delete() if checkInfosChannel else None

            del guildData["checkInfosChannelId"]

            updatedGuildData = {**guildData, "enabled": False}
            update_guild(col, updatedGuildData)

            await ctx.send("Disabled!")
        else:
            await ctx.send("Already disabled!")


def setup(client):
    client.add_cog(Disable(client))
