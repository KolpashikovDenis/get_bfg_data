import json
import requests
import configparser
import sys, os
import datetime as dt
from datetime import timedelta
from urllib.parse import quote

configfilename = os.path.abspath(os.path.dirname(sys.argv[0])) + '\properties.ini'
config = configparser.ConfigParser()

config.read(configfilename)
hostname = config['DEFAULT']['hostname']
login = config['DEFAULT']['login']
password = config['DEFAULT']['password']
str_date = config['DEFAULT']['date']

datefrom = dt.datetime.strptime(str_date, '%Y-%m-%d').date()
date_to = dt.datetime.strptime(str_date, '%Y-%m-%d') + timedelta(days=1)-timedelta(seconds=1)

filter = "filter={{start_date ge %s}} and {{stop_date lt %s}}" % (datefrom.strftime('%Y-%m-%dT%H:%M:%S'), date_to.strftime('%Y-%m-%dT%H:%M:%S'))

path = os.path.abspath(os.path.dirname(sys.argv[0])) + '\\' + config['DEFAULT']['folder']
if not os.path.exists(path):
    os.mkdir(path)

auth_data = "{\"action\":\"login\",\"data\":{\"login\":\""+login+"\",\"password\":\""+password+"\"}}"

req = requests.Session()
responce = req.post(hostname+'/action/login', data=auth_data)
c = req.cookies
h = req.headers

responce = req.get(hostname+'/rest/collection/entity_batch?with=entity_route_sheet', cookies=c, headers=h)
j = json.loads(responce.text)
print(j)
responce = req.get(hostname+'/rest/collection/entity_route_sheet?with=entity_batch', cookies=c, headers=h)
j = json.loads(responce.text)
print(j)
# if j['meta']['count'] != 0:
#     for item in j['entity']:
#         line = "%s;%s;%s;%s;%s" % (item['id'], item['identity'], item['group'], item['name'], item['code'])
#         print(line)