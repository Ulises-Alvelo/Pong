# Pong
## Proyecto realizado por: Ulises Alvelo, Barbara Gamarra, Thiago Martinez, Benicio Vargas y Brian Villca

Pong multijugador en red.

## Requisitos

- **Python** 3.12+
- **pygame** 2.6.1 (instalado automáticamente en el entorno virtual)

## Instalación

Se debe crear un entorno virtual (utilizando python 3.12.X):

```bash
python -m venv .venv
source .venv/bin/activate
pip install pygame
```

## Cómo ejecutar

Se necesitan **3 terminales** (una para el servidor y dos para los jugadores).

### 1. Iniciar el servidor

```bash
source .venv/bin/activate
python server.py
```

El servidor escucha en `0.0.0.0:5555`, y acepta hasta 2 clientes.

### 2. Iniciar los clientes (jugadores)

En dos terminales distintas, cada una con el entorno virtual activado:

```bash
python pong.py
```

Al iniciar, el juego pedirá la IP del servidor. Si el servidor corre en la misma máquina, presiona Enter para usar `127.0.0.1`.

El **primer cliente** en conectarse es el **Jugador 1 (Host)**. El **segundo** es el **Jugador 2 (Guest)**.

Si un tercer cliente intenta conectarse, recibirá el mensaje `"Sala llena"` y la conexión se rechazará.

## Conexión a un servidor remoto

1. En la máquina servidora, ejecuta `python server.py` (asegúrate de que el puerto `5555` esté abierto en el firewall).
2. En cada máquina cliente, ejecuta `python pong.py` e ingresa la IP del servidor cuando se solicite.

## Controles

| Tecla       | Acción     |
|-------------|------------|
| `W` / `↑`   | Mover arriba |
| `S` / `↓`   | Mover abajo  |
| `ESC`       | Salir del juego |

Ambos jugadores usan las mismas teclas en sus respectivas máquinas.

## Arquitectura

```
┌──────────┐       TCP :5555       ┌──────────┐
│ Cliente 1 │◄────────────────────►│ Cliente 2 │
│ (Jugador 1)│       ┌──────────┐   │ (Jugador 2)│
│  (Host)   │◄──────►│ Servidor │◄─►│  (Guest)  │
│           │  relay │ (solo    │   │           │
│           │        │  reenvía)│   │           │
└──────────┘        └──────────┘   └──────────┘
```

- **Servidor** (`server.py`): Relay TCP sin estado. Reenvía todo lo que recibe de un cliente al otro. No tiene lógica de juego.
- **Cliente** (`client.py`): Clase `RedCliente` que maneja la conexión TCP, envío y recepción de mensajes JSON delimitados por `\n`.
- **Juego** (`pong.py`): Bucle principal con Pygame. El **Jugador 1** es autoritativo: simula la física de la pelota, colisiones y puntuación, y envía el estado completo al otro jugador. El **Jugador 2** solo envía su posición de paleta y renderiza el estado que recibe.

### Protocolo

Los mensajes se codifican como **JSON** seguido de un salto de línea (`\n`).

**Jugador 1 → Servidor → Jugador 2** (cada frame):

```json
{
  "jugador1_y": 250.0,
  "jugador2_y": 250.0,
  "pelota_x": 400.0,
  "pelota_y": 300.0,
  "puntaje1": 2,
  "puntaje2": 1,
  "modificador_tocado": null
}
```

**Jugador 2 → Servidor → Jugador 1** (cada frame):

```json
{"jugador_y": 245.0}
```

## Personalización

Todas las constantes del juego están hardcodeadas en `pong.py`:

| Constante       | Valor |
|----------------|-------|
| Ventana        | 800×600 |
| FPS            | 60    |
| Velocidad paleta | 7 px/frame |
| Velocidad pelota | 5 px/frame |
| Vel. máxima    | 15 px/frame |
| Puerto servidor | 5555  |
