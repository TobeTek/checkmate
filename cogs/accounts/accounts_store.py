""" Cogs for managing user accounts on Discord and WebApp
    
    UpdateUsername: Cog for Updating Discord Usernames on WebApp BE
"""

import os
import sys
import json
import uuid

import __services as services

import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext import tasks

# Load Config
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

# General Variables
MIN_TO_SECONDS = 60
UPDATE_USERNAME_INTERVAL = config.get("UPDATE_USERNAME_INTERVAL", 1 * MIN_TO_SECONDS)
UPDATE_USERNAME_ENDPOINT = config.get("UPDATE_USERNAME_ENDPOINT", "http://httpbin.org")


class UpdateUsername(commands.Cog, name="accounts_store"):
    def __init__(self, client):
        self.client = client
        self.config = config
        self.username_queue = {}

    def _add_to_queue(self, payload: dict):
        entry_key = str(uuid.uuid4())
        self.username_queue.update({entry_key: payload})

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_db_task.start()

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        print(
            f"Username: {before.name=} {after.name=}, DisplayName {before.display_name=} {after.display_name=}"
        )
        self._add_to_queue(
            {
                "before_username": before.name,
                "before_display_name": before.display_name,
                "after_username": after.name,
                "after_display_name": after.display_name,
            }
        )

    @tasks.loop(seconds=UPDATE_USERNAME_INTERVAL)
    async def update_db_task(self, *args):
        print("Running Background Task")

        if len(self.username_queue) > 0:
            updated_records = []

            for key, record in self.username_queue.items():

                status = await services.accounts.update_username(
                    self.client.session, record, url_endpoint=UPDATE_USERNAME_ENDPOINT
                )
                if status:
                    updated_records.append(key)

            # Clear successful queries from the queue
            [self.username_queue.pop(key) for key in updated_records]


def setup(client):
    client.add_cog(UpdateUsername(client))
