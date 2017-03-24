"""CoRR api module."""
import flask as fk
from ssodb.common.core import setup_app
from ssodb.common.models import Country
from ssodb.common.models import City
from ssodb.common.models import Service
from ssodb.common.models import User
from ssodb.common.models import Activity
import tempfile
from io import StringIO
from io import BytesIO
import os
import simplejson as json
import datetime
import traceback

import requests
from datetime import date, timedelta
from functools import update_wrapper
from calendar import monthrange
import time

import glob
from translate import Translator

# Flask app instance
app = setup_app(__name__)

# The sms sso service's version
SERVICE_VERSION = 0.1
# The sms sso service base url
SERVICE_URL = '/sms/services/sso/v{0}'.format(SERVICE_VERSION)


def service_response(code, title, content):
    """Provides a common structure to represent the response
    from any api's endpoints.
        Returns:
            Flask response with a prettified json content.
    """
    import flask as fk
    response = {'service':'sms-sso', 'code':code, 'title':title, 'content':content}
    return fk.Response(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')

def data_pop(data=None, element=''):
    """Pop an element of a dictionary.
    """
    if data != None:
        try:
            del data[element]
        except:
            pass

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def menu():
    return "Welcome to a world of SMS Service that we value for you."

def get_menu(service):
    r = requests.get('{0}/menu'.format(service.host))
    response = json.loads(r.text)
    return response['content']

def smartWelcome(services=[], country=None):
    language = 'en'
    if country.language != 'unknown':
        language = country.language
    translator = Translator(to_lang=language)
    content = ["sms-services"]
    content.append("{0}".format(translator.translate(menu())))
    if len(services) > 0:
        content.append(translator.translate("You are automatically registered to some default services."))
    for service in services:
        content.append(service.name)
        content.append("{0}".format(translator.translate(get_menu(service))))
    return '\n'.join(content)

def fetch_city(city, country):
    r = requests.get('http://autocomplete.wunderground.com/aq?query={0}&c={1}'.format(city, country))
    response = json.loads(r.text)
    results = response["RESULTS"]
    if len(results) == 0:
        return "capital"
    else:
        return results[0]["name"].split(',')[0]

# import all the api endpoints.
import sso.endpoints
