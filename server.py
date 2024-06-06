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
        CORS(self.app, origins='*')
        self.socketio = SocketIO(self.app, cors_allowed_origins='*')
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
            frame = base64.b64encode(frame).decode('utf-8')
            return frame, 200

        @self.socketio.on('streamViewerConfirm')
        def handle_viewer_confirm(data):
            try:
                camera_name = data['camera']
                if camera_name not in self.streams:
                    return
                with self.lock:
                    self.streams[camera_name]['lastConfirmedTime'] = time.time()
            except KeyError as e:
                return

        @self.app.route('/stream/<camera_name>')
        def stream(camera_name):
            cam = cameras[camera_name] if camera_name in cameras else None
            if not cam:
                return {"error": "Invalid camera name"}, 400

            with self.lock:
                if camera_name not in self.streams:
                    self.streams[camera_name] = {
                        'thread': self.socketio.start_background_task(self.stream_video, cam, camera_name),
                        'lastConfirmedTime': time.time(),
                    }
                    return {"message": f"Started streaming video feed for camera \"{camera_name}\""}, 200
                else:
                    return {"message": f"Already streaming video feed for camera \"{camera_name}\""}, 200

    def stream_video(self, cam: Camera, camera_name: str):
        request_frequency = 10
        request_timeout = 30
        last_request_time = time.time()

        print(f"Starting stream for camera \"{camera_name}\"")

        while True:
            frame = cam.capture_frame()
            frame = convert(frame, file_format=".jpg")
            frame = base64.b64encode(frame).decode('utf-8')
            self.socketio.emit('video_feed', {'camera': camera_name, 'frame': frame})

            if time.time() - last_request_time > request_frequency:
                self.socketio.emit('streamViewerCheck', {'camera': camera_name})
                last_request_time = time.time()

            with self.lock:
                last_confirmed_time = self.streams[camera_name]['lastConfirmedTime']
                if camera_name not in self.streams or time.time() - last_confirmed_time > request_timeout:
                    print(f"Stopping stream for camera \"{camera_name}\"")
                    self.streams.pop(camera_name)
                    break
            eventlet.sleep()

    def run(self, port=None, debug=False):
        print("Starting server...")
        self.socketio.run(self.app, port=port, debug=debug, log_output=debug, use_reloader=debug)


if __name__ == '__main__':
    server = Server()
    server.run(debug=False)
