import requests as req


def is_endpoint_ok(url):
    try:
        res = req.get(url)
        return True
    except:
        return False


def email_in_endpoint(email, url):
    r = req.post(url, data={"email": email})
    res = r.json()
    return res.ok
