import json
from datetime import datetime, timezone

import requests
import sqlite3
import sys

con = sqlite3.connect(sys.argv[1])
cur = con.cursor()
(cloud_id, account_id) = cur.execute('select cloud_id, account_id from config').fetchone()
(client_id, client_secret) = cur.execute('select client_id, client_secret from app').fetchone()
jira_refresh_token = cur.execute("select refresh_token from token where product = 'jira'").fetchone()[0]
print('refreshing access token')
res = requests.post('https://auth.atlassian.com/oauth/token', json={
    'grant_type': 'refresh_token',
    'client_id': client_id,
    'client_secret': client_secret,
    'refresh_token': jira_refresh_token
})
if res.status_code == 200:
    print('200 -> updating tokens')
    cur.execute("update token set access_token = ?, refresh_token = ? where product = 'jira'", (res.json()['access_token'], res.json()['refresh_token']))
    con.commit()
    create_issue_res = requests.post('https://api.atlassian.com/ex/jira/{}/rest/api/3/issue'.format(cloud_id),
                         headers={'Authorization': 'Bearer {}'.format(res.json()['access_token'])}, json={
            'fields': {'summary': 'One ping only @ {}'.format(datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M')),
                       'project': {'key': 'PING'}, 'issuetype': {'id': '10024'}, 'assignee': {'id': account_id}}}).json()
    print(json.dumps(create_issue_res))
    print(requests.post('https://api.atlassian.com/ex/jira/{}/rest/api/3/issue/{}/transitions'.format(cloud_id, create_issue_res['id']),
                                   headers={'Authorization': 'Bearer {}'.format(res.json()['access_token'])},
                                   json={'transition':{'id':'31'}}).status_code)
else:
    print(res.status_code)
    print(json.dumps(res.json()))

con.close()
