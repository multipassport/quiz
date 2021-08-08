import logging
import os

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


def read_file(filepath):
    with open(filepath, 'r', encoding='KOI8-R') as file:
        return file.read()


def get_quiz_content(folder):
    files = os.listdir(folder)
    for file in files:
        filepath = os.path.join(folder, file)
        file_content = read_file(filepath)
        paragraphs = file_content.split('\n\n')
        questions = [paragraph for paragraph in paragraphs if paragraph.startswith('Вопрос')]
        answers = [paragraph for paragraph in paragraphs if paragraph.startswith('Ответ')]
        yield from zip(questions, answers)


def start(update, context):
    quiz_keyboard = [['Новый вопрос', 'Сдаться'],
                     ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(quiz_keyboard)
    message = 'Привет, я QuizBot!'
    update.message.reply_text(message, reply_markup=reply_markup)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    folder = 'questions'
    quiz_content = dict(get_quiz_content(folder))
    tg_token = os.getenv('TG_BOT_TOKEN')

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))

    dispatcher.add_error_handler(error)

    updater.start_polling()
