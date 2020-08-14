from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField
from config import DATABASE

database = SqliteDatabase(DATABASE)

class BaseModel(Model):
    class Meta:
        database = database

class Goods(BaseModel):
    item = CharField(unique=True)
    amount = IntegerField()
    subitems_id = ForeignKeyField('self', null=True, backref='children')