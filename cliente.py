import socket
import random
import time

# Configura el cliente
host = '172.26.48.117'  # Utiliza la dirección IP local de la misma computadora
port = 12345

# Crea un socket del cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

# Función para agregar un carácter aleatorio al texto
def agregar_caracter_aleatorio(texto):
    caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    caracter_aleatorio = random.choice(caracteres)
    return texto + caracter_aleatorio

try:
    texto_recibido = client_socket.recv(1024).decode()
    print(f"Texto recibido del servidor: {texto_recibido}")

    while True:
        texto_modificado = agregar_caracter_aleatorio(texto_recibido)
        print(f"Texto modificado: {texto_modificado}")

        # Envía la respuesta al servidor
        client_socket.send(texto_modificado.encode())

        # Agrega una pausa de 2 segundos
        time.sleep(2)

        texto_recibido = client_socket.recv(1024).decode()
        print(f"Texto recibido del servidor: {texto_recibido}")

        # Agrega una pausa de 2 segundos
        time.sleep(2)

except KeyboardInterrupt:
    print("Servidor desconectado.")

# Cierra la conexión
client_socket.close()
