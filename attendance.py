import requests
from bs4 import BeautifulSoup as bs


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Origin": "https://academia.srmist.edu.in",
}

url = "https://academia.srmist.edu.in/srm_university/academia-academic-services/page/My_Time_Table_2020_21_22"
info_and_tt = None


def gettt(token):

    payload = {
        "sharedBy": "srm_university", "appLinkName": "academia-academic-services", "viewLinkName": "My_Time_Table_2020_21_22",
        "zccpn": token['zccpn'],
        "urlParams": "{}", "isPageLoad": "true"
    }

    res = requests.post(url, data=payload, headers=headers, cookies=token).text

    s1 = """$("#zc-viewcontainer_My_Time_Table_2020_21_22").prepend(pageSanitizer.sanitize('"""
    s2 = """});</script>"""

    try:
        c, d = res.find(s1), res.find(s2)
    except:
        return "error"

    time_dic = {}
    personal_data = []
    details = {}

    er = (r"\x3C\x2Ftr\x3E\x0A\x09\x09\x09\x3Ctd\x3E",
          r"\x3C\x2Ftr\x3E\x3Ctd\x3E")
    html = res[c + len(s1):d - 5].replace(er[0], er[1]
                                          ).encode().decode("unicode-escape")
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
            time_dic[tuple(filter(None, z[8].split("-")))
                    ] = [z[2], z[6], z[11]]
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
