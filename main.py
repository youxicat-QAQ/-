"""
像素冲浪猫娘 - 像素冲浪猫娘小游戏
使用Pygame制作的横向卷轴冲浪游戏
"""

import pygame  # 导入Pygame库，用于游戏开发
import random  # 导入随机数模块，用于随机事件
import math  # 导入数学模块，用于数学计算
import struct  # 导入结构体模块，用于音频数据处理
import sys  # 导入系统模块，用于退出程序
import os  # 导入操作系统模块，用于字体文件路径检测

# ============================================================
# INITIALIZATION
# ============================================================
pygame.init()  # 初始化Pygame
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)  # 初始化音频混音器

# ============================================================
# CONSTANTS
# ============================================================
WIDTH, HEIGHT = 800, 400  # 屏幕宽度和高度
FPS = 60  # 每秒帧数
GRAVITY = 0.6  # 重力加速度
JUMP_VEL = -9.5  # 跳跃初始速度
BASE_SCROLL = 3  # 基础滚动速度
MAX_SCROLL = 8  # 最大滚动速度
PLAYER_X = 160  # 玩家X位置
WATER_BASE = 290  # 水面基础Y位置
INITIAL_LIVES = 3  # 初始生命数
OBSTACLE_INTERVAL = 90  # 障碍物间隔帧数（随时间减少）
MIN_OBSTACLE_INTERVAL = 35  # 最小障碍物间隔

# States
TITLE, PLAYING, GAME_OVER = 0, 1, 2  # 游戏状态：标题、游戏中、游戏结束

# ============================================================
# COLORS (bright pixel palette)
# ============================================================
SKY_TOP = (80, 160, 255)  # 天空顶部颜色
SKY_BOTTOM = (180, 220, 255)  # 天空底部颜色
SUN_COLOR = (255, 240, 80)  # 太阳颜色
SUN_GLOW = (255, 250, 180)  # 太阳光晕颜色
CLOUD_WHITE = (255, 255, 255)  # 云白色
CLOUD_SHADOW = (220, 220, 230)  # 云阴影

WATER_DEEP = (20, 60, 160)  # 深水颜色
WATER_MID = (30, 100, 200)  # 中水颜色
WATER_LIGHT = (60, 160, 240)  # 浅水颜色
WAVE_FOAM = (220, 240, 255)  # 波浪泡沫颜色
WAVE_HIGHLIGHT = (120, 200, 255)  # 波浪高光颜色

SAND = (230, 200, 150)  # 沙滩颜色
SAND_DARK = (200, 170, 120)  # 深沙滩颜色

CAT_FUR = (255, 220, 220)  # 猫毛颜色
CAT_SWIMSUIT = (255, 80, 140)  # 猫泳衣颜色
CAT_SWIMSUIT_DARK = (220, 50, 110)  # 猫泳衣深色
CAT_EARS_INNER = (255, 180, 190)  # 猫耳朵内侧颜色
CAT_EYES = (60, 40, 40)  # 猫眼睛颜色
CAT_MOUTH = (200, 60, 60)  # 猫嘴巴颜色
CAT_WHISKERS = (80, 60, 60)  # 猫胡须颜色
CAT_TAIL_TIP = (255, 255, 255)  # 猫尾巴尖颜色
CAT_HEADBAND = (255, 100, 150)  # 猫头带颜色
CAT_BLUSH = (255, 160, 180)  # 猫脸红颜色

SURFBOARD_TOP = (255, 150, 40)  # 冲浪板顶部颜色
SURFBOARD_BOTTOM = (200, 190, 180)  # 冲浪板底部颜色
SURFBOARD_STRIPE1 = (255, 255, 255)  # 冲浪板条纹1颜色
SURFBOARD_STRIPE2 = (80, 200, 255)  # 冲浪板条纹2颜色

ROCK_MAIN = (130, 115, 100)  # 岩石主颜色
ROCK_LIGHT = (155, 140, 125)  # 岩石亮色
ROCK_DARK = (100, 85, 70)  # 岩石暗色

WOOD_MAIN = (160, 120, 70)  # 木头主颜色
WOOD_DARK = (120, 85, 45)  # 木头暗色
WOOD_LIGHT = (180, 145, 95)  # 木头亮色

SEAGULL_BODY = (240, 240, 245)  # 海鸥身体颜色
SEAGULL_WING = (200, 200, 210)  # 海鸥翅膀颜色
SEAGULL_BEAK = (255, 200, 50)  # 海鸥喙颜色
SEAGULL_EYE = (40, 40, 40)  # 海鸥眼睛颜色

SHARK_MAIN = (90, 90, 105)  # 鲨鱼主颜色
SHARK_DARK = (65, 65, 80)  # 鲨鱼暗色
SHARK_LIGHT = (120, 120, 135)  # 鲨鱼亮色

UI_WHITE = (255, 255, 255)  # UI白色
UI_BLACK = (20, 20, 30)  # UI黑色
UI_SHADOW = (0, 0, 0, 80)  # UI阴影
UI_GOLD = (255, 215, 0)  # UI金色
UI_PINK = (255, 150, 200)  # UI粉色

GRASS_GREEN = (100, 200, 80)  # 草绿色
SHELL_PINK = (255, 180, 170)  # 贝壳粉色

# ============================================================
# SOUND GENERATION
# ============================================================
def make_sound(freq, duration, vol=0.25, wave='square'):  # 生成合成音效函数
    """Generate a synth sound effect. wave: square|sine|saw|noise"""
    sr = 22050  # 采样率
    n = int(sr * duration)  # 样本数
    frames = []  # 帧列表
    for i in range(n):  # 循环生成每个样本
        t = i / sr  # 时间
        phase = (t * freq) % 1.0  # 相位
        if wave == 'square':  # 方波
            v = 1.0 if phase < 0.5 else -1.0  # 方波值
        elif wave == 'saw':  # 锯齿波
            v = 2.0 * phase - 1.0  # 锯齿波值
        elif wave == 'sine':  # 正弦波
            v = math.sin(2 * math.pi * freq * t)  # 正弦波值
        elif wave == 'noise':  # 噪声
            v = random.uniform(-1, 1)  # 随机噪声值
        else:  # 默认正弦波
            v = math.sin(2 * math.pi * freq * t)  # 正弦波值

        sample = int(v * vol * 30000)  # 计算样本值
        sample = max(-32768, min(32767, sample))  # 限制范围
        frames.append(struct.pack('<h', sample))  # 添加左声道
        frames.append(struct.pack('<h', sample))  # 添加右声道

    return pygame.mixer.Sound(buffer=b''.join(frames))  # 返回声音对象


def make_sweep(freq_start, freq_end, duration, vol=0.2):  # 生成频率扫描音效函数
    """Frequency sweep sound effect."""
    sr = 22050  # 采样率
    n = int(sr * duration)  # 样本数
    frames = []  # 帧列表
    for i in range(n):  # 循环生成每个样本
        t = i / sr  # 时间
        progress = t / duration  # 进度
        freq = freq_start + (freq_end - freq_start) * progress  # 当前频率
        phase = (t * freq) % 1.0  # 相位
        v = 1.0 if phase < 0.5 else -1.0  # 方波值
        env = 1.0 - progress  # 包络
        sample = int(v * vol * env * 30000)  # 计算样本值
        sample = max(-32768, min(32767, sample))  # 限制范围
        frames.append(struct.pack('<h', sample))  # 添加左声道
        frames.append(struct.pack('<h', sample))  # 添加右声道
    return pygame.mixer.Sound(buffer=b''.join(frames))  # 返回声音对象


def make_music():  # 生成背景音乐函数
    """Generate background chiptune music loop (about 4 seconds)."""
    sr = 22050  # 采样率
    duration = 4.0  # 时长
    n = int(sr * duration)  # 样本数

    # Melody notes (C major pentatonic feel)
    melody = [  # 旋律音符
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
    bass = [  # 贝斯音符
        (131, 0.5), (165, 0.5), (131, 0.5), (165, 0.5),
        (131, 0.5), (165, 0.5), (131, 0.5), (165, 0.5),
        (110, 0.5), (131, 0.5), (110, 0.5), (131, 0.5),
        (98, 0.5), (131, 0.5), (98, 0.5), (131, 0.5),
    ]

    # Hi-hat pattern
    hat = []  # 军鼓模式
    for i in range(int(duration / 0.125)):  # 循环生成军鼓
        hat.append((0, 0.1) if i % 2 == 0 else (0, 0.05))  # 交替音量

    # Generate all audio data
    frames = bytearray(n * 4)  # 16位立体声 = 4字节每帧
    for i in range(n):  # 循环生成每个样本
        t = i / sr  # 时间

        # Melody
        mel_idx = int(t / 0.3) % len(melody)  # 旋律索引
        mel_freq, mel_dur = melody[mel_idx]  # 旋律频率和时长
        local_t = t % 0.3  # 本地时间
        if local_t < mel_dur and mel_freq > 0:  # 如果在音符内
            mel_phase = (local_t * mel_freq) % 1.0  # 旋律相位
            mel_v = 1.0 if mel_phase < 0.5 else -1.0  # 旋律值
            mel_env = 1.0 - local_t / mel_dur  # 旋律包络
            mel_sample = mel_v * 0.08 * mel_env  # 旋律样本
        else:  # 否则静音
            mel_sample = 0  # 旋律样本为0

        # Bass
        bass_idx = int(t / 0.5) % len(bass)  # 贝斯索引
        bass_freq, bass_dur = bass[bass_idx]  # 贝斯频率和时长
        local_t_bass = t % 0.5  # 本地贝斯时间
        if local_t_bass < bass_dur and bass_freq > 0:  # 如果在贝斯音符内
            bass_phase = (local_t_bass * bass_freq) % 1.0  # 贝斯相位
            bass_v = 1.0 if bass_phase < 0.5 else -1.0  # 贝斯值
            bass_env = 1.0 - local_t_bass / bass_dur  # 贝斯包络
            bass_sample = bass_v * 0.12 * bass_env  # 贝斯样本
        else:  # 否则静音
            bass_sample = 0  # 贝斯样本为0

        # Hi-hat
        hat_idx = int(t / 0.125) % len(hat)  # 军鼓索引
        _, hat_dur = hat[hat_idx]  # 军鼓时长
        local_t_hat = t % 0.125  # 本地军鼓时间
        hat_v = 0  # 军鼓值
        if local_t_hat < hat_dur:  # 如果在军鼓内
            hat_v = random.uniform(-1, 1) * 0.04 * (1 - local_t_hat / hat_dur)  # 军鼓值

        # Mix
        mixed = mel_sample + bass_sample + hat_v  # 混合
        mixed = max(-1, min(1, mixed))  # 限制混合值
        sample = int(mixed * 30000)  # 计算样本
        sample = max(-32768, min(32767, sample))  # 限制样本

        offset = i * 4  # 偏移
        frames[offset:offset+4] = struct.pack('<h', sample) + struct.pack('<h', sample)  # 打包帧

    return pygame.mixer.Sound(buffer=bytes(frames))  # 返回声音对象


# ============================================================
# PRE-RENDER STATIC BACKGROUND
# ============================================================
def render_static_bg():  # 渲染静态背景函数
    """Render sky gradient + sun to a surface (no clouds/waves)."""
    surf = pygame.Surface((WIDTH, HEIGHT))  # 创建表面
    # Sky gradient
    for y in range(WATER_BASE - 40):  # 循环Y坐标
        t = y / (WATER_BASE - 40)  # 插值因子
        r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)  # 红色分量
        g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)  # 绿色分量
        b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)  # 蓝色分量
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))  # 绘制线

    # Sun glow
    sun_x, sun_y = 680, 60  # 太阳位置
    for r in range(60, 0, -4):  # 循环半径
        alpha = max(0, 80 - r * 2)  # 透明度
        glow = (SUN_GLOW[0], SUN_GLOW[1], SUN_GLOW[2])  # 光晕颜色
        pygame.draw.circle(surf, glow, (sun_x, sun_y), r)  # 绘制光晕
    # Sun
    pygame.draw.circle(surf, SUN_COLOR, (sun_x, sun_y), 25)  # 绘制太阳
    pygame.draw.circle(surf, (255, 245, 150), (sun_x, sun_y), 20)  # 绘制太阳内部

    # Distant beach strip
    beach_y = WATER_BASE - 25  # 海滩Y位置
    for y_offset in range(25):  # 循环偏移
        y = beach_y + y_offset  # 当前Y
        shade = 1.0 - y_offset / 25  # 阴影因子
        c = (int(SAND[0] * shade + WATER_MID[0] * (1 - shade)),  # 颜色计算
             int(SAND[1] * shade + WATER_MID[1] * (1 - shade)),
             int(SAND[2] * shade + WATER_MID[2] * (1 - shade)))
        pygame.draw.line(surf, c, (0, y), (WIDTH, y))  # 绘制线

    return surf  # 返回表面


# ============================================================
# DRAWING FUNCTIONS
# ============================================================
def draw_clouds(surf, time):  # 绘制云函数
    """Draw pixel-art clouds scrolling at different speeds."""
    colors = [(255, 255, 255), (245, 245, 250), (235, 235, 245)]  # 云颜色
    layers = [  # 云层
        (0.2, [(100, 50, 60), (400, 80, 50), (650, 40, 70)]),
        (0.5, [(200, 90, 40), (550, 70, 55), (720, 100, 35)]),
        (0.8, [(50, 110, 45), (300, 130, 50), (600, 120, 40)]),
    ]
    for speed, clouds in layers:  # 循环层
        offset = int(time * speed * 0.5) % (WIDTH + 200)  # 偏移
        for cx, cy, size in clouds:  # 循环云
            x = (cx - offset) % (WIDTH + 200) - 100  # X位置
            y = cy  # Y位置
            # Draw cloud as overlapping circles
            c = colors[layers.index((speed, clouds))]  # 颜色
            for dx, dy, r in [(0, 0, size//2), (size//3, -2, size//3),  # 循环绘制圆
                              (-size//3, 2, size//3), (size//2, 2, size//4)]:
                pygame.draw.circle(surf, c, (x + dx, y + dy), r)  # 绘制圆


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
def load_chinese_font(size):
    """加载支持中文显示的系统字体，解决中文显示为方框的问题"""
    # 优先尝试从Windows字体目录加载中文字体文件
    font_paths = [
        'C:/Windows/Fonts/msyh.ttc',     # 微软雅黑
        'C:/Windows/Fonts/msyhbd.ttc',   # 微软雅黑粗体
        'C:/Windows/Fonts/simhei.ttf',   # 黑体
        'C:/Windows/Fonts/simsun.ttc',   # 宋体
    ]
    for path in font_paths:
        if os.path.exists(path):
            return pygame.font.Font(path, size)
    # 如果字体文件找不到，尝试通过系统名称加载
    sys_font = pygame.font.SysFont(['microsoftyaheui', 'simhei', 'simsun'], size)
    if sys_font:
        return sys_font
    # 最终回退默认字体（可能不显示中文）
    return pygame.font.Font(None, size)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("像素冲浪猫娘")
        self.clock = pygame.time.Clock()
        self.font_large = load_chinese_font(64)
        self.font_medium = load_chinese_font(36)
        self.font_small = load_chinese_font(24)

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
                                         f"连击x{self.combo} +{bonus}",
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
                                     "哎呀!", (255, 80, 80))
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
        score_text = self.font_medium.render(f"分数: {self.score}", True, UI_WHITE)
        # 分数阴影
        score_shadow = self.font_medium.render(f"分数: {self.score}", True, UI_BLACK)
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
        speed_text = self.font_small.render(f"速度: {speed_pct}%", True, UI_WHITE)
        self.screen.blit(speed_text, (WIDTH // 2 - 30, 12))

        # Obstacle counter
        obs_text = self.font_small.render(f"障碍: {len(self.obstacles)}", True, (200, 200, 200))
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
        title = self.font_large.render("像素冲浪猫娘", True, UI_WHITE)
        title_shadow = self.font_large.render("像素冲浪猫娘", True, UI_BLACK)
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
            start_text = self.font_medium.render("按空格键开始", True, UI_GOLD)
            start_rect = start_text.get_rect(center=(WIDTH // 2, 320))
            self.screen.blit(start_text, start_rect)

        # Footer
        footer = self.font_small.render("v2.0 - 使用Pygame制作", True, (150, 150, 180))
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
        game_over = self.font_large.render("游戏结束", True, (255, 80, 80))
        go_shadow = self.font_large.render("游戏结束", True, UI_BLACK)
        go_rect = game_over.get_rect(center=(WIDTH // 2, 100))
        self.screen.blit(go_shadow, (WIDTH // 2 - go_rect.width // 2 + 2, 102))
        self.screen.blit(game_over, go_rect)

        # Final score
        score_label = self.font_medium.render("最终分数", True, (200, 200, 200))
        score_label_rect = score_label.get_rect(center=(WIDTH // 2, 160))
        self.screen.blit(score_label, score_label_rect)

        score_value = self.font_large.render(str(self.score), True, UI_GOLD)
        score_value_rect = score_value.get_rect(center=(WIDTH // 2, 205))
        self.screen.blit(score_value, score_value_rect)

        # Best combo
        if self.combo > 0:
            combo_text = self.font_small.render(f"最高连击: x{self.combo}", True, UI_PINK)
            combo_rect = combo_text.get_rect(center=(WIDTH // 2, 245))
            self.screen.blit(combo_text, combo_rect)

        # Stats
        survived = int(self.time)
        stats = f"存活时间: {survived // 60}:{survived % 60:02d}"
        stats_text = self.font_small.render(stats, True, (180, 180, 200))
        stats_rect = stats_text.get_rect(center=(WIDTH // 2, 270))
        self.screen.blit(stats_text, stats_rect)

        # Restart prompt (blinking)
        if int(self.time * 2) % 2 == 0:
            restart = self.font_medium.render("按R或空格键重新开始", True, UI_WHITE)
            restart_rect = restart.get_rect(center=(WIDTH // 2, 330))
            self.screen.blit(restart, restart_rect)

        # Quit hint
        quit_text = self.font_small.render("按ESC退出", True, (120, 120, 140))
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
