from pymongo import MongoClient


def connect() -> dict:
    """
    Create the connection to the database
    """
    try:
        conn = MongoClient()
        print("Connected successfully to MongoDB!")
        return {"conn": conn, "db": conn.checkmate}
    except:
        raise Exception("Could not connect to MongoDB...")


def guild_exists(col, guildId) -> bool:
    """
    Check if a guild already exists in the database
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
    Add a guild to the database
    :param col: The database collection.
    :param guildData: The informations about the guild (check the docs for more infos on this object).
    """
    if not guild_exists(col, guildData["guildId"]):
        recId = col.insert_one(guildData)
        return recId
    else:
        raise Exception("A guild with the same id already exists!")


def remove_guild(col, guildId) -> None:
    """
    Remove a guild from the database
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
        updatedGuildData = {"$set": guildData}
        col.update_one(query, updatedGuildData)
    else:
        raise Exception("No guild found with this id...")


def get_guild(col, guildId) -> dict:
    """
    Retrieve a guild infos
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
    Retrieve all the guilds infos
    :param col: The database collection.
    """
    res = col.find()

    return list(res)


# conn = connect()
# col = conn["db"].guilds
