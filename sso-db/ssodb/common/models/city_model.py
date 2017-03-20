import datetime
from ..core import db
import json
from bson import ObjectId
from ..model import Country

class City(db.Document):
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    updated_at = db.StringField(default=str(datetime.datetime.utcnow()))
    name = db.StringField(required=True)
    country = db.ReferenceField(Country, required=True)

    def save(self, *args, **kwargs):
        self.updated_at = str(datetime.datetime.utcnow())
        return super(City, self).save(*args, **kwargs)

    def info(self):
        data = {'updated-at':self.updated_at, 'id':str(self.id),
        'created_at':self.created_at, 'name':self.name,
        'country':self.country}
        return data

    def to_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
