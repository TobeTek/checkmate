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
from helpers import accounts
from helpers.embed import custom_embed
from helpers.api import email_in_endpoint
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
        print("Handling Button Click")
        try:
            # Send empty message to avoid "interaction failed"" error
            await interaction.response.send_message()
        except Exception as e:
            print(e)
            pass

        conn = connect()
        col = conn["db"].guilds

        guildData = get_guild(col, interaction.user.guild.id)

        member = interaction.user

        if member != self.client.user:
            embed = discord.Embed(
                title=f"Checkmate | verification process 1/2",
                description=f"> ✉️ Hi there,\n\nTo access the server kindly send me the email associated with your account on The Dynamics App to receive a verification code\n\nDon't have an account? create one at https://app.thedynamics.tech/signup\n\nPS: it's the same as the one for Codetivate registration\n\nThanks!
            .",
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
            except Exception as e:
                print(e)
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
                            title=f"Checkmate | verification failed",
                            description=f"> ❌ Oops, you don't have an account on **{self.client.get_guild(interaction.user.guild.id).name}**'s app... make sure that you entered the email you registered with on the website!\n\nClick on the verification button in {checkInfosChannel.mention} to start the process again.",
                            color=0xF6E6CC,
                        )
                        await member.send(embed=embed)
                        return

                embed = discord.Embed(
                    title=f"Checkmate | verification process 2/2",
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
                print(f"\n\n{realCode=}")
                userCode = await self.client.wait_for(
                    "message", check=checks.is_author(member), timeout=60 * 10
                )

                # Check if the generated code and the code entered by theuser are the same
                if realCode == userCode.content:

                    # Update Website database with new user details
                    payload = {"discordId": member.id, "email": email.content}

                    embed = discord.Embed(
                        title=f"Checkmate | securing connection",
                        description=f"Connecting your account to the app...",
                        color=0xF6E6CC,
                    )
                    await member.send(embed=embed)

                    print(f"\n{payload=}")
                    status = accounts.link_user_account_to_webapp(
                        payload, self.config["ADD_VERIFIED_USER_EMAIL_ENDPOINT"]
                    )

                    # Revert process
                    if not status:
                        embed = discord.Embed(
                            title=f"Checkmate | verification failed",
                            description=f"> ❌ Oops, Couldn't complete your verification! Make sure you have an account on the app before trying again. If you have an account, try again in few minutes.\n\nCick the verification button in {checkInfosChannel.mention} to start the process again.",
                            color=0xF6E6CC,
                        )
                        await member.send(embed=embed)
                        return

                    embed = discord.Embed(
                        title=f"Checkmate | verification successful",
                        description=f"🎉 Congrats, you are now verified!",
                        color=0xF6E6CC,
                    )
                    await member.send(embed=embed)

                    rolesIds = []
                    [rolesIds.append(role.id) for role in member.guild.roles]

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
                        title=f"Checkmate | invalid code",
                        description=f"> ❌ Oops, invalid code entered!\n\nClick on the verification button in {checkInfosChannel.mention} to start the process again.",
                        color=0xF6E6CC,
                    )
                    await member.send(embed=embed)
                return
            else:
                embed = discord.Embed(
                    title=f"checkmate | Check Process Error",
                    description=f"> ❌ Oops, the email you entered is invalid!\n\nClick on the verification button in {checkInfosChannel.mention} to start the process again.",
                    color=0xF6E6CC,
                )
                await member.send(embed=embed)
                return

    @commands.command(name="clear", help="this command will clear msgs in a cannel")
    async def clear(
        self, ctx: Context, channel_to_clear: discord.TextChannel, amount: int = 5
    ):
        await channel_to_clear.purge(limit=amount)

    @commands.command(
        name="add_vb", description="Add verify button to verify channel manually"
    )
    @checks.is_owner()
    async def add_vb(self, ctx: Context, verify_channel: discord.TextChannel):

        # Set description depending on the extentsions added
        description = f">Hi there ✌😎 \n\nTo access this discord server, please click on the start verification button and follow the instructions that I will send in a private message!\n\nMake sure that you are already registered on **{ctx.guild}**'s App."

        embed = discord.Embed(
            title=f"Checkmate | unlock this server",
            description=description,
            color=0xF6E6CC,
        )

        # Create the button
        button = Button(label="Start your verification", emoji="✅")

        button.callback = self.handleButtonClick

        view = View(timeout=60 * 15)
        view.add_item(button)

        # Send the message in chech-infos channel
        message = await verify_channel.send(embed=embed, view=view)

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
                "verify-email", overwrites=overwrites
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

            view = View(timeout=None)
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
