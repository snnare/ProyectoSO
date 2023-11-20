import socket
import cv2
import numpy as np
import time


def start_server():
    host = '127.0.0.1'
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Servidor escuchando en {host}:{port}")

    return server_socket

def send_image(client_socket, image):
    # Convertir la imagen en una cadena de bytes
    _, img_encoded = cv2.imencode('.png', image)
    img_bytes = img_encoded.tobytes()

    # Enviar el tamaño de la imagen al cliente
    size = len(img_bytes)
    send_message(client_socket, str(size))

    client_socket.sendall(img_bytes)
    print("Enviando Imagen")

def receive_image(client_socket):
    # Recibir el tamaño de la imagen
    size_str = receive_message(client_socket)
    print(f"Tamaño recibido: {size_str}")
    size = int(size_str)

    # Recibir imagen 
    img_bytes = client_socket.recv(size)
    print("Recibiendo imagen")

    # Decodificar la imagen
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return image

def send_message(client_socket, message):
    client_socket.sendall(message.encode('utf-8'))

def receive_message(client_socket):
    data = client_socket.recv(1024)
    return data.decode('utf-8')

def cargar_imagen(path):
    return cv2.imread(path)

def guardar_imagen(filename, image):
    cv2.imwrite(filename, image)

def mostrar_imagen(titulo, image, tiempo_espera=1000, tiempo_sleep=0.5):
    cv2.imshow(titulo, image)
    cv2.waitKey(tiempo_espera)  # Esperar el tiempo especificado
    time.sleep(tiempo_sleep)

def modificar_imagen(image):
    matriz_rotacion_original = cv2.getRotationMatrix2D((image.shape[1] // 2, image.shape[0] // 2), 45, 1)
    return cv2.warpAffine(image, matriz_rotacion_original, (image.shape[1], image.shape[0]))

def handle_client_connection(client_socket, num_iterations):
    # Obtiene la dirección y puerto del cliente conectado
    client_address = client_socket.getpeername()
    print(f"Conexión establecida desde {client_address}")

    # Enviar el número de iteraciones al cliente
    send_message(client_socket, str(num_iterations))

    # Cargamos la imagen original
    imagen = cargar_imagen('Original/pikachu.png')

    for iteration in range(1, num_iterations + 1):
        # Rotar la imagen
        imagen_rotada = modificar_imagen(imagen)

        # Mostrar la imagen rotada
        mostrar_imagen('Enviando Imagen', imagen_rotada)

        # Enviar la imagen al cliente
        send_image(client_socket, imagen_rotada)

        # Tiempo de espera
        time.sleep(1)

        # Recibir la imagen del cliente
        imagen_recibida = receive_image(client_socket)

        mostrar_imagen('Recibiendo Imagen', imagen_recibida)
        # Guardar la imagen recibida del cliente con nombre único x iteración
        nombre_archivo = f'Recibidas/IMG_recibida{iteration:02d}.png'
        guardar_imagen(nombre_archivo, imagen_recibida)

        # Utilizar la imagen rotada para la siguiente iteración
        imagen = cargar_imagen(nombre_archivo)

    cv2.destroyAllWindows()
    client_socket.close()

def main():
    server_socket = start_server()
    num_iterations = 3  

    while True:
        client_socket, _ = server_socket.accept()
        handle_client_connection(client_socket, num_iterations)

    server_socket.close()

if __name__ == "__main__":
    main()
