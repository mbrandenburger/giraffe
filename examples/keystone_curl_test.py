__author__ = 'marcus'

import requests
import simplejson as json
import keystone.middleware.auth_token as auth


USERNAME = ''
PASSWORD = ''
TENANT = ''
ADMIN_TOKEN = ''


print '-----------------------------------\n' \
      'post user credentials and get token\n' \
      '-----------------------------------\n'

auth_url = 'http://cloud2.ibr.cs.tu-bs.de:35357/v2.0/tokens'
auth_header = {'Content-type': 'application/json'}
auth_data = {'auth':
                 {'passwordCredentials':
                      {'username': USERNAME,
                       'password': PASSWORD}
                 }
            }
print '[AUTH_URL: ', auth_url, ']\n'
print '<send> auth_data: ', auth_data, '\n'

r = requests.post(url=auth_url,
                  data=json.dumps(auth_data, indent=4),
                  headers=auth_header)

print '<receive> response: ', json.dumps(r.json, indent=4), '\n'
unscoped_token = str(json.loads(r.text)['access']['token']['id'])
# print '<receive> unscoped token: ', unscoped_token


print '-----------\n' \
      'get tenants\n' \
      '-----------\n'

auth_url = 'http://cloud2.ibr.cs.tu-bs.de:5000/v2.0/tenants'
auth_header = {'X-Auth-Token': unscoped_token}

print '[AUTH_URL: ', auth_url, ']\n'
print '<send> auth_header: ', auth_header, '\n'

r = requests.post(url=auth_url,
                  data={},
                  headers=auth_header)

print '<receive> response: ', json.dumps(r.json, indent=4), '\n'


print '-----------------------------------------------\n' \
      'post user credentials with tenant and get token\n' \
      '-----------------------------------------------\n'

auth_url = 'http://cloud2.ibr.cs.tu-bs.de:35357/v2.0/tokens'
auth_header = {'Content-type': 'application/json'}
auth_data = {'auth':
                 {'tenantName': TENANT,
                  'token': {'id': unscoped_token}
                 }
            }

print '[AUTH_URL: ', auth_url, ']\n'
print '<send> auth_data: ', auth_data, '\n'

r = requests.post(url=auth_url,
                  data=json.dumps(auth_data, indent=4),
                  headers=auth_header)

print '<receive> response: ', json.dumps(r.json, indent=4), '\n'

scoped_token = str(json.loads(r.text)['access']['token']['id'])
# print '<receive> scoped token: ', scoped_token


print '-----------\n' \
      'check token\n' \
      '-----------\n'

auth_url = 'http://cloud2.ibr.cs.tu-bs.de:35357/v2.0/tokens/' + scoped_token
auth_header = {'X-Auth-Token': ADMIN_TOKEN}

print '[AUTH_URL: ', auth_url, ']\n'
print '<send> auth_header: ', auth_header, '\n'

r = requests.get(url=auth_url,
                 headers=auth_header)

print '<receive> response: ', json.dumps(r.json, indent=4), '\n'
