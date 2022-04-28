import requests
import json

# { discordId: "254247454940069889", email: "test@email.com" }
def link_user_account_to_webapp(user_details: dict, url_endpoint) -> bool:

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
