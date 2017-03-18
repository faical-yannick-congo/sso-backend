import simplejson as json

from flask.ext.api import status
import flask as fk

from ssodb.common import crossdomain
from sso import app, SERVICE_URL, service_response
from ssodb.common.models import Country, Service, User, Activity

import mimetypes
import traceback
import datetime
import random
import string
from io import StringIO
import hashlib
import phonenumbers

@app.route(SERVICE_URL + '/users/countries', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(fk=fk, app=app, origin='*')
def users_countries():
    if fk.request.method == 'GET':
        countries = [ c.info() for c in Country.objects()]
        return service_response(200, 'Users countries', {'size':len(countries), 'countries':countries})
    else:
        return service_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(SERVICE_URL + '/user/register', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(fk=fk, app=app, origin='*')
def user_register():
    if fk.request.method == 'POST':
        if fk.request.data:
            print(fk.request.data)
            data = json.loads(fk.request.data)
            phone = data.get('phone', None)
            service = data.get('service', None)
            if phone is None and service is None:
                return service_response(405, 'User registration denied', 'A user has to contain a phone number and specify at least one service.')
            else:
                _service = Service.objects(name=service).first()
                _user = User.objects(phone=phone).first()
                if _user is None:
                    if _service is None:
                        return service_response(204, 'User registration denied', 'No service with this name was found.')
                    country = str(phonenumbers.parse(phone, None).country_code)
                    _user = User(created_at=str(datetime.datetime.utcnow()))
                    _user.phone = phone
                    _country = Country.objects(code=country).first()
                    if _country:
                        _country.users = _country.users + 1
                        _country.save()
                    else:
                        _country = Country(created_at=str(datetime.datetime.utcnow()), name=country, code=country)
                        _country.users = 1
                        _country.save()
                    _user.country = _country
                    _user.services.append(_service)
                    _user.save()
                    return service_response(201, 'Account created', smartWelcome(_service.name, country))
                else:
                    return service_response(204, 'User registration denied', 'A user with this phone number already exists.')
        else:
            return service_response(204, 'User registration failed', 'No data submitted.')
    else:
        return service_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(SERVICE_URL + '/users/country/<country>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(fk=fk, app=app, origin='*')
def users_by_country(country):
    if fk.request.method == 'GET':
        if country == 'all':
            users = [u.info() for u in User.objects()]
        else:
            _country = Country.objects(code=country).first()
            if _country is None:
                _country = Country.objects(name=country).first()
            users = [u.info() for u in User.objects(country=_country)]
        return service_response(200, 'Country {0} users'.format(country), {'size':len(users), 'users':users})
    else:
        return service_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(SERVICE_URL + '/user/pull/<country>/<index>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(fk=fk, app=app, origin='*')
def user_pull_country(country, index):
    if fk.request.method == 'GET':
        if country == 'all':
            users = [u.info() for u in User.objects()]
        else:
            _country = Country.objects(code=country).first()
            if _country is None:
                _country = Country.objects(name=country).first()
            users = [u.info() for u in User.objects(country=_country)]
        if index >= len(users) or index == "-1":
            return service_response(205, 'End of the list', 'No users anymore.')
        else:
            user = users[int(index)]
            data = user.info()
            if int(index)+1 >= len(users):
                data['next'] = -1
            else:
                data['next'] = int(index)+1
            data['upcoming'] = len(users) - (index+1)
            day = str(datetime.date.today().isoformat())
            activity = Activity.objects(user=user, day=day).first()
            if activity is None:
                activity =  Activity(created_at=str(datetime.datetime.utcnow()), user=user, day=day)
                activity.save()
            activity.sms = activity.sms + 1
            activity.save()
            return service_response(200, 'Country {0} user {1}'.format(country, index), data)
    else:
        return service_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(SERVICE_URL + '/user/delete/<user_id_or_phone>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(fk=fk, app=app, origin='*')
def user_delete(user_id_or_phone):
    if fk.request.method == 'GET':
        if '+' not in user_id_or_phone:
            _userID = User.objects.with_id(user_id_or_phone)
            _userPh = None
        else:
            _userID = None
            _userPh = User.objects(phone=user_id_or_phone).first()
        if _userID:
            _userID.delete()
            return service_response(200, 'Deletion succeeded', 'User {0} deleted.'.format(user_id_or_phone))
        elif _userPh:
            _userPh.delete()
            return service_response(200, 'Deletion succeeded', 'User {0} deleted.'.format(user_id_or_phone))
        else:
            return service_response(204, 'Unknown user', 'No corresponding user found.')
    else:
        return service_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')
