import datetime
from ..core import db
from ..models import Country, Service
import json
from bson import ObjectId

class User(db.Document):
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    updated_at = db.StringField(default=str(datetime.datetime.utcnow()))
    phone = db.StringField(unique=True, required=True)
    country = db.ReferenceField(Country, required=True)
    services = db.ListField(db.ReferenceField(Service))

    def save(self, *args, **kwargs):
        self.updated_at = str(datetime.datetime.utcnow())
        return super(Radio, self).save(*args, **kwargs)

    def info(self):
        data = {'updated-at':self.updated_at, 'id':str(self.id),
        'created_at':self.created_at, 'phone':self.name,
        'country':self.country.name, 'services':[s.name for s in self.services]}
        return data

    def to_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
