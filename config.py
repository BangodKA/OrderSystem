from tok import token
DATABASE = 'fair.db'

password = '1234'

name = ''
amount = 0

reading_id = 1

order_item_status = 0

full_category = ''

add_properties = ['add_item', 'Новая категория', 'Выберите категорию:']
delete_properties = ['delete_item', 'Удалить категорию', 'Выберите категорию для удаления:']
name_properties = ['name_item', 'Изменить категорию', 'Выберите категорию для изменения:']
change_properties = ['amount_item', 'Изменить категорию', 'Выберите категорию для изменения:']
properties = {
  'add' : add_properties,
  'delete' : delete_properties,
  'name' : name_properties,
  'amount' : change_properties
}