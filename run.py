import logging
import os
import redis

from dotenv import load_dotenv
from random import choice
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, CallbackContext, ConversationHandler)

from quiz_content import read_file, get_quiz_content


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

QUESTION, ANSWER = range(2)


def start(update, context):
    quiz_keyboard = [['Новый вопрос', 'Сдаться'],
                     ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(quiz_keyboard)
    message = 'Привет, я QuizBot!'
    update.message.reply_text(message, reply_markup=reply_markup)
    return QUESTION


def handle_input(update, context):
    if update.message.text == 'Новый вопрос':
        quiz_content = dict(get_quiz_content(folder))
        question, answer = choice(list(quiz_content.items()))
        redis_db = context.bot_data['redis']
        chat_id = update.message.chat_id
        redis_db.set(chat_id, question)
        update.message.reply_text(question)
        print(answer)
        return ANSWER


def check_answer(update, context):
    chat_id = update.message.chat_id
    question = context.bot_data['redis'].get(chat_id)
    answer = quiz_content.get(question.decode('utf-8')).lower()
    if update.message.text.lower() == answer:
        update.message.reply_text('Верно! Для продолжения нажми «Новый вопрос»')
        return QUESTION
    update.message.reply_text('Неверно. Попробуй ещё раз')


def give_up(update, context, check_update=False):
    chat_id = update.message.chat_id
    quiz_content = dict(get_quiz_content(folder))
    question = context.bot_data['redis'].get(chat_id)
    answer = quiz_content.get(question.decode('utf-8'))
    reply = f'Правильный ответ - {answer}.\nЧтобы продолжить - нажми «Новый вопрос»'
    context.bot.send_message(chat_id, reply)
    return QUESTION


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    load_dotenv()

    folder = 'questions'
    tg_token = os.getenv('TG_BOT_TOKEN')
    redis_host = os.getenv('REDIS_ENDPOINT')
    redis_port = os.getenv('REDIS_PORT')
    redis_pass = os.getenv('REDIS_PASSWORD')

    quiz_content = dict(get_quiz_content(folder))

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    context = CallbackContext(dispatcher)
    context.bot_data['redis'] = redis.Redis(
        host=redis_host, port=redis_port, db=0, password=redis_pass
    )

    conversation = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            QUESTION: [MessageHandler(Filters.text, handle_input)],
            ANSWER: [
                MessageHandler(Filters.text('Сдаться'), give_up),
                MessageHandler(Filters.text, check_answer),
            ],
        },
        fallbacks=[MessageHandler(Filters.text, error)]
    )
    dispatcher.add_handler(conversation)

    dispatcher.add_error_handler(error)

    updater.start_polling()
