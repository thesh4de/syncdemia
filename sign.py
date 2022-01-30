import requests
import json

headers = {'Origin': 'https://academia.srmist.edu.in/',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'}
url = "https://academia.srmist.edu.in/accounts/signin.ac"


def getoken(username, password):
    payload = {'username': username, 'password': password, 'client_portal': 'true', 'portal': '10002227248', 'servicename': 'ZohoCreator',
               'serviceurl': 'https://academia.srmist.edu.in/', 'grant_type': 'password', 'service_language': 'en', 'is_ajax': 'true'}

    res = requests.post(url, data=payload, headers=headers)
    json_data = json.loads(res.text)

    if "error" in json_data:
        if "password" in json_data["error"]:
            er_msg = json_data["error"]["password"]
        elif "msg" in json_data["error"]:
            er_msg = json_data["error"]["msg"]
        json_o = {"status": "error", "msg": er_msg}
        return json_o

    else:
        session = requests.Session()
        session.get(json_data['data']['oauthorize_uri'], headers=headers)
        token = session.cookies.get_dict()
        json_o = {"status": "success", "token": token}
        return json_o
