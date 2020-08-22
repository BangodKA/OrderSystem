from models import database, Goods, Admins, Orders_Info, Orders_Content
from random import choice, seed
import config
from datetime import datetime
import time

def create_tables():
    database.connect()
    database.create_tables([Goods, Admins, Orders_Info, Orders_Content], safe=True)
    Goods.create(name = '.BASE_CAT', amount = 0)
    brcls = Goods.create(name = 'Браслеты', amount = 100, parent_id = 1)
    pins = Goods.create(name = 'Значки', amount = 75, parent_id = 1)
    Goods.create(name = 'Кружки', amount = 150, price = 100, parent_id = 1)
    Goods.create(name = 'Синие', amount = 50, price = 10, parent_id = brcls)
    Goods.create(name = 'Красные', amount = 36, price = 15, parent_id = brcls)
    Goods.create(name = 'Желтые', amount = 14, price = 20, parent_id = brcls)
    Goods.create(name = 'Жестяные', amount = 30, price = 17, parent_id = pins)
    Goods.create(name = 'Деревянные', amount = 45, price = 13, parent_id = pins)
    Admins.create(chat_id='1234')
    database.close()

# –––––––––––––ADMIN––––––––––––

def get_password():
    password = Admins.select().where(Admins.id == 1)[0]
    return password.chat_id

def reg_admin(chat_id):
    admin = Admins.select().where(Admins.chat_id == chat_id)
    if (not admin.exists()):
        Admins.create(chat_id = chat_id)

def demote_admin(chat_id):
    query = Admins.delete().where(Admins.chat_id == chat_id)
    query.execute()

def get_admin():
    admins = Admins.select().where(Admins.id != 1)
    if (not admins.exists()):
        raise OverflowError('Магазин закрыт!')
    chat_ids = [admin.chat_id for admin in admins]
    chat_id = choice(chat_ids)
    return chat_id
    

def check_id(chat_id):
    admins = Admins.select()
    chat_ids = [admin.chat_id for admin in admins]
    return chat_id in chat_ids

def update_amount(id_, amount_):
    item = Goods.select().where(Goods.id == id_)[0]
    query = Goods.update({Goods.amount : Goods.amount + amount_}).where(Goods.id == id_)
    query.execute()
    if (item.parent_id != None):
        update_amount(item.parent_id, amount_)

def update_name(id_, name):
    Goods.select().where(Goods.id == id_)[0]
    query = Goods.update({Goods.name : name}).where(Goods.id == id_)
    query.execute()

def get_full_name_by_id(id_):
    if id_ == 1:
        return ''
    item = Goods.select().where(Goods.id == id_)
    if (item[0].parent_id.id != 1):
        res = '{}::{}'.format(get_full_name_by_id(item[0].parent_id), item[0].name)
    else:
        res = item[0].name
    return res

def add(name_, amount_, parent_id_, price_):
    item = Goods.create(name = name_, amount = amount_, price = price_, parent_id = parent_id_)
    if (amount_ != 0 and parent_id_ == 1):
        update_amount(item.parent_id, amount_)
    return item.id

def change(id_, amount_):
    item = Goods.select().where(Goods.id == id_)[0]
    query = Goods.update({Goods.amount : amount_}).where(Goods.id == id_)
    query.execute()
    amount = amount_ - item.amount
    if (amount_ != 0):
        update_amount(item.parent_id, amount)
    return item

def get_item_by_id(id_):
    item = Goods.select().where(Goods.id == id_)
    return item[0]

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
    query = Goods.update({Goods.amount: 0}).where(Goods.id == 0)
    query.execute()
    query = Orders_Info.delete().where(Orders_Info.id > 0)
    query.execute()
    query = Orders_Content.delete().where(Orders_Content.id > 0)
    query.execute()

def check_fair():
    admins = Admins.select().where(Admins.id != 1)
    if (admins.exists()):
        return True
    return False


# –––––––––––––USER–––––––––––––

def get_prev_level(id_):
    item = Goods.select().where(Goods.id == id_)
    return item[0].parent_id.id

def get_immed_heirs(parent_id, admin=True):
    items = Goods.select().where(Goods.parent_id == parent_id)
    res = [[item.name, item.id, item.amount, item.price] for item in items if item.amount > 0 or admin]
    return res

def buy_item(id_, amount_, order_id):
    item = Goods.select().where(Goods.id == id_)[0]
    if (item.amount < amount_):
        raise OverflowError(' '.join(['Этого товара осталось всего', str(item.amount), '\nВведите другое количество']))
    if (amount_ <= 0):
        raise OverflowError('\n'.join(['Число товаров должно быть натуральным', 'Введите другое количество']))
    
    price = Goods.select().where(Goods.id == id_)[0].price
    same_item = Orders_Content.select().where(
        (Orders_Content.order_id == order_id) & (Orders_Content.item_id == id_))
    if same_item.exists():
        query = Orders_Content.update({Orders_Content.amount : Orders_Content.amount + amount_,
                                        Orders_Content.cost : Orders_Content.cost + amount_ * price}).where(
            (Orders_Content.order_id == order_id) & (Orders_Content.item_id == id_))
        query.execute()
    else:
        Orders_Content.create(order_id=order_id, item_id=id_, amount=amount_, cost = price * amount_)

    query = Orders_Info.update({Orders_Info.time : time.time()}).where(Orders_Info.id == order_id)
    query.execute()
    
    update_amount(id_, -amount_)

def add_new_order(chat_id, admin):
    item = Orders_Info.create(chat_id=chat_id, admin=admin,
                                time=time.time(), status='CREATE')
    return item.id

def finish_order(order_id):
    query = Orders_Info.update({Orders_Info.time : time.time(), Orders_Info.status : 'PROCESS'}).where(Orders_Info.id == order_id)
    query.execute()

    order_content = Orders_Content.select().where(Orders_Content.order_id == order_id)

    order = '\n'.join(['{}::{} – {} радиан'.format(get_full_name_by_id(inst.item_id), inst.amount, inst.cost) for inst in order_content])
    
    order_info = Orders_Info.select().where(Orders_Info.id == order_id)
    return order_info[0].admin, order, order_id

def check_timestamps():
    time_ = time.time()

    canceled_orders = Orders_Info.select().where(
        Orders_Info.status == 'CREATE').where(time_ - Orders_Info.time > 10)
    not_finished_orders = Orders_Info.select().where(
        Orders_Info.status == 'AWAIT').where(time_ - Orders_Info.time > 10)

    message_info = []
    for c_order in canceled_orders:
        items = Orders_Content.select().where(Orders_Content.order_id == c_order.id)
        for item in items:
            update_amount(item.item_id, item.amount)

        message_info.append([c_order.id, c_order.admin, c_order.chat_id])

    for nf_order in not_finished_orders:
        items = Orders_Content.select().where(Orders_Content.order_id == nf_order.id)
        for item in items:
            update_amount(item.item_id, item.amount)

        message_info.append([nf_order.id, -1, nf_order.chat_id])

    query = Orders_Info.update({Orders_Info.status : 'DEL'}).where(
        (Orders_Info.status == 'AWAIT') | (Orders_Info.status == 'CREATE')).where(time_ - Orders_Info.time > 10)
    query.execute()

    return message_info

def cancel_by_id(id_, chat_id):
    order = Orders_Info.select().where((Orders_Info.id == id_) & (Orders_Info.chat_id == chat_id))
    if not order.exists():
        raise NameError('Не ваш заказ, ая-яй-яй!')
    query = Orders_Info.update({Orders_Info.status : 'DEL'}).where(Orders_Info.id == id_)
    query.execute()
    items = Orders_Content.select().where(Orders_Content.order_id == id_)
    for item in items:
        update_amount(item.item_id, item.amount)

    return order[0].admin, order[0].chat_id

def get_order_items(id_, chat_id):
    order = Orders_Info.select().where((Orders_Info.id == id_) & (Orders_Info.chat_id == chat_id))
    if not order.exists():
        raise NameError('Не ваш заказ, ая-яй-яй!')
    items = Orders_Content.select().where(Orders_Content.order_id == order[0].id)
    return [[get_full_name_by_id(item.item_id), item.item_id, item.amount] for item in items]

def erase_item_order_by_ids(id_, order_id):
    item = Orders_Content.select().where(Orders_Content.item_id == id_).where(Orders_Content.order_id == order_id)
    amount = item[0].amount
    update_amount(id_, amount)
    query = Orders_Content.delete().where(Orders_Content.item_id == id_).where(Orders_Content.order_id == order_id)
    query.execute()
    return amount

def set_time_order(id_):
    query = Orders_Info.update({Orders_Info.status : 'AWAIT', Orders_Info.time : time.time()}).where(Orders_Info.id == id_)
    query.execute()
    order = Orders_Info.select().where(Orders_Info.id == id_)
    return order[0].chat_id

def complete_order(id_):
    query = Orders_Info.update({Orders_Info.status : 'COMPLETE'}).where(Orders_Info.id == id_)
    query.execute()


def check_order(order_id):
    items = Orders_Content.select().where(Orders_Content.order_id == order_id)
    if (items.exists()):
        return True
    query = Orders_Info.update({Orders_Info.status : 'DEL'}).where(Orders_Info.id == order_id)
    query.execute()
    return False