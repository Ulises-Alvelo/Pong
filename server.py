import socket
import threading
import json

HOST = '0.0.0.0'
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(2)

clientes = []

def broadcast(mensaje_dict, remitente=None):
    data = json.dumps(mensaje_dict).encode('utf-8') + b'\n'
    for c in list(clientes):
        if c != remitente:
            try:
                c.sendall(data)
            except Exception:
                pass

def manejar_clientes(conn, addr):
    print(f"Usuario {addr} conectado")
    while True:
        try:
            datos = conn.recv(2048)
            if not datos:
                break
            for c in list(clientes):
                if c != conn:
                    try:
                        c.sendall(datos)
                    except Exception:
                        pass
        except Exception:
            break

    print(f"El usuario con la direccion {addr} se desconecto")
    if conn in clientes:
        clientes.remove(conn)
    conn.close()

    # Notificar al cliente restante que el rival se fue
    broadcast({"rival_desconectado": True})

print(f"[INICIANDO] Servidor escuchando el puerto {PORT}")

while True:
    conn, addr = server.accept()

    if len(clientes) < 2:
        clientes.append(conn)
        player_num = len(clientes)

        # Asignación de jugador inicial
        asignacion = json.dumps({"jugador": player_num}).encode('utf-8') + b'\n'
        conn.sendall(asignacion)

        thread = threading.Thread(target=manejar_clientes, args=(conn, addr), daemon=True)
        thread.start()
        print(f"Jugadores conectados: {len(clientes)}/2 (asignado como jugador {player_num})")

        # Si ya están los 2 jugadores conectados, avisar a ambos que empiece
        if len(clientes) == 2:
            broadcast({"inicio": True})
    else:
        print(f"La sala esta llena, conexion denegada a: {addr}")
        conn.sendall(b"Sala llena\n")
        conn.close()