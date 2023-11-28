import socket
import threading
import os
from PIL import Image

# Semáforo para sincronizar el acceso a la sección crítica
message_lock = threading.Lock()

# Variable para contar el número de iteraciones en el cliente
iteration_count = 0

def rotate_image(image_path):
    try:
        original_image = Image.open(image_path)
        rgb_image = Image.new("RGB", original_image.size)
        rgb_image.paste(original_image)
        rotated_image = rgb_image.rotate(45)
        rotated_image_path = os.path.splitext(image_path)[0] + "_rotated.jpg"
        rotated_image.save(rotated_image_path)
        return rotated_image_path
    except Exception as e:
        print(f"Error al rotar la imagen: {e}")
        return None

def send_and_receive_images(client_socket, initial_image_path):
    global iteration_count
    try:
        current_image_path = initial_image_path

        while iteration_count < 10:
            # Rota la imagen antes de enviarla
            rotated_image_path = rotate_image(current_image_path)

            if rotated_image_path is None:
                print("Error al rotar la imagen. Saliendo del envío de imágenes.")
                break

            with open(rotated_image_path, 'rb') as file:
                # Obtiene el nombre del archivo
                filename = os.path.basename(rotated_image_path)
                filename_length = len(filename).to_bytes(4, byteorder='big')

                # Obtiene los datos de la imagen
                image_data = file.read()
                data_length = len(image_data).to_bytes(8, byteorder='big')

                # Envía la longitud del nombre del archivo
                client_socket.send(filename_length)

                # Envía el nombre del archivo
                client_socket.send(filename.encode('latin-1'))

                # Envía la longitud de los datos de la imagen
                client_socket.send(data_length)

                # Envía los datos de la imagen
                client_socket.send(image_data)

                print(f"Imagen enviada y rotada: {filename}")

                # Recibe la respuesta del servidor

                # Recibe la longitud del nombre del archivo de respuesta
                response_filename_length = client_socket.recv(4)
                if not response_filename_length:
                    print("El servidor cerró la conexión.")
                    break

                # Convierte la longitud del nombre del archivo de respuesta a un entero
                response_filename_length = int.from_bytes(response_filename_length, byteorder='big')

                # Recibe el nombre del archivo de respuesta
                response_filename = client_socket.recv(response_filename_length).decode('latin-1')

                # Recibe la longitud de los datos de la imagen de respuesta
                response_data_length = client_socket.recv(8)
                response_data_length = int.from_bytes(response_data_length, byteorder='big')

                # Recibe los datos de la imagen de respuesta
                response_image_data = client_socket.recv(response_data_length)

                with message_lock:
                    # Guarda la imagen de respuesta en el cliente
                    with open(response_filename, 'wb') as response_file:
                        response_file.write(response_image_data)

                    print(f"Imagen de respuesta recibida: {response_filename}")

                    # Actualiza la imagen actual a la recibida
                    current_image_path = response_filename

            iteration_count += 1

    except Exception as e:
        print(f"Error en la conexión con el servidor: {e}")
    finally:
        client_socket.close()

def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 5555))

        # Pasa la ruta de la imagen al cliente (modificar según tus necesidades)
        initial_image_path = "Original/pikachu.png"

        # Hilo para enviar y recibir imágenes continuamente
        send_and_receive_images(client, initial_image_path)

    except KeyboardInterrupt:
        print("Cliente interrumpido.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
