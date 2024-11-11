import eventlet
eventlet.monkey_patch()  # Перемещаем вызов monkey_patch() в самое начало

from flask import Flask, request
from flask_socketio import SocketIO, emit
import time

# Создаем приложение
app = Flask(__name__)
socketio = SocketIO(app)

# Размеры пиксельного поля
WIDTH, HEIGHT = 150, 150  # Укажите нужные размеры

# Словарь для хранения состояния пикселей
pixels = [[{"color": "#FFFFFF", "timestamp": 0} for _ in range(WIDTH)] for _ in range(HEIGHT)]

# Словарь для хранения времени последней активности каждого пользователя
user_last_activity = {}

# Интервал времени для ограничения (в секундах)
COOLDOWN_TIME = 5  # Ограничение в 5 секунд

@socketio.on('connect')
def handle_connect():
    # Когда пользователь подключается, присваиваем уникальный идентификатор сессии
    user_last_activity[request.sid] = time.time()
    
    # Отправляем текущие цвета всех пикселей новым пользователям
    emit('initialize_pixels', {'pixels': pixels})

@socketio.on('disconnect')
def handle_disconnect():
    # Когда пользователь отключается, удаляем его из отслеживаемых
    if request.sid in user_last_activity:
        del user_last_activity[request.sid]

@socketio.on('paint_pixel')
def handle_paint_pixel(data):
    x, y, color = data['x'], data['y'], data['color']
    current_time = time.time()
    pixel = pixels[y][x]
    
    # Проверка, прошло ли достаточно времени с последней активности
    last_activity_time = user_last_activity.get(request.sid, 0)
    
    if current_time - last_activity_time >= COOLDOWN_TIME:
        # Обновляем пиксель, если прошло больше 5 секунд
        pixels[y][x] = {"color": color, "timestamp": current_time}
        user_last_activity[request.sid] = current_time  # Обновляем время последней активности

        # Отправка обновлений всем клиентам
        emit('update_pixel', {'x': x, 'y': y, 'color': color}, broadcast=True)
    else:
        # Отправляем пользователю информацию о времени, оставшемся до следующей покраски
        time_left = int(COOLDOWN_TIME - (current_time - last_activity_time))
        emit('cooldown', {'x': x, 'y': y, 'time_left': time_left})

if __name__ == '__main__':
    socketio.run(app)
