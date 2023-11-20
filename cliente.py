import socket
import cv2
import numpy as np
import time

def connect_to_server():
    host = '127.0.0.1'
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    print(f"Conectado al servidor en {host}:{port}")
    return client_socket

def send_image(client_socket, image):
    _, img_encoded = cv2.imencode('.png', image)
    img_bytes = img_encoded.tobytes()

    size = len(img_bytes)
    send_message(client_socket, str(size))

    client_socket.sendall(img_bytes)
    print("Imagen enviada al servidor")

def receive_image(client_socket):
    size_str = receive_message(client_socket)
    size = int(size_str)

    img_bytes = client_socket.recv(size)
    print("Imagen recibida del servidor")

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
    cv2.waitKey(tiempo_espera)
    time.sleep(tiempo_sleep)

def modificar_imagen(image):
    matriz_rotacion_original = cv2.getRotationMatrix2D((image.shape[1] // 2, image.shape[0] // 2), 45, 1)
    return cv2.warpAffine(image, matriz_rotacion_original, (image.shape[1], image.shape[0]))

def close_connection(client_socket):
    client_socket.close()

def main():
    client_socket = connect_to_server()

    num_iterations = int(receive_message(client_socket))
    print(f"Recibido el número de iteraciones: {num_iterations}")

    for iteration in range(1, num_iterations + 1):
        received_image = receive_image(client_socket)
       
        mostrar_imagen(f"Imagen recibida en iteración {iteration}", received_image)

        modified_image = modificar_imagen(received_image)

        guardar_imagen(f"Enviadas/IMG_server{iteration}.png", modified_image)

        if received_image is not None and received_image.shape[0] > 0 and received_image.shape[1] > 0:
            mostrar_imagen(f"Imagen recibida en iteración {iteration}", received_image)
        else:
            print(f"Imagen recibida en iteración {iteration} no válida")

        send_image(client_socket, modified_image)

    client_socket.close()

if __name__ == "__main__":
    main()
