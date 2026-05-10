"""
Pixel Surf Cat - 像素冲浪猫娘小游戏
A side-scrolling surf game built with Pygame.
"""

import pygame
import random
import math
import struct
import sys

# ============================================================
# INITIALIZATION
# ============================================================
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)

# ============================================================
# CONSTANTS
# ============================================================
WIDTH, HEIGHT = 800, 400
FPS = 60
GRAVITY = 0.6
JUMP_VEL = -9.5
BASE_SCROLL = 3
MAX_SCROLL = 8
PLAYER_X = 160
WATER_BASE = 290
INITIAL_LIVES = 3
OBSTACLE_INTERVAL = 90  # frames between obstacles (decreases over time)
MIN_OBSTACLE_INTERVAL = 35

# States
TITLE, PLAYING, GAME_OVER = 0, 1, 2

# ============================================================
# COLORS (bright pixel palette)
# ============================================================
SKY_TOP = (80, 160, 255)
SKY_BOTTOM = (180, 220, 255)
SUN_COLOR = (255, 240, 80)
SUN_GLOW = (255, 250, 180)
CLOUD_WHITE = (255, 255, 255)
CLOUD_SHADOW = (220, 220, 230)

WATER_DEEP = (20, 60, 160)
WATER_MID = (30, 100, 200)
WATER_LIGHT = (60, 160, 240)
WAVE_FOAM = (220, 240, 255)
WAVE_HIGHLIGHT = (120, 200, 255)

SAND = (230, 200, 150)
SAND_DARK = (200, 170, 120)

CAT_FUR = (255, 220, 220)
CAT_SWIMSUIT = (255, 80, 140)
CAT_SWIMSUIT_DARK = (220, 50, 110)
CAT_EARS_INNER = (255, 180, 190)
CAT_EYES = (60, 40, 40)
CAT_MOUTH = (200, 60, 60)
CAT_WHISKERS = (80, 60, 60)
CAT_TAIL_TIP = (255, 255, 255)
CAT_HEADBAND = (255, 100, 150)
CAT_BLUSH = (255, 160, 180)

SURFBOARD_TOP = (255, 150, 40)
SURFBOARD_BOTTOM = (200, 190, 180)
SURFBOARD_STRIPE1 = (255, 255, 255)
SURFBOARD_STRIPE2 = (80, 200, 255)

ROCK_MAIN = (130, 115, 100)
ROCK_LIGHT = (155, 140, 125)
ROCK_DARK = (100, 85, 70)

WOOD_MAIN = (160, 120, 70)
WOOD_DARK = (120, 85, 45)
WOOD_LIGHT = (180, 145, 95)

SEAGULL_BODY = (240, 240, 245)
SEAGULL_WING = (200, 200, 210)
SEAGULL_BEAK = (255, 200, 50)
SEAGULL_EYE = (40, 40, 40)

SHARK_MAIN = (90, 90, 105)
SHARK_DARK = (65, 65, 80)
SHARK_LIGHT = (120, 120, 135)

UI_WHITE = (255, 255, 255)
UI_BLACK = (20, 20, 30)
UI_SHADOW = (0, 0, 0, 80)
UI_GOLD = (255, 215, 0)
UI_PINK = (255, 150, 200)

GRASS_GREEN = (100, 200, 80)
SHELL_PINK = (255, 180, 170)

# ============================================================
# SOUND GENERATION
# ============================================================
def make_sound(freq, duration, vol=0.25, wave='square'):
    """Generate a synth sound effect. wave: square|sine|saw|noise"""
    sr = 22050
    n = int(sr * duration)
    frames = []
    for i in range(n):
        t = i / sr
        phase = (t * freq) % 1.0
        if wave == 'square':
            v = 1.0 if phase < 0.5 else -1.0
        elif wave == 'saw':
            v = 2.0 * phase - 1.0
        elif wave == 'sine':
            v = math.sin(2 * math.pi * freq * t)
        elif wave == 'noise':
            v = random.uniform(-1, 1)
        else:
            v = math.sin(2 * math.pi * freq * t)

        sample = int(v * vol * 30000)
        sample = max(-32768, min(32767, sample))
        frames.append(struct.pack('<h', sample))
        frames.append(struct.pack('<h', sample))

    return pygame.mixer.Sound(buffer=b''.join(frames))


def make_sweep(freq_start, freq_end, duration, vol=0.2):
    """Frequency sweep sound effect."""
    sr = 22050
    n = int(sr * duration)
    frames = []
    for i in range(n):
        t = i / sr
        progress = t / duration
        freq = freq_start + (freq_end - freq_start) * progress
        phase = (t * freq) % 1.0
        v = 1.0 if phase < 0.5 else -1.0
        env = 1.0 - progress
        sample = int(v * vol * env * 30000)
        sample = max(-32768, min(32767, sample))
        frames.append(struct.pack('<h', sample))
        frames.append(struct.pack('<h', sample))
    return pygame.mixer.Sound(buffer=b''.join(frames))


def make_music():
    """Generate background chiptune music loop (about 4 seconds)."""
    sr = 22050
    duration = 4.0
    n = int(sr * duration)

    # Melody notes (C major pentatonic feel)
    melody = [
        (523, 0.15), (587, 0.15), (659, 0.15), (784, 0.15),
        (659, 0.15), (587, 0.15), (523, 0.15), (784, 0.15),
        (440, 0.15), (523, 0.15), (587, 0.15), (659, 0.15),
        (523, 0.15), (659, 0.15), (784, 0.15), (1047, 0.15),
        (392, 0.15), (440, 0.15), (523, 0.15), (659, 0.15),
        (587, 0.15), (523, 0.15), (440, 0.15), (392, 0.15),
        (349, 0.15), (392, 0.15), (440, 0.15), (523, 0.15),
        (587, 0.15), (659, 0.15), (784, 0.3), (0, 0.15),
        (659, 0.15), (784, 0.15), (880, 0.15), (1047, 0.15),
        (784, 0.15), (880, 0.15), (1047, 0.15), (1175, 0.15),
        (1047, 0.15), (880, 0.15), (784, 0.15), (659, 0.15),
        (587, 0.15), (523, 0.15), (440, 0.15), (392, 0.15),
        (523, 0.3), (0, 0.15), (659, 0.3), (0, 0.15),
        (784, 0.15), (659, 0.15), (523, 0.15), (659, 0.15),
        (784, 0.3), (1047, 0.3), (784, 0.3), (523, 0.3),
    ]

    # Bass notes
    bass = [
        (131, 0.5), (165, 0.5), (131, 0.5), (165, 0.5),
        (131, 0.5), (165, 0.5), (131, 0.5), (165, 0.5),
        (110, 0.5), (131, 0.5), (110, 0.5), (131, 0.5),
        (98, 0.5), (131, 0.5), (98, 0.5), (131, 0.5),
    ]

    # Hi-hat pattern
    hat = []
    for i in range(int(duration / 0.125)):
        hat.append((0, 0.1) if i % 2 == 0 else (0, 0.05))

    # Generate all audio data
    frames = bytearray(n * 4)  # 16-bit stereo = 4 bytes per frame
    for i in range(n):
        t = i / sr

        # Melody
        mel_idx = int(t / 0.3) % len(melody)
        mel_freq, mel_dur = melody[mel_idx]
        local_t = t % 0.3
        if local_t < mel_dur and mel_freq > 0:
            mel_phase = (local_t * mel_freq) % 1.0
            mel_v = 1.0 if mel_phase < 0.5 else -1.0
            mel_env = 1.0 - local_t / mel_dur
            mel_sample = mel_v * 0.08 * mel_env
        else:
            mel_sample = 0

        # Bass
        bass_idx = int(t / 0.5) % len(bass)
        bass_freq, bass_dur = bass[bass_idx]
        local_t_bass = t % 0.5
        if local_t_bass < bass_dur and bass_freq > 0:
            bass_phase = (local_t_bass * bass_freq) % 1.0
            bass_v = 1.0 if bass_phase < 0.5 else -1.0
            bass_env = 1.0 - local_t_bass / bass_dur
            bass_sample = bass_v * 0.12 * bass_env
        else:
            bass_sample = 0

        # Hi-hat
        hat_idx = int(t / 0.125) % len(hat)
        _, hat_dur = hat[hat_idx]
        local_t_hat = t % 0.125
        hat_v = 0
        if local_t_hat < hat_dur:
            hat_v = random.uniform(-1, 1) * 0.04 * (1 - local_t_hat / hat_dur)

        # Mix
        mixed = mel_sample + bass_sample + hat_v
        mixed = max(-1, min(1, mixed))
        sample = int(mixed * 30000)
        sample = max(-32768, min(32767, sample))

        offset = i * 4
        frames[offset:offset+4] = struct.pack('<h', sample) + struct.pack('<h', sample)

    return pygame.mixer.Sound(buffer=bytes(frames))


# ============================================================
# PRE-RENDER STATIC BACKGROUND
# ============================================================
def render_static_bg():
    """Render sky gradient + sun to a surface (no clouds/waves)."""
    surf = pygame.Surface((WIDTH, HEIGHT))
    # Sky gradient
    for y in range(WATER_BASE - 40):
        t = y / (WATER_BASE - 40)
        r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    # Sun glow
    sun_x, sun_y = 680, 60
    for r in range(60, 0, -4):
        alpha = max(0, 80 - r * 2)
        glow = (SUN_GLOW[0], SUN_GLOW[1], SUN_GLOW[2])
        pygame.draw.circle(surf, glow, (sun_x, sun_y), r)
    # Sun
    pygame.draw.circle(surf, SUN_COLOR, (sun_x, sun_y), 25)
    pygame.draw.circle(surf, (255, 245, 150), (sun_x, sun_y), 20)

    # Distant beach strip
    beach_y = WATER_BASE - 25
    for y_offset in range(25):
        y = beach_y + y_offset
        shade = 1.0 - y_offset / 25
        c = (int(SAND[0] * shade + WATER_MID[0] * (1 - shade)),
             int(SAND[1] * shade + WATER_MID[1] * (1 - shade)),
             int(SAND[2] * shade + WATER_MID[2] * (1 - shade)))
        pygame.draw.line(surf, c, (0, y), (WIDTH, y))

    return surf


# ============================================================
# DRAWING FUNCTIONS
# ============================================================
def draw_clouds(surf, time):
    """Draw pixel-art clouds scrolling at different speeds."""
    colors = [(255, 255, 255), (245, 245, 250), (235, 235, 245)]
    layers = [
        (0.2, [(100, 50, 60), (400, 80, 50), (650, 40, 70)]),
        (0.5, [(200, 90, 40), (550, 70, 55), (720, 100, 35)]),
        (0.8, [(50, 110, 45), (300, 130, 50), (600, 120, 40)]),
    ]
    for speed, clouds in layers:
        offset = int(time * speed * 0.5) % (WIDTH + 200)
        for cx, cy, size in clouds:
            x = (cx - offset) % (WIDTH + 200) - 100
            y = cy
            # Draw cloud as overlapping circles
            c = colors[layers.index((speed, clouds))]
            for dx, dy, r in [(0, 0, size//2), (size//3, -2, size//3),
                              (-size//3, 2, size//3), (size//2, 2, size//4)]:
                pygame.draw.circle(surf, c, (x + dx, y + dy), r)


def draw_ocean(surf, time):
    """Draw ocean with animated waves."""
    # Main water body
    water_top = WATER_BASE - 5
    water_rect = pygame.Rect(0, water_top, WIDTH, HEIGHT - water_top)
    pygame.draw.rect(surf, WATER_DEEP, water_rect)

    # Mid water layer
    mid_rect = pygame.Rect(0, water_top + 20, WIDTH, HEIGHT - water_top - 20)
    pygame.draw.rect(surf, WATER_MID, mid_rect)

    # Wave surface - multiple sine waves
    for x in range(0, WIDTH, 4):
        wave = math.sin(x * 0.025 + time * 0.04) * 6 + math.sin(x * 0.05 + time * 0.06) * 3
        wy = water_top + wave
        # Wave body
        pygame.draw.line(surf, WATER_LIGHT, (x, wy), (x, water_top + 20), 4)
        # Foam crest
        if wave > 1:
            pygame.draw.line(surf, WAVE_FOAM, (x, wy), (x, wy - 1), 2)
            pygame.draw.line(surf, WAVE_HIGHLIGHT, (x, wy + 1), (x, wy + 3), 2)

    # Wave crest highlights (white streaks)
    for i in range(12):
        phase = (time * 0.03 + i * 0.8) % (math.pi * 2)
        cx = int(i * 70 + math.sin(time * 0.02 + i) * 30) % WIDTH
        cy = water_top + math.sin(phase) * 5
        streak_len = 15 + int(math.sin(phase) * 8)
        if streak_len > 5:
            alpha = max(0, min(200, 150 + int(math.sin(phase) * 80)))
            c = (WAVE_FOAM[0], WAVE_FOAM[1], WAVE_FOAM[2])
            pygame.draw.line(surf, c, (cx, cy), (cx + streak_len, cy - 2), 2)

    # Distant wave lines
    for y in range(water_top + 35, water_top + 80, 12):
        offset = math.sin(time * 0.02 + y * 0.1) * 20
        for x in range(0, WIDTH, 40):
            wx = (x + offset) % WIDTH
            c = (WATER_MID[0] + 20, WATER_MID[1] + 20, WATER_MID[2] + 15)
            pygame.draw.line(surf, c, (wx, y), (wx + 15, y), 1)


def get_water_y(x, time):
    """Get water surface Y at given X position and time."""
    if x < 0 or x >= WIDTH:
        return WATER_BASE
    wave = math.sin(x * 0.025 + time * 0.04) * 6 + math.sin(x * 0.05 + time * 0.06) * 3
    return WATER_BASE - 5 + wave


def draw_surfboard(surf, x, y, tilt=0, color=SURFBOARD_TOP):
    """Draw a surfboard at (x, y) center-bottom."""
    # Board shadow
    shadow_rect = pygame.Rect(x - 24, y - 1, 48, 8)
    pygame.draw.ellipse(surf, (0, 0, 0, 30), shadow_rect)

    # Board bottom
    rect = pygame.Rect(x - 22, y - 4, 44, 7)
    pygame.draw.ellipse(surf, SURFBOARD_BOTTOM, rect)

    # Board top
    rect_top = pygame.Rect(x - 20, y - 6, 40, 6)
    pygame.draw.ellipse(surf, color, rect_top)

    # Stripes
    for i, stripe_x in enumerate([x - 12, x - 4, x + 4, x + 12]):
        c = SURFBOARD_STRIPE1 if i % 2 == 0 else SURFBOARD_STRIPE2
        pygame.draw.rect(surf, c, (stripe_x - 1, y - 6, 3, 5))

    # Board tip
    pygame.draw.circle(surf, color, (x - 20, y - 3), 4)
    pygame.draw.circle(surf, color, (x + 20, y - 3), 4)

    # Tail fin
    fin_pts = [(x + 18, y - 3), (x + 22, y - 7), (x + 22, y - 2)]
    pygame.draw.polygon(surf, SURFBOARD_BOTTOM, fin_pts)


def draw_cat_girl(surf, x, y, state, frame, on_ground=True):
    """Draw the pixel cat girl character. (x,y) is board bottom-center."""
    bob = math.sin(frame * 0.12) * 1.5 if state == 'normal' else 0
    is_ducking = (state == 'ducking')
    is_jumping = (state == 'jumping')

    if is_ducking:
        # === DUCKING POSE ===
        board_y = y
        body_bottom = board_y - 6

        # Surfboard (tilted back slightly)
        draw_surfboard(surf, x, board_y, color=SURFBOARD_TOP)

        # Body (crouched ball)
        body_r = pygame.Rect(x - 12, body_bottom - 14, 24, 16)
        pygame.draw.ellipse(surf, CAT_FUR, body_r)

        # Swimsuit strip
        swim_r = pygame.Rect(x - 12, body_bottom - 10, 24, 8)
        pygame.draw.ellipse(surf, CAT_SWIMSUIT, swim_r)

        # Arms in front
        pygame.draw.ellipse(surf, CAT_FUR, (x - 16, body_bottom - 8, 8, 10))
        pygame.draw.ellipse(surf, CAT_FUR, (x + 8, body_bottom - 8, 8, 10))

        # Head (lowered)
        head_y = body_bottom - 20
        head_r = pygame.Rect(x - 11, head_y, 22, 16)
        pygame.draw.ellipse(surf, CAT_FUR, head_r)

        # Ears (small)
        ear1 = [(x - 8, head_y + 2), (x - 5, head_y - 6), (x - 1, head_y + 2)]
        ear2 = [(x + 1, head_y + 2), (x + 5, head_y - 6), (x + 8, head_y + 2)]
        pygame.draw.polygon(surf, CAT_FUR, ear1)
        pygame.draw.polygon(surf, CAT_FUR, ear2)
        pygame.draw.polygon(surf, CAT_EARS_INNER,
                            [(x - 7, head_y + 1), (x - 5, head_y - 4), (x - 2, head_y + 1)])
        pygame.draw.polygon(surf, CAT_EARS_INNER,
                            [(x + 2, head_y + 1), (x + 5, head_y - 4), (x + 7, head_y + 1)])

        # Eyes (squished - closed)
        pygame.draw.line(surf, CAT_EYES, (x - 6, head_y + 8), (x - 2, head_y + 8), 2)
        pygame.draw.line(surf, CAT_EYES, (x + 2, head_y + 8), (x + 6, head_y + 8), 2)

    else:
        # === STANDING / JUMPING POSE ===
        board_y = y + bob
        tilt = -5 if is_jumping else bob * 1.5

        # Surfboard
        draw_surfboard(surf, x, board_y, color=SURFBOARD_TOP)

        body_bottom = board_y - 8
        body_top = body_bottom - 28

        # Tail
        tail_swing = math.sin(frame * 0.1) * 12
        tail_pts = [
            (x - 8, body_bottom - 4),
            (x - 16 + int(tail_swing * 0.5), body_top + 8),
            (x - 22 + int(tail_swing), body_top - 2),
        ]
        pygame.draw.lines(surf, CAT_FUR, False, tail_pts, 4)
        # Tail tip
        tail_tip = tail_pts[-1]
        if tail_tip:
            pygame.draw.circle(surf, CAT_TAIL_TIP, tail_tip, 4)

        # Legs
        leg_swing = math.sin(frame * 0.15) * 4 if not is_jumping else 2
        pygame.draw.rect(surf, CAT_FUR, (x - 8, body_bottom - 12, 6, 14 + int(leg_swing)))
        pygame.draw.rect(surf, CAT_FUR, (x + 2, body_bottom - 12, 6, 14 - int(leg_swing)))

        # Body / torso
        body_r = pygame.Rect(x - 11, body_top, 22, 28)
        pygame.draw.rect(surf, CAT_FUR, body_r)

        # Swimsuit top (pink)
        swim_r = pygame.Rect(x - 11, body_top + 2, 22, 12)
        pygame.draw.rect(surf, CAT_SWIMSUIT, swim_r)
        # Swimsuit bottom
        swim_b = pygame.Rect(x - 11, body_top + 16, 22, 8)
        pygame.draw.rect(surf, CAT_SWIMSUIT, swim_b)
        # Swimsuit strap
        pygame.draw.line(surf, CAT_SWIMSUIT_DARK, (x, body_top + 2), (x, body_top + 14), 2)

        # Arms
        arm_x = math.sin(frame * 0.12) * 3 if not is_jumping else -20
        # Left arm
        pygame.draw.rect(surf, CAT_FUR, (x - 16, body_top + 4 + int(arm_x * 0.5), 5, 12))
        # Right arm (raised when jumping)
        if is_jumping:
            pygame.draw.rect(surf, CAT_FUR, (x + 11, body_top - 2, 5, 10))
        else:
            pygame.draw.rect(surf, CAT_FUR, (x + 11, body_top + 4 - int(arm_x * 0.5), 5, 12))

        # Headband (cute accessory)
        headband_y = body_top - 2
        headband_r = pygame.Rect(x - 12, headband_y, 24, 3)
        pygame.draw.rect(surf, CAT_HEADBAND, headband_r)
        # Bow on headband
        bow_pts = [(x + 4, headband_y), (x + 10, headband_y - 4),
                   (x + 6, headband_y), (x + 10, headband_y + 4)]
        pygame.draw.polygon(surf, CAT_HEADBAND, bow_pts)

        # Head
        head_y = body_top - 16
        head_r = pygame.Rect(x - 12, head_y, 24, 18)
        pygame.draw.rect(surf, CAT_FUR, head_r)
        # Round top of head
        pygame.draw.ellipse(surf, CAT_FUR, (x - 12, head_y - 2, 24, 12))

        # Ears
        ear1 = [(x - 8, head_y + 2), (x - 4, head_y - 10), (x, head_y + 2)]
        ear2 = [(x, head_y + 2), (x + 4, head_y - 10), (x + 8, head_y + 2)]
        pygame.draw.polygon(surf, CAT_FUR, ear1)
        pygame.draw.polygon(surf, CAT_FUR, ear2)
        # Inner ears
        ear1_in = [(x - 7, head_y + 1), (x - 4, head_y - 7), (x - 1, head_y + 1)]
        ear2_in = [(x + 1, head_y + 1), (x + 4, head_y - 7), (x + 7, head_y + 1)]
        pygame.draw.polygon(surf, CAT_EARS_INNER, ear1_in)
        pygame.draw.polygon(surf, CAT_EARS_INNER, ear2_in)

        # Eyes
        eye_y = head_y + 8
        eye_x_offset = int(math.sin(frame * 0.08) * 1)  # slight eye movement
        # Left eye (big cute eyes)
        pygame.draw.rect(surf, CAT_EYES, (x - 7 + eye_x_offset, eye_y - 1, 4, 5))
        pygame.draw.rect(surf, CAT_EYES, (x + 3 + eye_x_offset, eye_y - 1, 4, 5))
        # Eye highlight
        pygame.draw.rect(surf, (255, 255, 255), (x - 6 + eye_x_offset, eye_y, 2, 2))
        pygame.draw.rect(surf, (255, 255, 255), (x + 4 + eye_x_offset, eye_y, 2, 2))

        # Blush
        pygame.draw.circle(surf, CAT_BLUSH, (x - 10, eye_y + 3), 3)
        pygame.draw.circle(surf, CAT_BLUSH, (x + 10, eye_y + 3), 3)

        # Nose
        pygame.draw.circle(surf, CAT_MOUTH, (x, eye_y + 5), 2)

        # Mouth (small smile)
        if is_jumping:
            # Open mouth (excited)
            pygame.draw.ellipse(surf, CAT_MOUTH, (x - 2, eye_y + 6, 4, 4))
        else:
            pygame.draw.arc(surf, CAT_MOUTH, (x - 3, eye_y + 4, 6, 4),
                            math.pi * 0.2, math.pi * 0.8, 1)

        # Whiskers
        for i, dx in enumerate([1, 2, 3]):
            wy = eye_y + 4 + i * 2
            pygame.draw.line(surf, CAT_WHISKERS, (x - 12, wy), (x - 12 - dx * 4, wy - 1), 1)
            pygame.draw.line(surf, CAT_WHISKERS, (x + 12, wy), (x + 12 + dx * 4, wy - 1), 1)

    return surf


def draw_rock(surf, x, y):
    """Draw a rock obstacle. (x,y) is bottom-center."""
    # Main rock body (jagged)
    pts = [
        (x - 18, y), (x - 22, y - 6), (x - 20, y - 16),
        (x - 14, y - 26), (x - 6, y - 30), (x, y - 28),
        (x + 6, y - 30), (x + 14, y - 26), (x + 20, y - 16),
        (x + 22, y - 6), (x + 18, y),
    ]
    pygame.draw.polygon(surf, ROCK_MAIN, pts)
    # Highlight
    highlight_pts = [
        (x - 6, y - 30), (x - 12, y - 22), (x - 16, y - 14),
        (x - 14, y - 18), (x - 8, y - 26),
    ]
    pygame.draw.polygon(surf, ROCK_LIGHT, highlight_pts)
    # Dark crevices
    pygame.draw.line(surf, ROCK_DARK, (x - 4, y - 24), (x + 2, y - 18), 2)
    pygame.draw.line(surf, ROCK_DARK, (x + 8, y - 20), (x + 12, y - 12), 2)
    # Under-water base
    pygame.draw.ellipse(surf, ROCK_DARK, (x - 22, y - 4, 44, 8))
    # Bottom edge
    pygame.draw.rect(surf, ROCK_DARK, (x - 20, y - 2, 40, 4))


def draw_driftwood(surf, x, y):
    """Draw a driftwood log. (x,y) is bottom-center."""
    # Main log
    wood_rect = pygame.Rect(x - 28, y - 10, 56, 14)
    pygame.draw.ellipse(surf, WOOD_MAIN, wood_rect)
    # Wood grain lines
    pygame.draw.line(surf, WOOD_DARK, (x - 22, y - 6), (x + 20, y - 6), 1)
    pygame.draw.line(surf, WOOD_LIGHT, (x - 18, y - 3), (x + 16, y - 3), 1)
    pygame.draw.line(surf, WOOD_DARK, (x - 24, y - 1), (x + 22, y - 1), 1)
    # Knot
    pygame.draw.circle(surf, WOOD_DARK, (x + 5, y - 5), 3)
    pygame.draw.circle(surf, WOOD_LIGHT, (x + 5, y - 5), 1)
    # Branch stub
    stub_pts = [(x - 26, y - 5), (x - 32, y - 12), (x - 30, y - 14), (x - 24, y - 7)]
    pygame.draw.polygon(surf, WOOD_DARK, stub_pts)
    # Barnacles (small dots)
    for bx, by in [(x - 15, y - 8), (x + 8, y - 9), (x + 18, y - 7), (x - 5, y - 9)]:
        pygame.draw.circle(surf, (200, 190, 180), (bx, by), 2)
    # Under-water part
    pygame.draw.ellipse(surf, WOOD_DARK, (x - 28, y - 2, 56, 6), 1)


def draw_seagull(surf, x, y, frame):
    """Draw a seagull. (x,y) is center. Wings flap with frame."""
    wing_up = math.sin(frame * 0.15) * 20

    # Body
    body_ellipse = pygame.Rect(x - 14, y - 4, 28, 10)
    pygame.draw.ellipse(surf, SEAGULL_BODY, body_ellipse)

    # Tail
    tail_pts = [(x + 14, y - 2), (x + 22, y - 5), (x + 20, y + 3), (x + 14, y + 2)]
    pygame.draw.polygon(surf, SEAGULL_BODY, tail_pts)

    # Left wing
    wing1_pts = [(x - 6, y - 2), (x - 2, y - 8 - int(wing_up)),
                 (x - 12, y - 16 - int(wing_up)), (x - 18, y - 12 - int(wing_up)),
                 (x - 14, y - 4)]
    pygame.draw.polygon(surf, SEAGULL_WING, wing1_pts)

    # Right wing
    wing2_pts = [(x + 6, y - 2), (x + 10, y - 6 - int(wing_up * 0.7)),
                 (x + 4, y - 14 - int(wing_up * 0.7)), (x - 2, y - 10 - int(wing_up * 0.7)),
                 (x + 2, y - 2)]
    pygame.draw.polygon(surf, SEAGULL_WING, wing2_pts)

    # Beak
    beak_pts = [(x - 14, y - 1), (x - 22, y - 3), (x - 20, y + 1), (x - 14, y + 1)]
    pygame.draw.polygon(surf, SEAGULL_BEAK, beak_pts)

    # Eye
    pygame.draw.circle(surf, SEAGULL_EYE, (x - 8, y - 2), 2)
    pygame.draw.circle(surf, (255, 255, 255), (x - 9, y - 3), 1)


def draw_shark_fin(surf, x, y, time):
    """Draw a shark fin cutting through water. (x,y) is water surface."""
    # Fin
    fin_pts = [
        (x, y - 5),
        (x - 6, y - 24),
        (x + 2, y - 28),
        (x + 10, y - 20),
        (x + 5, y - 5),
    ]
    pygame.draw.polygon(surf, SHARK_MAIN, fin_pts)
    # Fin dark tip
    tip_pts = [(x - 4, y - 22), (x + 2, y - 28), (x + 6, y - 22)]
    pygame.draw.polygon(surf, SHARK_DARK, tip_pts)
    # Water ripple around fin
    ripple = math.sin(time * 0.08 + x * 0.05) * 3
    pygame.draw.ellipse(surf, WAVE_HIGHLIGHT,
                        (x - 14, y - 4 + ripple, 28, 8), 1)

    # Shadow under water
    shadow_r = pygame.Rect(x - 12, y - 2, 24, 6)
    shadow = pygame.Surface((24, 6), pygame.SRCALPHA)
    shadow.fill((50, 70, 120, 60))
    surf.blit(shadow, (x - 12, y - 2))

    # Dorsal fin detail
    pygame.draw.line(surf, SHARK_LIGHT, (x - 2, y - 18), (x + 4, y - 22), 1)


# ============================================================
# GAME CLASS
# ============================================================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pixel Surf Cat")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        self.static_bg = render_static_bg()

        # Sounds
        self.snd_jump = make_sweep(300, 900, 0.12, 0.15)
        self.snd_duck = make_sound(200, 0.08, 0.1, 'square')
        self.snd_score = make_sweep(500, 1200, 0.1, 0.12)
        self.snd_hit = make_sound(80, 0.3, 0.3, 'saw')
        self.snd_gameover = make_sweep(600, 100, 0.5, 0.2)

        self.music = make_music()
        self.music.set_volume(0.35)
        self.music_playing = False

        self.reset()

    def reset(self):
        self.state = TITLE
        self.score = 0
        self.lives = INITIAL_LIVES
        self.scroll_speed = BASE_SCROLL
        self.time = 0
        self.frame = 0
        self.game_over_frame = 0

        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_interval = OBSTACLE_INTERVAL
        self.last_obstacle_score = 0

        self.player_vy = 0
        self.player_y = WATER_BASE - 8
        self.player_target_y = WATER_BASE - 8
        self.player_state = 'normal'
        self.player_on_ground = True
        self.player_ducking = False

        self.particles = []
        self.score_popups = []
        self.flash_timer = 0
        self.combo = 0

        self.music_stopped = False

    def play_music(self):
        if not self.music_playing:
            self.music.play(-1)
            self.music_playing = True

    def stop_music(self):
        if self.music_playing:
            self.music.stop()
            self.music_playing = False
            self.music_stopped = True

    def spawn_obstacle(self):
        """Spawn a random obstacle at the right edge."""
        obstacle_type = random.choice(['rock', 'rock', 'driftwood', 'driftwood', 'seagull', 'shark'])

        if obstacle_type == 'rock':
            wy = get_water_y(WIDTH, self.time) - 2
            y_pos = wy
            self.obstacles.append({
                'type': 'rock',
                'rect': pygame.Rect(WIDTH, y_pos - 30, 44, 30),
                'y': y_pos,
                'passed': False,
                'width': 44,
                'height': 30,
            })
        elif obstacle_type == 'driftwood':
            wy = get_water_y(WIDTH, self.time) - 4
            y_pos = wy
            self.obstacles.append({
                'type': 'driftwood',
                'rect': pygame.Rect(WIDTH, y_pos - 10, 56, 14),
                'y': y_pos,
                'passed': False,
                'width': 56,
                'height': 14,
            })
        elif obstacle_type == 'seagull':
            y_pos = 150 + random.randint(0, 60)
            self.obstacles.append({
                'type': 'seagull',
                'rect': pygame.Rect(WIDTH, y_pos - 12, 44, 28),
                'y': y_pos,
                'passed': False,
                'width': 44,
                'height': 28,
                'spawn_frame': self.frame,
            })
        else:  # shark
            wy = get_water_y(WIDTH, self.time) - 2
            y_pos = wy
            self.obstacles.append({
                'type': 'shark',
                'rect': pygame.Rect(WIDTH, y_pos - 30, 30, 30),
                'y': y_pos,
                'passed': False,
                'width': 30,
                'height': 30,
            })

    def add_particles(self, x, y, color, count=8):
        """Add particle effects."""
        for _ in range(count):
            self.particles.append({
                'x': x + random.randint(-5, 5),
                'y': y + random.randint(-5, 5),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-4, 1),
                'life': 20 + random.randint(0, 15),
                'max_life': 35,
                'color': color,
                'size': random.randint(2, 5),
            })

    def add_score_popup(self, x, y, text, color=UI_GOLD):
        """Add floating score text."""
        self.score_popups.append({
            'x': x, 'y': y, 'text': text,
            'color': color, 'life': 40, 'max_life': 40,
        })

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == TITLE:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.state = PLAYING
                        self.play_music()
                        self.reset_playing_state()
                elif self.state == PLAYING:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        if self.player_on_ground:
                            self.player_vy = JUMP_VEL
                            self.player_on_ground = False
                            self.player_state = 'jumping'
                            self.snd_jump.play()
                            self.add_particles(PLAYER_X, self.player_y,
                                               WAVE_FOAM, 6)
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.player_ducking = True
                        self.player_state = 'ducking'
                        self.snd_duck.play()
                elif self.state == GAME_OVER:
                    if event.key == pygame.K_r or event.key == pygame.K_SPACE:
                        self.reset()
                        self.state = PLAYING
                        self.play_music()
                    elif event.key == pygame.K_ESCAPE:
                        return False

            if event.type == pygame.KEYUP:
                if self.state == PLAYING:
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.player_ducking = False
                        if self.player_on_ground:
                            self.player_state = 'normal'

        # Continuous key handling
        keys = pygame.key.get_pressed()
        if self.state == PLAYING:
            # A/D movement
            pass  # Player stays at PLAYER_X for simplicity

        return True

    def reset_playing_state(self):
        """Reset playing-specific state, keeping score/lives intact."""
        self.obstacles = []
        self.spawn_timer = 0
        self.scroll_speed = BASE_SCROLL
        self.player_vy = 0
        self.player_state = 'normal'
        self.player_on_ground = True
        self.player_ducking = False
        self.particles = []
        self.score_popups = []
        self.flash_timer = 0
        self.combo = 0

    def update(self):
        self.time += 1 / FPS
        self.frame += 1

        if self.state == TITLE:
            return

        if self.state == GAME_OVER:
            self.game_over_frame += 1
            # Update existing particles
            self.update_particles()
            return

        # === PLAYING STATE ===

        # Scroll speed increases over time
        self.scroll_speed = BASE_SCROLL + (self.score / 200) * 0.5
        self.scroll_speed = min(self.scroll_speed, MAX_SCROLL)

        # Spawn obstacles
        self.spawn_timer += 1
        self.spawn_interval = max(MIN_OBSTACLE_INTERVAL,
                                  OBSTACLE_INTERVAL - int(self.score / 50) * 3)
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            if random.random() < 0.75:  # 75% chance to spawn (gives some breathing room)
                self.spawn_obstacle()

        # Move obstacles
        to_remove = []
        for obs in self.obstacles:
            obs['rect'].x -= self.scroll_speed
            if obs['rect'].x < -60:
                to_remove.append(obs)
                continue

            # Check if player passed the obstacle (for scoring)
            if not obs['passed'] and obs['rect'].x + obs['width'] < PLAYER_X:
                obs['passed'] = True
                self.score += 10
                self.combo += 1
                self.snd_score.play()
                self.add_score_popup(PLAYER_X + 30, self.player_y - 60,
                                     f"+10", UI_GOLD)
                if self.combo > 2:
                    bonus = self.combo * 2
                    self.score += bonus
                    self.add_score_popup(PLAYER_X + 30, self.player_y - 85,
                                         f"COMBOx{self.combo} +{bonus}",
                                         UI_PINK)

        for obs in to_remove:
            self.obstacles.remove(obs)

        # Player physics
        if not self.player_on_ground:
            self.player_vy += GRAVITY
            self.player_y += self.player_vy

            # Check landing
            wy = get_water_y(PLAYER_X, self.time) - 8
            if self.player_y >= wy:
                self.player_y = wy
                self.player_vy = 0
                self.player_on_ground = True
                if not self.player_ducking:
                    self.player_state = 'normal'
                else:
                    self.player_state = 'ducking'
                self.add_particles(PLAYER_X, self.player_y,
                                   WAVE_FOAM, 3)
        else:
            # Follow wave
            wy = get_water_y(PLAYER_X, self.time) - 8
            self.player_y = wy

            if self.player_ducking:
                self.player_state = 'ducking'
            else:
                self.player_state = 'normal'

        # Player hitbox
        if self.player_state == 'ducking':
            player_hitbox = pygame.Rect(PLAYER_X - 12, self.player_y - 22, 24, 22)
        else:
            player_hitbox = pygame.Rect(PLAYER_X - 10, self.player_y - 44, 20, 44)

        # Collision detection
        for obs in self.obstacles:
            if player_hitbox.colliderect(obs['rect']):
                self.lives -= 1
                self.flash_timer = 10
                self.snd_hit.play()
                self.add_particles(obs['rect'].centerx, obs['rect'].centery,
                                   (255, 100, 100), 12)
                self.add_score_popup(PLAYER_X, self.player_y - 50,
                                     "OW!", (255, 80, 80))
                self.obstacles.remove(obs)
                self.combo = 0

                if self.lives <= 0:
                    self.state = GAME_OVER
                    self.game_over_frame = 0
                    self.stop_music()
                    self.snd_gameover.play()
                break

        # Survival score (1 point per second)
        if self.frame % FPS == 0:
            self.score += 1

        # Flash timer
        if self.flash_timer > 0:
            self.flash_timer -= 1

        # Update particles and popups
        self.update_particles()
        self.update_popups()

    def update_particles(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.15
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)

    def update_popups(self):
        for p in self.score_popups[:]:
            p['y'] -= 1.5
            p['life'] -= 1
            if p['life'] <= 0:
                self.score_popups.remove(p)

    def draw(self):
        # Static background
        self.screen.blit(self.static_bg, (0, 0))

        if self.state == TITLE:
            self.draw_title()
        else:
            # Clouds
            draw_clouds(self.screen, self.time)

            # Ocean
            draw_ocean(self.screen, self.time)

            # Obstacles
            for obs in self.obstacles:
                if obs['type'] == 'rock':
                    draw_rock(self.screen, obs['rect'].centerx, obs['y'])
                elif obs['type'] == 'driftwood':
                    draw_driftwood(self.screen, obs['rect'].centerx, obs['y'])
                elif obs['type'] == 'seagull':
                    draw_seagull(self.screen, obs['rect'].centerx, obs['y'],
                                 obs.get('spawn_frame', 0) + self.frame)
                elif obs['type'] == 'shark':
                    draw_shark_fin(self.screen, obs['rect'].centerx, obs['y'],
                                   self.time)

            # Player (with flash effect)
            if self.flash_timer > 0 and self.flash_timer % 3 == 0:
                pass  # Skip drawing (flash effect)
            else:
                draw_cat_girl(self.screen, PLAYER_X, self.player_y,
                              self.player_state, self.frame, self.player_on_ground)

            # Particles
            for p in self.particles:
                alpha = int(255 * (p['life'] / p['max_life']))
                c = p['color']
                pygame.draw.circle(self.screen, c,
                                   (int(p['x']), int(p['y'])), p['size'])

            # Score popups
            for p in self.score_popups:
                alpha = int(255 * (p['life'] / p['max_life']))
                text = self.font_small.render(p['text'], True, p['color'])
                text.set_alpha(alpha)
                text_rect = text.get_rect(center=(int(p['x']), int(p['y'])))
                self.screen.blit(text, text_rect)

            # HUD
            self.draw_hud()

            if self.state == GAME_OVER:
                self.draw_game_over()

        pygame.display.flip()

    def draw_hud(self):
        """Draw score, lives, and combo on screen."""
        # Score
        score_text = self.font_medium.render(f"SCORE: {self.score}", True, UI_WHITE)
        # Score shadow
        score_shadow = self.font_medium.render(f"SCORE: {self.score}", True, UI_BLACK)
        self.screen.blit(score_shadow, (11, 11))
        self.screen.blit(score_text, (10, 10))

        # Lives
        heart_x = WIDTH - 120
        for i in range(self.lives):
            heart = self.font_small.render("♥", True, (255, 60, 80))
            self.screen.blit(heart, (heart_x + i * 30, 12))

        # Empty hearts
        for i in range(self.lives, INITIAL_LIVES):
            heart = self.font_small.render("♥", True, (100, 40, 50))
            self.screen.blit(heart, (heart_x + i * 30, 12))

        # Speed indicator
        speed_pct = int((self.scroll_speed - BASE_SCROLL) / (MAX_SCROLL - BASE_SCROLL) * 100)
        speed_text = self.font_small.render(f"SPD: {speed_pct}%", True, UI_WHITE)
        self.screen.blit(speed_text, (WIDTH // 2 - 30, 12))

        # Obstacle counter
        obs_text = self.font_small.render(f"OBS: {len(self.obstacles)}", True, (200, 200, 200))
        self.screen.blit(obs_text, (WIDTH // 2 + 60, 12))

    def draw_title(self):
        """Draw the title screen."""
        # Ocean on title
        draw_clouds(self.screen, self.time)
        draw_ocean(self.screen, self.time)

        # Draw a cat girl on the title
        wy = get_water_y(WIDTH // 2, self.time) - 8
        draw_cat_girl(self.screen, WIDTH // 2, wy, 'normal', self.frame, True)

        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 120))
        self.screen.blit(overlay, (0, 0))

        # Title
        title = self.font_large.render("PIXEL SURF CAT", True, UI_WHITE)
        title_shadow = self.font_large.render("PIXEL SURF CAT", True, UI_BLACK)
        title_rect = title.get_rect(center=(WIDTH // 2, 90))
        self.screen.blit(title_shadow, (WIDTH // 2 - title_rect.width // 2 + 2, 92))
        self.screen.blit(title, title_rect)

        # Subtitle/subtitle
        subtitle = self.font_medium.render("~ 像素冲浪猫娘 ~", True, UI_PINK)
        sub_rect = subtitle.get_rect(center=(WIDTH // 2, 140))
        self.screen.blit(subtitle, sub_rect)

        # Controls
        controls = [
            "W / UP   - 跳跃",
            "S / DOWN - 蹲下",
            "A / D    - 移动 (左右)",
        ]
        for i, ctrl in enumerate(controls):
            t = self.font_small.render(ctrl, True, (200, 200, 220))
            tr = t.get_rect(center=(WIDTH // 2, 200 + i * 30))
            self.screen.blit(t, tr)

        # Start prompt (blinking)
        if int(self.time * 2) % 2 == 0:
            start_text = self.font_medium.render("PRESS SPACE TO START", True, UI_GOLD)
            start_rect = start_text.get_rect(center=(WIDTH // 2, 320))
            self.screen.blit(start_text, start_rect)

        # Footer
        footer = self.font_small.render("v1.0 - Made with Pygame", True, (150, 150, 180))
        self.screen.blit(footer, (WIDTH // 2 - 80, HEIGHT - 30))

        # Cat face decoration
        cat_face_x = WIDTH - 80
        cat_face_y = HEIGHT - 50
        pygame.draw.circle(self.screen, CAT_FUR, (cat_face_x, cat_face_y), 15)
        ear1 = [(cat_face_x - 12, cat_face_y - 5), (cat_face_x - 6, cat_face_y - 18), (cat_face_x, cat_face_y - 5)]
        ear2 = [(cat_face_x, cat_face_y - 5), (cat_face_x + 6, cat_face_y - 18), (cat_face_x + 12, cat_face_y - 5)]
        pygame.draw.polygon(self.screen, CAT_FUR, ear1)
        pygame.draw.polygon(self.screen, CAT_FUR, ear2)

    def draw_game_over(self):
        """Draw the game over overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over = self.font_large.render("GAME OVER", True, (255, 80, 80))
        go_shadow = self.font_large.render("GAME OVER", True, UI_BLACK)
        go_rect = game_over.get_rect(center=(WIDTH // 2, 100))
        self.screen.blit(go_shadow, (WIDTH // 2 - go_rect.width // 2 + 2, 102))
        self.screen.blit(game_over, go_rect)

        # Final score
        score_label = self.font_medium.render("FINAL SCORE", True, (200, 200, 200))
        score_label_rect = score_label.get_rect(center=(WIDTH // 2, 160))
        self.screen.blit(score_label, score_label_rect)

        score_value = self.font_large.render(str(self.score), True, UI_GOLD)
        score_value_rect = score_value.get_rect(center=(WIDTH // 2, 205))
        self.screen.blit(score_value, score_value_rect)

        # Best combo
        if self.combo > 0:
            combo_text = self.font_small.render(f"Best Combo: x{self.combo}", True, UI_PINK)
            combo_rect = combo_text.get_rect(center=(WIDTH // 2, 245))
            self.screen.blit(combo_text, combo_rect)

        # Stats
        survived = int(self.time)
        stats = f"Survived: {survived // 60}:{survived % 60:02d}"
        stats_text = self.font_small.render(stats, True, (180, 180, 200))
        stats_rect = stats_text.get_rect(center=(WIDTH // 2, 270))
        self.screen.blit(stats_text, stats_rect)

        # Restart prompt (blinking)
        if int(self.time * 2) % 2 == 0:
            restart = self.font_medium.render("PRESS R OR SPACE TO RESTART", True, UI_WHITE)
            restart_rect = restart.get_rect(center=(WIDTH // 2, 330))
            self.screen.blit(restart, restart_rect)

        # Quit hint
        quit_text = self.font_small.render("Press ESC to quit", True, (120, 120, 140))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, 365))
        self.screen.blit(quit_text, quit_rect)

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    Game().run()
