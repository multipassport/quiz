# QuizBot

Викторина, подключенная к ботам VK и Telegram. Считывает вопросы и ответы из папки с заготовками.

## Установка

Для запуска программы должен быть установлен Python 3.

Скачайте код и установите требуемые библиотеки командой

```bash
pip install -r requirements.txt

```

## Переменные окружения

Для запуска ботов понадобится `.env` файл следующего содержимого:

* `TG_BOT_TOKEN` - токен Telegram бота. Получается у [@BotFather](https://telegram.me/BotFather)
* `REDIS_ENDPOINT` - адрес базы данных [redis](https://app.redislabs.com/)
* `REDIS_PORT` - номер порта базы данных
* `REDIS_PASSWORD` - пароль от базы данных
* `VK_API_KEY` - получается в настройках группы VK в разделе "Работа с API". Требует право доступа к сообщениям сообщества.
* `TG_CHAT_ID`=1285793181
* `TG_LOG_BOT_TOKEN` - токен запасного Telegram бота. Получается у [@BotFather](https://telegram.me/BotFather)

## Запуск ботов

Боты запускаются командами 

```bash
python tg_bot.py

```

```bash
python vk_bot.py

```

## Предварительный просмотр

* VK бот доступен [здесь](https://vk.com/im?sel=-206398414)
* TG бот доступен [здесь](@very_umnich_bot)

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
