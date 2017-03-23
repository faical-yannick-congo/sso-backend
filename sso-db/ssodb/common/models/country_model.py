import datetime
from ..core import db
import json
from bson import ObjectId

class Country(db.Document):
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    updated_at = db.StringField(default=str(datetime.datetime.utcnow()))
    name = db.StringField(required=True, unique=True)
    code = db.StringField(required=True, unique=True)
    zone = db.StringField(default="unknown")
    users = db.IntField(default=0)
    language = db.StringField()
    latitude = db.StringField(default="")
    longitude = db.StringField(default="")

    def save(self, *args, **kwargs):
        self.updated_at = str(datetime.datetime.utcnow())
        return super(Country, self).save(*args, **kwargs)

    def info(self):
        data = {'updated-at':self.updated_at, 'id':str(self.id),
        'created_at':self.created_at, 'name':self.name,
        'code':self.code, 'zone':self.zone, 'users':self.users,
        'language':self.language}
        try:
            if self.latitude == "":
                data['lat'] = ""
                data['lng'] = ""
            else:
                data['lat'] = float(self.latitude)
                data['lng'] = float(self.longitude)
        except:
            data['lat'] = ""
            data['lng'] = ""

        return data

    def to_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
