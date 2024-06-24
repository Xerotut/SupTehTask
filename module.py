from datetime import datetime, timedelta
from random import randint, choice, sample, choices
from collections import deque
import random_data
from math import floor
import json

"""
Эмуляция происходит за счёт класса Time, который эмулирует течение времени. 
Так как в задании было сказано, что нужно хранить время отправки сообщений, а чаты назначаются на "свободных" операторов, необходимо как-то 
отслеживать, сколько у операторов уходит времени на каждый ответ, и когда пользователи отправляют сообщения. Я стремился к тому, чтобы сущности 
выполняли только те действия, которые присущи им - то есть, например, платформа не может заставить оператора ответить или пользователя поставить оценку.
Поэтому нужен был какой-то внешний фактор, от которого они бы все могли отталкиваться. 
Эмуляция течения времени показалась мне подходящим способом. 
"""
#Используется пользователями, чтобы решить, будут они ставить ксат или нет. 
def roll(succes_chance=50):
    if randint(1,100)<=succes_chance:
        return True 
    else:        
        return False

#Функция, которая берёт лист объектов, запрашивает репрезентацию этого объекта в виде словаря (у объекта должна быть функция to_dict), печатает этот словарь
#и после этого экспоритрует все объекты в json файл. Конечно, если нужно выгрузить не просто однотипную информацию - например, если нужно выгрузить не просто чаты какого-то
# пользователя, а ещё и информацию о самом пользователе в рамках одного запроса - это работать не будет
def export_as_json(exporting_elements, filename):
    all_elements_as_dicts =[]
    for element in exporting_elements:
        element_as_dict = element.to_dict()
        print(element_as_dict)
        all_elements_as_dicts.append(element_as_dict)
    with open(filename, 'w') as f:
        json.dump(all_elements_as_dicts, f,indent=4, ensure_ascii=False, default=str)

#Класс, от которого наследуют пользователи и операторы поддержки. 
class Person:

    def __init__(self, id, name, family_name, surname, city, date_of_birth):
        self.id = id
        self.name = name
        self.family_name = family_name
        self.surname = surname
        self.city = city
        self.date_of_birth = date_of_birth
        self.chats = []

    def send_message(self, message_text, chat = None):
        pass

#Используется для выгрузки профилей в json. так как мы нигде не печатаем класс отдельно, это имеет больше смысла, чем __str__ 
    def to_dict(self):
        full_name = f"{self.name} {self.family_name} {self.surname}"
        return {
            "id": self.id,
            "name": full_name,
            "city_of_residence": self.city,
            "date_of_birth": self.date_of_birth
        }
    
    @staticmethod
    def export_profiles_to_json(list_of_profiles, filename):
        export_as_json(list_of_profiles, filename)

    @staticmethod
    def export_person_chats_to_json(id, person_list, filename):
        person = None
        try:
            person = person_list[id]
        except IndexError:
            print("Человека с таким id не существует :О")
        else:
            export_as_json(person.chats, filename)
    
 
#Пользователи. в задании было сказано, что чаты создают пользователи, но я не был уверен, насколько это железобетонное требование - мне показалось, что,
#раз платформа управляет чатами, было бы логичнее чтобы пользователь отправлял запрос платформе, а уже она создавла чат
class User(Person):

    def __init__(self,name, family_name, surname, city, date_of_birth):
        id = len(User.users)
        super().__init__(id, name, family_name, surname, city, date_of_birth)
        User.users.append(self)

    users =[]

    """
    Пользователь направляет запрос на создание чата, когда отправляет сообщение. 
    Полсле этого каждую секунду (симулируемую) пользователь проверяет, пришёл ли ответ - со временем ему может надоесть, и он перестанет следить. 
    Если пользователь всё ещё следит, когда ответ получен, он может поставить ксат. Его усидчивость и вероятность поставить csat определяются рандомно 
    с помощью функцции roll в начале модуля. 
    Я видел два альтернативных способа сделать так, чтобы пользователь ставил (или принимал решение не ставить) ксат, когда появлялся ответ - либо 
    rate_chat должен был вызываться платформой для чатов, либо он должен был как-то подписываться на функцию, закрывающую чат или отправляющую сообщение. 
    Первый способ мне не нравится, потому что, как я говорил выше, я стремился к тому, чтобы все сущности делали только то, что присуще им - а платформа
    не имеет никакого отношения к тому, поставит пользователь оценку или нет. Ивентов в питоне нет, так что мне бы пришлось пытаться сделать их своими силами - поэтому
    я решил, что в рамках поставленной задачи использовать Time будет достаточно.
    """
    def send_message(self, message_text):
        chat = Platform.create_chat(self, message_text)
        self.chats.append(chat)
        Time.subscribe_to_time(Time.simulated_time+1, self.check_chat, chat)

    def check_chat(self, chat):
        if chat._is_open and roll(90):
            Time.subscribe_to_time(Time.simulated_time+1, self.check_chat, chat)
        elif roll(70):
            self.rate_chat(chat)
        
    def rate_chat(self,chat):
        chat.csat = randint(1,5)
    
    @staticmethod
    def export_profiles_to_json():
        Person.export_profiles_to_json(User.users, "Users.json")
    
    @staticmethod
    def export_person_chats_to_json(id):
        Person.export_person_chats_to_json(id, User.users, f"User{id}Chats.json")

#Агенты поддержки
class Support(Person):
 
    def __init__(self, name, family_name, surname, city, date_of_birth, job_title, length_of_service):
        id = len(Support.supports)
        super().__init__(id, name, family_name, surname, city, date_of_birth)
        self.job_title = job_title
        self.length_of_service = length_of_service
        self.current_chat = None
        Support.supports.append(self)
        
    supports=[]
    #Эта функция используется в начале симуляции, чтобы подготовить всех агентов, а также во время её течениея - таким образом агенты говорят платформе, что они готовы принимать чаты.
    #В более сложной симуляции агенты могли бы приходить на смену во время её течения. 
    def prepare_for_work(self):
        Platform.support_ready(self)

    #Эта функция использутся платформой, чтобы передать чат агенту. 
    #Время, которое нужно агенту, чтобы дать ответ, определяется случайным образом. 
    #После этого функция отправки сообщения подписывается на соответствующей момент времени - агент ответит, когда он наступит.
    def get_chat(self, chat):
        self.chats.append(chat)
        self.current_chat = chat
        time_required = randint(1,10)
        Time.subscribe_to_time(Time.simulated_time+time_required, self.send_message)
    #Так как отношения агентов с чатом ближе, чем у пользователей, они добавляют сообщения в чат и закрывают его напрямую, а не через платформу.
    def send_message(self):
        self.current_chat.add_message(choice(random_data.answers))
        self.close_current_chat()
    #Агент закрывает чат и говорит платформе, что он готов принимать следующий
    def close_current_chat(self):
        self.current_chat.close_chat()
        Platform.support_ready(self)

    def to_dict(self):
        sup_dict = super().to_dict()
        sup_dict["job_title"] = self.job_title
        sup_dict["length_of_service"] = self.length_of_service
        return sup_dict

    @staticmethod
    def export_profiles_to_json():
        Person.export_profiles_to_json(Support.supports, "SupportAgents.json")
    
    @staticmethod
    def export_person_chats_to_json(id):
        Person.export_person_chats_to_json(id, Support.supports, f"SupportAgent{id}Chats.json")
 

#Как было сказано выше, этот класс используется для симуляции течения времени. 
class Time:
    #Для точки отсчёта используется настоящий   
    real_time = datetime.now()
    #Измеряется в секундах
    simulated_time = 0

    subscribers = {}

    #Каждую виртуальную секунду вызываются все функции, которые должны быть вызваны в этот момент времени, после чего 
    #время двигается на 1 секунду вперёд
    @staticmethod
    def pass_time():
        Time.fire_event(Time.simulated_time)
        Time.simulated_time+=1
    
    #Функция, которая используется, чтобы подписать другую функцию на какой-то момент времени. 
    #Словарь subscribers - это словарь, где ключи это секунды, а значения - лист, состоящий из подписывающей функции, а также её параметров при вызове
    @staticmethod
    def subscribe_to_time(time, subscriber, *args, **kwargs):
        if time not in Time.subscribers:
            Time.subscribers[time] =[]
        Time.subscribers[time].append((subscriber, args, kwargs))

    #Функция проверяет, подписаны ли на эту секунду какие-то функции, и если да, она вызывает их
    @staticmethod
    def fire_event(time):
        if time in Time.subscribers:
            for subscriber, args, kwargs in Time.subscribers[time]:
                subscriber(*args, **kwargs)


#Чаты. Ими управляет платформа для чатов и немного агенты. 
class Chat:
    chats = []
    def __init__(self, user, first_message):
        self.id = len(Chat.chats)
        self.csat = None
        self.user = user
        self.support = None
        self._is_open = True
        self._messages = []
        self.add_message(first_message)

#Для времени, когда сообщение было отправлено, используется точка отсчёта + прошедшее виртуальное время (в секундах)
    def add_message(self, text):
        time = Time.real_time + timedelta(seconds = Time.simulated_time)
        time = time.strftime("%x %X")
        message = {
        "time_sent": time,
        "text": text
        }
        self._messages.append(message)

#Различные события могут быть связаны с закрытием чата, поэтому это реализовано с помощью функции, а не делается другими сущностями напрямую. 
#Я не захотел использовать сеттер, потому что close_chat лучше передаёт суть происходящего, чем chat.is_open=false (если бы это вызывало какие-то другие события,
#то такой подход делал бы их потенциальное наличие более явным)
    def close_chat(self):
        self._is_open = False
#На некоторые чаты может быть не назначен агент поддержки, поэтому нужно это учесть при конвертации в словарь
    def to_dict(self):
        support_id = "not_assigned"
        messages_info ={}
        for message in self._messages:
            messages_info[self._messages.index(message)] = message
        if self.support:
            support_id = self.support.id
        return {
            "chat_id": self.id,
            "csat": self.csat,
            "user_id": self.user.id,
            "support_id": support_id,
            "is_closed": not self._is_open,
            "messages_info": messages_info
        }

  
#Платформа для чатов
class Platform:
    
    #В задании было сказано, что чаты назначаются на случайного свободного агента, поэтому для хранения свободных агентов я использую лист. 
    #Про чаты ничего сказано не было, поэтому для них я использую очередь 
    _unhandled_chats = deque()
    _free_supports=[]

#Эта функция вызывается когда создаётся новый чат и когда освобождается агент - она назначает чаты из очереди, если они есть, свободным агентам.
    @staticmethod
    def look_for_free_supports():
        if Platform._unhandled_chats:
            try:
                support = choice(Platform._free_supports)
            except IndexError:
                print("All supports are busy!")
            else:
                chat = Platform._unhandled_chats.popleft()
                chat.support = support
                Platform._free_supports.remove(support)
                Support.get_chat(support, chat)
  
#Эта функция используется агентами, чтобы сообщить платформе, что он закончил с чатом и готов к работе
    @staticmethod
    def support_ready(support):
        Platform._free_supports.append(support)
        Platform.look_for_free_supports()

#Эта функция исползуется пользователями, чтобы создавать чаты. Как я сказал выше, мне показалось логичнее, что в таком случае
#пользователи лишь отправляют запрос, а чат создаёт платформа. Пользователи всё ещё сами назначают на себя чат (ну то есть, сущность пользователя назначает его на себя) 
    @staticmethod
    def create_chat(user,first_message):
        new_chat = Chat(user,first_message)
        Chat.chats.append(new_chat)
        Platform._unhandled_chats.append(new_chat)
        Platform.look_for_free_supports()
        return new_chat
    
    @staticmethod
    def export_chats_as_json():
        export_as_json(Chat.chats, "Chats.json")
       
def generate_name():
    gender = "m" if roll() else "f"
    full_name = random_data.generate_random_name(gender)
    return full_name
   
#Фукнции, которые генерируют нужное количество пользователей и сапортов. Для атрибутов используют случайные значения из заранее заготовленных листов. 
#Гендер хранить не нужно, но он нужен, чтобы сгенерировать нормальное имя.
def generate_users(n):
    for _ in range(n):
        full_name = generate_name()
        User(full_name[0], full_name[1], full_name[2], choice(random_data.cities), random_data.generate_random_date())
def generate_supports(n):
    for _ in range(n):
        #Агентов L1 больше, чем агентов L2, так что мы используем отразим это при генерации должностей
        title = choices(random_data.jod_titles, [10,1])
        full_name = generate_name()
        Support(full_name[0], full_name[1], full_name[2], choice(random_data.cities), random_data.generate_random_date(), 
                title, random_data.generate_length_of_service())

#Фунция, которая вызывается каждую виртуальную секунду и случайным образом определяет, какое количество пользователей напишет сообщение в чат. 
#В текущем виде приводит к тому, что количество чатов неумолимо увеличивается - этого достаточно для симуляции отношений между тремя сущностями, 
#но не очень реалистично. 
def generate_chats():
    number_of_sending_users = randint(0, floor(len(User.users) * 0.1))
    sending_users = sample(User.users, number_of_sending_users)
    for user in sending_users:
        Time.subscribe_to_time(Time.simulated_time + randint(0,100), user.send_message, choice(random_data.questions))
    Time.subscribe_to_time(Time.simulated_time+1, generate_chats)

#Функция, которая используется, чтобы начать симуляцию. Скриптом используется только она и функции для выгрузки json
def start_emulation(users_to_generate=None, supports_to_generate=None):
    generate_users(users_to_generate) if users_to_generate else generate_users(randint(25,50))
    generate_supports(supports_to_generate) if supports_to_generate else generate_supports(randint(5,10))

    Time.subscribe_to_time(Time.simulated_time, generate_chats)

#В начале симуляции агенты говорят платформе, что они готовы к работе. В более сложной симуляции у них может быть разное время, когда они приступают к работе, так что подобный 
#подход оставляет простраство для расширения функционала 
    for support in Support.supports:
        support.prepare_for_work()

#Симуляция продолжает работать, пока создано меньше 100 чатов. Не все из них будут закрытыми, но, так как они назначаются из очереди, незакрытыми будут те, 
#которые были сгенерированы позже, так как на них просто не успели ответить к моменту завершения симуляции. Всего чатов может быть сгенерировано и больше 100, если 
#в последний тик времени будет сгенерировано сразу несколько чатов. Технически все условия задания выполнены, но, понятное дело, что функционал можно менять - 
#например, сделать желаемое количество генерируемых чатов одним из возможных параметров для функции эмуляции. 
    while len(Chat.chats)<100:
        Time.pass_time()

    


    
    
   
    
