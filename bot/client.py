import discord
import json

with open("config.json", "r") as f:
    secrets = json.load(f)

assert "botToken" in secrets
assert "botStatus" in secrets

client = discord.Client()


@client.event
async def on_ready():
    print("------")
    print("Client logged in as :")
    print(f"Username : {client.user.name}")
    print(f"Id : {client.user.id}")
    print("------")

    await client.change_presence(activity=discord.Game(name=secrets["botStatus"]))


@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        await message.channel.send("I work!")


client.run(secrets["botToken"])
