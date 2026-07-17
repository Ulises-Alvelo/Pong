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

def pantalla_inicio():
    #inicio creacion
    pygame.init()  # Arranca todos los motores internos de Pygame
    pantalla = pygame.display.set_mode((WIDTH, HEIGHT))  #Crea la ventana con las medidas configuradas arriba
    pygame.display.set_caption("Pong Online - Inicio")  #título de la ventana
    reloj = pygame.time.Clock()  # Crea el reloj para controlar los Fotogramas Por Segundo (FPS)necesario para un limite de 60
    
    # Fuente gigante para el título del juego
    fuente_titulo = pygame.font.SysFont("consolas", 72, bold=True)
    # Fuente mediana para las opciones ("Multijugador", "Salir")
    fuente_opciones = pygame.font.SysFont("consolas", 32, bold=True)

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
        #width // es a la mitad de la pantalla - titulo...get_width //2 es para restarle la mitad del ancho del titulo para acomodarlo y el +3 para dibujar bien la sombra y no se tape todo
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


def get_ip():
    ip = input("IP del servidor (Enter para 127.0.0.1): ").strip()
    return ip if ip else "127.0.0.1"


def main():
    ip = get_ip()
    red = RedCliente(server_ip=ip)
    red.conectar()

    if not red.conectado or red.player_num is None:
        print("No se pudo conectar o no se recibio la asignacion de jugador. Cerrando.")
        return

    be_host = (red.player_num == 1)
    print(f"Eres el jugador {red.player_num} ({'host simulates the ball' if be_host else 'invitado'})")

    pygame.init()
    pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Pong Online - Jugador {red.player_num}")
    reloj = pygame.time.Clock()
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

    corriendo = True
    while corriendo:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

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

        if ticks_modificador > 0:
            ticks_modificador -= 1
            texto_mod = fuente_chica.render(f"Modificador: {active_modifier}", True, YELLOW)
            pantalla.blit(texto_mod, (WIDTH // 2 - texto_mod.get_width() // 2, HEIGHT - 30))

        pygame.display.flip()

        if not red.conectado:
            corriendo = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    pantalla_inicio() # Muestra el menú primero
    main()