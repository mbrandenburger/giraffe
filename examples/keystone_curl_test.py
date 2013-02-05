__author__ = 'marcus'

import requests
import simplejson as json
import keystoneclient.middleware.auth_token as auth


USERNAME = ''
PASSWORD = ''
TENANT = ''
ADMIN_TOKEN = ''

"""
    post user credentials and get token
"""
auth_url = 'http://cloud2.ibr.cs.tu-bs.de:35357/v2.0/tokens'
auth_header = {'Content-type': 'application/json'}
auth_data = {'auth':
                 {'passwordCredentials':
                      {'username': USERNAME,
                       'password': PASSWORD}
                 }
            }
r = requests.post(url=auth_url, data=json.dumps(auth_data, indent=4),
                    headers=auth_header)
print json.dumps(r.json, indent=4)

parsed_data = json.loads(r.text)
unscoped_token = str(parsed_data['access']['token']['id'])

"""
    get tenents
"""
auth_url = 'http://cloud2.ibr.cs.tu-bs.de:5000/v2.0/tenants'
auth_header = {'X-Auth-Token': unscoped_token}
r = requests.post(url=auth_url, data={}, headers=auth_header)
print json.dumps(r.json, indent=4)

"""
    post user credentials with tenant and get token
"""
auth_url = 'http://cloud2.ibr.cs.tu-bs.de:35357/v2.0/tokens'
auth_header = {'Content-type': 'application/json'}
auth_data = {'auth':
                 {'tenantName': TENANT,
                  'token': {'id': unscoped_token}
                 }
            }
r = requests.post(url=auth_url, data=json.dumps(auth_data, indent=4),
                    headers=auth_header)
print json.dumps(r.json, indent=4)

parsed_data = json.loads(r.text)
token = str(parsed_data['access']['token']['id'])

"""
    check token
"""
auth_url = 'http://cloud2.ibr.cs.tu-bs.de:35357/v2.0/tokens/' + token
auth_header = {'X-Auth-Token': ADMIN_TOKEN}
r = requests.get(url=auth_url, headers=auth_header)
print r.text
print json.dumps(r.json, indent=4)
