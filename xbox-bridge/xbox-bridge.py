import argparse
import sys
import time
import pygame

# ---- Settings ----
DEADZONE = 0.15     # ignore micro-movements
ROUND = 2           # decimals shown for axes
FPS = 120           # reading frequency

def clamp_deadzone(value: float, dz: float) -> float:
    # Applies deadzone and rescales the rest to keep useful range
    if abs(value) < dz:
        return 0.0
    # Linearly rescales from the edge of the deadzone
    sign = 1 if value > 0 else -1
    out = (abs(value) - dz) / (1.0 - dz)
    return round(sign * out, ROUND)

def get_state(js: pygame.joystick.Joystick):
    axes = {}
    buttons = {}
    hats = {}

    # Analog axes (sticks, triggers)
    for i in range(js.get_numaxes()):
        raw = js.get_axis(i)
        axes[f"A{i}"] = clamp_deadzone(raw, DEADZONE)

    # Digital buttons
    for i in range(js.get_numbuttons()):
        buttons[f"B{i}"] = int(js.get_button(i))

    # D-Pad (hat)
    for i in range(js.get_numhats()):
        hats[f"H{i}"] = js.get_hat(i)  # tuple (x,y) with -1,0,1

    return {"axes": axes, "buttons": buttons, "hats": hats}

def main():
    global DEADZONE

    parser = argparse.ArgumentParser(description="Read gamepad (Xbox 360) with pygame")
    parser.add_argument("--index", type=int, default=0, help="Joystick index (default 0)")
    parser.add_argument("--print-every", type=float, default=0.0, help="Force print every N seconds (0 = only changes)")
    parser.add_argument("--deadzone", type=float, default=DEADZONE, help="Deadzone for axes (0..0.3 typical)")
    args = parser.parse_args()

    DEADZONE = max(0.0, min(args.deadzone, 0.5))

    pygame.init()
    pygame.joystick.init()

    count = pygame.joystick.get_count()
    if count == 0:
        print("No joysticks detected. Connect the receiver/controller and try again.")
        sys.exit(1)

    if args.index < 0 or args.index >= count:
        print(f"Invalid index {args.index}. There are {count} joystick(s) available.")
        for i in range(count):
            j = pygame.joystick.Joystick(i)
            j.init()
            print(f"  [{i}] {j.get_name()}")
        sys.exit(1)

    js = pygame.joystick.Joystick(args.index)
    js.init()
    print(f"Using joystick [{args.index}]: {js.get_name()}")
    print(f"Axes={js.get_numaxes()}  Buttons={js.get_numbuttons()}  Hats={js.get_numhats()}")
    print("Move sticks/buttons; Ctrl+C to exit.\n")

    clock = pygame.time.Clock()
    prev = None
    last_forced = time.time()

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt

            state = get_state(js)

            # Print changes or every certain args.print_every seconds
            changed = (state != prev)
            forced = (args.print_every > 0 and (time.time() - last_forced) >= args.print_every)

            if changed or forced:
                # Tip: typical mapping Xbox 360 with SDL:
                #  A0: LX, A1: LY, A2: RX, A3: RY, A4: LT, A5: RT
                #  Buttons: B0=A, B1=B, B2=X, B3=Y, B4=LB, B5=RB, B6=Back, B7=Start, B8=StickL, B9=StickR
                print(state)
                prev = state
                last_forced = time.time()

            clock.tick(FPS)

    except KeyboardInterrupt:
        print("\nExiting…")
    finally:
        js.quit()
        pygame.joystick.quit()
        pygame.quit()

if __name__ == "__main__":
    main()
