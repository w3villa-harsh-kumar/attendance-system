from flask import Flask
from routers.routes import init_routes

app = Flask(__name__)
app.config.from_pyfile('config.py')
init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
