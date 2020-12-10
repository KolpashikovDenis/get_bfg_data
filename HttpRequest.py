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

responce = req.get(hostname+'/rest/collection/entity?order_by=id', cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\entity.csv', 'w') as fout:
    fout.write('id;identity;group;name;code\n')
    if j['meta']['count'] != 0:
        for item in j['entity']:
            line = "%s;%s;%s;%s;%s\n" % (item['id'], item['identity'], item['group'], item['name'], item['code'])
            fout.write(line)

responce = req.get(hostname+'/rest/collection/entity_route_sheet?order_by=id&'+filter, cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+ '\entity_route_sheet.csv', 'w') as fout:
    fout.write('id;desc;identity;entity_batch_id;stop_date;note;start_date;type\n')
    if j['meta']['count'] != 0:
        for item in j['entity_route_sheet']:
            line = "%s;%s;%s;%s;%s;%s;%s;%s\n" % (item['id'], item['desc'],item['identity'], item['entity_batch_id'], item['stop_date'], item['note'], item['start_date'], item['type'])
            fout.write(line)

responce = req.get(hostname+'/rest/collection/entity_route_sheet_operation?order_by=id&'+filter, cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\entity_route_sheet_operation.csv', 'w') as fout:
    fout.write('id;calculation_identity;operation_id;equipment_id;equipment_class_id;stop_date;progress;department_id;note;calculation_session_id;start_date;executor_id;entity_route_sheet_id;status\n')
    if j['meta']['count'] != 0:
        for item in j['entity_route_sheet_operation']:
            line = "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n" % \
                   (item['id'], item['calculation_identity'], item['operation_id'], item['equipment_id'], item['equipment_class_id'],
                    item['stop_date'], item['progress'], item['department_id'], item['note'], item['calculation_session_id'],
                    item['start_date'], item['executor_id'], item['entity_route_sheet_id'], item['status'])
            fout.write(line)

# print()
# responce = req.get(hostname+'/rest/collection/executor', cookies=c, headers=h)
# j = json.loads(responce.text)
# with open('executor.csv', 'w') as fout:
#     for item in j['executor']:
#         fout.write("{0}\n".format(item['identity']))
#         print("{0}".format(item['identity']))

responce = req.get(hostname+'/rest/collection/operation?order_by=id', cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\operation.csv', 'w') as fout:
    fout.write("id;nop;identity;name\n")
    if j['meta']['count'] != 0:
        for item in j['operation']:
            line = line = "%s;%s;%s;%s\n" % (item['id'], item['nop'], item['identity'], item['name'])
            fout.write(line)

responce = req.get(hostname+'/rest/collection/department?order_by=id', cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\department.csv', 'w') as fout:
    fout.write('id;identity;name\n')
    if j['meta']['count'] != 0:
        for item in j['department']:
            line = line = "%s;%s;%s\n" % (item['id'], item['identity'], item['name'])
            fout.write(line)

responce = req.get(hostname+'/rest/collection/equipment_class?order_by=id', cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\equipment_class.csv', 'w') as fout:
    fout.write('id;identity;name\n')
    if j['meta']['count'] != 0:
        for item in j['equipment_class']:
            line = line = "%s;%s;%s\n" % (item['id'], item['identity'], item['name'])
            fout.write(line)

responce = req.get(hostname+'/rest/collection/entity_batch', cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\eentity_batch.csv', 'w') as fout:
    fout.write('id;calculation_identity;order_id;identity;parent_id;picked;from_state;entity_id;note;calculation_session_id;quantity;status\n')
    if j['meta']['count'] != 0:
        for item in j['entity_batch']:
            line = line = "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;\n" % \
                          (item['id'], item['calculation_identity'], item['order_id'], item['identity'],item['parent_id'], item['picked'],
                           item['from_state'], item['entity_id'], item['note'],item['calculation_session_id'], item['quantity'], item['status'])
            fout.write(line)

responce = req.get(hostname+'/rest/collection/user', cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\\user.csv', 'w') as fout:
    fout.write('id;disabled;identity;create_stamp;patronymic_name;last_name;name\n')
    if j['meta']['count'] != 0:
        for item in j['user']:
            line = line = "%s;%s;%s;%s;%s;%s;%s\n" % (item['id'], item['disabled'], item['identity'], item['create_stamp'],
                                                      item['patronymic_name'], item['last_name'], item['name'])
            fout.write(line)

responce = req.get(hostname+'/action/logout', cookies=c, headers=h)
print('Done.')