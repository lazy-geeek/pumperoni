import requests
from config import GMGN_API, PUMPFUN_API


# Market trend tracking
def fetch_trends():
    try:
        gmgn_response = requests.get(GMGN_API.format(token="trends"))
        pumpfun_response = requests.get(PUMPFUN_API)
        gmgn_trends = gmgn_response.json() if gmgn_response.status_code == 200 else []
        pumpfun_trends = (
            pumpfun_response.json() if pumpfun_response.status_code == 200 else []
        )
        return gmgn_trends + pumpfun_trends
    except requests.RequestException as e:
        print(f"Error fetching trends: {e}")
        return []
