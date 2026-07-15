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
    main()