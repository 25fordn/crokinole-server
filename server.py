from flask import Flask
from flask_cors import CORS


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        self.add_routes()

    def add_routes(self):
        @self.app.route('/test')
        def serve():
            return {"message": "This is the server speaking!"}, 200

    def run(self, port=None, debug=False):
        self.app.run(port=port, debug=debug)


if __name__ == '__main__':
    server = Server()
    server.run(debug=True)
