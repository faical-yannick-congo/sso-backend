import datetime
from ..core import db
import json
from bson import ObjectId

class Service(db.Document):
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    updated_at = db.StringField(default=str(datetime.datetime.utcnow()))
    name = db.StringField(required=True, unique=True)
    host = db.StringField()
    possible_status = ["active", "innactive"]
    status = db.StringField(default="innactive", choices=possible_status)
    menu_endpoint = db.StringField() # Endpoint that take care of providing the sms menu to the service.

    def save(self, *args, **kwargs):
        self.updated_at = str(datetime.datetime.utcnow())
        self.day = str(datetime.date.today().isoformat())
        return super(Service, self).save(*args, **kwargs)

    def info(self):
        data = {'updated-at':str(self.updated_at), 'id':str(self.id),
        'created-at':str(self.created_at), 'status':self.status, 'name':self.name, 'host':self.host,
        'menu-endpoint':self.menu_endpoint}
        return data

    def to_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
