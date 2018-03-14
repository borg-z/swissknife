from flask_mongoengine import MongoEngine

from flask_login import UserMixin
db = MongoEngine()


class Device(db.Document):
    devid = db.StringField(required=True, unique=True)
    devtype = db.StringField()
    addr = db.StringField()
    alias = db.StringField()
    uri = db.StringField()
    ports = db.ListField(db.DictField())



class System(db.Document):
    siteupdate = db.DateTimeField()
    graphupdate = db.DateTimeField()
    graph = db.FileField()

class Stpdomins(db.Document):
    domain = db.StringField()
    devices = db.ListField(db.StringField())

class DBUser(db.Document, UserMixin):
    user = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)


class Templates(db.Document):
    name = db.StringField(required=True, unique=True)
    description = db.StringField()
    variables =  db.ListField(db.DictField())  
    template = db.StringField()
