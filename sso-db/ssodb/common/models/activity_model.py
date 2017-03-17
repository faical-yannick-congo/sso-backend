import datetime
from ..core import db
from ..models import User, Service
import json
from bson import ObjectId

class Activity(db.Document):
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    updated_at = db.StringField(default=str(datetime.datetime.utcnow()))
    day = db.StringField(default=str(datetime.date.today().isoformat()), required=True)
    user = db.ReferenceField(User, required=True)
    service = db.ReferenceField(Service, required=True)
    sms = db.IntField(default=0)

    def save(self, *args, **kwargs):
        self.updated_at = str(datetime.datetime.utcnow())
        return super(Coverage, self).save(*args, **kwargs)

    def info(self):
        data = {'updated-at':self.updated_at, 'id':str(self.id),
        'created_at':self.created_at, 'day':str(self.day), 'user':self.user.phone,
        'service':self.service.name, 'sms':self.sms}
        return data

    def to_json(self):
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
