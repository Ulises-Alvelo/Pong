import socket
import threading
import json


class RedCliente:
    def __init__(self, server_ip='127.0.0.1', puerto=5040):
        self.clientes = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.puerto = puerto

        self.datos_recibidos = {}
        self.conectado = False
        self.player_num = None  # 1 (host), 2 (guest)

        # Buffer to fix messages since TCP may not send exactly one message, they're separed by '\n', and they accumulate until there's a full line 
        self._buffer = b''

    def _leer_linea(self):
        # Wait until get full message, returns it as a text.
        while b'\n' not in self._buffer:
            chunk = self.clientes.recv(2048)
            if not chunk:
                raise ConnectionError("El servidor cerro la conexion")
            self._buffer += chunk
        linea, self._buffer = self._buffer.split(b'\n', 1)
        return linea.decode('utf-8')

    def conectar(self):
        try:
            self.clientes.connect((self.server_ip, self.puerto))
            self.conectado = True
            print("Conectando al servidor")

            # Server sends initial message with player number before the game initializes
            first_message = self._leer_linea()

            if first_message == "Sala llena":
                print("La sala esta llena.")
                self.conectado = False
                self.clientes.close()
                return

            asign = json.loads(first_message)
            self.player_num = asign.get("jugador")
            print(f"Asignado como jugador {self.player_num}")

            hilo_recepcion = threading.Thread(target=self.recibir_datos, daemon=True)
            hilo_recepcion.start()
        except Exception as e:
            print(f"Error al conectarse con el servidor: {e}")
            self.conectado = False

    def recibir_datos(self):
        while self.conectado:
            try:
                chunk = self.clientes.recv(2048)
                if not chunk:
                    raise ConnectionError("El servidor cerro la conexion")
                self._buffer += chunk

                # More than one message could've arrived, its separed wit '\n', we only get the last full message
                partes = self._buffer.split(b'\n')
                self._buffer = partes[-1]  # if there's something incomplete, it stays for the next recieve.
                mensajes_completos = partes[:-1]

                if mensajes_completos:
                    ultimo = mensajes_completos[-1]
                    if ultimo:
                        self.datos_recibidos = json.loads(ultimo.decode('utf-8'))

            except Exception as e:
                print(f"Desconectado del servidor: {e}")
                self.conectado = False
                self.clientes.close()
                break

    def enviar_datos(self, datos_diccionario):
        # Send local state to server
        if self.conectado:
            try:
                datos_codificados = json.dumps(datos_diccionario).encode('utf-8') + b'\n'
                self.clientes.sendall(datos_codificados)
            except socket.error as e:
                print(f"Error al enviar. {e}")


if __name__ == "__main__":
    import time

    net = RedCliente()
    net.conectar()

    try:
        while net.conectado:
            estado_local = {
                "jugador_y": 150,
                "modificador_tocado": "velocidad_x2"
            }
            net.enviar_datos(estado_local)
            time.sleep(0.05)
    except KeyboardInterrupt:
        net.conectado = False
        net.clientes.close()