import configparser
import logging

import re
import telegram
from flask import Flask, request

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.ext import Dispatcher, MessageHandler, Filters

# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

token = (config['TELEGRAM']['ACCESS_TOKEN'])
webhook_url = (config['TELEGRAM']['WEBHOOK_URL'])

# Initial bot by Telegram access token
bot = telegram.Bot(token=token)


@app.route('/hook', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'


def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ],
        [InlineKeyboardButton("Option 3", callback_data='3')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'ok'


def button(update: Update, context: CallbackContext):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text="Selected option: {}".format(query.data))
    return 'ok'


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("Use /start to test this bot.")
    return 'ok'


def alert_command(update: Update, context: CallbackContext):
    text = update.message.text.encode('utf-8').decode()
    msg_id = update.message.message_id

    # for debugging purposes only
    print("got text message :", text)

    # check whether the quote can be found
    company = text.replace("/alert", "").trim
    print(company)
    update.message.reply_text("Searching for" + company)
    return 'ok'


def position_command(update: Update, context: CallbackContext):
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'ok'


def reply_handler(bot, update):
    """Reply message."""
    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    msg_id = update.message.message_id
    chat_id = update.message.chat_id
    # for debugging purposes only
    print("got text message :", text)
    if text == "/start":
        # print the welcoming message
        bot_welcome = """
        Welcome to the finance bot.
        """
        # send the welcoming message
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)


    else:
        try:
            # clear the message we got from any non alphabets
            text = re.sub(r"\W", "_", text)
            # create the api link for the avatar based on http://avatars.adorable.io/
            url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
            # reply with a photo to the name the user sent,
            # note that you can send photos by url and telegram will fetch it for you
            bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
        except Exception:
            # if things went wrong
            bot.sendMessage(chat_id=chat_id,
                            text="There was a problem in the name you used, please enter different name",
                            reply_to_message_id=msg_id)
    # update.message.reply_text(text)

    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # we use the bot object to link the bot to our app which live
    # in the link provided by URL
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=webhook_url, HOOK=token))
    # something to let us know things work
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/deletewebhook', methods=['GET', 'POST'])
def delete_webhook():
    s = bot.delete_webhook()
    if s:
        return "webhook delete ok"
    else:
        return "webhook delete failed"


@app.route('/')
def index():
    return '.'


# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_handler(CommandHandler('help', help_command))
dispatcher.add_handler(CommandHandler('alert', alert_command))


if __name__ == "__main__":
    # Running server
    app.run(host='0.0.0.0', port=8443, debug=True)
    # app.run(debug=True)

