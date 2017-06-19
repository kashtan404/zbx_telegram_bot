import json
import requests


def parsed(func):
    def wrapper(self, *args, **kwargs):
        return json.loads(func(self, *args, **kwargs).content.decode("utf-8"))
    return wrapper


@parsed
def auth(url, user, password):
    req = {
            "jsonrpc": "2.0",
            "method": "user.login",
             "params": {
                "user": user,
                "password": password
                },
            "id": 1,
    }
    resp = requests.post(url, json=req)
    return resp


class Zabbix(object):


    def __init__(self, auth, url):
        self.__auth = auth
        self.__url = url

    def select_command(self, message):
        command_text = message.split(' ')
        command_text.pop(0)
        try:
            command = self._ZBX_COMMANDS.get(command_text[0]).get(command_text[1])(self, command_text[2:])
        except IndexError and AttributeError:
            return 'Invalid command'
        except TypeError:
            return 'Command not realized'
        return command

    def get(self, message):
        return message + ' success get reply'

    def set(self, message):
        return message + ' success set reply'

    def ping(self, message):
        return message + ' success ping reply'

    @staticmethod
    def parse_json(json_object):
        result = json.loads(json_object.content.decode("utf-8"))
        return result

    def gethostgroup(self, **options):
        # groups = []
        req = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": "extend",
            },
            "auth": self.__auth,
            "id": 1
        }
        resp = requests.post(self.__url, json=req)
        # groups = [group['name'] for group in self.parse_json(resp)['result']]
        # return str(groups).replace(',', ',\n')
        return str(self.parse_json(resp)['result'])


    def getevent(self, **options):
        req = {
            "jsonrpc": "2.0",
            "method": "event.get",
            "params": {
                "output": "extend",
                "acknowledged": "false",
                "sortfield": ["clock", "eventid"],
                "sortorder": "DESC",
                "limit": 20
            },
            "auth": self.__auth,
            "id": 1
        }

        resp = requests.post(self.__url, json=req)
        return str(self.parse_json(resp)['result'])

    def gethost(self, zbx_hosts):
        filter = None
        output = ''
        if zbx_hosts[-1] in self._host_filters.keys():
            filter = zbx_hosts[-1]
            zbx_hosts.pop(-1)
        req = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": "extend",
                "filter": {
                    "host": zbx_hosts
                }
            },
            "auth": self.__auth,
            "id": 1
        }
        if filter:
            req["params"][self._host_filters[filter]] = "extend"
        else:
            req["params"]["selectGroups"] = "extend"
            req["params"]["selectInterfaces"] = "extend"
        resp = requests.post(self.__url, json=req)
        result = self.parse_json(resp)['result']
        for host in result:
            output += host['name'] + '\n'
            for element in host[filter]:
                output += 'id ' + element['triggerid'] + ' ' + 'desc: ' + element['description'] + '\n'
        print(output)
        return output

    _host_filters = {
        'discoveries': "selectDiscoveries",
        'graphs': "selectGraphs",
        'http': "selectHttpTests",
        'inventory': "selectInventory",
        'items': "selectItems",
        'triggers': "selectTriggers"
    }

    _ZBX_COMMANDS = {
        # Веб-сценарий
        'httptest': {
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # График
        'graph': {
            'create': None,
            'delete': None,
            'get': None,
            'update': None
        },
        # Группа пользователей
        'usergroup': {
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'massadd': None,
            'massupdate': None,
            'update': None
        },
        # Группа узлов сети
        'hostgroup': {
            'create': None,
            'delete': None,
            'get': gethostgroup,
            'isreadable': None,
            'iswritable': None,
            'massadd': None,
            'massremove': None,
            'massupdate': None,
            'update': None
        },
        # Группа элементов данных
        'application': {
            'create': None,
            'delete': None,
            'get': None,
            'massadd': None,
            'update': None
        },
        # Действие
        'action': {
            'create': None,
            'delete': None,
            'get': None,
            'update': None
        },
        # Динамика изменений
        'trend': {
            'get': None
        },
        # Изображение
        'image': {
            'create': None,
            'delete': None,
            'get': None,
            'update': None
        },
        # Интерфейс узла сети
        'hostinterface': {
            'create': None,
            'delete': None,
            'get': None,
            'massadd': None,
            'massremove': None,
            'replacehostinterfaces': None,
            'update': None
        },
        # Информация о API
        'apiinfo': {
            'version': None
        },
        # История
        'history': {
            'get': None
        },
        # Карта сети
        'map': {
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # Комплексный экран
        'screen': {
            'create': None,
            'delete': None,
            'get': None,
            'update': None
        },
        # Комплексный экран шаблона
        'templatescreen': {
            'copy': None,
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # Конфигурация
        'configuration': {
            'export': None,
            'import': None
        },
        # Корреляция
        'correlation': {
            'create': None,
            'delete': None,
            'get': None,
            'update': None
        },
        # Обнаруженный сервис
        'dservice': {
            'get': None
        },
        # Обнаруженный узел сети
        'dhost': {
            'get': None
        },
        # Обслуживание
        'maintenance': {
            'create': None,
            'delete': None,
            'get': None,
            'update': None
        },
        # Оповещение
        'alert': {
            'get': None
        },
        # Оповещение пользователя
        'usermedia': {
            'get': None
        },
        # Пользователь
        'user': {
            'addmedia': None,
            'create': None,
            'delete': None,
            'deletemedia': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'login': None,
            'logout': None,
            'update': None,
            'updatemedia': None,
            'updateprofile': None
        },
        # Пользовательский макрос
        'usermacro': {
            'create': None,
            'createglobal': None,
            'delete': None,
            'deleteglobal': None,
            'get': None,
            'update': None,
            'updateglobal': None
        },
        # Правило LLD
        'discoveryrule': {
            'copy': None,
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # Правило обнаружения
        'drule': {
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # Преобразование значений
        'valuemap': {
            'create': None,
            'delete': None,
            'get': None,
            'update': None
        },
        # Проблема
        'problem': {
            'get': None
        },
        # Проверка обнаружения
        'dcheck': {
            'get': None
        },
        # Прокси
        'proxy': {
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # Прототип графиков
        'graphprototype': {
            'create': None,
            'delete': None,
            'get': None,
            'update': None
        },
        # Прототип триггеров
        'triggerprototype': {
            'create': None,
            'delete': None,
            'get': None,
            'update': None
        },
        # Прототип узлов сети
        'hostprototype': {
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # Прототип элементов данных
        'itemprototype': {
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # Скрипт
        'script': {
            'create': None,
            'delete': None,
            'execute': None,
            'get': None,
            'getscriptsbyhosts': None,
            'update': None
        },
        # Событие
        'event': {
            'acknowledge': None,
            'get': getevent
        },
        # Соответствие иконок
        'iconmap': {
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # Способ оповещения
        'mediatype': {
            'create': None,
            'delete': None,
            'get': None,
            'update': None
        },
        # Триггер
        'trigger': {
            'adddependencies': None,
            'create': None,
            'delete': None,
            'deletedependencies': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # Узел сети
        'host': {
            'create': None,
            'delete': None,
            'get': gethost,
            'isreadable': None,
            'iswritable': None,
            'massadd': None,
            'massremove': None,
            'massupdate': None,
            'update': None
        },
        # Услуга IT
        'service': {
            'adddependencies': None,
            'addtimes': None,
            'create': None,
            'delete': None,
            'deletedependencies': None,
            'deletetimes': None,
            'get': None,
            'getsla': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # Шаблон
        'template': {
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'massadd': None,
            'massremove': None,
            'massupdate': None,
            'update': None
        },
        # Элемент графика
        'graphitem': {
            'get': None
        },
        # Элемент данных
        'item': {
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None
        },
        # Элемент комплексного экрана
        'screenitem': {
            'create': None,
            'delete': None,
            'get': None,
            'isreadable': None,
            'iswritable': None,
            'update': None,
            'updatebyposition': None
        },
        # Элемент комплексного экрана шаблона
        'templatescreenitem': {
            'get': None
        }
    }
