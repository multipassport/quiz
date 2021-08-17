import logging
import os
import redis
import vk_api

from dotenv import load_dotenv
from random import choice
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from log_handler import TelegramBotHandler
from quiz import get_quiz_content

logger = logging.getLogger('quiz')


def send_message(event, vk, message, keyboard):
    vk.messages.send(
        random_id=get_random_id(),
        user_id=event.user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
    )


def greet(event, vk, keyboard):
    message = 'Приветствуем в нашей викторине! Для участия нажмите «Новый вопрос».'
    send_message(event, vk, message, keyboard)


def ask(event, vk, keyboard, redis_db, quiz_content):
    question, answer = choice(list(quiz_content.items()))
    redis_db.set(event.user_id, question)
    send_message(event, vk, question, keyboard)


def check_answer(event, vk, keyboard, redis_db, quiz_content):
    message = 'Неверный ответ или команда. Попробуй ещё раз'
    question = redis_db.get(event.user_id).decode('utf-8')
    answer = quiz_content.get(question).lower()
    if answer == event.text.lower():
        message = 'Верно! Для продолжения нажми «Новый вопрос».'
        redis_db.delete(event.user_id)

    send_message(event, vk, message, keyboard)


def concede(event, vk, keyboard, redis_db, quiz_content):
    question = redis_db.get(event.user_id).decode('utf-8')
    redis_db.delete(event.user_id)
    answer = quiz_content.get(question)
    message = f'Правильный ответ {answer}. Для продолжения нажми «Новый вопрос».'
    send_message(event, vk, message, keyboard)


def set_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.SECONDARY)
    return keyboard


def run_bot(vk_token, redis_db, quiz_content):
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()

    keyboard = set_keyboard()

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        try:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.message_id == 1 or event.text.lower() == 'привет':
                    greet(event, vk, keyboard)
                    continue
                if event.text == 'Новый вопрос':
                    ask(event, vk, keyboard, redis_db, quiz_content)
                    continue
                if event.text == 'Сдаться':
                    concede(event, vk, keyboard, redis_db, quiz_content)
                    continue
                check_answer(event, vk, keyboard, redis_db, quiz_content)

        except Exception as error:
            logger.exception(f'Message from user {event.user_id} caused {error}')


def main():
    load_dotenv()

    folder = 'questions'
    redis_host = os.getenv('REDIS_ENDPOINT')
    redis_port = os.getenv('REDIS_PORT')
    redis_pass = os.getenv('REDIS_PASSWORD')
    vk_token = os.getenv('VK_API_KEY')
    logbot_token = os.getenv('TG_LOG_BOT_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')

    logger.addHandler(TelegramBotHandler(logbot_token, chat_id))

    redis_db = redis.Redis(
        host=redis_host, port=redis_port, db=0, password=redis_pass
    )

    quiz_content = dict(get_quiz_content(folder))

    run_bot(vk_token, redis_db, quiz_content)


if __name__ == '__main__':
    main()
