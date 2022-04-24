import servus
import json


async def update_username(client_session, payload, url_endpoint="http://httpbin.org"):
    try:
        print(f"Updating Username {payload=}")
        data = json.loads(payload)
        resp = await servus.post(client_session, url=url_endpoint, data=data)
        return resp

    except:
        # Failed to complete tranasction
        return False
