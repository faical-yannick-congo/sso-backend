import json

from flask.ext.api import status
import flask as fk

from ssodb.common import crossdomain
from sso import app, SERVICE_URL, service_response
from ssodb.common.models import User, Service

import mimetypes
import json
import traceback
import datetime
import random
import string
from io import StringIO
import hashlib

@app.route(SERVICE_URL + '/service/add', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(fk=fk, app=app, origin='*')
def add_service():
    if fk.request.method == 'POST':
        if fk.request.data:
            data = json.loads(fk.request.data)
            name = data.get('name', None)
            host = data.get('host', 'undefined')
            status = data.get('status', 'innactive')
            menu_endpoint = data.get('menu-endpoint', 'undefined')
            if name is None:
                return service_response(405, 'Service addition denied', 'A service has to contain a name.')
            else:
                _service = Service.objects(name=name).first()
                if _service is None:
                    _service = Service(created_at=str(datetime.datetime.utcnow()))
                    _service.name = name
                    _service.host = host
                    _service.country = country
                    _service.status = status
                    _service.menu_endpoint = menu_endpoint
                    _service.save()
                    return service_response(200, 'Service created', 'Service added with success.')
                else:
                    return service_response(204, 'Service addition denied', 'A Service with this name already exists.')
        else:
            return service_response(204, 'Service addition failed', 'No data submitted.')
    else:
        return service_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(SERVICE_URL + '/service/edit/<service_name_or_id>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(fk=fk, app=app, origin='*')
def edit_service(service_name_or_id):
    if fk.request.method == 'GET':
        _service = Service.objects(name=service_name_or_id).first()
        if _service is None:
            try:
                _service = Service.objects.with_id(service_name_or_id)
            except:
                _service = None
        if _service:
            if fk.request.data:
                data = json.loads(fk.request.data)
                name = data.get('name', _service.name))
                host = data.get('host', _service.host))
                status = data.get('status', _service.status)
                menu_endpoint = data.get('menu-endpoint', _service.menu_endpoint)

                if name != _service.name:
                    _service_check = Service.objects(name=name).first()
                    if _service_check is None:
                        _service.name = name
                    else:
                        return service_response(204, 'Service edition denied', 'A service with this name already exists.')
                _service.host = host
                _service.status = status
                _service.menu_endpoint = menu_endpoint
                _service.save()
                return service_response(200, 'Edition succeeded', 'Service {0} edited.'.format(service_name_or_id))
            else:
                return service_response(204, 'Service edition failed', 'No data submitted.')
        else:
            return service_response(204, 'Unknown service', 'No corresponding service found.')
    else:
        return service_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(SERVICE_URL + '/service/show/<service_name_or_id>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(fk=fk, app=app, origin='*')
def show_service(service_name_or_id):
    if fk.request.method == 'GET':

        if service_name_or_id == 'all':
            services = [s.info() for s in Service.objects()]
            return service_response(200, 'Services list', {'size':len(services), 'services':services})
        else:
            service = Service.objects(name=service_name_or_id)
            if _service is None:
                try:
                    _service = Service.objects.with_id(service_name_or_id)
                except:
                    _service = None
            if _service:
                return service_response(200, 'Service {0} info'.format(service_name_or_id), _service.info())
            else:
                return service_response(204, 'Unknown service', 'No corresponding service found.')
    else:
        return service_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(SERVICE_URL + '/service/delete/<service_name_or_id>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(fk=fk, app=app, origin='*')
def delete_service(service_name_or_id):
    if fk.request.method == 'GET':
        if service_name_or_id == "all":
            for _service in Service.objects():
                _new.delete()
            return service_response(200, 'Deletion succeeded', 'All services deleted')
        else:
            _service = Service.objects(name=service_name_or_id)
            if _service is None:
                try:
                    _service = Service.objects.with_id(service_name_or_id)
                except:
                    _service = None
            if _service:
                _service.delete()
                return service_response(200, 'Deletion succeeded', 'Service {0} deleted.'.format(service_name_or_id))
            else:
                return service_response(204, 'Unknown service', 'No corresponding service found.')
    else:
        return service_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')
