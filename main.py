import json
from datetime import datetime, timezone

import requests
import sqlite3
import sys

def ping_summary():
    return 'One ping only @ {}'.format(datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M'))

con = sqlite3.connect(sys.argv[1])
cur = con.cursor()
(username, token) = cur.execute('select username, token from auth').fetchone()
(url, project, issuetype, assignee, transition, space_id, parent) = cur.execute('select * from config').fetchone()
create_issue_res = requests.post('https://{}/rest/api/3/issue'.format(url),
                     auth=(username, token), json={
        'fields': {'summary': ping_summary(),
                   'project': {'key': project}, 'issuetype': {'id': issuetype}, 'assignee': {'id': assignee}}}).json()
print(json.dumps(create_issue_res))
print(requests.post('https://{}/rest/api/3/issue/{}/transitions'.format(url, create_issue_res['id']),
                    auth=(username, token),
                    json={'transition':{'id':transition}}).status_code)
print(requests.post('https://{}/wiki/api/v2/pages'.format(url),
                    auth=(username, token), json={
        'spaceId': space_id,'status': 'current','title': ping_summary(), 'parentId': parent,
        'body': {'representation': 'storage', 'value': ''}
    }).json())
con.close()
