from datetime import datetime
from functools import partialmethod
from urllib.parse import urljoin

from requests import Session
from tqdm import tqdm

from base import Base

__all__ = [
    'GetDataFromBFG',
]


class GetDataFromBFG(Base):

    def __init__(self, login, password, base_url,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = Session()
        self._base_url = base_url
        self._login = login
        self._password = password

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def _make_url(self, uri):
        return urljoin(self._base_url, uri)

    def _perform_json_request(self, http_method, uri, **kwargs):
        url = self._make_url(uri)
        logger = self._logger

        logger.debug('Выполнение {} запроса '
                     'по ссылке {!r}.'.format(http_method, url))

        logger.debug('Отправляемые данные: {!r}.'.format(kwargs))

        response = self._session.request(http_method,
                                         url=url,
                                         **kwargs).json()

        logger.debug('Получен ответ на {} запрос по ссылке {!r}: '
                     '{!r}'.format(http_method, url, response))
        return response

    _perform_get = partialmethod(_perform_json_request, 'GET')

    def _perform_post(self, uri, data):
        return self._perform_json_request('POST', uri, json=data)

    def _perform_put(self, uri, data):
        return self._perform_json_request('PUT', uri, json=data)

    def _perform_action(self, uri_part, **data):
        return self._perform_post(
            '/action/{}'.format(uri_part),
            data=data
        )

    def _perform_login(self):
        return self._perform_action(
            'login',
            data={
                    'login': self._login,
                    'password': self._password
                },
            action='login'
        )['data']

    def get_from_rest_collection(self, table, *args, **kwargs):
        request = 'rest/collection/{}?{}&'.format(
                table,
                '&'.join(
                    ['%s=%s' % (key, value) for (key, value) in kwargs.items()]
                )
            )
        for row in args:
            request += '&'.join(row)
            request += '&'
        return self._perform_get(request)

    def _get_orders(self, plan_id, *args, **kwargs):
        kwargs['column_names'] = 'plan_id'
        kwargs['search'] = plan_id
        kwargs['search_type'] = 1
        return self._perform_get(
            'rest/order?'+'&'.join(
                ['%s=%s' % (key, value) for (key, value) in kwargs.items()])
        )

    def _get_plan_id(self, session_id):
        return self.get_from_rest_collection(
            'simulation_session',
            {
                'with': 'plan',
                'filter': '{{ id eq {} }}'.format(session_id)
            },
        )['plan'][0]['id']

    def _get_sessions_id(self):
        sessions_info = self.get_from_rest_collection(
            table='simulation_session',
            filter='{{ deleted is false } and {status eq 0}}'
        )['simulation_session']
        return [x['id'] for x in sessions_info]

    def _get_max_dateto(self, session_id):
        return datetime.fromisoformat(
            self._get_orders(
                plan_id=self._get_plan_id(session_id),
                limit=1,
                page=1,
                sort_by='date_to',
                asc='false'
            )['order'][0]['date_to']
        )

    def _get_detailed_equipment_utilization(self, session_id, department_id, equipment_class_id):
        answer = self.get_from_rest_collection(
            'simulation_equipment_class_period_occupy',
            sort_by='start_date',
            filter='{{ simulation_session_id eq {} }} and {{ department_id eq {} }} and {{ equipment_class_id eq {} }}'.format(
                session_id,
                department_id,
                equipment_class_id
            )
        )['simulation_equipment_class_period_occupy']
        factory = self.factory[session_id]
        for row in answer:
            dept = factory.departments[row['department_id']]
            equipment_class = dept.equipment[factory.equipment_classes[row['equipment_class_id']]]
            equipment_class.period_info.append(row)

    def _get_detailed_profession_utilization(self, session_id, department_id, profession_id):
        answer = self.get_from_rest_collection(
            'simulation_profession_period_occupy',
            sort_by='start_date',
            filter='{{ simulation_session_id eq {} }} and {{ department_id eq {} }} and {{ profession_id eq {} }}'.format(
                session_id,
                department_id,
                profession_id
            )
        )['simulation_profession_period_occupy']
        factory = self.factory[session_id]
        for row in answer:
            dept = factory.departments[row['department_id']]
            profession = dept.profession[factory.professions[row['profession_id']]]
            profession.period_info.append(row)

    def _get_resources_data(self, session_id):
        time_schedule = {
            row['id']: row['name']
            for row in self._perform_get(
                '/rest/time_schedule'
            )['time_schedule']
        }

        employee_variation = self._perform_get(
            '/rest/employee_variation?id={}'.format(
                self.get_from_rest_collection(
                    'simulation_session',
                    filter='{{ id eq {} }}'.format(session_id)
                )['simulation_session'][0]['employee_variation_id'])
        )['employee_variation'][0]['data']

        default_time_schedule = time_schedule[employee_variation['default_time_schedule']]
        department_time_schedule = {
            row['department_id']: time_schedule[row['time_schedule_id']]
            for row in employee_variation['department_time_schedule']
        }

        answer = self._perform_get(
            'data/simulation_result/{}/resource_types'.format(session_id)
        )
        factory = self.factory[session_id]
        for row in answer['department']:
            factory.add_department(
                row['id'],
                row['identity'],
                row['name'],
                department_time_schedule.get(row['id']) or default_time_schedule
            )

        for row in answer['equipment_class']:
            factory.add_equipment_class(row['id'], row['identity'], row['name'])

        for row in answer['profession']:
            factory.add_profession(row['id'], row['identity'], row['name'])

        for row in answer['data']:
            dept = factory.departments[row['department_id']]
            dept.add_equipment(
                factory.equipment_classes.get(row.get('equipment_class_id')), row['occupy'], row['count']
            )
            dept.add_profession(
                factory.professions.get(row.get('profession_id')), row['occupy'], row['count']
            )


    @classmethod
    def from_config(cls, config):
        return cls(
            config['input']['login'],
            str(config['input']['password']),
            config['input']['url'],
        )
