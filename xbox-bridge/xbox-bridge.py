import argparse
import sys
import time
import pygame

# ---- Ajustes ----
DEADZONE = 0.15     # ignora micro-movimientos
ROUND = 2           # decimales que mostramos para ejes
FPS = 120           # frecuencia de lectura

def clamp_deadzone(value: float, dz: float) -> float:
    # Aplica deadzone y reescala el resto para mantener rango útil
    if abs(value) < dz:
        return 0.0
    # Reescala linealmente desde el borde de la deadzone
    sign = 1 if value > 0 else -1
    out = (abs(value) - dz) / (1.0 - dz)
    return round(sign * out, ROUND)

def get_state(js: pygame.joystick.Joystick):
    axes = {}
    buttons = {}
    hats = {}

    # Ejes analógicos (sticks, triggers)
    for i in range(js.get_numaxes()):
        raw = js.get_axis(i)
        axes[f"A{i}"] = clamp_deadzone(raw, DEADZONE)

    # Botones digitales
    for i in range(js.get_numbuttons()):
        buttons[f"B{i}"] = int(js.get_button(i))

    # D-Pad (hat)
    for i in range(js.get_numhats()):
        hats[f"H{i}"] = js.get_hat(i)  # tupla (x,y) con -1,0,1

    return {"axes": axes, "buttons": buttons, "hats": hats}

def main():
    global DEADZONE

    parser = argparse.ArgumentParser(description="Leer gamepad (Xbox 360) con pygame")
    parser.add_argument("--index", type=int, default=0, help="Índice del joystick (default 0)")
    parser.add_argument("--print-every", type=float, default=0.0, help="Forzar impresión cada N segundos (0 = solo cambios)")
    parser.add_argument("--deadzone", type=float, default=DEADZONE, help="Deadzone para ejes (0..0.3 típico)")
    args = parser.parse_args()

    DEADZONE = max(0.0, min(args.deadzone, 0.5))

    pygame.init()
    pygame.joystick.init()

    count = pygame.joystick.get_count()
    if count == 0:
        print("No se detectaron joysticks. Conectá el receptor/control y probá de nuevo.")
        sys.exit(1)

    if args.index < 0 or args.index >= count:
        print(f"Índice inválido {args.index}. Hay {count} joystick(s) disponible(s).")
        for i in range(count):
            j = pygame.joystick.Joystick(i)
            j.init()
            print(f"  [{i}] {j.get_name()}")
        sys.exit(1)

    js = pygame.joystick.Joystick(args.index)
    js.init()
    print(f"Usando joystick [{args.index}]: {js.get_name()}")
    print(f"Ejes={js.get_numaxes()}  Botones={js.get_numbuttons()}  Hats={js.get_numhats()}")
    print("Mové sticks/botones; Ctrl+C para salir.\n")

    clock = pygame.time.Clock()
    prev = None
    last_forced = time.time()

    try:
        while True:
            # Pygame necesita procesar eventos para actualizar internamente
            for event in pygame.event.get():
                # No necesitamos manejar eventos específicos; la lectura es «polling»
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt

            state = get_state(js)

            # Impresión solo si hay cambios o si se pide print periódico
            changed = (state != prev)
            forced = (args.print_every > 0 and (time.time() - last_forced) >= args.print_every)

            if changed or forced:
                # Tip: Mapeo típico Xbox 360 con SDL:
                #  A0: LX, A1: LY, A2: RX, A3: RY, A4: LT, A5: RT  (puede variar según sistema)
                #  Botones: B0=A, B1=B, B2=X, B3=Y, B4=LB, B5=RB, B6=Back, B7=Start, B8=StickL, B9=StickR
                print(state)
                prev = state
                last_forced = time.time()

            clock.tick(FPS)

    except KeyboardInterrupt:
        print("\nSaliendo…")
    finally:
        js.quit()
        pygame.joystick.quit()
        pygame.quit()

if __name__ == "__main__":
    main()
