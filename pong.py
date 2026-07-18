import sys
import random
import pygame
from client import RedCliente

# Config
WIDTH, HEIGHT = 800, 600
FPS = 60

HEIGHT_PALETA = 100
WIDTH_PALETA = 15
MARGIN_PALETA = 30
VEL_PALETA = 7

RADIO_PELOTA = 9
VEL_PELOTA_BASE = 5
VEL_PELOTA_MAX = 15

WHITE = (240, 240, 240)
BLACK = (12, 12, 18)
GRAY = (60, 60, 70)
CYAN = (80, 220, 255)
YELLOW = (255, 210, 60)

# Class declaration

class Paleta:
    def __init__(self, x):
        self.x = x
        self.y = HEIGHT / 2 - HEIGHT_PALETA / 2

    def rect(self):
        return pygame.Rect(self.x, self.y, WIDTH_PALETA, HEIGHT_PALETA)

    def move(self, dy):
        self.y += dy
        self.y = max(0, min(HEIGHT - HEIGHT_PALETA, self.y))


class Pelota:
    def __init__(self):
        self.reset()

    def reset(self, hacia_derecha=True):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        direccion_x = 1 if hacia_derecha else -1
        self.vel_x = VEL_PELOTA_BASE * direccion_x
        self.vel_y = VEL_PELOTA_BASE * random.uniform(-0.6, 0.6)

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def rect(self):
        return pygame.Rect(
            self.x - RADIO_PELOTA, self.y - RADIO_PELOTA,
            RADIO_PELOTA * 2, RADIO_PELOTA * 2
        )

# Main function declaration

def pantalla_inicio(pantalla, reloj):
    # Fuente gigante para el título del juego
    fuente_titulo = pygame.font.SysFont("consolas", 72, bold=True)
    # Fuente mediana para las opciones ("Multijugador", "Salir")
    fuente_opciones = pygame.font.SysFont("consolas", 32, bold=True)

    logo = pygame.image.load("./img/Logo.png")
    pygame.display.set_icon(logo)
   #menu configuracion
    # Lista con los textos de las opciones disponibles
    opciones = ["Multijugador - Online", "Salir"]
    # Variable para saber qué opción está resaltada. Empieza en 0 ("Multijugador - Online")
    seleccion_actual = 0  

    corriendo_menu = True  # bucle del menu 
    
    #bucle menu princiapl
    while corriendo_menu:
        reloj.tick(FPS)  # Hace que el menú corra a la misma velocidad que el juego (ej: 60 FPS)
        
        #CONTROL DE EVENTOS
        for evento in pygame.event.get(): #el pygame.ev... revisa las acciones y vacia las acciones pendientes mediante una cola para seguir con la otra accion
            # Si el usuario hace clic en la "X" roja de la ventana para cerrarla
            if evento.type == pygame.QUIT:
                pygame.quit()  # Apaga Pygame
                sys.exit()     # Cierra el programa por completo
                
            #asignacion de teclas
            if evento.type == pygame.KEYDOWN:
                # si presiona la flecha arriba o la tecla "w"
                if evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    # resta 1 a la selección. El "% len(opciones)" hace que si subes estando en el primero, salte al último.
                    seleccion_actual = (seleccion_actual - 1) % len(opciones)
                
                # si presiona la flecha abajo o la tecla "s"
                elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    # suma 1 a la selección. Si bajas estando en el último, salta al primero.
                    seleccion_actual = (seleccion_actual + 1) % len(opciones)
                
                # si presiona la tecla ENTER (RETURN)
                elif evento.key == pygame.K_RETURN:
                    # Verifica cuál es el número de la opción seleccionada actualmente
                    if seleccion_actual == 0:  # Opción 0 es "Multijugador - Online"
                        return  # Rompe esta función, saliendo del menú para que inicie main() donde se ubica el juego 
                    elif seleccion_actual == 1:  # Opción 1 es "Salir"
                        pygame.quit()  # Apaga Pygame
                        sys.exit()     # Cierra el programa por completo

        #diseño de panatalla
        #cambia todo el fondo de la ventana de un color azul oscuro
        pantalla.fill((10, 15, 25)) 
        # Renderiza el texto gris que usaremos como sombra
        titulo_sombra = fuente_titulo.render("PONG ONLINE", True, (100, 100, 100))
        # Renderiza el texto blanco que irá por encima
        titulo_principal = fuente_titulo.render("PONG ONLINE", True, (255, 255, 255)) 
        
        # pega la sombra corrida 3 píxeles hacia la derecha y abajo (+3)
        pantalla.blit(titulo_sombra, (WIDTH // 2 - titulo_principal.get_width() // 2 + 3, HEIGHT // 4 + 3))#blit copia y pega sobre la otra
        #width // es a la mitad de la pantalla - titulo...get_width //2 es para restarle la mitad del ancho del titulo para acomodarlo y el +3 para interfacial de la sombra y no se tape todo
        #heigt // 4 para ubicarlo en la parte superior diviendo la altura en 4 partes dejandola en la parte superior y +3 para la sombra 
        pantalla.blit(titulo_principal, (WIDTH // 2 - titulo_principal.get_width() // 2, HEIGHT // 4))#aca el blit pega sobre la sombra para el diseño
        #width // es a la mitad de la pantalla - titulo...get_width //2 es para restarle la mitad del ancho del titulo para acomodarlo sin +3 para no tapar la sombra
        #heigt // 4 para ubicarlo en la parte superior diviendo la altura en 4 partes dejandola en la parte superior y sin +3 para no tapar la sombra
        espacio_entre_opciones = 60  # Distancia en píxeles entre cada opción hacia abajo
        inicio_y = HEIGHT // 2       # Altura en la pantalla donde empezará a dibujarse la primera opción

        # Recorremos la lista. 'indice' es el número (0 o 1) y 'texto_opcion' es el texto real
        for indice, texto_opcion in enumerate(opciones):
            
            # Si el índice que estamos dibujando coincide con el que el usuario tiene seleccionado...
            if indice == seleccion_actual:
                # Le agregamos las flechitas a los costados
                texto_a_mostrar = f"> {texto_opcion} <"
                # Le asignamos el color blanco 
                color_texto = (255, 255, 255) 
            
            # Si NO es el que el usuario tiene seleccionado...
            else:
                # Dejamos el texto tal cual (sin flechas)
                texto_a_mostrar = texto_opcion
                # Le asignamos un gris apagado para que quede en segundo plano
                color_texto = (100, 120, 140) 

            # Renderizamos el texto final de la opción con el color que le tocó
            superficie_texto = fuente_opciones.render(texto_a_mostrar, True, color_texto)
            
            # Calculamos su posición X para que quede centrado
            pos_x = WIDTH // 2 - superficie_texto.get_width() // 2
            # Calculamos su posición Y multiplicando su índice por el espacio, para que queden uno debajo del otro
            pos_y = inicio_y + (indice * espacio_entre_opciones)#para delimitar que las opciones cumplan con el es espacio de 60 pixeles = 0 * 60 = 0 inicio- 1 * 60 = 1 espacio
            
            # Pegamos el texto de esta opción en la pantalla
            pantalla.blit(superficie_texto, (pos_x, pos_y))# ponemos en pantalla las opciones con los espacios definidos con el calculo anterior

        #Muestra todo lo que acabamos de dibujar al usuario actualizando el monitor
        pygame.display.flip()


def menu_multijugador(pantalla, reloj):
    # Fuentes para los textos del submenú de red
    fuente_titulo = pygame.font.SysFont("consolas", 36)
    fuente_interfaz = pygame.font.SysFont("consolas", 22)

    # Crea el rectángulo del cuadro de texto para ingresar la IP
    input_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 40)
    color_input_activo = CYAN
    color_input_inactivo = GRAY
    color_input = color_input_inactivo
    activo = False  # Indica si el usuario hizo clic dentro de la caja de texto para escribir
    ip_texto = "127.0.0.1"  # Valor por defecto (Localhost)

    # Crea el rectángulo del botón "CONECTAR"
    boton_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 45)
    color_boton = YELLOW

    ejecutando_menu = True
    while ejecutando_menu:
        reloj.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()  # Obtiene las coordenadas del puntero del mouse

        # Captura las interacciones en el menú de la IP
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Control de clics del mouse
            if evento.type == pygame.MOUSEBUTTONDOWN:
                # Si hace clic dentro del cuadro gris, se activa la escritura
                if input_rect.collidepoint(evento.pos):
                    activo = True
                else:
                    activo = False

                # Si hace clic arriba del botón amarillo, envía la IP ingresada y avanza
                if boton_rect.collidepoint(evento.pos):
                    return ip_texto.strip()

            # Control de escritura por teclado
            if evento.type == pygame.KEYDOWN:
                if activo:
                    if evento.key == pygame.K_RETURN:  # ENTER también sirve para conectar
                        return ip_texto.strip()
                    elif evento.key == pygame.K_BACKSPACE:  # Borra el último caracter escrito
                        ip_texto = ip_texto[:-1]
                    else:
                        # Si no superó los 15 caracteres (límite máximo de una IP), agrega lo tipeado
                        if len(ip_texto) < 15:
                            ip_texto += evento.unicode

        # Cambia el color del borde del cuadro si está seleccionado para escribir
        color_input = color_input_activo if activo else color_input_inactivo

        # Renderizado gráfico de la interfaz del submenú
        pantalla.fill(BLACK)
        txt_titulo = fuente_titulo.render("MODO MULTIJUGADOR", True, WHITE)
        pantalla.blit(txt_titulo, (WIDTH // 2 - txt_titulo.get_width() // 2, HEIGHT // 2 - 140))

        txt_label = fuente_interfaz.render("IP del Servidor:", True, WHITE)
        pantalla.blit(txt_label, (input_rect.x, input_rect.y - 30))

        # Dibuja la caja de texto y le introduce la string de la IP actual
        pygame.draw.rect(pantalla, color_input, input_rect, 2, border_radius=5)
        txt_ip = fuente_interfaz.render(ip_texto, True, WHITE)
        pantalla.blit(txt_ip, (input_rect.x + 10, input_rect.y + 8))

        # Efecto visual: Si el mouse está sobre el botón, este se vuelve ligeramente más oscuro
        color_render_boton = (max(0, color_boton[0]-40), max(0, color_boton[1]-40), max(0, color_boton[2]-40)) if boton_rect.collidepoint(mouse_pos) else color_boton
        pygame.draw.rect(pantalla, color_render_boton, boton_rect, border_radius=5)
        
        # Centra y pega el texto adentro del botón "CONECTAR"
        txt_boton = fuente_interfaz.render("CONECTAR", True, BLACK)
        pantalla.blit(txt_boton, (boton_rect.x + (boton_rect.width // 2 - txt_boton.get_width() // 2), boton_rect.y + 11))

        pygame.display.flip()


def limitar_vel(pelota):
    pelota.vel_x = max(-VEL_PELOTA_MAX, min(VEL_PELOTA_MAX, pelota.vel_x))
    pelota.vel_y = max(-VEL_PELOTA_MAX, min(VEL_PELOTA_MAX, pelota.vel_y))


def rebotar_en_paleta(pelota, paleta):
    pelota.vel_x *= -1.08
    centro_paleta = paleta.y + HEIGHT_PALETA / 2
    offset = (pelota.y - centro_paleta) / (HEIGHT_PALETA / 2)  # -1 a 1
    pelota.vel_y = VEL_PELOTA_BASE * offset * 1.6
    limitar_vel(pelota)

    # si la pelota es mas rapida que el arranque, queda como "modificador" para avisarle al otro cliente y mostrarlo en pantalla
    if abs(pelota.vel_x) > VEL_PELOTA_BASE * 1.8:
        return "velocidad_x2"
    return None


def main():
    # Inicialización centralizada de Pygame para mantener viva una única ventana gráfica
    pygame.init()
    pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong Online")
    logo = pygame.image.load("./img/Logo.png")
    pygame.display.set_icon(logo)
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
            # Cargamos la imagen con soporte de transparencia y la escalamos
            img = pygame.image.load(ruta).convert_alpha()
            imagenes_powerups[mod] = pygame.transform.scale(img, tamano_icono)
        except Exception as e:
            print(f"Advertencia: No se pudo cargar {ruta} -> {e}")

    # Bucle infinito estructural: Mantiene el flujo activo permitiendo ciclar entre menús y partidas recurrentemente
    while True:
        pantalla_inicio(pantalla, reloj)  # Llama a la portada del juego pasándole la ventana única
        ip = menu_multijugador(pantalla, reloj)  # Pasa al menú de IP y rescata el string resultante
        
        # Configuración del socket del cliente e intento de conexión
        red = RedCliente(server_ip=ip)
        red.conectar()

        # Si el servidor no está encendido o rechaza la conexión, despliega pantalla de error integrada
        if not red.conectado or red.player_num is None:
            fuente_error = pygame.font.SysFont("consolas", 20)
            pantalla.fill(BLACK)
            txt_err1 = fuente_error.render("ERROR: No se pudo conectar al servidor.", True, (255, 100, 100))
            txt_err2 = fuente_error.render("Asegurate de que server.py este corriendo.", True, WHITE)
            pantalla.blit(txt_err1, (WIDTH // 2 - txt_err1.get_width() // 2, HEIGHT // 2 - 20))
            pantalla.blit(txt_err2, (WIDTH // 2 - txt_err2.get_width() // 2, HEIGHT // 2 + 10))
            pygame.display.flip()
            
            pygame.time.wait(3000)  # Sostiene el error por 3 segundos
            continue  # Reinicia el bucle estructural, regresando directamente a la pantalla de inicio

        be_host = (red.player_num == 1)
        print(f"Eres el jugador {red.player_num} ({'host simulates the ball' if be_host else 'invitado'})")

        pygame.display.set_caption(f"Pong Online - Jugador {red.player_num}")
        fuente_puntaje = pygame.font.SysFont("consolas", 48)
        fuente_chica = pygame.font.SysFont("consolas", 18)

        paleta_1 = Paleta(MARGIN_PALETA)  # left player one
        paleta_2 = Paleta(WIDTH - MARGIN_PALETA - WIDTH_PALETA)  # right player two
        pelota = Pelota()

        puntaje_1 = 0
        puntaje_2 = 0

        active_modifier = None
        ticks_modificador = 0

        mi_paleta = paleta_1 if be_host else paleta_2

        # Variables de estado internas para el control del bucle de juego y pausas interactivas
        corriendo = True
        pausado = False
        
        en_cuenta_pausa = False    # Alerta visual previa a congelar la simulación
        en_cuenta_reanudar = False # Cuenta regresiva para reanudar dinámicamente el juego
        ticks_contador = 0         # Almacena los frames remanentes de los temporizadores (60 ticks = 1 segundo)

        # Configuración de las opciones del menú superpuesto de pausa
        opciones_menu = ["Reanudar", "Menu Principal"]
        indice_seleccionado = 0

        # Bucle de simulación del partido activo
        while corriendo:
            reloj.tick(FPS)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if evento.type == pygame.KEYDOWN:
                    # Si se presiona la tecla 'P' y el juego corre normalmente, inicia pre-pausa cronometrada
                    if evento.key == pygame.K_p and not pausado and not en_cuenta_pausa and not en_cuenta_reanudar:
                        en_cuenta_pausa = True
                        ticks_contador = 180  # Define 3 segundos de margen (180 ticks / 60 FPS)
                    
                    # Controles de navegación de opciones dentro del estado de pausa
                    elif pausado and not en_cuenta_reanudar:
                        if evento.key == pygame.K_UP or evento.key == pygame.K_w:
                            indice_seleccionado = (indice_seleccionado - 1) % len(opciones_menu)
                        elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                            indice_seleccionado = (indice_seleccionado + 1) % len(opciones_menu)
                        
                        # Ejecución de la opción resaltada en la pausa al pulsar ENTER o ESPACIO
                        elif evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                            if indice_seleccionado == 0:  # Opción: Reanudar
                                pausado = False
                                en_cuenta_reanudar = True
                                ticks_contador = 180  # Da 3 segundos para reacomodar las manos antes de mover la pelota
                            elif indice_seleccionado == 1:  # Opción: Volver al Menú Principal
                                red.conectado = False  # Cambia el flag local para detener el hilo de escucha de la red
                                try:
                                    red.clientes.close()  # Apaga el socket TCP de forma limpia
                                except:
                                    pass
                                corriendo = False  # Apaga este bucle, liberando el flujo hacia el While estructural superior

            # Si el servidor se apaga o el rival se desconecta, rompe el partido en curso inmediatamente
            if not red.conectado:
                corriendo = False

            # Decrementa el reloj de la pre-pausa. Al expirar, detiene el partido y despliega el menú
            if en_cuenta_pausa:
                ticks_contador -= 1
                if ticks_contador <= 0:
                    en_cuenta_pausa = False
                    pausado = True
                    indice_seleccionado = 0

            # Decrementa el reloj de la cuenta regresiva previa a reanudar el partido físico
            if en_cuenta_reanudar:
                ticks_contador -= 1
                if ticks_contador <= 0:
                    en_cuenta_reanudar = False

            # Lógica de juego activa (Solo se procesa si no está pausado ni en cuentas regresivas de reanudación)
            if not pausado and not en_cuenta_reanudar:
                teclas = pygame.key.get_pressed()
                dy = 0
                if teclas[pygame.K_UP] or teclas[pygame.K_w]:
                    dy = -VEL_PALETA
                if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
                    dy = VEL_PALETA
                mi_paleta.move(dy)

                datos_recibidos = red.datos_recibidos
                modificador_tocado = None

                if be_host:
                    # Update rival's ball with the last movement
                    y_rival = datos_recibidos.get("jugador_y")
                    if y_rival is not None:
                        paleta_2.y = max(0, min(HEIGHT - HEIGHT_PALETA, y_rival))

                    # Ball physics
                    pelota.move()

                    if pelota.y - RADIO_PELOTA <= 0 or pelota.y + RADIO_PELOTA >= HEIGHT:
                        pelota.vel_y *= -1

                    if pelota.vel_x < 0 and pelota.rect().colliderect(paleta_1.rect()):
                        modificador_tocado = rebotar_en_paleta(pelota, paleta_1)
                    elif pelota.vel_x > 0 and pelota.rect().colliderect(paleta_2.rect()):
                        modificador_tocado = rebotar_en_paleta(pelota, paleta_2)

                    if pelota.x < 0:
                        puntaje_2 += 1
                        pelota.reset(hacia_derecha=True)
                    elif pelota.x > WIDTH:
                        puntaje_1 += 1
                        pelota.reset(hacia_derecha=False)

                    estado = {
                        "jugador1_y": paleta_1.y,
                        "jugador2_y": paleta_2.y,
                        "pelota_x": pelota.x,
                        "pelota_y": pelota.y,
                        "puntaje1": puntaje_1,
                        "puntaje2": puntaje_2,
                        "modificador_tocado": modificador_tocado,
                    }
                    red.enviar_datos(estado)

                else:
                    # guest only sends their screen
                    red.enviar_datos({"jugador_y": paleta_2.y})

                    # and takes the updated state from host
                    paleta_1.y = datos_recibidos.get("jugador1_y", paleta_1.y)
                    pelota.x = datos_recibidos.get("pelota_x", pelota.x)
                    pelota.y = datos_recibidos.get("pelota_y", pelota.y)
                    puntaje_1 = datos_recibidos.get("puntaje1", puntaje_1)
                    puntaje_2 = datos_recibidos.get("puntaje2", puntaje_2)
                    modificador_tocado = datos_recibidos.get("modificador_tocado")

                if modificador_tocado:
                    active_modifier = modificador_tocado
                    ticks_modificador = FPS  # show for 1 sec
            else:
                # Si el juego está en pausa, seguimos enviando datos estáticos para no congelar la red
                if be_host:
                    red.enviar_datos({
                        "jugador1_y": paleta_1.y, "jugador2_y": paleta_2.y,
                        "pelota_x": pelota.x, "pelota_y": pelota.y,
                        "puntaje1": puntaje_1, "puntaje2": puntaje_2,
                        "modificador_tocado": None
                    })
                else:
                    red.enviar_datos({"jugador_y": paleta_2.y})

            # Draw
            pantalla.fill(BLACK)
            pygame.draw.line(pantalla, GRAY, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
            pygame.draw.rect(pantalla, CYAN, paleta_1.rect())
            pygame.draw.rect(pantalla, YELLOW, paleta_2.rect())
            pygame.draw.circle(pantalla, WHITE, (int(pelota.x), int(pelota.y)), RADIO_PELOTA)

            texto_puntaje = fuente_puntaje.render(f"{puntaje_1}   {puntaje_2}", True, WHITE)
            pantalla.blit(texto_puntaje, (WIDTH // 2 - texto_puntaje.get_width() // 2, 20))

            estado_conexion = "Conectado" if red.conectado else "Desconectado"
            texto_estado = fuente_chica.render(estado_conexion, True, GRAY)
            pantalla.blit(texto_estado, (10, 10))

            if not pausado and not en_cuenta_reanudar and ticks_modificador > 0:
                ticks_modificador -= 1
                texto_mod = fuente_chica.render(f"Modificador: {active_modifier}", True, YELLOW)
                pantalla.blit(texto_mod, (WIDTH // 2 - texto_mod.get_width() // 2, HEIGHT - 30))
                if active_modifier in imagenes_powerups:
                    icono = imagenes_powerups[active_modifier]
                    # Centramos el icono horizontalmente
                    pos_x = WIDTH // 2 - icono.get_width() // 2
                    # Posicionamos el icono justo por encima del texto
                    pos_y = HEIGHT - 30 - icono.get_height() - 10
                    pantalla.blit(icono, (pos_x, pos_y))

            # Renderiza el letrero de advertencia previo a congelar el juego
            if en_cuenta_pausa:
                segundo_actual = (ticks_contador // 60) + 1
                texto_timer = fuente_puntaje.render(f"Pausa en: {segundo_actual}", True, YELLOW)
                pantalla.blit(texto_timer, (WIDTH // 2 - texto_timer.get_width() // 2, HEIGHT // 2 - 150))

            # Renderiza los números de la cuenta regresiva antes de volver a mover la pelota
            if en_cuenta_reanudar:
                segundo_actual = (ticks_contador // 60) + 1
                texto_timer = fuente_puntaje.render(f"Reanudando en: {segundo_actual}", True, CYAN)
                pantalla.blit(texto_timer, (WIDTH // 2 - texto_timer.get_width() // 2, HEIGHT // 2 - 50))

            # Renderiza la capa translúcida oscura y las opciones interactivas si el juego está en pausa
            if pausado:
                superficie_pausa = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                superficie_pausa.fill((0, 0, 0, 180))  # Oscurece el juego de fondo de manera sutil
                pantalla.blit(superficie_pausa, (0, 0))
                
                texto_pausa = fuente_puntaje.render("JUEGO PAUSADO", True, YELLOW)
                pantusa_pos = (WIDTH // 2 - texto_pausa.get_width() // 2, HEIGHT // 2 - 140)
                pantalla.blit(texto_pausa, pantusa_pos)

                # Dibuja la lista del menú de pausa alternando colores de selección
                for i, opcion in enumerate(opciones_menu):
                    if i == indice_seleccionado:
                        texto_opc = fuente_chica.render(f"> {opcion} <", True, CYAN)
                    else:
                        texto_opc = fuente_chica.render(opcion, True, WHITE)
                    
                    pantalla.blit(texto_opc, (WIDTH // 2 - texto_opc.get_width() // 2, HEIGHT // 2 - 20 + (i * 40)))

            pygame.display.flip()


if __name__ == "__main__":
    main()