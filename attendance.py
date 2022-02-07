import requests
import sign
from bs4 import BeautifulSoup as bs


info_and_tt = None


def gettt(token):

    url = "https://academia.srmist.edu.in/srm_university/academia-academic-services/page/My_Time_Table_2020_21_22"
    headers = {
        "Host": "academia.srmist.edu.in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
    }

    res = requests.get(url, headers=headers, cookies=token).text

    s1 = """pageSanitizer.sanitize('"""
    s2 = """');function doaction(recType)"""

    try:
        c, d = res.find(s1), res.find(s2)
    except:
        return "error"

    time_dic = {}
    personal_data = []
    details = {}

    html = res[c + len(s1):d].replace("\\\\", "\\").encode().decode("unicode-escape")
    html = html.replace("</tr><td>", "</tr><tr><td>")
    parsed_html = bs(html, "lxml")

    personal_html = parsed_html.find("table").find_all("tr")
    for x in personal_html:
        z = [y.string.replace(
            ":", "") if y.string is not None else '' for y in x]
        personal_data += z
    details["personal"] = personal_data[:-1]
    time_t = parsed_html.find("table", border="1").find_all("tr")
    for y in time_t[1:-1]:
        z = [x.string for x in y]
        if z[8] is not None:
            for slot in tuple(filter(None, z[8].split("-"))):
                time_dic[slot] = [z[2], z[6], z[11]]
    details["tt"] = time_dic
    global info_and_tt
    info_and_tt = details
    return info_and_tt


def get_personal_and_tt(token, selection):
    if not info_and_tt:
        tables = gettt(token)
        if tables == "error":
            return tables
        return tables[selection]
    else:
        return info_and_tt[selection]


def get_batch_no(token):
    personal = get_personal_and_tt(token, "personal")
    batch_index = personal.index("Batch") + 1
    return int(personal[batch_index])


def clear_tt():
    global info_and_tt
    info_and_tt = None
