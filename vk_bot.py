import logging
import os

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from dotenv import load_dotenv


logger = logging.getLogger('intents')


def answer(event, vk, keyboard):
    message = 'Приветствуем в нашей викторине! Для участия нажмите «Новый вопрос».'
    vk.messages.send(
        random_id=get_random_id(),
        user_id=event.user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
    )


def main():
    load_dotenv()

    vk_token = os.getenv('VK_API_KEY')
    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.SECONDARY)

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        try:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer(event, vk, keyboard)
        except Exception as error:
            logger.exception(error)


if __name__ == '__main__':
    main()
