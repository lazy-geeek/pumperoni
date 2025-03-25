import requests
from .config import RUGCHECK_API


# RugCheck verification
def check_token_safety(token):
    url = RUGCHECK_API.format(token=token)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("status") == "Good"
    return False
