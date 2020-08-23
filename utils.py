from telebot import types
import views
import telebot
import config
import sys

import threading

bot = telebot.TeleBot(config.token)

def add_price(message, parent_id, name, amount):
    try:
        price = int(message.text)
        id_ = views.add(name, amount, parent_id, price)
        full_name = views.get_full_name_by_id(id_)
        bot.send_message(message.chat.id, 
                text= '{} {} {} {} {} {}'.format('Товар', full_name, 'стоимостью', price,
                                'добавлен в количестве', amount))
    except ValueError:
        bot.send_message(message.chat.id, text='Введите цену числом!')
        bot.register_next_step_handler(message, add_price, parent_id, name, amount)
    except:
        bot.send_message(message.chat.id, text=sys.exc_info()[1])

def add_amount(message, parent_id, name):
    try:
        amount = int(message.text)
        bot.send_message(message.chat.id, text='Введите цену:')
        # id_ = views.add(name, amount, parent_id)
        # full_name = views.get_full_name_by_id(id_)
        # bot.send_message(message.chat.id, 
        #         text= '{} {} {} {}'.format('Товар', full_name,
        #                         'добавлен в количестве', amount))
        bot.register_next_step_handler(message, add_price, parent_id, name, amount)
    except ValueError:
        bot.send_message(message.chat.id, text='Введите цену числом!')
        bot.register_next_step_handler(message, add_amount, parent_id, name)
    except:
        bot.send_message(message.chat.id, text=sys.exc_info()[1])


def add_name(message, parent_id):
    name = message.text
    bot.send_message(message.chat.id, text='Введите количество:')
    bot.register_next_step_handler(message, add_amount, parent_id, name)

def change_name(message, id_, old_category):
    name = message.text
    views.update_name(id_, name)
    text= '{} {} {} {}'.format('Товар', old_category,
                        'изменен на', name)
    bot.send_message(message.chat.id, text=text)


def change_amount(message, id_):
    try:
        amount = int(message.text)
        views.change(id_, amount)
        full_name = views.get_full_name_by_id(id_)
        text = '{} {}: {}'.format('Новое кол-во товара', full_name, amount)
        bot.send_message(message.chat.id, text=text)
    except:
        bot.send_message(message.chat.id, text='Введите количество числом!')
        bot.register_next_step_handler(message, change_amount, id_)


def generate_markup(variants, keyboard_type, stop_button, level, order_id=''):
    markup = types.InlineKeyboardMarkup()

    for item in variants:
        markup.add(types.InlineKeyboardButton('{}::{} – {} радиан'.format(item[0], item[-2], item[-1]), callback_data=('_'.join([keyboard_type, str(order_id), str(level), str(item[1])]))))
    
    if (keyboard_type == 'order'):
        markup.add(types.InlineKeyboardButton('Отменить выбор', callback_data=('_'.join([keyboard_type, str(order_id), str(level), '-2']))))

    if ((keyboard_type == 'add_item' or keyboard_type == 'items_all' or keyboard_type == 'del_item' or level != 1) and len(stop_button) != 0):
        markup.add(types.InlineKeyboardButton(stop_button, callback_data=('_'.join([keyboard_type, str(order_id), str(level), '0']))))
    
    if (level != 1):
        markup.add(types.InlineKeyboardButton('Назад', callback_data=('_'.join([keyboard_type, str(order_id), str(level), '-1']))))

    return markup



@bot.callback_query_handler(lambda query: 
                        query.data.startswith('add_item') or
                        query.data.startswith('delete_item') or
                        query.data.startswith('name_item') or
                        query.data.startswith('amount_item') or
                        query.data.startswith('items_all'))
def process_callback(query):
    bot.answer_callback_query(query.id, text = None, show_alert = False)
    bot.delete_message(query.message.chat.id, query.message.message_id)

    data = query.data.split(sep='_')
    command = data[0]
    id_ = int(data[-1])
    parent_id = int(data[-2])
    if (id_ == -1):
        higher_id = views.get_prev_level(parent_id)
        process_command(query.message, command, higher_id)
    elif (id_ != 0):
        process_command(query.message, command, id_)
    else:
        if (query.data.startswith('add_item')):
            bot.send_message(query.message.chat.id, 'Введите наименование товара:')
            bot.register_next_step_handler(query.message, add_name, parent_id)
        elif (query.data.startswith('delete_item')):
            category = views.get_full_name_by_id(parent_id)
            views.delete(parent_id)
            bot.send_message(query.message.chat.id, '{} {} {}'.format('Категория', category,  'удалена'))
        elif (query.data.startswith('name_item')):
            category = views.get_full_name_by_id(parent_id)
            bot.send_message(query.message.chat.id, 'Введите новое наименование товара:')
            bot.register_next_step_handler(query.message, change_name, parent_id, category)
        elif (query.data.startswith('amount_item')):
            bot.send_message(query.message.chat.id, 'Введите новое количество товара:')
            bot.register_next_step_handler(query.message, change_amount, parent_id)
        # elif (query.data.startswith('items_all')):
        #     bot.send_message(query.message.chat.id, 'Что еще поделаем?')

# –––––––––––––ADMIN––––––––––––

@bot.message_handler(commands=['admin'])
def reg_admin(message):
    password = views.get_password()
    if (message.text[7:] == password):
        views.reg_admin(message.chat.id)
        bot.send_message(message.chat.id, text='Слушаюсь и повинуюсь, мой господин!')
    else:
        bot.send_message(message.chat.id, text=message.text)

@bot.message_handler(commands=['demote'])
def demote(message):
    if (views.check_id(str(message.chat.id))):
        views.demote_admin(message.chat.id)
        bot.send_message(message.chat.id, text='Теперь Бот свободен!')
    else:
        bot.send_message(message.chat.id, text=message.text)

def process_command(message, command, level):
    add_properties = ['add_item', 'Новая категория', 'Выберите категорию:']
    delete_properties = ['delete_item', 'Удалить категорию', 'Выберите категорию для удаления:']
    name_properties = ['name_item', 'Изменить категорию', 'Выберите категорию для изменения:']
    change_properties = ['amount_item', 'Изменить категорию', 'Выберите категорию для изменения:']
    items_properties = ['items_all', 'Завершить просмотр', 'Категория:']
    properties_ = {
        'add' : add_properties,
        'delete' : delete_properties,
        'name' : name_properties,
        'amount' : change_properties,
        'items' : items_properties,
    }
    properties = properties_[command]
    all_items = views.get_immed_heirs(level)
    if (command != 'add' and level == 1 and len(all_items) == 0):
        bot.send_message(message.chat.id, text='Товаров нет!')
    else:
        markup = generate_markup(all_items, properties[0], properties[1], level)
        message_ = properties[2] + views.get_full_name_by_id(level)
        bot.send_message(message.chat.id, text=message_, reply_markup=markup)

@bot.message_handler(commands=['add', 'delete', 'name', 'amount', 'items'])
def get_command(message):
    if (views.check_id(str(message.chat.id))):
        process_command(message, message.text[1:], 1)
    else:
        bot.send_message(message.chat.id, text=message.text)

@bot.message_handler(commands=['clear'])
def clear(message):
    if (views.check_id(str(message.chat.id))):
        views.clear_base()
        bot.send_message(message.chat.id, text='Товаров нет, но вы держитесь!')
    else:
        bot.send_message(message.chat.id, text=message.text)

@bot.message_handler(commands=['ready'])
def ready(message):
    if (views.check_id(str(message.chat.id))):
        id_ = int(message.text[7:])
        chat_id = views.set_time_order(id_)
        bot.send_message(message.chat.id, text='Заказ собран!')
        text = ' '.join(['Ваш заказ готов. Подойдите в течение 10 минут,',
                    'чтобы оплатить и забрать его, иначе он пропадет.',
                    'На пункте выдачи надо назвать номер заказа.'])
        bot.send_message(chat_id, text=text)
    else:
        bot.send_message(message.chat.id, text=message.text)

@bot.message_handler(commands=['complete'])
def complete(message):
    if (views.check_id(str(message.chat.id))):
        id_ = int(message.text[10:])
        views.complete_order(id_)
        bot.send_message(message.chat.id, text='Заказ выдан!')
    else:
        bot.send_message(message.chat.id, text=message.text)


# –––––––––––––USER–––––––––––––

def process_next_order_step(chat_id, order_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Выбрать другой товар', callback_data='_'.join(['order', str(order_id), '1', '1'])))
    markup.add(types.InlineKeyboardButton('Удалить товар из заказа', callback_data='_'.join(['erase', str(order_id), '1'])))
    markup.add(types.InlineKeyboardButton('Подтвердить заказ', callback_data='_'.join(['finish', str(order_id)])))
    markup.add(types.InlineKeyboardButton('Отменить заказ', callback_data='_'.join(['cancel', str(order_id)])))
    bot.send_message(chat_id, text='Что вы хотите сделать?', reply_markup=markup)

def order_amount (message, id_, name, order_id):
    try:
        amount = int(message.text)
        views.buy_item(id_, amount, order_id)
        bot.send_message(message.chat.id, 
        text= '{} {} {} {}'.format('Товар', 
                        name,
                        'добавлен в количестве', amount))
        process_next_order_step(message.chat.id, order_id)

    except ValueError:
        bot.send_message(message.chat.id, text='Введите количество числом!')
        bot.register_next_step_handler(message, order_amount, id_, name, order_id)
    except OverflowError:
        bot.send_message(message.chat.id, text=sys.exc_info()[1])
        bot.register_next_step_handler(message, order_amount, id_, name, order_id)

def check_timeout():
    message_info = views.check_timestamps()
    for message in message_info:
        text = '{} {} {}'.format('Заказ номер', message[0], 'отменен')
        bot.send_message(message[-1], text=text)
        if (message[1] != -1):
            bot.send_message(message[1], text=text)
    
    threading.Timer(10, check_timeout).start()

@bot.callback_query_handler(lambda query: query.data.startswith('finish'))
def finish_order_callback(query):
    bot.answer_callback_query(query.id, text = None, show_alert = False)
    bot.delete_message(query.message.chat.id, query.message.message_id)

    data = query.data.split(sep='_')
    order_id = int(data[-1])

    order_status = views.check_order(order_id)

    if (order_status == 0):
        admin, order, order_id = views.finish_order(order_id)
        text = '{}: {}!\n{}:\n{}'.format('Номер заказа', order_id, 'Заказ', order)
        bot.send_message(query.message.chat.id, text=text)
        bot.send_message(query.message.chat.id, text='Для отмены заказа введите /cancel')
        bot.send_message(admin, text=text)
    elif (order_status == -1):
        bot.send_message(query.message.chat.id, text='Нельзя создать пустой заказ!')
    else:
        bot.send_message(query.message.chat.id, text='Заказ удален!')
        # start(query.message)
    check_timeout()

@bot.callback_query_handler(lambda query: query.data.startswith('cancel'))
def cancel_processing_order(query):
    bot.answer_callback_query(query.id, text = None, show_alert = False)
    bot.delete_message(query.message.chat.id, query.message.message_id)

    id_ = int(query.data.split('_')[-1])
    if (id_ != 0):
        admin, _ = views.cancel_by_id(id_, query.message.chat.id)
        bot.send_message(query.message.chat.id, text='Заказ отменен!')
        text = '{} {} {}'.format('Заказ номер', id_, 'отменен')
        bot.send_message(admin, text=text)
    else:
        bot.send_message(query.message.chat.id, text='Заказ был пуст!')
        # start(query.message)

def cancel_complete_order(message):
    try:
        id_ = int(message.text)
        admin, chat_id = views.cancel_by_id(id_, message.chat.id)
        text = '{} {} {}'.format('Заказ номер', id_, 'отменен')
        bot.send_message(chat_id, text=text)
        if (admin != -1):
            bot.send_message(admin, text=text)
    except ValueError:
        bot.send_message(message.chat.id, text='Неверный номер')
    except NameError:
        bot.send_message(message.chat.id, text=sys.exc_info()[1])

@bot.message_handler(commands=['cancel'])
def cancel_order_callback(message):
    bot.send_message(message.chat.id, text='Введите номер')
    bot.register_next_step_handler(message, cancel_complete_order)

@bot.callback_query_handler(lambda query: query.data.startswith('del_item'))
def finish_delete_item_processing_order(query):
    bot.answer_callback_query(query.id, text = None, show_alert = False)
    bot.delete_message(query.message.chat.id, query.message.message_id)

    data = query.data.split(sep='_')
    id_ = int(data[-1])
    order_id = int(data[-3])

    if (id_ != 0):
        amount = views.erase_item_order_by_ids(id_, order_id)
        name = views.get_full_name_by_id(id_)
        text = '{} {}::{} {}'.format('Товар', name, amount, 'удален')
        bot.send_message(query.message.chat.id, text=text)

    process_next_order_step(query.message.chat.id, order_id)


@bot.callback_query_handler(lambda query: query.data.startswith('erase'))
def delete_item_processing_order(query):
    bot.answer_callback_query(query.id, text = None, show_alert = False)
    bot.delete_message(query.message.chat.id, query.message.message_id)

    id_ = int(query.data.split('_')[-2])
    order_status = views.check_order(id_)
    if (order_status == 0):
        order_items = views.get_order_items(id_, query.message.chat.id)
        markup = generate_markup(order_items, 'del_item', 'Отменить', 1, id_)
        bot.send_message(query.message.chat.id, text='Что удалить?', reply_markup=markup)
    elif (order_status == -1):
        bot.send_message(query.message.chat.id, text='Заказ был пуст!')
    else:
        bot.send_message(query.message.chat.id, text='Заказ удален!')

@bot.callback_query_handler(lambda query: query.data.startswith('order'))
def process_order_callback(query):
    bot.answer_callback_query(query.id, text = None, show_alert = False)
    bot.delete_message(query.message.chat.id, query.message.message_id)
    data = query.data.split(sep='_')
    id_ = int(data[-1])
    parent_id = int(data[-2])
    order_id = int(data[-3])
    if (views.check_order(order_id) == -2 and order_id != 0):
        bot.send_message(query.message.chat.id, text='Заказ удален!')
    else:
        if (id_ == -2):
            process_next_order_step(query.message.chat.id, order_id)
        else:
            if (id_ == -1):
                id_ = views.get_prev_level(parent_id)
            items = views.get_immed_heirs(id_, False)
            full_category = views.get_full_name_by_id(id_)
            if (len(items) != 0):
                markup = generate_markup(items, 'order', '', id_, order_id)
                bot.send_message(query.message.chat.id,
                        text='Выберите категорию: ' + full_category,
                        reply_markup=markup)
            else:
                if (id_ != 1):
                    try:
                        if (order_id == 0):
                            admin = views.get_admin()
                            order_id = views.add_new_order(query.message.chat.id, admin)
                            text = '{} {} {}'.format('Заказ', order_id, 'начат!')
                            bot.send_message(admin, text=text)
                            bot.send_message(query.message.chat.id, text=text)
                        check_timeout()
                        bot.send_message(query.message.chat.id, text=full_category)
                        bot.send_message(query.message.chat.id, text='Введите количество:')
                        bot.register_next_step_handler(query.message, order_amount, id_, full_category, order_id)
                    except OverflowError:
                        bot.send_message(query.message.chat.id, text=sys.exc_info()[1])
                else:
                    bot.send_message(query.message.chat.id, text='Товаров нет!')

@bot.message_handler(commands=['start', 'order'])
def start(message):
    if (views.check_fair()):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Посмотреть товары', url='https://vk.com/bangod'))
        markup.add(types.InlineKeyboardButton('Перейти к заказу', callback_data=('order_0_0_1')))
        bot.send_message(message.chat.id, text='Что вы хотите сделать?', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text='Магазин не работает')






@bot.message_handler(func=lambda message: True, content_types=['text'])
def process_order(message):
    bot.send_message(message.chat.id, text=message.text)