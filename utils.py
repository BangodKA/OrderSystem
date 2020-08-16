from telebot import types
import views
import telebot
import config
import sys

bot = telebot.TeleBot(config.token)

def generate_markup(variants, keyboard_type, stop_button, level):
    markup = types.InlineKeyboardMarkup()

    if (keyboard_type == 'add_item' or level != 1):
        markup.add(types.InlineKeyboardButton(stop_button, callback_data=(keyboard_type + '0')))

    for item in variants:
        markup.add(types.InlineKeyboardButton('{}::{}'.format(item[0], item[-1]), callback_data=(keyboard_type + str(item[1]))))
    
    return markup

@bot.callback_query_handler(lambda query: 
                        query.data.startswith('add_item') or
                        query.data.startswith('delete_item') or
                        query.data.startswith('change_item'))
def process_callback(query):
    bot.answer_callback_query(query.id, text = None, show_alert = False)
    bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id)


    config.add_item_status = 0
    config.change_item_status = 0
    if (query.data[-1] != '0'):
        bot.delete_message(query.message.chat.id, query.message.message_id)
        id_ = int(query.data[-1])
        category_name = views.get_name_by_id(id_)
        config.categories += ':{}:'.format(category_name)
        command = query.data.split(sep='_')[0]
        process_command(query.message, command, id_)
    else:
        text = query.message.text.split(sep='::', maxsplit=1)
        if (len(text) <= 1):
            text = 'Базовая категория'
        else:
            text = text[1]
        bot.edit_message_text(text, query.message.chat.id, query.message.message_id)
        if (query.data.startswith('add_item')):
            config.add_item_status = 1
            bot.send_message(query.message.chat.id, 'Введите наименование товара:')
        elif (query.data.startswith('delete_item')):
            views.delete(config.writing_id)
            bot.send_message(query.message.chat.id, '{} {} {}'.format
                                            ('Категория', text, 'удалена'))
            bot.delete_message(query.message.chat.id, query.message.message_id)
        elif (query.data.startswith('change_item')):
            config.change_item_status = 1
            id_ = int(query.data[-1])
            bot.send_message(query.message.chat.id, 'Введите новое наименование товара:')

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
    config.writing_id = level
    all_items = views.get_immed_heirs(level)
    markup = generate_markup(all_items, properties[0], properties[1], level)
    message_ = properties[2] if level == 1 else message.text + config.categories
    config.categories = ''
    bot.send_message(message.chat.id, 
            text=message_,
            reply_markup=markup)

@bot.message_handler(commands=['add', 'delete', 'change'])
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


@bot.message_handler(func=lambda message: views.check_id(message.chat.id), content_types=['text'])
def process_text(message):
    if (config.add_item_status == 1):
        config.add_item_status = 2
        config.name = message.text
        bot.send_message(message.chat.id, text='Введите количество:')
    elif (config.add_item_status == 2):
        config.add_item_status = 0
        config.amount = int(message.text)
        parent_name = views.add(config.name, config.amount, config.writing_id)
        bot.send_message(message.chat.id, 
        text= '{}: {}({})::{}'.format('Добавлен товар', config.name, parent_name, config.amount))

    elif (config.change_item_status == 1):
        config.change_item_status = 2
        config.name = message.text
        bot.send_message(message.chat.id, text='Введите новое количество:')
    elif (config.change_item_status == 2):
        config.change_item_status = 0
        config.amount = int(message.text)
        prev_item = views.change(config.name, config.amount, config.writing_id)
        parent_name = views.get_name_by_id(prev_item.parent_id)
        bot.send_message(message.chat.id, 
        text= '{}: {}({})::{} {} {}({})::{}'.format('Товар изменен c', 
                        prev_item.name, parent_name, prev_item.amount,
                        'на', config.name, parent_name, config.amount))

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
    category_name = views.get_name_by_id(id_)
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
    markup.add(types.InlineKeyboardButton('Посмотреть товары', url=config.items_pictures))
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