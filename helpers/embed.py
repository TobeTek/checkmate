import discord


async def custom_embed(client, label, channelId, success) -> None:
    channel = client.get_channel(channelId)

    emoji = ""
    if success == True:
        emoji = "✅"
    elif success == False:
        emoji = "❌"
    elif success == None:
        emoji = ""

    embed = discord.Embed(
        description=f"> {emoji} {label}",
        color=0xF6E6CC,
    )
    await channel.send(embed=embed)
