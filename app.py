from flask import Flask, render_template

app = Flask(__name__)

# Счетчик посещений
visits = 0

@app.route('/')
def index():
    global visits
    visits += 1
    return render_template('index.html', visits=visits)

if __name__ == '__main__':
    app.run(debug=True)
