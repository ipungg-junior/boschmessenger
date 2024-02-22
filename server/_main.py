import socket
import threading
import json

# Inisialisasi server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 5555)
server_socket.bind(server_address)
server_socket.listen(5)

# Dictionary untuk menyimpan koneksi aktif dan status pengguna
active_connections = {}
user_status = {}

def handle_client(client_socket):
    try:
        while True:
            # Terima data dari klien
            data = client_socket.recv(1024)
            if not data:
                break

            # Proses data JSON
            try:
                message = json.loads(data.decode('utf-8'))
                message_type = message.get("type")

                # Handling berdasarkan jenis pesan
                if message_type == "auth":
                    handle_authentication(client_socket, message)
                elif message_type == "text_message":
                    handle_text_message(client_socket, message)
                # Tambahkan jenis pesan lainnya jika diperlukan

            except json.JSONDecodeError:
                send_error(client_socket, "Invalid JSON format")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Tutup koneksi ketika klien terputus
        username = active_connections.get(client_socket)
        if username:
            del active_connections[client_socket]
            del user_status[username]
            notify_user_status_change(username, "offline")
        client_socket.close()

def handle_authentication(client_socket, message):
    # Proses autentikasi, contoh sederhana: cek username dan password
    username = message.get("username")
    password = message.get("password")
    success = True  # Ganti dengan logika autentikasi sesuai kebutuhan

    response = {"type": "auth_response", "success": success, "message": "Authentication success" if success else "Authentication failed"}
    
    client_socket.send(json.dumps(response).encode('utf-8'))

    # Jika autentikasi berhasil, tambahkan ke daftar koneksi aktif
    if success:
        active_connections[client_socket] = username
        user_status[username] = "online"
        notify_user_status_change(username, "online")

def handle_text_message(client_socket, message):
    to_user = message.get("to")
    text = message.get("message")
    from_user = active_connections.get(client_socket)

    if to_user in user_status and user_status[to_user] == "online":
        # Kirim pesan ke pengguna yang dituju
        to_socket = next(socket for socket, user in active_connections.items() if user == to_user)
        to_socket.send(json.dumps({"type": "text_message", "from": from_user, "message": text}).encode('utf-8'))
        client_socket.send(json.dumps({"type": "text_message_response", "success": True, "message": "Message sent"}).encode('utf-8'))
    else:
        send_error(client_socket, "User is offline or does not exist")

def notify_user_status_change(username, status):
    # Kirim notifikasi perubahan status pengguna ke semua klien
    for socket, user in active_connections.items():
        if user != username:
            socket.send(json.dumps({"type": "user_" + status, "username": username}).encode('utf-8'))

def send_error(client_socket, error_message):
    # Kirim pesan error ke klien
    client_socket.send(json.dumps({"type": "error", "code": "1", "message": error_message}).encode('utf-8'))

# Main loop untuk menerima koneksi
try:
    while True:
        print("Menunggu koneksi...")
        client_socket, client_address = server_socket.accept()
        print(f"Terhubung dengan {client_address}")
        
        # Mulai thread baru untuk menangani koneksi dari klien
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

except KeyboardInterrupt:
    print("Server ditutup.")
finally:
    server_socket.close()
