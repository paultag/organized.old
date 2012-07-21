from organized.db import db
from collections import defaultdict

from datetime import timedelta
import datetime as dt

def date_to_stamp(time):
    return time.strftime("%Y-%m-%d")


def dayterate(start_date, end_date):
    cur = dt.datetime.strptime(start_date, "%Y-%m-%d")
    end = dt.datetime.strptime(end_date, "%Y-%m-%d")
    while cur < end:
        yield cur.strftime("%Y-%m-%d")
        cur += timedelta(days=1)


def twixt_dates(start_date, end_date):
    cur_date = start_date

    while cur_date < end_date:
        old_date = cur_date
        cur_date += timedelta(weeks=1)
        yield (
            old_date.strftime("%Y-%m-%d"),
            cur_date.strftime("%Y-%m-%d")
        )


def generate_daily_bugs(project, **kwargs):
    spec = kwargs
    spec.update({ "_project": project })

    issues = db.issues.find(spec).sort('created_at',  1)

    if issues.count() == 0:
        return ([], {})

    start_date = issues[0]['created_at']
    ret = defaultdict(list)
    for issue in issues:
        ret[date_to_stamp(issue['created_at'])].append({
            "action": "open",
            "num": issue['number']
        })
        if not issue['closed_at'] is None:
            ret[date_to_stamp(issue['closed_at'])].append({
                "action": "close",
                "num": issue['number']
            })
    real_ret = {}

    for date in twixt_dates(start_date, dt.datetime.now()):
        s, e = date
        closed = 0
        opened = 0
        for day in dayterate(s, e):
            if day in ret:
                for action in ret[day]:
                    if action['action'] == 'open':
                        opened += 1
                    elif action['action'] == 'close':
                        closed += 1

        real_ret[s] = (closed, opened)
    keys = real_ret.keys()
    keys.sort()
    return (keys, real_ret)
