from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField, TimestampField
from config import DATABASE

database = SqliteDatabase(DATABASE)

class BaseModel(Model):
    class Meta:
        database = database

class Goods(BaseModel):
    name = CharField(default='Item')
    amount = IntegerField(default=0)
    parent_id = ForeignKeyField('self', null=True, backref='children')

class Admins(BaseModel):
    chat_id = CharField(unique=True)

class Orders(BaseModel):
    order_id = IntegerField()
    item_id = IntegerField()
    amount = IntegerField()
    time = TimestampField()
    status = IntegerField()
