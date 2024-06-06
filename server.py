import base64
import time
from threading import Lock

import eventlet.wsgi
eventlet.monkey_patch()

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from hardware.camera import Camera, cameras, convert


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.streams = {}
        self.lock = Lock()
        self.add_routes()

    def add_routes(self):
        @self.app.route('/test')
        def serve():
            return {"message": "This is the server speaking!"}, 200

        @self.app.route('/capture/<camera_name>')
        def capture(camera_name):
            cam = cameras[camera_name] if camera_name in cameras else None
            if not cam:
                return {"message": "Invalid camera name"}, 400
            frame = cam.capture_frame()
            frame = convert(frame, file_format=".jpg")
            return frame, 200

        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')

        @self.app.route('/stream/<camera_name>')
        def stream(camera_name):
            cam = cameras[camera_name] if camera_name in cameras else None
            if not cam:
                return {"error": "Invalid camera name"}, 400

            with self.lock:
                if camera_name not in self.streams:
                    self.streams[camera_name] = self.socketio.start_background_task(self.stream_video, cam, camera_name)
                    return {"message": f"Started streaming video feed for camera \"{camera_name}\""}, 200
                else:
                    return {"message": f"Already streaming video feed for camera \"{camera_name}\""}, 200

    def stream_video(self, cam: Camera, camera_name: str):
        last = time.time()
        while True:
            frame = cam.capture_frame()
            frame = convert(frame, file_format=".jpg")
            frame = base64.b64encode(frame).decode('utf-8')
            self.socketio.emit('video_feed', {'camera': camera_name, 'frame': frame})
            curr = time.time()
            if curr - last >= 3:
                print(f"Streaming video feed for camera \"{camera_name}\"")
                last = curr
            with self.lock:
                if camera_name not in self.streams:
                    break
            eventlet.sleep()

    def run(self, port=None, debug=False):
        self.socketio.run(self.app, port=port, debug=debug, log_output=debug, use_reloader=debug)


if __name__ == '__main__':
    server = Server()
    server.run(debug=False)
