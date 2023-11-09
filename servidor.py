import socket
import random
import time

# Configura el servidor
host = '0.0.0.0'  # Escucha en todas las interfaces de red
port = 12345  # Puerto de escucha

# Crea un socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print(f"Esperando una conexión en {host}:{port}...")

# Acepta la conexión del cliente
client_socket, client_address = server_socket.accept()
print(f"Conexión establecida con {client_address}")

# Función para agregar un carácter aleatorio al texto
def agregar_caracter_aleatorio(texto):
    caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    caracter_aleatorio = random.choice(caracteres)
    return texto + caracter_aleatorio

try:
    while True:
        texto = input("Ingrese un texto inicial: ")

        while True:
            texto = agregar_caracter_aleatorio(texto)
            print(f"Texto enviado al cliente: {texto}")

            # Envía el texto al cliente
            client_socket.send(texto.encode())

            # Agrega una pausa de 2 segundos
            time.sleep(2)

            # Recibe la respuesta del cliente
            respuesta = client_socket.recv(1024).decode()
            print(f"Respuesta del cliente: {respuesta}")

            # Agrega una pausa de 2 segundos
            time.sleep(2)

except KeyboardInterrupt:
    print("Cliente desconectado.")

# Cierra la conexión
client_socket.close()
server_socket.close()
