import random
import nltk
import pyowm

from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer

apiKey = '66243e5a44f3ceeb217716d067fb80b6'

f = open('bot_config.txt', encoding='utf-8')
BOT_CONFIG = eval(f.read())
f.close()


X_text = [] #Список примеров
y = [] #Список интентов
for intent, intent_data in BOT_CONFIG['intents'].items():
        for example in intent_data['examples']:
            X_text.append(example)
            y.append(intent)

vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 3))
X = vectorizer.fit_transform(X_text)
clf = LinearSVC()
clf.fit(X,y)


def clear_phrase(phrase):    
    phrase = phrase.lower()
    
    alphabet = 'абвгдеёжзийклмнопрстуфхчцшщъыьэюя- '
    result = ''.join(symbol for symbol in phrase if symbol in alphabet)
    
    return result.strip()


def classify_intent(replica):
    replica = clear_phrase(replica)
    intent = clf.predict(vectorizer.transform([replica]))[0]
    
    
    for example in BOT_CONFIG['intents'][intent]['examples']:
        example = clear_phrase(example)
        distance = nltk.edit_distance(replica, example)
        if example and distance/len(example) <= 0.5:
            return intent 


def get_answer_by_intent(intent):
    if intent in BOT_CONFIG['intents']:
        responses = BOT_CONFIG['intents'][intent]['responses']
    return random.choice(responses)


with open('dialogues.txt', encoding='utf-8') as f:
    content = f.read()
    
dialogues_str = content.split('\n\n')
dialogues = [dialogues_str.split('\n')[:2] for dialogues_str in dialogues_str]

dialogues_filtered =[]
questions = set()
for dialogue in dialogues:
    if len(dialogue) != 2:
        continue
        
    question, answer = dialogue
    question = clear_phrase(question[2:])
    answer = answer[2:]
    
    if question != '' and question not in questions:
        questions.add(question)
        dialogues_filtered.append([question, answer])

dialogues_structured ={}

for question, answer in dialogues_filtered:
    words = set(question.split(' '))
    for word in words:
        if word not in dialogues_structured:
            dialogues_structured[word] = []
        dialogues_structured[word].append([question, answer])
        
dialogues_structured_cut={}
for word, pairs in dialogues_structured.items():
    pairs.sort(key=lambda pair: len(pair[0]))
    dialogues_structured_cut[word]=pairs[:1000]

        
def genarate_answer(replica):
    replica = clear_phrase(replica)
    words = set(replica.split(' '))
    mini_dataset = []
    for word in words:
        if word in dialogues_structured_cut:
            mini_dataset += dialogues_structured_cut[word]
    
    answers = [] #[[proba, question, answer]]
    
    for question, answer in mini_dataset:
        if abs(len(replica) - len(question)) / len(question) < 0.2:
            distance = nltk.edit_distance(replica, question)
            distance_weighted = distance / len(question)
            if distance_weighted < 0.2:
                answers.append([distance_weighted, question, answer])
    if answers:
        return min(answers, key=lambda three: three[0])[2]


def get_failure_phase():
    failure_phrases = BOT_CONFIG['failure_phrases']
    return random.choice(failure_phrases)

stats = {'intent':0, 'generate':0, 'failure':0}


def bot(replica):
    #NLU
    intent = classify_intent(replica)
    
    #answer generation
    #выбор заготовленной реплики
    if intent:                
        answer = get_answer_by_intent(intent)
        if answer:
            stats['intent'] += 1
            return answer

    #вызов генеративной модели    
    answer = genarate_answer(replica)
    if answer:
        stats['generate'] += 1
        return answer

    #берем заглушку
    stats['failure'] += 1
    return get_failure_phase()


import telebot
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
bot = telebot.TeleBot("1695086032:AAHvXo4YjjBmch1NSEYO_Pcor58FA308BWw")

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def run_bot(update: Update, context: CallbackContext) -> None:
    replica = update.message.text
    #answer = bot(replica)
    
    if classify_intent(replica)=='weather':        
        owm = OWM(apiKey)
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place('Москва')#city)
        w = observation.weather
        temp = w.temperature('celsius')["temp"]        

        answer = f"В городе Москва сейчас {w.detailed_status}\n"
        answer += "Температура сейчас в районе "+ str(temp) + "\n\n"

    update.message.reply_text(answer)
    
    print(stats)
    print(replica)
    print(answer)
    print()
    
def main():
    """Start the bot."""
    updater = Updater("1695086032:AAHvXo4YjjBmch1NSEYO_Pcor58FA308BWw")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, run_bot))

    updater.start_polling()
    updater.idle()


main()










'''
place = input(">> ")

owm = OWM(apiKey)
mgr = owm.weather_manager()
observation = mgr.weather_at_place(place)
w = observation.weather

temp = w.temperature('celsius')["temp"]

#print(w.detailed_status)
print(f"В городе Москва сейчас {w.detailed_status}\n")
print(f"Средняя температура {temp}")
'''

#@bot.message_handler(commands=['city'])
'''
def cmd_city(message):
    send = bot.send_message(message.chat.id, 'Введи город')
    bot.register_next_step_handler(send, city)
    log(message)

def city(message):
    bot.send_message(message.chat.id, 'Ищу погоду в городе {city}'.format(city=message.text))

def city(a):
    print('TYT')
    a = bot.send_message(update.message.chat_id, 'Ищу погоду в городе {city}'.format(city=update.message.text))
    print(a)

cit = ''
send = bot.send_message(update.message.chat_id, 'Введи город')
#print('1- ', send)
bot.register_next_step_handler(send, city(cit))
#log(update.message)
print('2- ', city)
'''
