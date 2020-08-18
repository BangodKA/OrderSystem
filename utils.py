from telebot import types
import views
import telebot
import config
import sys

bot = telebot.TeleBot(config.token)

def add_amount(message, parent_id, name):
    # try:
        amount = int(message.text)
        # views.update_amount(id_, amount)
        id_ = views.add(name, amount, parent_id)
        full_name = views.get_full_name_by_id(id_)
        bot.send_message(message.chat.id, 
                text= '{} {} {} {}'.format('Товар', full_name,
                                'добавлен в количестве', amount))
    # except:
    #     bot.send_message(message.chat.id, text='Invalid amount')


def add_name(message, parent_id):
    name = message.text
    bot.send_message(message.chat.id, text='Введите количество:')
    bot.register_next_step_handler(message, add_amount, parent_id, name)

def change_name (message, id_, old_category):
    name = message.text
    views.update_name(id_, name)
    text= '{} {} {} {}'.format('Товар', old_category,
                        'изменен на', name)
    bot.send_message(message.chat.id, text=text)


def change_amount(message, id_):
    amount = int(message.text)
    views.change(id_, amount)
    full_name = views.get_full_name_by_id(id_)
    text = '{} {} == {}'.format('Новое кол-во товара', full_name, amount)
    bot.send_message(message.chat.id, text=text)


def generate_markup(variants, keyboard_type, stop_button, level):
    markup = types.InlineKeyboardMarkup()

    if (keyboard_type == 'add_item' or level != 1):
        markup.add(types.InlineKeyboardButton(stop_button, callback_data=('_'.join([keyboard_type, str(level), '0']))))

    for item in variants:
        markup.add(types.InlineKeyboardButton('{}::{}'.format(item[0], item[-1]), callback_data=('_'.join([keyboard_type, str(level), str(item[1])]))))
    
    return markup



@bot.callback_query_handler(lambda query: 
                        query.data.startswith('add_item') or
                        query.data.startswith('delete_item') or
                        query.data.startswith('name_item') or
                        query.data.startswith('amount_item'))
def process_callback(query):
    bot.answer_callback_query(query.id, text = None, show_alert = False)
    bot.delete_message(query.message.chat.id, query.message.message_id)

    data = query.data.split(sep='_')
    command = data[0]
    id_ = int(data[-1])
    parent_id = int(data[-2])
    if (id_ != 0):
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

# @bot.message_handler(commands=['rename'])
# def change_username(message):
#     try:
#         views.rename(message.text)
#     except:
#         bot.send_message(message.chat.id, text='Not unique name.')
#     bot.send_message(message.chat.id, text='Your username: ' + config.username)

# –––––––––––––ADMIN––––––––––––

@bot.message_handler(commands=['admin'])
def reg_admin(message):
    if (message.text[7:] == config.password):
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
    properties = config.properties[command]
    all_items = views.get_immed_heirs(level)
    markup = generate_markup(all_items, properties[0], properties[1], level)
    message_ = properties[2] + views.get_full_name_by_id(level)
    bot.send_message(message.chat.id, text=message_, reply_markup=markup)

@bot.message_handler(commands=['add', 'delete', 'name', 'amount'])
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


# –––––––––––––USER–––––––––––––

@bot.callback_query_handler(lambda query: query.data.startswith('order'))
def process_order_callback(query):
    bot.answer_callback_query(query.id, text = None, show_alert = False)
    bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id)
    id_ = int(query.data[-1])
    config.reading_id = id_
    items = views.get_immed_heirs(id_)
    category_name = views.get_item_by_id(id_).name
    config.categories += ':{}:'.format(category_name)
    message_ = query.message.text + config.categories
    config.categories = ''
    if (len(items) != 0):
        config.order_item_status = 0
        markup = generate_markup(items, 'order_', '', 1)
        bot.send_message(query.message.chat.id,
                text=message_,
                reply_markup=markup)
    else:
        text = message_.split(sep='::', maxsplit=1)
        config.full_category = text[1]
        bot.edit_message_text(config.full_category, query.message.chat.id, query.message.message_id)
        config.order_item_status = 1
        bot.send_message(query.message.chat.id, text='Введите количество:')

@bot.message_handler(commands=['start', 'order'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Посмотреть товары', url='https://vk.com/bangod'))
    markup.add(types.InlineKeyboardButton('Перейти к заказу', callback_data=('order_1')))
    bot.send_message(message.chat.id, text='Что вы хотите сделать?', reply_markup=markup)






@bot.message_handler(func=lambda message: True, content_types=['text'])
def process_order(message):
    if (config.order_item_status == 1):
        config.order_item_status = 0
        config.amount = int(message.text)
        try:
            views.buy_item(config.reading_id, config.amount)
            bot.send_message(message.chat.id, 
            text= '{}: {} {} {}'.format('Товар', 
                            config.full_category,
                            'добавлен в количестве', config.amount))
        except:
            print(sys.exc_info()[1])
    else:
        bot.send_message(message.chat.id, text=message.text)