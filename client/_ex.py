import socket
import json
import threading

class MessengerClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 5555)
        self.username = None

    def connect_to_server(self):
        self.client_socket.connect(self.server_address)
        print("Terhubung ke server.")

    def authenticate(self, username, password):
        auth_message = {"type": "auth", "username": username, "password": password}
        self.send_message(auth_message)

        # Terima respons autentikasi dari server
        auth_response = json.loads(self.client_socket.recv(1024).decode('utf-8'))
        if auth_response["success"]:
            self.username = username
            print("Autentikasi berhasil.")
            return True
        else:
            print(f"Autentikasi gagal: {auth_response['message']}")
            return False

    def send_message(self, message):
        self.client_socket.send(json.dumps(message).encode('utf-8'))

    def receive_messages(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                message = json.loads(data.decode('utf-8'))
                self.handle_message(message)

        except Exception as e:
            print(f"Error: {e}")

    def handle_message(self, message):
        message_type = message.get("type")

        if message_type == "text_message":
            print(f"Pesan dari {message['from']}: {message['message']}")
        elif message_type == "user_online":
            print(f"{message['username']} online.")
        elif message_type == "user_offline":
            print(f"{message['username']} offline.")
        elif message_type == "error":
            print(f"Error ({message['code']}): {message['message']}")

    def start_messaging(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()

        while True:
            to_user = input("Masukkan nama pengguna penerima: ")
            message_text = input("Masukkan pesan: ")

            message = {"type": "text_message", "to": to_user, "message": message_text}
            self.send_message(message)

if __name__ == "__main__":
    client = MessengerClient()
    client.connect_to_server()

    username = input("Masukkan nama pengguna: ")
    password = input("Masukkan kata sandi: ")

    if client.authenticate(username, password):
        client.start_messaging()
