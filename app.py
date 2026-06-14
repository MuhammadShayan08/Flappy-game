import random
import math
import sys

import pygame

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 470, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Sky Pro - Python Version")
CLOCK = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
YELLOW = (255, 202, 40)
ORANGE = (255, 143, 0)
GREEN = (55, 200, 70)
DARK_GREEN = (10, 90, 30)
SKY_TOP = (99, 204, 255)
SKY_BOTTOM = (139, 221, 121)
DIRT = (139, 90, 43)

FONT_BIG = pygame.font.SysFont("arial", 42, bold=True)
FONT_MED = pygame.font.SysFont("arial", 24, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 16, bold=True)

state = "menu"
frame = 0
score = 0
coins = 0
best = 0
level = 1
camera_shake = 0
slow_motion = 0

bird = {
    "x": 105,
    "y": 330,
    "r": 18,
    "vy": 0,
    "gravity": 0.38,
    "jump": -7.9,
    "wing": 0,
    "shield": 0,
}

pipes = []
items = []
particles = []

clouds = [
    {
        "x": random.randint(0, WIDTH),
        "y": random.randint(35, 260),
        "s": random.uniform(0.5, 1.7),
        "v": random.uniform(0.18, 0.42),
    }
    for _ in range(10)
]

mountains = [
    {
        "x": i * 95 - 30,
        "h": random.randint(120, 230),
        "w": random.randint(140, 220),
    }
    for i in range(9)
]

grass = [
    {
        "x": i * 8,
        "h": random.randint(12, 30),
    }
    for i in range(80)
]


def draw_text(text, font, color, x, y, center=True):
    img = font.render(str(text), True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    SCREEN.blit(img, rect)


def draw_rounded_rect(surface, color, rect, radius=12):
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def make_sound(freq=440, duration=0.08, volume=0.20):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    for i in range(n_samples):
        t = i / sample_rate
        wave = math.sin(2 * math.pi * freq * t)
        val = int(32767 * volume * wave)
        buf += val.to_bytes(2, byteorder="little", signed=True)
    try:
        return pygame.mixer.Sound(buffer=bytes(buf))
    except Exception:
        return None


SND_FLAP = make_sound(520, 0.07, 0.18)
SND_COIN = make_sound(880, 0.09, 0.20)
SND_HIT = make_sound(90, 0.18, 0.22)
SND_POWER = make_sound(660, 0.12, 0.18)


def play(sound):
    if sound:
        sound.play()


def reset_game():
    global state, frame, score, coins, level, pipes, items, particles, camera_shake, slow_motion
    state = "play"
    frame = 0
    score = 0
    coins = 0
    level = 1
    pipes = []
    items = []
    particles = []
    camera_shake = 0
    slow_motion = 0
    bird["y"] = 330
    bird["vy"] = 0
    bird["wing"] = 0
    bird["shield"] = 0
    add_pipe()


def flap():
    global state
    if state in ["menu", "over"]:
        reset_game()
        play(SND_POWER)
        return
    if state == "pause":
        return
    bird["vy"] = bird["jump"]
    bird["wing"] = 16
    play(SND_FLAP)
    burst(bird["x"] - 12, bird["y"] + 11, 14, "feather")


def burst(x, y, n, kind="spark"):
    for _ in range(n):
        angle = random.random() * math.pi * 2
        speed = random.uniform(1, 4.8)
        particles.append(
            {
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed - (1.8 if kind == "feather" else 0),
                "vy": math.sin(angle) * speed,
                "life": random.randint(25, 50),
                "max": 50,
                "size": random.uniform(2, 5),
                "kind": kind,
            }
        )


def add_pipe():
    gap = max(138, 178 - score * 0.55)
    margin = 95
    top = margin + random.random() * (HEIGHT - 250 - gap)
    moving = score > 8 and random.random() < 0.35
    pipes.append(
        {
            "x": WIDTH + 60,
            "w": 76,
            "top": top,
            "bottom": top + gap,
            "base_top": top,
            "gap": gap,
            "speed": 2.75 + min(2.25, score * 0.035),
            "passed": False,
            "moving": moving,
            "phase": random.random() * math.pi * 2,
        }
    )

    if random.random() < 0.78:
        items.append(
            {
                "x": WIDTH + 105,
                "y": top + gap / 2,
                "type": "shield" if random.random() < 0.18 else "coin",
                "r": 12,
                "collected": False,
                "spin": 0,
            }
        )


def draw_sky():
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(SKY_TOP[0] * (1 - t) + SKY_BOTTOM[0] * t)
        g = int(SKY_TOP[1] * (1 - t) + SKY_BOTTOM[1] * t)
        b = int(SKY_TOP[2] * (1 - t) + SKY_BOTTOM[2] * t)
        pygame.draw.line(SCREEN, (r, g, b), (0, y), (WIDTH, y))

    sun_x = 70 + ((math.sin(frame * 0.002) + 1) / 2) * 330
    sun_y = 95 + math.sin(frame * 0.003) * 22
    pygame.draw.circle(SCREEN, (255, 245, 160), (int(sun_x), int(sun_y)), 34)

    for c in clouds:
        c["x"] -= c["v"] * (1 + level * 0.05)
        if c["x"] < -160:
            c["x"] = WIDTH + 120
            c["y"] = random.randint(35, 260)
            c["s"] = random.uniform(0.5, 1.7)

        x, y, s = c["x"], c["y"], c["s"]
        color = (245, 250, 255)
        pygame.draw.circle(SCREEN, color, (int(x), int(y + 20 * s)), int(24 * s))
        pygame.draw.circle(SCREEN, color, (int(x + 30 * s), int(y + 5 * s)), int(34 * s))
        pygame.draw.circle(SCREEN, color, (int(x + 65 * s), int(y + 20 * s)), int(27 * s))
        pygame.draw.circle(SCREEN, color, (int(x + 38 * s), int(y + 28 * s)), int(32 * s))


def draw_land():
    for i, m in enumerate(mountains):
        m["x"] -= 0.45 + level * 0.025
        if m["x"] < -m["w"]:
            m["x"] = WIDTH + random.randint(20, 100)

        color = (38, 91, 71) if i % 2 else (29, 74, 82)
        points = [
            (m["x"], HEIGHT - 90),
            (m["x"] + m["w"] * 0.5, HEIGHT - 90 - m["h"]),
            (m["x"] + m["w"], HEIGHT - 90),
        ]
        pygame.draw.polygon(SCREEN, color, points)

    pygame.draw.rect(SCREEN, (70, 181, 77), (0, HEIGHT - 90, WIDTH, 90))

    for g in grass:
        g["x"] -= 2.8 + level * 0.18
        if g["x"] < -10:
            g["x"] = WIDTH + random.randint(0, 20)

        x = int(g["x"])
        pygame.draw.polygon(
            SCREEN,
            (46, 125, 50),
            [(x, HEIGHT - 90), (x + 3, HEIGHT - 90 - g["h"]), (x + 6, HEIGHT - 90)],
        )

    pygame.draw.rect(SCREEN, DIRT, (0, HEIGHT - 52, WIDTH, 52))


def draw_pipes():
    for p in pipes:
        x = int(p["x"])
        w = p["w"]
        top = int(p["top"])
        bottom = int(p["bottom"])

        draw_rounded_rect(SCREEN, GREEN, (x, -25, w, top + 25), 18)
        draw_rounded_rect(SCREEN, GREEN, (x, bottom, w, HEIGHT - bottom - 52), 18)

        draw_rounded_rect(SCREEN, DARK_GREEN, (x - 10, top - 25, w + 20, 31), 10)
        draw_rounded_rect(SCREEN, DARK_GREEN, (x - 10, bottom, w + 20, 31), 10)

        pygame.draw.rect(SCREEN, (170, 255, 170), (x + 14, 2, 10, max(0, top - 34)))
        pygame.draw.rect(SCREEN, (170, 255, 170), (x + 14, bottom + 34, 10, HEIGHT - bottom - 88))


def draw_items():
    for it in items:
        if it["collected"]:
            continue

        it["spin"] += 0.12
        x, y = int(it["x"]), int(it["y"])

        if it["type"] == "coin":
            pygame.draw.circle(SCREEN, (255, 213, 79), (x, y), 14)
            pygame.draw.circle(SCREEN, (255, 171, 0), (x, y), 7)
        else:
            pygame.draw.circle(SCREEN, (179, 245, 255), (x, y), 16, 4)
            pygame.draw.circle(SCREEN, (122, 232, 255), (x, y), 9)


def draw_bird():
    x, y = int(bird["x"]), int(bird["y"])

    if bird["shield"] > 0:
        pygame.draw.circle(SCREEN, (125, 235, 255), (x, y), 34 + int(math.sin(frame * 0.18) * 2), 4)

    pygame.draw.ellipse(SCREEN, YELLOW, (x - 28, y - 21, 52, 42))

    wing_y = y + math.sin(frame * 0.55) * 7 - bird["wing"]
    pygame.draw.ellipse(SCREEN, ORANGE, (x - 31, wing_y - 8, 30, 16))

    pygame.draw.circle(SCREEN, WHITE, (x + 10, y - 8), 8)
    pygame.draw.circle(SCREEN, BLACK, (x + 12, y - 8), 3)

    pygame.draw.polygon(SCREEN, (255, 112, 67), [(x + 18, y - 2), (x + 38, y + 5), (x + 18, y + 12)])

    bird["wing"] *= 0.72


def draw_particles():
    for pt in particles:
        alpha = max(0, pt["life"] / pt["max"])
        if pt["kind"] == "coin":
            color = (255, 213, 79)
        elif pt["kind"] == "shield":
            color = (179, 245, 255)
        elif pt["kind"] == "feather":
            color = (255, 248, 198)
        else:
            color = (255, 140, 80)

        pygame.draw.circle(SCREEN, color, (int(pt["x"]), int(pt["y"])), int(pt["size"] * alpha + 1))


def end_game():
    global state, camera_shake, slow_motion
    if state != "play":
        return
    state = "over"
    camera_shake = 22
    slow_motion = 25
    play(SND_HIT)
    burst(bird["x"], bird["y"], 45, "spark")


def update_game():
    global frame, score, coins, best, level, slow_motion, camera_shake

    if state != "play":
        return

    speed_factor = 0.55 if slow_motion > 0 else 1

    frame += 1
    level = 1 + score // 8

    bird["vy"] += bird["gravity"] * speed_factor
    bird["y"] += bird["vy"] * speed_factor

    if bird["shield"] > 0:
        bird["shield"] -= 1

    if slow_motion > 0:
        slow_motion -= 1

    if len(pipes) == 0 or pipes[-1]["x"] < WIDTH - 185:
        add_pipe()

    for p in pipes:
        p["x"] -= p["speed"] * speed_factor

        if p["moving"]:
            p["top"] = p["base_top"] + math.sin(frame * 0.035 + p["phase"]) * 32
            p["bottom"] = p["top"] + p["gap"]

        if not p["passed"] and p["x"] + p["w"] < bird["x"]:
            p["passed"] = True
            score += 1
            best = max(best, score)

        close_x = max(p["x"], min(bird["x"], p["x"] + p["w"]))
        hit_top_y = max(-20, min(bird["y"], p["top"]))
        hit_bottom_y = max(p["bottom"], min(bird["y"], HEIGHT - 52))

        d_top = math.hypot(bird["x"] - close_x, bird["y"] - hit_top_y)
        d_bottom = math.hypot(bird["x"] - close_x, bird["y"] - hit_bottom_y)

        if (d_top < bird["r"] or d_bottom < bird["r"]) and bird["shield"] <= 0:
            end_game()

        if (d_top < bird["r"] or d_bottom < bird["r"]) and bird["shield"] > 0:
            p["x"] = -200
            bird["shield"] = 0
            camera_shake = 12
            burst(bird["x"], bird["y"], 24, "shield")
            play(SND_POWER)

    pipes[:] = [p for p in pipes if p["x"] + p["w"] > -80]

    for it in items:
        it["x"] -= (2.75 + min(2.25, score * 0.035)) * speed_factor
        if not it["collected"] and math.hypot(bird["x"] - it["x"], bird["y"] - it["y"]) < bird["r"] + it["r"]:
            it["collected"] = True
            if it["type"] == "coin":
                coins += 1
                score += 1
                burst(it["x"], it["y"], 18, "coin")
                play(SND_COIN)
            else:
                bird["shield"] = 520
                burst(it["x"], it["y"], 24, "shield")
                play(SND_POWER)

    items[:] = [it for it in items if it["x"] > -50 and not it.get("dead", False)]

    for pt in particles:
        pt["x"] += pt["vx"] * speed_factor
        pt["y"] += pt["vy"] * speed_factor
        pt["vy"] += 0.045
        pt["life"] -= 1

    particles[:] = [pt for pt in particles if pt["life"] > 0]

    if (bird["y"] + bird["r"] > HEIGHT - 90 or bird["y"] - bird["r"] < 0) and bird["shield"] <= 0:
        end_game()

    if bird["y"] + bird["r"] > HEIGHT - 90 and bird["shield"] > 0:
        bird["y"] = HEIGHT - 90 - bird["r"]
        bird["vy"] = -5
        bird["shield"] = 0
        camera_shake = 10


def draw_hud():
    draw_rounded_rect(SCREEN, (0, 0, 0), (14, 14, 164, 42), 18)
    draw_text(f"BEST {best}", FONT_SMALL, WHITE, 28, 27, center=False)

    draw_rounded_rect(SCREEN, (0, 0, 0), (WIDTH - 168, 14, 154, 42), 18)
    text = FONT_SMALL.render(f"COINS {coins}", True, WHITE)
    SCREEN.blit(text, (WIDTH - 31 - text.get_width(), 27))

    draw_text(score, FONT_BIG, WHITE, WIDTH // 2, 73)
    draw_text(f"LEVEL {level}", FONT_SMALL, WHITE, WIDTH // 2, 111)

    if bird["shield"] > 0:
        draw_rounded_rect(SCREEN, (0, 0, 0), (WIDTH // 2 - 70, 122, 140, 24), 12)
        pygame.draw.rect(SCREEN, (179, 245, 255), (WIDTH // 2 - 62, 129, int(124 * (bird["shield"] / 520)), 10))


def panel(title, subtitle, lines):
    draw_rounded_rect(SCREEN, (2, 16, 32), (35, 190, WIDTH - 70, 280), 30)
    pygame.draw.rect(SCREEN, (255, 255, 255), (48, 203, WIDTH - 96, 254), 2)

    draw_text(title, FONT_BIG, WHITE, WIDTH // 2, 260)
    draw_text(subtitle, FONT_MED, WHITE, WIDTH // 2, 303)

    for i, line in enumerate(lines):
        draw_text(line, FONT_SMALL, WHITE, WIDTH // 2, 342 + i * 28)

    draw_text("Tap / Click / SPACE to play", FONT_SMALL, (255, 213, 79), WIDTH // 2, 430)


def draw_overlays():
    if state == "menu":
        panel(
            "FLAPPY SKY",
            "Python Pygame Edition",
            [
                "Collect coins • Grab shield power-up",
                "Pipes become faster and moving",
                "Press M to mute sounds",
            ],
        )
    elif state == "pause":
        panel("PAUSED", "Press P to continue", [f"Score: {score}", f"Best: {best}", f"Coins: {coins}"])
    elif state == "over":
        panel(
            "GAME OVER",
            f"Your score: {score}",
            [f"Best score: {best}", f"Coins collected: {coins}", "Press R or tap to restart"],
        )


running = True
while running:
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.code == pygame.K_SPACE:
                flap()
            elif event.key == pygame.K_p:
                if state == "play":
                    state = "pause"
                elif state == "pause":
                    state = "play"
            elif event.key == pygame.K_r:
                reset_game()

        if event.type == pygame.MOUSEBUTTONDOWN:
            flap()

    shake_x = 0
    shake_y = 0
    if camera_shake > 0:
        shake_x = random.uniform(-camera_shake, camera_shake)
        shake_y = random.uniform(-camera_shake, camera_shake)
        camera_shake *= 0.84

    SCREEN.fill((0, 0, 0))
    temp = pygame.Surface((WIDTH, HEIGHT))
    old_screen = SCREEN

    draw_sky()
    draw_land()
    update_game()
    draw_pipes()
    draw_items()
    draw_particles()
    draw_bird()
    draw_hud()
    draw_overlays()

    if state != "play":
        frame += 1

    pygame.display.flip()
    CLOCK.tick(FPS)

pygame.quit()
sys.exit()
