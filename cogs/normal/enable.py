import json
import os
import sys

import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import Context
from discord.ui import Button, View
from pydantic import validate_email

# from sympy import O

from db.api import connect, get_guild, update_guild

from helpers import checks
from helpers.embed import custom_embed
from helpers.requests import email_in_endpoint
from mailing.api import send_code


class Enable(commands.Cog, name="enable"):
    def __init__(self, client):
        if not os.path.isfile("config.json"):
            sys.exit("'config.json' not found! Please add it and try again.")
        else:
            with open("config.json") as file:
                config = json.load(file)

        self.client = client
        self.config = config

    async def handleButtonClick(self, interaction):
        """
        The code in this event is executed every time a member reacts to a message
        """
        try:
            # Send empty message to avoid "interaction failed"" error
            await interaction.response.send_message()
        except:
            pass

        conn = connect()
        col = conn["db"].guilds

        guildData = get_guild(col, interaction.user.guild.id)

        member = interaction.user

        if member != self.client.user:
            embed = discord.Embed(
                title=f"checkmate | Check Process 1/2",
                description=f"> ✉️ This is the beginning of the check process! Please send me your email.",
                color=0xF6E6CC,
            )
            await member.send(embed=embed)

            # Ask for user's email
            email = await self.client.wait_for(
                "message", check=checks.is_author(member), timeout=60 * 10
            )

            # Check is the email is valid
            try:
                isValid = validate_email(email.content)
            except:
                isValid = False

            checkInfosChannel = (
                get(
                    self.client.get_guild(interaction.guild_id).channels,
                    id=guildData["checkInfosChannelId"],
                )
                if "checkInfosChannelId" in guildData.keys()
                else None
            )

            if isValid:
                # If email-check extension is added, check if the email is in the endpoint
                if "email-check" in guildData["extensions"]:
                    if email_in_endpoint(
                        email.content, guildData["extensions"]["email-check"]
                    ):
                        pass
                    else:
                        embed = discord.Embed(
                            title=f"checkmate | Check Process Error",
                            description=f"> ❌ Oops, you are not registered on **{self.client.get_guild(interaction.user.guild.id).name}**'s website... Make sure that you entered the email you registered with on their website!\n\nReact again with the message in {checkInfosChannel.mention} to start the process again.",
                            color=0xF6E6CC,
                        )
                        embed.set_footer(text="Made with 🤍 by Bonsaï#8521")
                        await member.send(embed=embed)
                        return

                embed = discord.Embed(
                    title=f"checkmate | Check Process 2/2",
                    description=f"> 🔒 A verification code has just been sent to your email. Please enter the code you received!",
                    color=0xF6E6CC,
                )
                await member.send(embed=embed)

                # Send a verification code to the user
                realCode = send_code(
                    self.config["gmailUser"],
                    self.config["gmailPassword"],
                    email.content,
                    self.client.get_guild(interaction.user.guild.id).name,
                    member.name,
                )
                userCode = await self.client.wait_for(
                    "message", check=checks.is_author(member), timeout=60 * 10
                )

                # Check if the generated code and the code entered by theuser are the same
                if realCode == userCode.content:
                    embed = discord.Embed(
                        title=f"checkmate | Check Process Completed",
                        description=f"🎉 Congrats, you are now checked!",
                        color=0xF6E6CC,
                    )
                    embed.set_footer(text="Made with 🤍 by Bonsaï#8521")
                    await member.send(embed=embed)

                    rolesIds = []
                    [rolesIds.append(role.id) for role in member.guild.roles]
                    #TODO: Send { email:$, user_id: $} to BE of WebAPP (Servus to the rescue)
                    # Give checked role to the user
                    if (
                        "checkedRoleId" in guildData.keys()
                        and guildData["checkedRoleId"] in rolesIds
                    ):
                        checkedRole = get(
                            member.guild.roles, id=guildData["checkedRoleId"]
                        )
                        await member.add_roles(checkedRole)

                    # Remove unchecked role from the user
                    if (
                        "uncheckedRoleId" in guildData.keys()
                        and guildData["uncheckedRoleId"] in rolesIds
                    ):
                        uncheckedRole = get(
                            member.guild.roles, id=guildData["uncheckedRoleId"]
                        )
                        await member.remove_roles(uncheckedRole)

                else:
                    embed = discord.Embed(
                        title=f"checkmate | Check Process Error",
                        description=f"> ❌ Oops, the code is not valid!\n\nReact again with the message in {checkInfosChannel.mention} to start the process again.",
                        color=0xF6E6CC,
                    )
                    await member.send(embed=embed)
                return
            else:
                embed = discord.Embed(
                    title=f"checkmate | Check Process Error",
                    description=f"> ❌ Oops, the email you entered is not valid!\n\nReact again with the message in {checkInfosChannel.mention} to start the process again.",
                    color=0xF6E6CC,
                )
                await member.send(embed=embed)
                return

    @commands.command(
        name="enable",
        description="Enables the email authentification on the server.",
    )
    @checks.is_owner()
    async def enable(self, ctx: Context) -> None:
        conn = connect()
        col = conn["db"].guilds

        guildData = get_guild(col, ctx.guild.id)

        # Check if the bot is already enabled
        if "enabled" in guildData.keys() and not guildData["enabled"]:
            # List all roles ids of the guild
            rolesIds = []
            [rolesIds.append(role.id) for role in ctx.guild.roles]

            # Role exists in the server & is already registered in db
            if (
                "uncheckedRoleId" in guildData
                and guildData["uncheckedRoleId"] in rolesIds
            ):
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
                ctx.guild.default_role: discord.PermissionOverwrite(
                    read_messages=False
                ),
                uncheckedRole: discord.PermissionOverwrite(read_messages=True),
            }

            # Create check-infos channel
            checkInfosChannel = await ctx.guild.create_text_channel(
                "check-infos", overwrites=overwrites
            )

            # Set description depending on the extentsions added
            description = (
                f"> In order to have access to the discord server, please react with this message and follow the instructions that I will send in private message!"
                if "email-check" not in guildData["extensions"]
                else f"> In order to have access to the discord server, please react with this message and follow the instructions that I will send in private message!\n\nMake sure that you are already registered on **{ctx.guild}**'s website."
            )

            embed = discord.Embed(
                title=f"checkmate | Check Infos",
                description=description,
                color=0xF6E6CC,
            )

            # Create the button
            button = Button(label="Start the check process", emoji="✅")

            button.callback = self.handleButtonClick

            view = View()
            view.add_item(button)

            # Send the message in chech-infos channel
            message = await checkInfosChannel.send(embed=embed, view=view)

            updatedGuildData = {
                **guildData,
                "enabled": True,
                "checkInfosChannelId": checkInfosChannel.id,
                "checkInfosMessageId": message.id,
                "uncheckedRoleId": uncheckedRole.id,
                "checkedRoleId": checkedRole.id,
            }

            update_guild(col, updatedGuildData)

            await custom_embed(
                self.client,
                "Bot enabled!",
                ctx.channel.id,
                True,
            )
        else:
            await custom_embed(
                self.client,
                "Bot is already enabled!",
                ctx.channel.id,
                False,
            )


def setup(client):
    client.add_cog(Enable(client))
