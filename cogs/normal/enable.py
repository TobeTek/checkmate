import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import Context
from db.api import connect, get_guild, update_guild

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
        conn = connect()
        col = conn["db"].guilds

        guildData = get_guild(col, ctx.guild.id)

        # Check if the bot is already enabled
        if not guildData["enabled"]:
            # List all roles ids of the guild
            rolesIds = []
            [rolesIds.append(role.id) for role in ctx.guild.roles]
            
            # Role exists in the server & is already registered in db
            if "uncheckedRoleId" in guildData and guildData["uncheckedRoleId"] in rolesIds:
                uncheckedRole = get(ctx.guild.roles, id=guildData["uncheckedRoleId"])
            else:
                uncheckedRole = await ctx.guild.create_role(name="unchecked")

            # Role exists in the server & is already registered in db
            if "checkedRoleId" in guildData and guildData["checkedRoleId"] in rolesIds:
                checkedRole = get(ctx.guild.roles, id=guildData["checkedRoleId"])
            else:
                checkedRole = await ctx.guild.create_role(name="checked")

            for role in ctx.guild.roles:
                # Remove all perms for default role
                if role.name == "@everyone":
                    perms = discord.Permissions()
                    perms.update(
                        read_messages=True,
                        read_message_history=True,
                        connect=False,
                        speak=False,
                        send_messages=False,
                        change_nickname=False,
                        view_channel=False,
                    )
                    await role.edit(reason=None, permissions=perms)
                # Give all perms to checked role
                elif role.id == checkedRole.id:
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
                    await role.edit(reason=None, permissions=perms)
                # Only allow access to check-infos channel for unchecked role
                elif role.id == uncheckedRole.id:
                    perms = discord.Permissions()
                    perms.update(
                        read_messages=True,
                        read_message_history=True,
                        connect=False,
                        speak=False,
                        send_messages=False,
                        change_nickname=False,
                        view_channel=False,
                    )
                    await role.edit(reason=None, permissions=perms)

            # Set check-infos channel perms (only viewable by unchecked role)
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                uncheckedRole: discord.PermissionOverwrite(read_messages=True),
            }

            # Create check-infos channel
            checkInfosChannel = await ctx.guild.create_text_channel("check-infos", overwrites=overwrites)

            updatedGuildData = {
                **guildData,
                "enabled": True,
                "checkInfosChannelId": checkInfosChannel.id,
                "uncheckedRoleId": uncheckedRole.id,
                "checkedRoleId": checkedRole.id,
            }

            update_guild(col, updatedGuildData)
            await ctx.send("Enabled!")
        else:
            await ctx.send("Already enabled!")


def setup(client):
    client.add_cog(Enable(client))
