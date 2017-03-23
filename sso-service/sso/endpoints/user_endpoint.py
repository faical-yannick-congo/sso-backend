import simplejson as json

from flask.ext.api import status
import flask as fk

from ssodb.common import crossdomain
from sso import app, SERVICE_URL, service_response, smartWelcome
from ssodb.common.models import Country, City, Service, User, Activity

import mimetypes
import traceback
import datetime
import random
import string
from io import StringIO
import hashlib
import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_country_code
from phonenumbers.phonenumberutil import region_code_for_number
import pycountry

from geopy import geocoders
from tzwhere import tzwhere
from pytz import timezone
from babel import Locale

@app.route(SERVICE_URL + '/users/countries', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(fk=fk, app=app, origin='*')
def users_countries():
    if fk.request.method == 'GET':
        countries = [ c.info() for c in Country.objects()]
        return service_response(200, 'Users countries', {'size':len(countries), 'countries':countries})
    else:
        return service_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(SERVICE_URL + '/users/cities/<country>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(fk=fk, app=app, origin='*')
def users_cities(country):
    if fk.request.method == 'GET':
        _country = Country.objects(code=country).first()
        if _country:
            cities = [ c.info() for c in City.objects(country=_country)]
            return service_response(200, 'Users cities', {'size':len(cities), 'cities':cities, 'language':_country.language})
        else:
            return service_response(204, 'User cities pull denied', 'No country with this code was found.')
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
            services = data.get('services', None)
            city = data.get('city', 'capital')
            if phone is None:
                return service_response(405, 'User registration denied', 'A user has to contain a phone number.')
            else:
                if services is None:
                    services = ["news-service", "weather-service"]
                _services = []
                for service in services:
                    _services.append(Service.objects(name=service).first())
                _user = User.objects(phone=phone).first()
                if _user is None:
                    if None is _services:
                        return service_response(204, 'User registration denied', 'one or more services were not found name was found.')
                    pn = phonenumbers.parse(phone, None)
                    country = str(pn.country_code)
                    _user = User(created_at=str(datetime.datetime.utcnow()))
                    _user.phone = phone
                    _country = Country.objects(code=country).first()
                    if _country:
                        _country.users = _country.users + 1
                        if _country.language == "unknown":
                            _country_name_short = region_code_for_country_code(pn.country_code)
                            _country.language = Locale.parse('und_{0}'.format(_country_name_short)).language
                        if _country.info()["lat"] == "":
                            g = geocoders.GoogleV3(api_key=" AIzaSyBDEqeJ4rV_yxArspKEm8ebr75VEJGaphk")
                            tz = tzwhere.tzwhere()
                            place, (lat, lng) = g.geocode(_country_object.name, timeout=10)
                            timeZoneStr = tz.tzNameAt(lat, lng)
                            _country.latitude = str(lat)
                            _country.longitude = str(lng)
                        _country.save()
                        _city = City.objects(name=city, country=_country).first()
                    else:
                        _country = Country(created_at=str(datetime.datetime.utcnow()), code=country)
                        _country_object = pycountry.countries.get(alpha_2=region_code_for_number(pn))
                        _country_name_short = region_code_for_country_code(pn.country_code)
                        _country.name = "{0}:{1}".format(_country_name_short, _country_object.name)
                        _country.language = Locale.parse('und_{0}'.format(_country_name_short)).language
                        _country.users = 1
                        g = geocoders.GoogleV3(api_key=" AIzaSyBDEqeJ4rV_yxArspKEm8ebr75VEJGaphk")
                        tz = tzwhere.tzwhere()
                        place, (lat, lng) = g.geocode(_country_object.name, timeout=10)
                        timeZoneStr = tz.tzNameAt(lat, lng)
                        _country.latitude = str(lat)
                        _country.longitude = str(lng)
                        timeZoneObj = timezone(timeZoneStr)
                        now_time = datetime.datetime.now(timeZoneObj)
                        time_block = str(now_time).split(" ")
                        if "-" in time_block[1]:
                            _country.zone = "GMT-{0}".format(time_block[1].split("-")[1].split(":")[0])
                        if "+" in time_block[1]:
                            _country.zone = "GMT+{0}".format(time_block[1].split("+")[1].split(":")[0])
                        _country.save()
                        _city = City(created_at=str(datetime.datetime.utcnow()), name=city, country=_country)
                        _city.save()
                    _user.country = _country
                    _user.city = _city
                    _user.services.extend(_services)
                    _user.save()

                    return service_response(201, 'Account created', smartWelcome(_user.services, _country))
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
            users = []
        service = fk.request.args.get('service', 'None')
        _service = Service.objects(name=service).first()
        if _service is None:
            return service_response(204, 'User pull failed', 'Unknown service specified.')
        else:
            for u in User.objects(country=_country):
                if _service.name in [s.name for s in u.services]:
                    users.append(u)
            if int(index) >= len(users) or index == "-1":
                return service_response(205, 'End of the list', 'No users anymore.')
            else:
                user = users[int(index)]
                data = user.info()
                if int(index)+1 >= len(users):
                    data['next'] = -1
                else:
                    data['next'] = int(index)+1
                data['upcoming'] = len(users) - (int(index)+1)
                day = str(datetime.date.today().isoformat())
                activity = Activity.objects(user=user, service=_service, day=day).first()
                if activity is None:
                    activity =  Activity(created_at=str(datetime.datetime.utcnow()), user=user, service=_service, day=day)
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
