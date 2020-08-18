from models import database, Goods, Admins, Orders
from datetime import date
from random import choice, seed
import config

def create_tables():
    database.connect()
    database.create_tables([Goods, Admins, Orders], safe=True)
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
    chat_id = choice(chat_ids)
    return chat_id

def check_id(chat_id):
    admins = Admins.select()
    chat_ids = [admin.chat_id for admin in admins]
    return chat_id in chat_ids


def get_all_items():
    items = Goods.select()
    all_items = [[item.name, item.id, item.amount] for item in items]
    return all_items

def update_amount(id_, amount_, add=False):
    item = Goods.select().where(Goods.id == id_)[0]
    # amount = amount_ - item.amount
    query = Goods.update({Goods.amount : Goods.amount + amount_}).where(Goods.id == id_)
    query.execute()
    # parent_id_ = Goods.select().where(Goods.id == id_)[0].parent_id
    # q = (Goods.update({Goods.amount: Goods.amount + amount}).where(Goods.id == parent_id_))
    # q.execute()
    if (item.parent_id != None and not add):
        update_amount(item.parent_id, amount_)
    return item

def update_name(id_, name):
    item = Goods.select().where(Goods.id == id_)[0]
    query = Goods.update({Goods.name : name}).where(Goods.id == id_)
    query.execute()
    return item

def get_full_name_by_id(id_):
    if id_ == 1:
        return ''
    item = Goods.select().where(Goods.id == id_)
    if (item[0].parent_id.id != 1):
        res = '{}::{}'.format(get_full_name_by_id(item[0].parent_id), item[0].name)
    else:
        res = item[0].name
    return res

# def add_new_item_parent(parent_id):
#     item = Goods.create(parent_id = parent_id)
#     return item.id

def add(name_, amount_, parent_id_):
    item = Goods.create(name = name_, amount = amount_, parent_id = parent_id_)
    if (amount_ != 0):
        update_amount(item.id, amount_)
    return item.id

def change(name_, amount_, id_):
    item = Goods.select().where(Goods.id == id_)[0]
    query = Goods.update({Goods.name : name_, Goods.amount : amount_}).where(Goods.id == id_)
    query.execute()
    amount = amount_ - item.amount
    if (amount_ != 0):
        update_amount(item.id, amount)
    return item

def get_item_by_id(id_):
    item = Goods.select().where(Goods.id == id_)
    return item[0]

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
    query = Goods.update({Goods.amount: 0})
    query.execute()


# –––––––––––––USER–––––––––––––

def get_immed_heirs(parent_id):
    items = Goods.select().where(Goods.parent_id == parent_id)
    res = [[item.name, item.id, item.amount] for item in items]
    return res

def buy_item(id_, amount_):
    item = Goods.select().where(Goods.id == id_)[0]
    if (item.amount < amount_):
        raise ValueError(str.join('Этого товара осталось всего ', str(item.amount)))
    q = (Goods.update({Goods.amount: Goods.amount - amount_}).where(Goods.id == id_))
    q.execute()
    update_amount(id_, -amount_)