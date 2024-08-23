import os
import redis
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from src.controller.vehicles import vehicle_controller_factory

app = Flask(__name__)
cors = CORS(app)
socket_io = SocketIO(app)

redis_client = redis.from_url(os.getenv('REDIS_URL'))

app.register_blueprint(vehicle_controller_factory(socket_io, redis_client), url_prefix='/vehicles')