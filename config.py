from tok import token
DATABASE = 'goods.db'

password = '1234'

name = ''
amount = 0
writing_id = 1
reading_id = 1

add_item_status = 0
change_item_status = 0
order_item_status = 0

items_pictures = 'https://vk.com/bangod'

admin_index = -1

categories = ''
full_category = ''

add_properties = ['add_item', 'Новая категория', 'Выберите категорию:']
delete_properties = ['delete_item', 'Удалить категорию', 'Выберите категорию для удаления:']
change_properties = ['change_item', 'Изменить категорию', 'Выберите категорию для изменения:']
properties = {
  'add' : add_properties,
  'delete' : delete_properties,
  'change' : change_properties
}