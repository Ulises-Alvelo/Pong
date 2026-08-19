import sys
import random
import socket
import threading
import json
import pygame

# ==========================================
# LÓGICA DE RED
# ==========================================
class RedCliente:
    def __init__(self, server_ip='127.0.0.1', puerto=5050):
        self.clientes = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.puerto = puerto
        self.datos_recibidos = {}
        self.conectado = False
        self.player_num = None  # 1 (host), 2 (guest)
        self._buffer = b''

    def _leer_linea(self):
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
                
                partes = self._buffer.split(b'\n')
                self._buffer = partes[-1]  
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
        if self.conectado:
            try:
                datos_codificados = json.dumps(datos_diccionario).encode('utf-8') + b'\n'
                self.clientes.sendall(datos_codificados)
            except socket.error as e:
                print(f"Error al enviar. {e}")


# ==========================================
# LÓGICA DEL JUEGO PONG
# ==========================================

# Configuración Base
WIDTH, HEIGHT = 800, 600
FPS = 60

HEIGHT_PALETA = 100
WIDTH_PALETA = 15
MARGIN_PALETA = 30
VEL_PALETA = 7

RADIO_PELOTA = 9
VEL_PELOTA_BASE = 5
VEL_PELOTA_MAX = 10
WHITE = (240, 240, 240)
BLACK = (12, 12, 18)
GRAY = (60, 60, 70)
CYAN = (80, 220, 255)
YELLOW = (255, 210, 60)

# NUEVOS LÍMITES DE CANCHA
LIMITE_SUPERIOR = 80
LIMITE_INFERIOR = 560

# Declaración de clases
class Paleta:
    def __init__(self, x):
        self.x = x
        self.altura = HEIGHT_PALETA
        self.y = HEIGHT / 2 - self.altura / 2

    def rect(self):
        return pygame.Rect(self.x, self.y, WIDTH_PALETA, self.altura)

    def move(self, dy):
        self.y += dy
        # Limita la paleta a los bordes blancos en lugar del borde de la ventana
        self.y = max(LIMITE_SUPERIOR, min(LIMITE_INFERIOR - self.altura, self.y))
        
    def actualizar_altura(self, nueva_altura):
        if self.altura != nueva_altura:
            diferencia = nueva_altura - self.altura
            self.y -= diferencia / 2  
            self.altura = nueva_altura
            # Vuelve a aplicar los nuevos límites de la cancha si el tamaño cambia
            self.y = max(LIMITE_SUPERIOR, min(LIMITE_INFERIOR - self.altura, self.y))

class Pelota:
    def __init__(self):
        self.radio = RADIO_PELOTA
        self.reset()

    def reset(self, hacia_derecha=True):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.radio = RADIO_PELOTA
        direccion_x = 1 if hacia_derecha else -1
        self.vel_x = VEL_PELOTA_BASE * direccion_x
        self.vel_y = VEL_PELOTA_BASE * random.uniform(-0.6, 0.6)

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def rect(self):
        return pygame.Rect(
            self.x - self.radio, self.y - self.radio,
            self.radio * 2, self.radio * 2
        )

class PowerUp:
    def __init__(self):
        self.activo = False
        self.x = 0
        self.y = 0
        self.tipo = None
        self.tamano = 45
        self.rect = pygame.Rect(0, 0, self.tamano, self.tamano)
        
    def generar(self, tipos_disponibles):
        self.x = random.randint(WIDTH // 4, (WIDTH * 3) // 4 - self.tamano)
        # Limita el spawn del powerup a los bordes blancos
        self.y = random.randint(LIMITE_SUPERIOR, LIMITE_INFERIOR - self.tamano)
        self.tipo = random.choice(tipos_disponibles)
        self.rect.topleft = (self.x, self.y)
        self.activo = True

# Declaración de funciones
def pantalla_inicio(pantalla, reloj):
    fuente_titulo = pygame.font.SysFont("consolas", 72, bold=True)
    fuente_opciones = pygame.font.SysFont("consolas", 32, bold=True)
    
    try:
        logo = pygame.image.load("./img/Logo.png")
        pygame.display.set_icon(logo)
    except: pass

    opciones = ["Multijugador - Online", "Salir"]
    seleccion_actual = 0  
    corriendo_menu = True
    
    while corriendo_menu:
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    seleccion_actual = (seleccion_actual - 1) % len(opciones)
                elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    seleccion_actual = (seleccion_actual + 1) % len(opciones)
                elif evento.key == pygame.K_RETURN:
                    if seleccion_actual == 0:
                        return
                    elif seleccion_actual == 1:
                        pygame.quit()
                        sys.exit()

        pantalla.fill((10, 15, 25))
        titulo_sombra = fuente_titulo.render("PONG ONLINE", True, (100, 100, 100))
        titulo_principal = fuente_titulo.render("PONG ONLINE", True, (255, 255, 255))
        pantalla.blit(titulo_sombra, (WIDTH // 2 - titulo_principal.get_width() // 2 + 3, HEIGHT // 4 + 3))
        pantalla.blit(titulo_principal, (WIDTH // 2 - titulo_principal.get_width() // 2, HEIGHT // 4))

        espacio_entre_opciones = 60
        inicio_y = HEIGHT // 2
        
        for indice, texto_opcion in enumerate(opciones):
            if indice == seleccion_actual:
                texto_a_mostrar = f"> {texto_opcion} <"
                color_texto = (255, 255, 255)
            else:
                texto_a_mostrar = texto_opcion
                color_texto = (100, 120, 140)

            superficie_texto = fuente_opciones.render(texto_a_mostrar, True, color_texto)
            pos_x = WIDTH // 2 - superficie_texto.get_width() // 2
            pos_y = inicio_y + (indice * espacio_entre_opciones)
            pantalla.blit(superficie_texto, (pos_x, pos_y))

        pygame.display.flip()

def adaptar_fondo(imagen, ancho_destino, alto_destino):
    ancho_img = imagen.get_width()
    alto_img = imagen.get_height()
    
    proporcion_img = ancho_img / alto_img
    proporcion_destino = ancho_destino / alto_destino
    
    if proporcion_img > proporcion_destino:
        nuevo_alto = alto_destino
        nuevo_ancho = int(nuevo_alto * proporcion_img)
    else:
        nuevo_ancho = ancho_destino
        nuevo_alto = int(nuevo_ancho / proporcion_img)
        
    img_escalada = pygame.transform.smoothscale(imagen, (nuevo_ancho, nuevo_alto))
    
    superficie_final = pygame.Surface((ancho_destino, alto_destino))
    x_offset = (ancho_destino - nuevo_ancho) // 2
    y_offset = (alto_destino - nuevo_alto) // 2
    superficie_final.blit(img_escalada, (x_offset, y_offset))
    
    return superficie_final
    
def menu_fondos(pantalla, reloj):
    fuente_titulo = pygame.font.SysFont("consolas", 42, bold=True)
    fuente_instruccion = pygame.font.SysFont("consolas", 22)
    
    rutas_fondos = ["img/fondo1.png", "img/fondo2.png", "img/fondo3.png"]
    imagenes_fondos = []
    
    for ruta in rutas_fondos:
        try:
            img = pygame.image.load(ruta).convert()
            img = adaptar_fondo(img, WIDTH, HEIGHT)
            imagenes_fondos.append(img)
        except Exception as e:
            superficie = pygame.Surface((WIDTH, HEIGHT))
            superficie.fill(BLACK)
            imagenes_fondos.append(superficie)
            
    seleccion_actual = 0
    ejecutando = True
    
    while ejecutando:
        reloj.tick(FPS)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT or evento.key == pygame.K_a:
                    seleccion_actual = (seleccion_actual - 1) % len(imagenes_fondos)
                elif evento.key == pygame.K_RIGHT or evento.key == pygame.K_d:
                    seleccion_actual = (seleccion_actual + 1) % len(imagenes_fondos)
                elif evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    return imagenes_fondos[seleccion_actual]

        pantalla.blit(imagenes_fondos[seleccion_actual], (0, 0))
        
        capa_oscura = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
        capa_oscura.fill((0, 0, 0, 160))
        pantalla.blit(capa_oscura, (0, 0))
        pantalla.blit(capa_oscura, (0, HEIGHT - 70))
        
        texto_titulo = fuente_titulo.render(f"ELIGE TU FONDO ({seleccion_actual + 1}/{len(imagenes_fondos)})", True, WHITE)
        pantalla.blit(texto_titulo, (WIDTH // 2 - texto_titulo.get_width() // 2, 20))
        
        texto_instruccion = fuente_instruccion.render("< FLECHAS: Cambiar  |  ENTER: Seleccionar >", True, YELLOW)
        pantalla.blit(texto_instruccion, (WIDTH // 2 - texto_instruccion.get_width() // 2, HEIGHT - 50))
        
        pygame.display.flip()

def menu_multijugador(pantalla, reloj):
    fuente_titulo = pygame.font.SysFont("consolas", 36)
    fuente_interfaz = pygame.font.SysFont("consolas", 22)
    
    input_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 40)
    color_input_activo = CYAN
    color_input_inactivo = GRAY
    color_input = color_input_inactivo
    activo = False
    ip_texto = "127.0.0.1"
    
    boton_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 45)
    color_boton = YELLOW
    
    ejecutando_menu = True
    while ejecutando_menu:
        reloj.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(evento.pos):
                    activo = True
                else:
                    activo = False
                    
                if boton_rect.collidepoint(evento.pos):
                    return ip_texto.strip()
                    
            if evento.type == pygame.KEYDOWN:
                if activo:
                    if evento.key == pygame.K_RETURN:
                        return ip_texto.strip()
                    elif evento.key == pygame.K_BACKSPACE:
                        ip_texto = ip_texto[:-1]
                    else:
                        if len(ip_texto) < 15:
                            ip_texto += evento.unicode
                            
        color_input = color_input_activo if activo else color_input_inactivo
        
        pantalla.fill(BLACK)
        txt_titulo = fuente_titulo.render("MODO MULTIJUGADOR", True, WHITE)
        pantalla.blit(txt_titulo, (WIDTH // 2 - txt_titulo.get_width() // 2, HEIGHT // 2 - 140))
        
        txt_label = fuente_interfaz.render("IP del Servidor:", True, WHITE)
        pantalla.blit(txt_label, (input_rect.x, input_rect.y - 30))
        
        pygame.draw.rect(pantalla, color_input, input_rect, 2, border_radius=5)
        txt_ip = fuente_interfaz.render(ip_texto, True, WHITE)
        pantalla.blit(txt_ip, (input_rect.x + 10, input_rect.y + 8))
        
        color_render_boton = (max(0, color_boton[0]-40), max(0, color_boton[1]-40), max(0, color_boton[2]-40)) if boton_rect.collidepoint(mouse_pos) else color_boton
        pygame.draw.rect(pantalla, color_render_boton, boton_rect, border_radius=5)
        
        txt_boton = fuente_interfaz.render("CONECTAR", True, BLACK)
        pantalla.blit(txt_boton, (boton_rect.x + (boton_rect.width // 2 - txt_boton.get_width() // 2), boton_rect.y + 11))
        
        pygame.display.flip()

def limitar_vel(pelota):
    pelota.vel_x = max(-VEL_PELOTA_MAX, min(VEL_PELOTA_MAX, pelota.vel_x))
    pelota.vel_y = max(-VEL_PELOTA_MAX, min(VEL_PELOTA_MAX, pelota.vel_y))

def rebotar_en_paleta(pelota, paleta):
    pelota.vel_x *= -1.08
    centro_paleta = paleta.y + paleta.altura / 2
    offset = (pelota.y - centro_paleta) / (paleta.altura / 2)  
    pelota.vel_y = VEL_PELOTA_BASE * offset * 1.6
    limitar_vel(pelota)
    return None

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong Online")
    
    try:
        logo = pygame.image.load("./img/Logo.png")
        pygame.display.set_icon(logo)
    except: pass
    
    reloj = pygame.time.Clock()
    
    imagenes_powerups = {}
    tamano_icono = (45, 45)
    
    rutas_imagenes = {
        "velocidad_x2": "img/Velocidad.png",
        "3_pelotas": "img/3pelotas.png",
        "bola_grande": "img/bola grande.jpg",
        "hielo": "img/Hielo.png",
        "lentitud": "img/Lentitud.png",
        "multiplicador": "img/multiplicador de puntos.png",
        "paleta_larga": "img/PaletaLarga.png",
        "pared": "img/Pared.png"
    }
    
    for mod, ruta in rutas_imagenes.items():
        try:
            img = pygame.image.load(ruta).convert_alpha()
            imagenes_powerups[mod] = pygame.transform.scale(img, tamano_icono)
        except Exception as e:
            pass

    while True:
        pantalla_inicio(pantalla, reloj)
        imagen_fondo = menu_fondos(pantalla, reloj)
        ip = menu_multijugador(pantalla, reloj)
        
        red = RedCliente(server_ip=ip)
        red.conectar()
        
        if not red.conectado or red.player_num is None:
            fuente_error = pygame.font.SysFont("consolas", 20)
            pantalla.fill(BLACK)
            txt_err1 = fuente_error.render("ERROR: No se pudo conectar al servidor.", True, (255, 100, 100))
            txt_err2 = fuente_error.render("Asegurate de que server.py este corriendo.", True, WHITE)
            pantalla.blit(txt_err1, (WIDTH // 2 - txt_err1.get_width() // 2, HEIGHT // 2 - 20))
            pantalla.blit(txt_err2, (WIDTH // 2 - txt_err2.get_width() // 2, HEIGHT // 2 + 10))
            pygame.display.flip()
            
            pygame.time.wait(3000)
            continue
            
        be_host = (red.player_num == 1)
        pygame.display.set_caption(f"Pong Online - Jugador {red.player_num}")
        
        fuente_puntaje = pygame.font.SysFont("consolas", 48)
        fuente_chica = pygame.font.SysFont("consolas", 18)
        
        paleta_1 = Paleta(MARGIN_PALETA)
        paleta_2 = Paleta(WIDTH - MARGIN_PALETA - WIDTH_PALETA)
        pelota = Pelota()
        
        puntaje_1 = 0
        puntaje_2 = 0
        active_modifier = None
        ticks_modificador = 0
        ultimo_golpe = 1  
        mi_paleta = paleta_1 if be_host else paleta_2
        
        powerup_en_cancha = PowerUp()
        
        tipos_powerups_activos = ["velocidad_x2", "lentitud", "bola_grande", "paleta_larga"]
        ticks_spawn = random.randint(FPS * 3, FPS * 8)

        corriendo = True
        pausado = False
        en_cuenta_pausa = False
        en_cuenta_reanudar = False
        ticks_contador = 0
        
        opciones_menu = ["Reanudar", "Menu Principal"]
        indice_seleccionado = 0
        
        while corriendo:
            reloj.tick(FPS)
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_p and not pausado and not en_cuenta_pausa and not en_cuenta_reanudar:
                        en_cuenta_pausa = True
                        ticks_contador = 180
                        
                    elif pausado and not en_cuenta_reanudar:
                        if evento.key == pygame.K_UP or evento.key == pygame.K_w:
                            indice_seleccionado = (indice_seleccionado - 1) % len(opciones_menu)
                        elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                            indice_seleccionado = (indice_seleccionado + 1) % len(opciones_menu)
                        elif evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                            if indice_seleccionado == 0:
                                pausado = False
                                en_cuenta_reanudar = True
                                ticks_contador = 180
                            elif indice_seleccionado == 1:
                                red.conectado = False
                                try:
                                    red.clientes.close()
                                except:
                                    pass
                                corriendo = False
                                
            if not red.conectado:
                corriendo = False
                
            if en_cuenta_pausa:
                ticks_contador -= 1
                if ticks_contador <= 0:
                    en_cuenta_pausa = False
                    pausado = True
                    indice_seleccionado = 0
                    
            if en_cuenta_reanudar:
                ticks_contador -= 1
                if ticks_contador <= 0:
                    en_cuenta_reanudar = False
                    
            if not pausado and not en_cuenta_reanudar:
                teclas = pygame.key.get_pressed()
                dy = 0
                if teclas[pygame.K_UP] or teclas[pygame.K_w]:
                    dy = -VEL_PALETA
                if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
                    dy = VEL_PALETA
                mi_paleta.move(dy)
                
                datos_recibidos = red.datos_recibidos
                
                if be_host:
                    y_rival = datos_recibidos.get("jugador_y")
                    if y_rival is not None:
                        paleta_2.y = max(LIMITE_SUPERIOR, min(LIMITE_INFERIOR - paleta_2.altura, y_rival))

                    pelota.move()
                    
                    # Rebote contra los nuevos límites de la cancha
                    if pelota.y - pelota.radio <= LIMITE_SUPERIOR:
                        pelota.y = LIMITE_SUPERIOR + pelota.radio
                        pelota.vel_y *= -1
                    elif pelota.y + pelota.radio >= LIMITE_INFERIOR:
                        pelota.y = LIMITE_INFERIOR - pelota.radio
                        pelota.vel_y *= -1

                    if pelota.vel_x < 0 and pelota.rect().colliderect(paleta_1.rect()):
                        rebotar_en_paleta(pelota, paleta_1)
                        ultimo_golpe = 1
                    elif pelota.vel_x > 0 and pelota.rect().colliderect(paleta_2.rect()):
                        rebotar_en_paleta(pelota, paleta_2)
                        ultimo_golpe = 2

                    if pelota.x + pelota.radio < 0:
                        puntaje_2 += 1
                        pelota.reset(hacia_derecha=True)
                        paleta_1.actualizar_altura(HEIGHT_PALETA)
                        paleta_2.actualizar_altura(HEIGHT_PALETA)
                    elif pelota.x - pelota.radio > WIDTH:
                        puntaje_1 += 1
                        pelota.reset(hacia_derecha=False)
                        paleta_1.actualizar_altura(HEIGHT_PALETA)
                        paleta_2.actualizar_altura(HEIGHT_PALETA)

                    # --- LÓGICA DE POWER-UPS ---
                    modificador_tocado = None
                    if not powerup_en_cancha.activo:
                        ticks_spawn -= 1
                        if ticks_spawn <= 0:
                            powerup_en_cancha.generar(tipos_powerups_activos)
                    else:
                        if pelota.rect().colliderect(powerup_en_cancha.rect):
                            modificador_tocado = powerup_en_cancha.tipo
                            powerup_en_cancha.activo = False
                            ticks_spawn = random.randint(FPS * 5, FPS * 12)
                            
                            if modificador_tocado == "velocidad_x2":
                                pelota.vel_x *= 1.5
                                pelota.vel_y *= 1.5
                            elif modificador_tocado == "lentitud":
                                pelota.vel_x *= 0.6
                                pelota.vel_y *= 0.6
                            elif modificador_tocado == "bola_grande":
                                pelota.radio = 22
                            elif modificador_tocado == "paleta_larga":
                                if ultimo_golpe == 1:
                                    paleta_1.actualizar_altura(180)
                                else:
                                    paleta_2.actualizar_altura(180)

                    estado = {
                        "jugador1_y": paleta_1.y,
                        "jugador2_y": paleta_2.y,
                        "pelota_x": pelota.x,
                        "pelota_y": pelota.y,
                        "puntaje1": puntaje_1,
                        "puntaje2": puntaje_2,
                        "modificador_tocado": modificador_tocado,
                        "pw_activo": powerup_en_cancha.activo,
                        "pw_x": powerup_en_cancha.x,
                        "pw_y": powerup_en_cancha.y,
                        "pw_tipo": powerup_en_cancha.tipo,
                        "p1_altura": paleta_1.altura,
                        "p2_altura": paleta_2.altura,
                        "pelota_radio": pelota.radio
                    }
                    red.enviar_datos(estado)
                else:
                    red.enviar_datos({"jugador_y": paleta_2.y})
                    
                    paleta_1.actualizar_altura(datos_recibidos.get("p1_altura", HEIGHT_PALETA))
                    paleta_2.actualizar_altura(datos_recibidos.get("p2_altura", HEIGHT_PALETA))
                    pelota.radio = datos_recibidos.get("pelota_radio", RADIO_PELOTA)
                    
                    paleta_1.y = datos_recibidos.get("jugador1_y", paleta_1.y)
                    pelota.x = datos_recibidos.get("pelota_x", pelota.x)
                    pelota.y = datos_recibidos.get("pelota_y", pelota.y)
                    puntaje_1 = datos_recibidos.get("puntaje1", puntaje_1)
                    puntaje_2 = datos_recibidos.get("puntaje2", puntaje_2)
                    modificador_tocado = datos_recibidos.get("modificador_tocado")
                    
                    powerup_en_cancha.activo = datos_recibidos.get("pw_activo", False)
                    powerup_en_cancha.x = datos_recibidos.get("pw_x", 0)
                    powerup_en_cancha.y = datos_recibidos.get("pw_y", 0)
                    powerup_en_cancha.tipo = datos_recibidos.get("pw_tipo", None)
                    if powerup_en_cancha.activo:
                        powerup_en_cancha.rect.topleft = (powerup_en_cancha.x, powerup_en_cancha.y)
                        
                if modificador_tocado:
                    active_modifier = modificador_tocado
                    ticks_modificador = FPS
            else:
                if be_host:
                    red.enviar_datos({
                        "jugador1_y": paleta_1.y, "jugador2_y": paleta_2.y,
                        "pelota_x": pelota.x, "pelota_y": pelota.y,
                        "puntaje1": puntaje_1, "puntaje2": puntaje_2,
                        "modificador_tocado": None,
                        "pw_activo": powerup_en_cancha.activo,
                        "pw_x": powerup_en_cancha.x,
                        "pw_y": powerup_en_cancha.y,
                        "pw_tipo": powerup_en_cancha.tipo,
                        "p1_altura": paleta_1.altura,
                        "p2_altura": paleta_2.altura,
                        "pelota_radio": pelota.radio
                    })
                else:
                    red.enviar_datos({"jugador_y": paleta_2.y})

            # Rendering Gráfico Modificado
            if imagen_fondo:
                pantalla.blit(imagen_fondo, (0, 0))
            else:
                pantalla.fill(BLACK)
                
            # --- DIBUJADO DE LÍMITES BLANCOS ---
            pygame.draw.rect(pantalla, WHITE, (0, LIMITE_SUPERIOR - 5, WIDTH, 5))
            pygame.draw.rect(pantalla, WHITE, (0, LIMITE_INFERIOR, WIDTH, 5))
            
            # --- DIBUJADO DE LA LÍNEA CENTRAL ---
            # Ahora la línea central solo abarca entre las dos líneas blancas
            pygame.draw.line(pantalla, WHITE, (WIDTH // 2, LIMITE_SUPERIOR), (WIDTH // 2, LIMITE_INFERIOR), 2)
            
            pygame.draw.rect(pantalla, CYAN, paleta_1.rect())
            pygame.draw.rect(pantalla, YELLOW, paleta_2.rect())
            pygame.draw.circle(pantalla, WHITE, (int(pelota.x), int(pelota.y)), int(pelota.radio))
            
            if powerup_en_cancha.activo and powerup_en_cancha.tipo in imagenes_powerups:
                pantalla.blit(imagenes_powerups[powerup_en_cancha.tipo], powerup_en_cancha.rect.topleft)
                
            texto_puntaje = fuente_puntaje.render(f"{puntaje_1}   {puntaje_2}", True, WHITE)
            pantalla.blit(texto_puntaje, (WIDTH // 2 - texto_puntaje.get_width() // 2, 20))
            
            estado_conexion = "Conectado" if red.conectado else "Desconectado"
            texto_estado = fuente_chica.render(estado_conexion, True, WHITE)
            pantalla.blit(texto_estado, (10, 10))
            
            if not pausado and not en_cuenta_reanudar and ticks_modificador > 0:
                ticks_modificador -= 1
                texto_mod = fuente_chica.render(f"Modificador: {active_modifier}", True, YELLOW)
                pantalla.blit(texto_mod, (WIDTH // 2 - texto_mod.get_width() // 2, HEIGHT - 30))
                
                if active_modifier in imagenes_powerups:
                    icono = imagenes_powerups[active_modifier]
                    pos_x = WIDTH // 2 - icono.get_width() // 2
                    pos_y = HEIGHT - 30 - icono.get_height() - 10
                    pantalla.blit(icono, (pos_x, pos_y))
                    
            if en_cuenta_pausa:
                segundo_actual = (ticks_contador // 60) + 1
                texto_timer = fuente_puntaje.render(f"Pausa en: {segundo_actual}", True, YELLOW)
                pantalla.blit(texto_timer, (WIDTH // 2 - texto_timer.get_width() // 2, HEIGHT // 2 - 150))
                
            if en_cuenta_reanudar:
                segundo_actual = (ticks_contador // 60) + 1
                texto_timer = fuente_puntaje.render(f"Reanudando en: {segundo_actual}", True, CYAN)
                pantalla.blit(texto_timer, (WIDTH // 2 - texto_timer.get_width() // 2, HEIGHT // 2 - 50))
                
            if pausado:
                superficie_pausa = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                superficie_pausa.fill((0, 0, 0, 180))
                pantalla.blit(superficie_pausa, (0, 0))
                
                texto_pausa = fuente_puntaje.render("JUEGO PAUSADO", True, YELLOW)
                pantusa_pos = (WIDTH // 2 - texto_pausa.get_width() // 2, HEIGHT // 2 - 140)
                pantalla.blit(texto_pausa, pantusa_pos)
                
                for i, opcion in enumerate(opciones_menu):
                    if i == indice_seleccionado:
                        texto_opc = fuente_chica.render(f"> {opcion} <", True, CYAN)
                    else:
                        texto_opc = fuente_chica.render(opcion, True, WHITE)
                    pantalla.blit(texto_opc, (WIDTH // 2 - texto_opc.get_width() // 2, HEIGHT // 2 - 20 + (i * 40)))
                    
            pygame.display.flip()

if __name__ == "__main__":
    main()