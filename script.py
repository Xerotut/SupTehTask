import module

user_quantity = None
support_quantity = None


#Функция, которая используется, если нужен имменно int инпут - чтобы узнать сколько сгенерировать пользователей или агентов
#или чтобы получить id нужного польозователя
def get_int_input(exception_text):
    while True:
        input_value = input()
        if input_value == "":
            return None
        try:
            return_value = int(input_value)
            return return_value
        except ValueError:
            print(exception_text) 

#Меню, которое позволяет вводить команды, чтобы выгрузить нужную информацию. 
def commands():
    while True:
        print("Доступны следующие команды:")
        print("get_all_chats - выгружает все сгенерированные чаты")
        print("get_all_users - выгружает всех сгенерированных пользователей")
        print("get_all_sups - выгружает всех сгенерированных операторов поддержки")
        print("get_user_chats - выгружает все чаты пользователя с id, который нужно ввести следующим инпутом")
        print("get_sup_chats - выгружает все чаты оператора поддержки с id, который нужно ввести следующим инпутом")
        command = input()
        match command:
            case "get_all_chats":
                print("Вывожу информацию в консоль и создаю json файл со всеми чатами:")
                module.Platform.export_chats_as_json()
            case "get_all_users":
                print("Вывожу информацию в консоль и создаю json файл со всеми пользователями:")
                module.User.export_profiles_to_json()
            case "get_all_sups":
                print("Вывожу информацию в консоль и создаю json файл со всеми операторами поддержки:")
                module.Support.export_profiles_to_json()
            case "get_user_chats":
                print("Введи id пользователя, чаты которого нужно выгрузить:")
                id = get_int_input("ID является целым числом. Чтобы вернуться к предыдущему шагу, нажми Enter")
                if id:
                    module.User.export_person_chats_to_json(id)
            case "get_sup_chats":
                print("Введи id оператора поддержки, чаты которого нужно выгрузить:")
                id = get_int_input("ID является целым числом. Чтобы вернуться к предыдущему шагу, нажми Enter")
                if id:
                    module.Support.export_person_chats_to_json(id)
            case "":
                break
            case _:
                print("Такой команды нет.")


print("Привет! Введи число пользователей, которое хочешь сгенерировать или нажми Enter, чтобы использовать значение по-умолчанию")
user_quantity = get_int_input("Используй тольько целые числа или нажми Enter, чтобы принять значение по-умолчанию")

print("Отлично, теперь введи количество операторов поддержки или нажми Enter")
support_quantity = get_int_input("Используй тольько целые числа или нажми Enter, чтобы принять значение по-умолчанию")

module.start_emulation(user_quantity, support_quantity)
print("Отлично, эмуляция завершена!")
commands()




