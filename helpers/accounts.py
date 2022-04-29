import requests
import json


def link_user_account_to_webapp(user_details: dict, url_endpoint) -> bool:
    """Check that 
    :param user_details: User's discord Id and email address
    :type: dict
    >>> user_details = { discordId: "254247454940069889", email: "test@email.com" }
    """

    # Sanity checks to make sure we have valid data
    if {"discordId", "email"}.issubset(user_details):

        data = json.dumps(user_details)
        resp = requests.post(
            url_endpoint,
        )
        return resp.ok

    else:
        # Invalid data was passed
        return False
