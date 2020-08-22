from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField, FloatField
# from config import DATABASE

database = SqliteDatabase('fair.db')

class BaseModel(Model):
    class Meta:
        database = database

class Goods(BaseModel):
    name = CharField(default='Item')
    amount = IntegerField(default=0)
    price = IntegerField(default=0)
    parent_id = ForeignKeyField('self', null=True, backref='children')

class Admins(BaseModel):
    chat_id = CharField()

class Orders_Info(BaseModel):
    chat_id = CharField()
    admin = CharField()
    time = FloatField()
    status = CharField()

class Orders_Content(BaseModel):
    order_id = ForeignKeyField(Orders_Info, backref='full_content')
    item_id = IntegerField()
    amount = IntegerField()
    cost = IntegerField()
