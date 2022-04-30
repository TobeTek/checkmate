import json
from bson import re
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def link_user_account_to_webapp(user_details: dict, url_endpoint, retries=5) -> bool:
    """Check that
    :param user_details: User's discord Id and email address
    :type: dict
    >>> user_details = { discordId: "254247454940069889", email: "test@email.com" }
    """
    # Sanity checks to make sure we have valid data
    if {"discordId", "email"}.issubset(user_details):

        data = json.dumps(user_details)

        session = requests.Session()
        retry = Retry(connect=8, backoff_factor=0.03)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        try:
            resp = session.post(url_endpoint, data=data, headers={'Content-Type': 'application/json'})
            print(f"{resp=} {resp.history} {resp.links}, {resp.json()}")
        except Exception as e:
            print(e)
            return False

        return True
    else:
        # Invalid data was passed
        print("Invalid data was passed")
        return False
