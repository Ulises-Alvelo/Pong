import socket
import threading
import json

HOST = '0.0.0.0'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(2)

#Diccionario de clientes que se usa de manera local para cada vez que se necesite llamar a uno
clientes = []

def manejar_clientes(conn, addr):
    print(f"Usuario {addr} conectado")
#Bucle que mantiene la conexion hasta que el jugador abandone el juego.
    while True:
        try:
            datos = conn.recv(2048)
            if not datos:
                break
            #Recorre el diccionario local de clientes enviandole el mensaje al rival
            for c in clientes:
                if c != conn:
                    c.sendall(datos)
        except Exception as e:
            print(f"Error: {e}")
            break

    print(f"El usuario con la direccion {addr} se desconecto")
    if conn in clientes:
        clientes.remove(conn)
    conn.close()


print(f"[INICIANDO] Servidor escuchando el puerto {PORT}")

while True:
    conn, addr = server.accept()

    if len(clientes) < 2:
        clientes.append(conn)
        player_num = len(clientes)  # 1 = host (simulates the ball), 2 = guest

        # Le avisamos al cliente que numero de jugador es, antes de arrancar
        # el relay normal de estados de juego.
        asignacion = json.dumps({"jugador": player_num}).encode('utf-8') + b'\n'
        conn.sendall(asignacion)

        thread = threading.Thread(target=manejar_clientes, args=(conn, addr))
        thread.start()
        print(f"Jugadores conectados: {len(clientes)}/2 (asignado como jugador {player_num})")
    else:
        print(f"La sala esta llena, conexion denegada a: {addr}")
        conn.sendall(b"Sala llena\n")
        conn.close()