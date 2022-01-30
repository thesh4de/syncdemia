import sqlite3
import datetime
import calendar


def getdo():
    con = sqlite3.connect('database/planner.db')
    cur = con.cursor()
    date = datetime.datetime.now()
    cur.execute("SELECT DO FROM {} WHERE Dt={}".format(
        date.strftime("%B"), date.strftime("%d")))
    do = cur.fetchone()[0]
    con.close()
    return do


def getslots(batch, do=getdo()):
    con = sqlite3.connect('database/com_tt.db')
    cur = con.cursor()
    if batch == 1:
        table = "stt1"
    elif batch == 2:
        table = "stt2"
    if do != '-':
        cur.execute("SELECT * FROM {0} WHERE DO={1}".format(table, do))
        slots = cur.fetchone()
        return {"isholiday": False, "slots": list(slots)[1:]}
    else:
        return {"isholiday": True}


def gethead():
    con = sqlite3.connect('database/com_tt.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM stt2")
    head = list(map(lambda x: x[0], cur.description))[1:]
    return head


def getdatesofdo(do, months):
    con = sqlite3.connect('database/planner.db')
    cur = con.cursor()
    date = datetime.datetime.now()
    month_no = int(date.strftime("%m"))
    cur.execute("SELECT Dt FROM {} WHERE DO={} AND Dt>={}".format(
        date.strftime("%B"), do, date.strftime("%d")))
    dts = ["{:02}".format(month_no) + '-' + "{:02}".format(date[0])
           for date in cur.fetchall()]
    for m in range(month_no + 1, month_no + months):
        cur.execute("SELECT Dt FROM {} WHERE DO={}".format(
            calendar.month_name[m], do))
        dts += ["{:02}".format(m) + '-' + "{:02}".format(date[0])
                for date in cur.fetchall()]
    return dts
