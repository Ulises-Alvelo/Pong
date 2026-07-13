import socket
import threading
import json

class RedCliente:
    def __init__(self, ip_servidor='127.0.0.1', puerto=5555):
        self.clientes = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_servidor = ip_servidor 
        self.puerto = puerto

        self.datos_recibidos = {}
        self.conectado  = False

    def conectar(self):
        try:
            self.clientes.connect((self.ip_servidor, self.puerto))
            self.conectado = True
            print("Conectando al servidor")

            hilo_recepcion = threading.Thread(target=self.recibir_datos, daemon = True)
            hilo_recepcion.start()
        except Exception as e:
            print(f"Error al conectarse con el servidor: {e}")
        
    def recibir_datos(self):
        while self.conectado:
            try:
                datos = self.clientes.recv(2048).decode('utf-8')
                if datos:
                    self.datos_recibidos = json.loads(datos)

            except Exception as e:
                print(f"Desconectado del servidor: {e}")
                self.conectado = False
                self.clientes.close()
                break

    def enviar_datos(self, datos_diccionario):
        """ Envia el estado local al servidor """
        if self.conectado:
            try:
                datos_codificados = json.dumps(datos_diccionario).encode('utf-8')
                self.clientes.sendall(datos_codificados)
            except socket.error as e:
                print(f"Error al enviar. {e}")

if __name__ == "__main__":
    import time

    red = RedCliente()
    red.conectar()

    try:
        while True:
            estado_local = {
                "jugador_y": 150,
                "modificador_tocado": "velocidad_x2"
            }
            red.enviar_datos(estado_local)
            time.sleep(0.05)
    except KeyboardInterrupt:
        red.conectado = False
        red.clientes.close()