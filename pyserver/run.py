# -*- coding: UTF-8 -*-
import eventlet
eventlet.monkey_patch(thread=False)
eventlet.import_patched('mongoengine')

from datetime import timedelta

from flask import Flask
from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_claims
from flask_socketio import SocketIO

from server3.route import file_route
from server3.route import ownership_route
from server3.route import project_route
from server3.route import data_route
from server3.route import staging_data_route
from server3.route import toolkit_route
from server3.route import user_route
from server3.route import monitor_route
from server3.route import model_route
from server3.route import visualization_route
from server3.repository import config
from server3.utility import json_utility

# from server3.sio import socketio

UPLOAD_FOLDER = config.get_file_prop('UPLOAD_FOLDER')

app = Flask(__name__, static_url_path='/static',
            static_folder='user_directory/model')
app.secret_key = 'super-super-secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

socketio = SocketIO(app,
                    logger=True,
                    engineio_logger=True,
                    async_mode='eventlet',
                    message_queue='redis://')

CORS(app, supports_credentials=True)

# Setup the Flask-JWT-Extended extension
jwt = JWTManager(app)


# This method will get whatever object is passed into the
# create_access_token method.
@jwt.user_claims_loader
def add_claims_to_access_token(user):
    # add more claims in the future
    user_json = json_utility.convert_to_json(user.to_mongo())
    user_json.pop('password')
    return {'user': user_json}


# This method will also get whatever object is passed into the
# create_access_token method, and let us define what the identity
# should be for this object
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.user_ID


# This is an example for jwt_required
# Protect a view with jwt_required, which requires a valid access token
# in the request to access.
@app.route('/refresh_token', methods=['GET'])
@jwt_required
def refresh_token():
    # Access the identity of the current user with get_jwt_identity
    # current_user = get_jwt_identity()
    claims = get_jwt_claims()
    return jsonify({'user': claims['user']}), 200


app.register_blueprint(file_route.file_app)
app.register_blueprint(ownership_route.ownership_app)
app.register_blueprint(project_route.project_app)
app.register_blueprint(data_route.data_app)
app.register_blueprint(staging_data_route.staging_data_app)
app.register_blueprint(toolkit_route.toolkit_app)
app.register_blueprint(model_route.model_app)
app.register_blueprint(user_route.user_app)
app.register_blueprint(monitor_route.monitor_app)
app.register_blueprint(visualization_route.visualization_app)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
