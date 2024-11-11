import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

WIDTH, HEIGHT = 150, 150
pixels = [[{"color": "#FFFFFF", "timestamp": 0} for _ in range(WIDTH)] for _ in range(HEIGHT)]
user_last_activity = {}
COOLDOWN_TIME = 0

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    user_last_activity[request.sid] = time.time()
    emit('initialize_pixels', {'pixels': pixels})

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in user_last_activity:
        del user_last_activity[request.sid]

@socketio.on('paint_pixel')
def handle_paint_pixel(data):
    x, y, color = data['x'], data['y'], data['color']
    current_time = time.time()
    pixel = pixels[y][x]
    last_activity_time = user_last_activity.get(request.sid, 0)

    if current_time - last_activity_time >= COOLDOWN_TIME:
        pixels[y][x] = {"color": color, "timestamp": current_time}
        user_last_activity[request.sid] = current_time
        emit('update_pixel', {'x': x, 'y': y, 'color': color}, broadcast=True)
    else:
        time_left = int(COOLDOWN_TIME - (current_time - last_activity_time))
        emit('cooldown', {'x': x, 'y': y, 'time_left': time_left})

if __name__ == '__main__':
    socketio.run(app, debug=True)
