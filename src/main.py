from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove, Update,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    CommandHandler, CallbackContext,
    ConversationHandler, MessageHandler,
    Filters, Updater, CallbackQueryHandler
)

# Define Options
CHOOSING, CLASS_STATE, SME_DETAILS, CHOOSE_PREF, \
    SME_CAT, ADD_PRODUCTS, SHOW_STOCKS, POST_VIEW_PRODUCTS = range(8)


from telegram.ext import *
import random
import json
import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

from ProductRequests import *
import Constans as keys
import Responses as Resp
import handlers

print("Bot is starting...")

isInventory = False

def start_command(update, context: CallbackContext) -> int:
    bot = context.bot
    chat_id = update.message.chat.id
    bot.send_message(chat_id=chat_id, text="Hola, soy un bot de prueba")
    return CHOOSING


def help_command(update, context):
    update.message.reply_text("Ask Google!\n")

#esta funcion es para manejar los mensajes del cliente. implementa NLP y tiene una serie de respuestas entrenadas dependiendo lo que pida el cliente
def handle_message(update, context: CallbackContext) -> int:
    bot = context.bot
    chat_id = update.message.chat.id
    user_message = update.message.text
    user_message = tokenize(user_message)

        
    X = bag_of_words(user_message, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    # print(prob.item())
    if prob.item() > 0.65:
        #ideas para el futuro
        # ya se mas o menos lo que hare, pues implementare respuestas personalizadas para las preguntas abiertas y para preguntas relacionadas con el inventario voy a hacer procesos para responder de manera certera.
        for intent in intents['intents']:
            if tag == intent["tag"]:
                if tag == "inventory":
                    bot.send_message(chat_id=chat_id, text="Hola, para comenzar escribe tu nombre, email y telefono en ese orden y separado por comas (,)")
                    return CHOOSING
                    # ProductRequests = ProductRequests(1, 1)
                bot.send_message(chat_id=chat_id, text=random.choice(intent['responses']))
    else:
        for intent in intents['intents']:
            if intent["tag"] == "noanswer":
                bot.send_message(chat_id=chat_id, text=random.choice(intent['responses']))

    return CHOOSING

#esta funcion muestra errores en consola
def errors(update, context):
    """Log Errors caused by Updates.""" 
    print('Update "{}" caused error "{}"'.format(update, context.error))
    # logger.warning('Update "%s" caused error "%s"', update, context.error)


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

#Esta parte trae los datos resultantes de haber entrenado el bot con el Json de entrenamiento 
FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

# Aqui estamos inicialdo el bot de telegram pasandole las credenciales
updater = Updater(keys.BOT_API_KEY, use_context=True)
dp = updater.dispatcher

def main():

    # dp.add_handler(CommandHandler("start", start_command))
    # dp.add_handler(CommandHandler("help", help_command))
    # dp.add_handler(CommandHandler("productos", products_command))
    # dp.add_handler(CommandHandler("exit", exit_command))
    

    # dp.add_handler(MessageHandler(Filters.text, handle_message))

    # dp.add_error_handler(errors)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handlers.start_command)],
        states={
            handlers.CHOOSING: [
                MessageHandler(
                    Filters.all, handlers.handleMesages
                )
            ],
            handlers.CLASS_STATE: [
                CallbackQueryHandler(handlers.classer)
            ],
            handlers.SHOW_STOCKS: [
                CallbackQueryHandler(handlers.showProduct)
            ],
            handlers.ADD_PRODUCTS: [
                CallbackQueryHandler(handlers.addProductToCart)
            ]
        },
        fallbacks=[CommandHandler('cancel', handlers.cancel)],
        allow_reentry=True
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()