import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import Context
from db.api import connect, get_guild, remove_guild

from helpers import checks
from helpers.embed import custom_embed


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
        checkInfosChannel = (
            get(ctx.guild.channels, id=guildData["checkInfosChannelId"])
            if "checkInfosChannelId" in guildData.keys()
            else None
        )
        await checkInfosChannel.delete() if checkInfosChannel else None

        uncheckedRole = (
            get(ctx.guild.roles, id=guildData["uncheckedRoleId"]) if "uncheckedRoleId" in guildData.keys() else None
        )
        checkedRole = (
            get(ctx.guild.roles, id=guildData["checkedRoleId"]) if "checkedRoleId" in guildData.keys() else None
        )

        # Delete checked & unchecked roles
        await uncheckedRole.delete() if uncheckedRole else None
        await checkedRole.delete() if checkedRole else None

        for role in ctx.guild.roles:
            # Reset all perms for default role
            if role.name == "@everyone":
                perms = discord.Permissions()
                perms.update(
                    read_messages=True,
                    read_message_history=True,
                    connect=True,
                    speak=True,
                    send_messages=True,
                    change_nickname=True,
                    view_channel=True,
                )
                await role.edit(reason=None, permissions=perms)

        await custom_embed(
            self.client,
            "I had a nice time there... but every good thing comes to an end. Bye!",
            ctx.channel.id,
            True,
        )

        remove_guild(col, ctx.guild.id)

        await ctx.guild.leave()


def setup(client):
    client.add_cog(Leave(client))
