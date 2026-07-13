import socket
import threading

HOST = '0.0.0.0'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

clientes = []

def manejar_clientes(conn,addr):
    print(f"Usuario {addr} conectado")

    while True:
        try:
            datos = conn.recv(2048)
            if not datos:
                break
            for c in clientes:
                if c != conn:
                    c.sendall(datos)
        except Exception as e:
            print(f"Error: {e}") 
            break
    print(f"El usuario con la direccion {addr} se a desconectado")
    clientes.remove(conn)
    conn.close()

print(f"[INICIANDO] Servidor escuchando el puerto {PORT}")

while True:
    conn,addr = server.accept()

    if len(clientes) < 2:
        clientes.append(conn)
        thread = threading.Thread(target=manejar_clientes, args=(conn,addr))
        thread.start()
        print(f"Jugadores conectados: {len(clientes)}/2")
    else:
        print(f"La sala esta llena, conexion denegada a: {addr}")
        conn.sendall(b"Sala llena")
        conn.close()