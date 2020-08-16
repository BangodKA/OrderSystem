from models import database, Goods, Admins
from datetime import date
from random import choice, seed
import config

def create_tables():
    database.connect()
    database.create_tables([Goods, Admins], safe=True)
    Goods.create(name = '.BASE_CAT', amount = 0)
    database.close()

# –––––––––––––ADMIN––––––––––––

def reg_admin(chat_id):
    Admins.create(chat_id = chat_id)

def demote_admin(chat_id):
    Admins.delete().where(Admins.chat_id == chat_id)

def get_chat_id():
    admins = Admins.select()
    chat_ids = [admin.chat_id for admin in admins]
    config.admin_index += 1
    config.admin_index %= len(admins)
    return chat_ids[config.admin_index]

def check_id(chat_id):
    admins = Admins.select()
    chat_ids = [admin.chat_id for admin in admins]
    return chat_id in chat_ids


def get_all_items():
    items = Goods.select()
    all_items = [[item.name, item.id, item.amount] for item in items]
    return all_items

def update_amount(id_, amount_):
    parent_id_ = Goods.select().where(Goods.id == id_)[0].parent_id
    q = (Goods.update({Goods.amount: Goods.amount + amount_}).where(Goods.id == parent_id_))
    q.execute()
    if (parent_id_ != None):
        update_amount(parent_id_, amount_)


def add(name_, amount_, parent_id_):
    item = Goods.create(name = name_, amount = amount_, parent_id = parent_id_)
    if (amount_ != 0):
        update_amount(item.id, amount_)
    return Goods.select().where(Goods.id == parent_id_)[0].name

def change(name_, amount_, id_):
    item = Goods.select().where(Goods.id == id_)[0]
    query = Goods.update({Goods.name : name_, Goods.amount : amount_}).where(Goods.id == id_)
    query.execute()
    amount = amount_ - item.amount
    if (amount_ != 0):
        update_amount(item.id, amount)
    return item

def get_name_by_id(id_):
    item = Goods.select().where(Goods.id == id_)
    return item[0].name

def new():
    b = Goods.select().where(Goods.subitems_id != None)
    Parent = Goods.alias()
    c = (Goods
            .select(Goods)
            .join(Parent, on=(Goods.subitems_id == Parent.id)))
    print(c[0].subitems_id.item)

def delete_children(id_):
    children = Goods.select().where(Goods.parent_id == id_)
    if (len(children) != 0):
        for child in children:
            delete(child.id)
    query = Goods.delete().where(Goods.id == id_)
    query.execute()

def delete(id_):
    children = Goods.select().where(Goods.parent_id == id_)
    if (len(children) != 0):
        for child in children:
            delete_children(child.id)
    
    if (id_ != 1):
        amount = Goods.select().where(Goods.id == id_)[0].amount
        update_amount(id_, -amount)
        query = Goods.delete().where(Goods.id == id_)
        query.execute()

def clear_base():
    query = Goods.delete().where(Goods.id != 1)
    query.execute()


# –––––––––––––USER–––––––––––––

def get_immed_heirs(parent_id):
    items = Goods.select().where(Goods.parent_id == parent_id)
    res = [[item.name, item.id, item.amount] for item in items]
    return res