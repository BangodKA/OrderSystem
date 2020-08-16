from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField
from config import DATABASE

database = SqliteDatabase(DATABASE)

class BaseModel(Model):
    class Meta:
        database = database

class Goods(BaseModel):
    name = CharField()
    amount = IntegerField(default=0)
    parent_id = ForeignKeyField('self', null=True, backref='children')

class Admins(BaseModel):
    chat_id = CharField(unique=True)