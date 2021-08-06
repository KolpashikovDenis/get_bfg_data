import json
import requests
import configparser
import sys, os
import datetime as dt
from datetime import timedelta

configfilename = os.path.abspath(os.path.dirname(sys.argv[0])) + '\properties.ini'
config = configparser.ConfigParser()

config.read(configfilename)
hostname = config['DEFAULT']['hostname']
login = config['DEFAULT']['login']
password = config['DEFAULT']['password']
str_start_date = config['DEFAULT']['startdate']
str_end_date = config['DEFAULT']['enddate']
# input_file = config['DEFAULT']['inputfile']
# is_entity = bool(config['DEFAULT']['entity'])
# is_entity_route_sheet_transaction = bool(config['DEFAULT']['entity_route_sheet_transaction'])
# is_entity_route_sheet = bool(config['DEFAULT']['entity_route_sheet'])
# is_entity_route_sheet_operation = bool(config['DEFAULT']['entity_route_sheet_operation'])
# is_operation = bool(config['DEFAULT']['operation'])
# is_department = bool(config['DEFAULT']['department'])
# is_equipment_class = bool(config['DEFAULT']['equipment_class'])
# is_entity_batch = bool(config['DEFAULT']['entity_batch'])
# is_user = bool(config['DEFAULT']['user'])

filter = str()
# if str_date:
#     datefrom = dt.datetime.strptime(str_date, '%Y-%m-%d').date()
#     date_to = dt.datetime.strptime(str_date, '%Y-%m-%d') + timedelta(days=1)-timedelta(seconds=1)
#     filter = "filter={{start_date ge %s}}" % (datefrom.strftime('%Y-%m-%dT%H:%M:%S'))

start_date = ""
end_date = ""

if str_start_date:
    datefrom = dt.datetime.strptime(str_start_date, '%Y-%m-%d').date()
    #date_to = dt.datetime.strptime(str_end_date, '%Y-%m-%d') + timedelta(days=1)-timedelta(seconds=1)
    #filter = "filter={{start_date ge %s}}" % (datefrom.strftime('%Y-%m-%dT%H:%M:%S'))
else:
    datefrom = dt.datetime.now()

start_date = "{start_date ge %s}" % (datefrom.strftime('%Y-%m-%dT%H:%M:%S'))

if str_end_date:
    date_to = dt.datetime.strptime(str_end_date, '%Y-%m-%d').date() + timedelta(days=1) - timedelta(seconds=1)
else:
    date_to = datefrom + timedelta(days=1) - timedelta(seconds=1)

end_date = "{stop_date le %s}" % (date_to.strftime('%Y-%m-%dT%H:%M:%S'))

filter = "filter={%s and %s}" % (start_date, end_date)


path = os.path.abspath(os.path.dirname(sys.argv[0])) + '\\' + config['DEFAULT']['folder']
if not os.path.exists(path):
    os.mkdir(path)

auth_data = "{\"action\":\"login\",\"data\":{\"login\":\""+login+"\",\"password\":\""+password+"\"}}"

req = requests.Session()
responce = req.post(hostname+'/action/login', data=auth_data)
c = req.cookies
h = req.headers

filter_by_entity = ''
filter_by_id = ''

filter_for_entity_batch = ''
filter_for_entity = ''
filter_for_equipment_class = ''
filter_for_operation = ''
filter_for_department = ''

filter_str = ''


# fout = open(input_file, 'r')
# st_list = fout.readlines()
# fout.close()
# st_list = st_list[1:]
# filter_entity_route_sheet = '["'
# for line in st_list:
#     st = line.strip().split(';')
#     filter_entity_route_sheet =  filter_entity_route_sheet + st[1] + '","'
# filter_entity_route_sheet = filter_entity_route_sheet[:len(filter_entity_route_sheet)-3] + '"]'

# if is_entity_route_sheet:
# filter_by_entity = 'filter={{identity in %s} and {%s} and {%s}}' % (filter_entity_route_sheet, start_date, end_date)
# filter_by_entity = 'filter={{identity in %s}}' % filter_entity_route_sheet
filter_by_entity = 'filter={{%s} and {%s}}' % (start_date, end_date)
str_request = hostname + '/rest/collection/entity_route_sheet?order_by=id&'+filter_by_entity
responce = req.get(str_request, cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+ '\entity_route_sheet.csv', 'w') as fout:
    fout.write('id;desc;identity;entity_batch_id;stop_date;note;start_date;type\n')
    if j['meta']['count'] != 0:
        filter_by_id = '['
        filter_for_entity_batch = '['
        for item in j['entity_route_sheet']:
            line = "%s;%s;%s;%s;%s;%s;%s;%s\n" % (item['id'], item['desc'],item['identity'], item['entity_batch_id'],
                                                  item['stop_date'], item['note'], item['start_date'], item['type'])
            fout.write(line)
            filter_by_id = filter_by_id + str(item['id']) + ','
            filter_for_entity_batch = filter_for_entity_batch + str(item['entity_batch_id']) + ','
        filter_by_id = filter_by_id[:len(filter_by_id)-1]+']'
        filter_for_entity_batch = filter_for_entity_batch[:len(filter_for_entity_batch)-1] + ']'

# if is_entity_route_sheet_operation:
filter_str = 'filter={{entity_route_sheet_id in %s}}' % (filter_by_id)
str_request = hostname+'/rest/collection/entity_route_sheet_operation?order_by=id&'+filter_str
responce = req.get(str_request, cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\entity_route_sheet_operation.csv', 'w') as fout:
    fout.write('id;calculation_identity;operation_id;equipment_id;equipment_class_id;stop_date;progress;department_id;note;calculation_session_id;start_date;executor_id;entity_route_sheet_id;status\n')
    if j['meta']['count'] != 0:
        filter_by_id = '['
        filter_for_operation = '['
        filter_for_department = '['
        filter_for_equipment_class = '['
        for item in j['entity_route_sheet_operation']:
            line = "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n" % \
                   (item['id'], item['calculation_identity'], item['operation_id'], item['equipment_id'],
                    item['equipment_class_id'], item['stop_date'], item['progress'], item['department_id'], item['note'],
                    item['calculation_session_id'], item['start_date'], item['executor_id'], item['entity_route_sheet_id'],
                    item['status'])
            fout.write(line)
            filter_by_id = filter_by_id + str(item['id']) + ','
            filter_for_operation = filter_for_operation + str(item['operation_id']) + ','
            filter_for_department = filter_for_department + str(item['department_id']) + ','
            filter_for_equipment_class = filter_for_equipment_class + str(item['equipment_class_id']) + ','
        filter_by_id = filter_by_id[:len(filter_by_id)-1]+']'
        filter_for_operation = filter_for_operation[:len(filter_for_operation)-1] + ']'
        filter_for_department = filter_for_department[:len(filter_for_department)-1] + ']'
        filter_for_equipment_class = filter_for_equipment_class[:len(filter_for_equipment_class)-1] + ']'

# if is_entity_route_sheet_transaction:
filter_str = 'filter={{entity_route_sheet_operation_id in %s}}' % (filter_by_id)
str_request = hostname + '/rest/collection/entity_route_sheet_transaction?order_by=id&'+filter_str
responce = req.get(str_request, cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+ '\entity_route_sheet_transaction.csv', 'w') as fout:
    fout.write('id;user_id;stop_progress;stop_date;start_date;entity_route_sheet_operation_id\n')
    if j['meta']['count'] != 0:
        for item in j['entity_route_sheet_transaction']:
            line = "%s;%s;%s;%s;%s;%s\n" % (item['id'], item['user_id'], item['stop_progress'], item['stop_date'],
                                            item['start_date'], item['entity_route_sheet_operation_id'])
            fout.write(line)

# if is_operation:
filter_str = 'filter={{id in %s}}' % (filter_for_operation)
str_request = hostname+'/rest/collection/operation?order_by=id&'+filter_str
responce = req.get(str_request, cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\operation.csv', 'w') as fout:
    fout.write("id;nop;identity;name\n")
    if j['meta']['count'] != 0:
        for item in j['operation']:
            line = line = "%s;%s;%s;%s\n" % (item['id'], item['nop'], item['identity'], item['name'])
            fout.write(line)

# if is_department:
filter_str = 'filter={{id in %s}}' % (filter_for_department)
str_request = hostname+'/rest/collection/department?order_by=id&'+filter_str
responce = req.get(str_request, cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\department.csv', 'w') as fout:
    fout.write('id;identity;name\n')
    if j['meta']['count'] != 0:
        for item in j['department']:
            line = line = "%s;%s;%s\n" % (item['id'], item['identity'], item['name'])
            fout.write(line)

# if is_equipment_class:
filter_str = 'filter={{id in %s}}' % (filter_for_equipment_class)
str_request = hostname+'/rest/collection/equipment_class?order_by=id&'+filter_str
responce = req.get(str_request, cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\equipment_class.csv', 'w') as fout:
    fout.write('id;identity;name\n')
    if j['meta']['count'] != 0:
        for item in j['equipment_class']:
            line = line = "%s;%s;%s\n" % (item['id'], item['identity'], item['name'])
            fout.write(line)

# if is_entity_batch:
filter_str = 'filter={{id in %s}}' % (filter_for_entity_batch)
str_request = hostname+'/rest/collection/entity_batch?order_by=id&' + filter_str
responce = req.get(str_request, cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\eentity_batch.csv', 'w') as fout:
    fout.write('id;calculation_identity;order_id;identity;parent_id;picked;from_state;entity_id;note;calculation_session_id;quantity;status\n')
    if j['meta']['count'] != 0:
        filter_for_entity = '['
        for item in j['entity_batch']:
            line = line = "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;\n" % \
                          (item['id'], item['calculation_identity'], item['order_id'], item['identity'],item['parent_id'],
                           item['picked'], item['from_state'], item['entity_id'], item['note'],item['calculation_session_id'],
                           item['quantity'], item['status'])
            fout.write(line)
            filter_for_entity = filter_for_entity + str(item['id']) + ','
        filter_for_entity = filter_for_entity[:len(filter_for_entity)-1] + ']'

# if is_entity:
filter_str = 'filter={{id in %s}}' % (filter_for_entity)
str_request = hostname+'/rest/collection/entity?order_by=id&'+filter_str
responce = req.get(str_request, cookies=c, headers=h)
j = json.loads(responce.text)
with open(path+'\entity.csv', 'w') as fout:
    fout.write('id;identity;group;name;code\n')
    if j['meta']['count'] != 0:
        for item in j['entity']:
            line = "%s;%s;%s;%s;%s\n" % (item['id'], item['identity'], item['group'], item['name'], item['code'])
            fout.write(line)

# if is_user:
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