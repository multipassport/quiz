import logging
import os
import redis

from dotenv import load_dotenv
from random import choice
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, CallbackContext, ConversationHandler)

from quiz import get_quiz_content


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger('quiz')

QUESTION, ANSWER = range(2)


def start(update, context):
    quiz_keyboard = [['Новый вопрос', 'Сдаться'],
                     ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(quiz_keyboard)
    message = 'Привет, я QuizBot!'
    update.message.reply_text(message, reply_markup=reply_markup)
    return QUESTION


def handle_input(update, context):
    chat_id = update.message.chat_id

    quiz_content = context.bot_data['quiz']
    redis_db = context.bot_data['redis']

    question, answer = choice(list(quiz_content.items()))
    redis_db.set(chat_id, question)
    update.message.reply_text(question)

    return ANSWER


def check_answer(update, context):
    chat_id = update.message.chat_id
    redis_db = context.bot_data['redis']
    question = redis_db.get(chat_id)
    quiz_content = context.bot_data['quiz']

    answer = quiz_content.get(question.decode('utf-8')).lower()
    if update.message.text.lower() == answer:
        update.message.reply_text('Верно! Для продолжения нажми «Новый вопрос»')
        redis_db.delete(chat_id)
        return QUESTION

    update.message.reply_text('Неверно. Попробуй ещё раз')


def give_up(update, context):
    chat_id = update.message.chat_id

    quiz_content = context.bot_data['quiz']
    redis_db = context.bot_data['redis']

    question = redis_db.get(chat_id)
    answer = quiz_content.get(question.decode('utf-8'))
    redis_db.delete(chat_id)

    reply = f'Правильный ответ - {answer}.\nЧтобы продолжить - нажми «Новый вопрос»'
    context.bot.send_message(chat_id, reply)

    return QUESTION


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def run_bot(tg_token, redis_db, quiz_content):
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    context = CallbackContext(dispatcher)
    context.bot_data['redis'] = redis_db

    context.bot_data['quiz'] = quiz_content

    conversation = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            QUESTION: [
                MessageHandler(Filters.text('Новый вопрос'), handle_input)
            ],
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


def main():
    load_dotenv()

    tg_token = os.getenv('TG_BOT_TOKEN')
    redis_host = os.getenv('REDIS_ENDPOINT')
    redis_port = os.getenv('REDIS_PORT')
    redis_pass = os.getenv('REDIS_PASSWORD')

    redis_db = redis.Redis(
        host=redis_host, port=redis_port, db=0, password=redis_pass
    )
    quiz_content = dict(get_quiz_content(folder='questions'))

    run_bot(tg_token, redis_db, quiz_content)


if __name__ == '__main__':
    main()
