import json
from datetime import datetime, timezone

import requests
import sqlite3
import sys

def ping_summary():
    return 'One ping only @ {}'.format(datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M'))

def adf(inlineCardUrl):
    return {
        'version': 1,
        'type': 'doc',
        'content': [
            {
                'type': 'paragraph',
                'content': [
                    {
                        'type': 'inlineCard',
                        'attrs': {
                            'url': inlineCardUrl
                        }
                    }
                ]
            }
        ]
    }

con = sqlite3.connect(sys.argv[1])
cur = con.cursor()
username, token = cur.execute('select username, token from auth').fetchone()
url, project, issuetype, assignee, transition, space_id, parent = cur.execute('select * from config').fetchone()
create_issue_res = requests.post('https://{}/rest/api/3/issue'.format(url), auth=(username, token), json={
    'fields': {
        'summary': ping_summary(),
        'project': {
            'key': project
        },
        'issuetype': {
            'id': issuetype
        },
        'assignee': {
            'id': assignee
        }
    }}).json()
create_page_res = requests.post('https://{}/wiki/api/v2/pages'.format(url), auth=(username, token), json={
    'spaceId': space_id,
    'status': 'current',
    'title': ping_summary(),
    'parentId': parent,
    'body': {
        'representation': 'atlas_doc_format',
        'value': json.dumps(adf('https://{}/browse/{}'.format(url, create_issue_res['key'])))
    }}).json()
requests.put('https://{}/rest/api/3/issue/{}'.format(url, create_issue_res['id']),
                   auth=(username, token), json={
        'fields': {
            'description': adf('{}{}'.format(create_page_res['_links']['base'], create_page_res['_links']['webui']))
        }
    })
requests.post('https://{}/rest/api/3/issue/{}/transitions'.format(url, create_issue_res['id']),
              auth=(username, token), json={
        'transition': {
            'id':transition
        }})
webhook, = cur.execute('select * from webhook').fetchone()
requests.post(webhook, json={'content':'https://{}/browse/{} & {}{}'.format(url, create_issue_res['key'], create_page_res['_links']['base'], create_page_res['_links']['webui'])})
con.close()
