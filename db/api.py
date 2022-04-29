import os, sys, json

import datetime
from pymongo import MongoClient


if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


def connect() -> dict:
    """
    Creates the connection to the database
    """
    try:
        conn = MongoClient(config["MONGO_DB_URL"])
        print("Connected successfully to MongoDB!")
        return {"conn": conn, "db": conn.checkmate}
    except:
        raise Exception("Could not connect to MongoDB...")


def guild_exists(col, guildId) -> bool:
    """
    Checks if a guild already exists in the database
    :param col: The database collection.
    :param guildId: The discord id of the guild.
    """
    query = {"guildId": guildId}
    res = col.find_one(query)

    if res:
        return True
    else:
        return False


def add_guild(col, guildData) -> int:
    """
    Adds a guild to the database
    :param col: The database collection.
    :param guildData: The informations about the guild (check the docs for more infos on this object).
    """
    if not guild_exists(col, guildData["guildId"]):
        ts = datetime.datetime.now().timestamp()
        recId = col.insert_one({**guildData, "created_at": ts})
        return recId
    else:
        raise Exception("A guild with the same id already exists!")


def remove_guild(col, guildId) -> None:
    """
    Removes a guild from the database
    :param col: The database collection.
    :param guildId: The discord id of the guild.
    """
    query = {"guildId": guildId}

    if guild_exists(col, guildId):
        col.delete_one(query)
    else:
        raise Exception("No guild found with this id...")


def update_guild(col, guildData) -> None:
    """
    Update guild infos in the database
    :param col: The database collection.
    :param guildData: The informations about the guild (check the docs for more infos on this object).
    """
    guildId = guildData["guildId"]
    query = {"guildId": guildId}

    if guild_exists(col, guildId):
        ts = datetime.datetime.now().timestamp()
        updatedGuildData = {**guildData, "updated_at": ts}
        col.replace_one(query, updatedGuildData)
    else:
        raise Exception("No guild found with this id...")


def get_guild(col, guildId) -> dict:
    """
    Retrieves a guild infos
    :param col: The database collection.
    :param guildId: The discord id of the guild.
    """
    query = {"guildId": guildId}
    res = col.find_one(query)

    if guild_exists(col, guildId):
        return res
    else:
        raise Exception("No guild found with this id...")


def get_guilds(col) -> dict:
    """
    Retrieves all the guilds infos
    :param col: The database collection.
    """
    res = col.find()

    return list(res)
