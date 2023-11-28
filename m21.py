import socket
import threading
import os
from PIL import Image

# Semáforo para sincronizar el acceso a la sección crítica
message_lock = threading.Lock()

# Variable para contar el número de iteraciones en el servidor
iteration_count = 0

# Variable para almacenar las imágenes en el servidor
server_images = {}

def handle_client(client_socket, initial_image_path):
    global iteration_count
    try:
        current_image_path = initial_image_path

        while iteration_count < 10:
            # Recibe la longitud del nombre del archivo
            filename_length = client_socket.recv(4)
            if not filename_length:
                break

            # Convierte la longitud del nombre del archivo a un entero
            filename_length = int.from_bytes(filename_length, byteorder='big')

            # Recibe el nombre del archivo
            filename = client_socket.recv(filename_length).decode('latin-1')

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

                # Rota la imagen antes de enviarla de vuelta al cliente
                rotated_image_path = rotate_image(filename)

                if rotated_image_path is not None:
                    with open(rotated_image_path, 'rb') as rotated_file:
                        # Obtiene el nombre del archivo de respuesta
                        response_filename = os.path.basename(rotated_image_path)
                        response_filename_length = len(response_filename).to_bytes(4, byteorder='big')

                        # Obtiene los datos de la imagen de respuesta
                        response_image_data = rotated_file.read()
                        response_data_length = len(response_image_data).to_bytes(8, byteorder='big')

                        # Envía la longitud del nombre del archivo de respuesta
                        client_socket.send(response_filename_length)

                        # Envía el nombre del archivo de respuesta
                        client_socket.send(response_filename.encode('latin-1'))

                        # Envía la longitud de los datos de la imagen de respuesta
                        client_socket.send(response_data_length)

                        # Envía los datos de la imagen de respuesta
                        client_socket.send(response_image_data)

                        print(f"Imagen rotada enviada al cliente: {response_filename}")

                iteration_count += 1

    except Exception as e:
        print(f"Error en la conexión con el cliente: {e}")
    finally:
        client_socket.close()


def rotate_image(image_path):
    try:
        original_image = Image.open(image_path)

        # Convierte la imagen a modo RGB antes de rotarla
        rgb_image = Image.new("RGB", original_image.size)
        rgb_image.paste(original_image)

        # Rota la imagen 45 grados
        rotated_image = rgb_image.rotate(45)

        # Guarda la imagen rotada con un nuevo nombre
        rotated_image_path = os.path.splitext(image_path)[0] + "_rotated.jpg"
        rotated_image.save(rotated_image_path)

        return rotated_image_path
    except Exception as e:
        print(f"Error al rotar la imagen: {e}")
        return None


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('192.168.100.45', 9999))
    server.listen(5)
    print("[*] Servidor escuchando en 192.168.100.45:9999")

    try:
        while iteration_count < 10:
            client_socket, addr = server.accept()
            print(f"[*] Conexión aceptada de {addr[0]}:{addr[1]}")

            # Pasa la ruta de la imagen al servidor (modificar según tus necesidades)
            initial_image_path = "Original/pikachu.jpg"

            client_handler = threading.Thread(target=handle_client, args=(client_socket, initial_image_path))
            client_handler.start()
    except KeyboardInterrupt:
        print("Servidor interrumpido.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
