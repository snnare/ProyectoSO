import socket
import threading
import os
from tkinter import Tk, filedialog

# Semáforo para sincronizar el acceso a la sección crítica
message_lock = threading.Lock()

def handle_client(client_socket):
    try:
        while True:
            # Recibe la longitud del nombre del archivo
            filename_length = client_socket.recv(4)
            if not filename_length:
                break

            # Convierte la longitud del nombre del archivo a un entero
            filename_length = int.from_bytes(filename_length, byteorder='big')

            # Recibe el nombre del archivo
            filename = client_socket.recv(filename_length).decode('latin-1')  # Cambiado a 'latin-1'

            # Recibe la longitud de los datos de la imagen
            data_length = client_socket.recv(8)
            data_length = int.from_bytes(data_length, byteorder='big')

            # Recibe los datos de la imagen
            image_data = client_socket.recv(data_length)

            with message_lock:
                # Guarda la imagen en el servidor
                with open(filename, 'wb') as file:
                    file.write(image_data)

                print(f"Imagen recibida: {filename}")

                # Solicita al usuario seleccionar una imagen para responder
                response_path = select_image()

                if not response_path:
                    print("No se seleccionó ninguna imagen para responder.")
                    continue

                with open(response_path, 'rb') as response_file:
                    # Obtiene el nombre del archivo de respuesta
                    response_filename = os.path.basename(response_path)
                    response_filename_length = len(response_filename).to_bytes(4, byteorder='big')

                    # Obtiene los datos de la imagen de respuesta
                    response_image_data = response_file.read()
                    response_data_length = len(response_image_data).to_bytes(8, byteorder='big')

                    # Envía la longitud del nombre del archivo de respuesta
                    client_socket.send(response_filename_length)

                    # Envía el nombre del archivo de respuesta
                    client_socket.send(response_filename.encode('latin-1'))  # Cambiado a 'latin-1'

                    # Envía la longitud de los datos de la imagen de respuesta
                    client_socket.send(response_data_length)

                    # Envía los datos de la imagen de respuesta
                    client_socket.send(response_image_data)

                    print(f"Imagen de respuesta enviada: {response_filename}")

    except Exception as e:
        print(f"Error en la conexión con el cliente: {e}")
    finally:
        client_socket.close()

def select_image():
    root = Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter
    file_path = filedialog.askopenfilename(title="Selecciona una imagen", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
    return file_path

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('172.26.49.26', 5555))
    server.listen(5)
    print("[*] Servidor escuchando en 0.0.0.0:5555")

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"[*] Conexión aceptada de {addr[0]}:{addr[1]}")

            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
    except KeyboardInterrupt:
        print("Servidor interrumpido.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
