#!/usr/bin/env python3
"""Box Head – 2.5D Isometric Edition  |  Neon Noire Visual Overhaul"""

import pygame
import math
import random
import sys

# ── Init ─────────────────────────────────────────────────────────────────────────
pygame.init()
WIDTH, HEIGHT = 1024, 768
FPS = 60
WW, WH = 1600, 1200
COS30 = math.cos(math.radians(30))
SIN30 = math.sin(math.radians(30))
SHD = 0.85
CAM_L = 0.08

# ═══════════════════════════════════════════════════════════════════════════════
# NEON NOIRE PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
C_BG         = (18, 18, 24)
C_FLOOR_A    = (32, 34, 42)
C_FLOOR_B    = (26, 28, 34)
C_FLOOR_LINE = (44, 46, 56)
C_WALL_BASE  = (58, 62, 78)
C_WALL_TOP   = (78, 82, 100)
C_WALL_LEFT  = (40, 44, 58)
C_WALL_EDGE  = (100, 110, 140)
C_DEST_WALL  = (110, 85, 55)
C_BARRICADE  = (70, 75, 90)
C_CRATE      = (130, 95, 45)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255, 50, 50)
GRAY   = (130, 130, 130)
DGRAY  = (60, 60, 60)

# Accent neon colours
NEON_CYAN    = (0, 229, 255)
NEON_PINK    = (255, 45, 120)
NEON_GREEN   = (170, 255, 0)
NEON_AMBER   = (255, 179, 0)
NEON_PURPLE  = (180, 80, 255)
NEON_RED     = (255, 30, 60)

# ── Isometric Math ───────────────────────────────────────────────────────────────
def w2s(wx, wy):
    return ((wx - wy) * COS30, (wx + wy) * SIN30)

def s2w(sx, sy):
    wx = (sx / COS30 + sy / SIN30) / 2
    wy = (sy / SIN30 - sx / COS30) / 2
    return wx, wy

# ── Game Data ────────────────────────────────────────────────────────────────────
WPN = {
    "pistol":  dict(dmg=30, rate=13, spd=16, spr=.03, n=1, ammo=9999, per=0, nm="Pistol",  gl=16, gw=5, bc=(255,255,100), fs=8, bl=12),
    "shotgun": dict(dmg=18, rate=39, spd=13, spr=.20, n=7, ammo=30,   per=8, nm="Shotgun", gl=24, gw=7, bc=(255,180,60),  fs=16,bl=10),
    "uzi":     dict(dmg=10, rate=3,  spd=19, spr=.09, n=1, ammo=150,  per=35,nm="Uzi",     gl=19, gw=5, bc=(255,240,200), fs=6, bl=18),
    "grenade": dict(dmg=120,rate=60, spd=9,  spr=.00, n=1, ammo=8,    per=2, nm="Grenade", gl=12, gw=8, bc=(90,90,90),    fs=6, bl=0),
}
WALLS_DEF = [
    (180,130,20,220),(180,130,220,20),(1200,130,20,260),(1200,130,220,20),
    (180,850,260,20),(180,850,20,220),(1160,850,20,220),(1160,1050,260,20),
    (580,380,70,70),(950,380,70,70),(580,750,70,70),(950,750,70,70),
    (340,230,20,160),(340,230,130,20),(1060,280,20,160),(940,280,140,20),
    (340,810,130,20),(340,660,20,170),(940,810,140,20),(1060,660,20,170),
    (500,540,90,20),(1010,540,90,20),(750,280,20,90),(830,830,20,90),
    (440,90,20,110),(1140,90,20,110),(440,1000,20,110),(1140,1000,20,110),
    (700,550,20,100),(880,550,20,100),(700,450,200,20),(700,730,200,20),
]
DST_SET = {8, 9, 10, 11, 20, 21}

Z_ST = {
    "normal": dict(hp=50, spd=1.3, dmg=10, sz=26, pt=10,
                   body=(75, 160, 55), head=(95, 190, 65), eye=(255, 40, 40), mouth=(35, 22, 18)),
    "fast":   dict(hp=30, spd=2.6, dmg=8,  sz=22, pt=15,
                   body=(190, 50, 50), head=(220, 70, 60), eye=(255, 255, 80), mouth=(45, 12, 12)),
    "big":    dict(hp=160,spd=.75, dmg=25, sz=38, pt=25,
                   body=(110, 70, 160), head=(140, 90, 185), eye=(255, 70, 70), mouth=(40, 18, 40)),
    "boss":   dict(hp=400,spd=1.0, dmg=35, sz=56, pt=100,
                   body=(180, 20, 20), head=(220, 35, 35), eye=(255, 255, 0), mouth=(55, 8, 8)),
}
PU_I = {
    "speed":  ((NEON_CYAN, "SPEED UP!")),
    "damage": ((NEON_AMBER, "DAMAGE x2!")),
    "shield": ((100, 200, 255), "SHIELD!"),
    "rapid":  ((NEON_GREEN, "RAPID FIRE!")),
}
POWERUP_TYPES = list(PU_I.keys())
STREAKS = [
    (3,"DOUBLE KILL",(NEON_GREEN)),(5,"TRIPLE KILL",(NEON_AMBER)),
    (8,"MULTI KILL",(255,150,0)),(12,"MEGA KILL",(NEON_PINK)),
    (16,"ULTRA KILL",(255,50,50)),(20,"UNSTOPPABLE!",NEON_PURPLE),
    (25,"GODLIKE!",NEON_AMBER),(30,"MASSACRE!",NEON_RED),
]
WPN_ICON_COL = {"pistol":(180,210,240),"shotgun":(NEON_AMBER),"uzi":(140,200,255),"grenade":(NEON_PINK)}
WPN_SLOT_KEY = {0:"1",1:"2",2:"3",3:"4"}

# ── Drawing Helpers ──────────────────────────────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Box Head – Neon Noire")
clock = pygame.time.Clock()
font_sm = pygame.font.SysFont("Arial", 13, bold=True)
font_md = pygame.font.SysFont("Arial", 18, bold=True)
font_lg = pygame.font.SysFont("Impact", 32)
font_xl = pygame.font.SysFont("Impact", 56)
font_title = pygame.font.SysFont("Impact", 78)
font_hud_num = pygame.font.SysFont("Consolas", 22, bold=True)
font_hud_sm = pygame.font.SysFont("Consolas", 13, bold=True)
font_combo = pygame.font.SysFont("Impact", 40, bold=True)
font_kf = pygame.font.SysFont("Arial", 12, bold=True)

# Pre-build vignette – deeper, more cinematic
vignette_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for i in range(120, 0, -1):
    alpha = int(255 * (1 - (i / 120.0)) ** 1.8 * 0.7)
    pygame.draw.circle(vignette_surf, (0, 0, 0, alpha), (WIDTH//2, HEIGHT//2), int(WIDTH*0.62 * (i/120.0)))

# Pre-build HUD panels – glassmorphism style
def _make_glass_panel(w, h, border_col=(60, 70, 100, 90), fill_col=(12, 12, 20, 175)):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill(fill_col)
    # Top highlight stripe
    pygame.draw.line(s, (*border_col[:3], 50), (1, 1), (w-2, 1), 1)
    pygame.draw.rect(s, border_col, (0, 0, w, h), 1, border_radius=8)
    return s

_hud_left_panel = _make_glass_panel(258, 215)
_hud_right_panel = _make_glass_panel(238, 98)

FLOOR_TILE = 40

def draw_text(surf, text, pos, color, font=font_md, center=False):
    ts = font.render(str(text), True, color)
    if center:
        r = ts.get_rect(center=pos)
        surf.blit(ts, r)
    else:
        surf.blit(ts, pos)

def draw_bar(surf, x, y, w, h, ratio, cf, ce, cb):
    pygame.draw.rect(surf, ce, (x, y, w, h))
    pygame.draw.rect(surf, cf, (x+1, y+1, int((w-2)*ratio), h-2))
    pygame.draw.rect(surf, cb, (x, y, w, h), 2)

def scale_color(c, f):
    return tuple(min(255, max(0, int(v * f))) for v in c)

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def draw_rounded_bar(surf, x, y, w, h, ratio, col_full, col_empty, radius=4):
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(bg, (*col_empty, 200), (0, 0, w, h), border_radius=radius)
    fw = max(0, int((w - 2) * ratio))
    if fw > 0:
        fill_s = pygame.Surface((fw, h - 2), pygame.SRCALPHA)
        top_c = tuple(min(255, c + 50) for c in col_full)
        bot_c = tuple(max(0, c - 40) for c in col_full)
        for row in range(h - 2):
            t = row / max(1, h - 3)
            c = lerp_color(top_c, bot_c, t)
            pygame.draw.line(fill_s, (*c, 235), (0, row), (fw, row))
        bg.blit(fill_s, (1, 1))
        if fw > 2:
            pygame.draw.line(bg, (*[min(255, c + 100) for c in col_full], 100), (2, 1), (fw, 1), 1)
            pygame.draw.line(bg, (*[min(255, c + 60) for c in col_full], 60), (2, 2), (fw, 2), 1)
    surf.blit(bg, (x, y))
    pygame.draw.rect(surf, (70, 75, 100, 130), (x, y, w, h), 1, border_radius=radius)

def draw_glow(surf, x, y, radius, color, alpha=80):
    gs = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -2):
        a = int(alpha * (r / radius) ** 0.4 * (1 - r / radius))
        if a > 0:
            pygame.draw.circle(gs, (*color, a), (radius, radius), r)
    surf.blit(gs, (x - radius, y - radius))

def draw_neon_glow(surf, x, y, radius, color, alpha=60):
    """Brighter, more focused neon glow with inner bloom."""
    gs = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        t = r / radius
        a = int(alpha * (1 - t ** 0.6) * t ** 0.3)
        if a > 0:
            c = lerp_color(color, WHITE, (1 - t) * 0.3)
            pygame.draw.circle(gs, (*c, a), (radius, radius), r)
    surf.blit(gs, (x - radius, y - radius))

# ═══════════════════════════════════════════════════════════════════════════════
# ISOMETRIC BLOCK  –  Neon Noire Edition
# ═══════════════════════════════════════════════════════════════════════════════
def draw_iso_block(surf, color, x, y, w, h, z_h=25, z_sort_offset=0):
    p1 = w2s(x, y); p2 = w2s(x+w, y); p3 = w2s(x+w, y+h); p4 = w2s(x, y+h)
    p5 = w2s(x, y-z_h); p6 = w2s(x+w, y-z_h); p7 = w2s(x+w, y+h-z_h); p8 = w2s(x, y+h-z_h)

    # ── Left face (darkest) ──
    left_c = scale_color(color, 0.55)
    pygame.draw.polygon(surf, left_c, [p1, p4, p8, p5])
    # Left face edge highlight (top edge)
    pygame.draw.line(surf, scale_color(color, 0.7), p5, p8, 1)

    # ── Right face (mid) ──
    right_c = scale_color(color, 0.8)
    pygame.draw.polygon(surf, right_c, [p2, p3, p7, p6])
    # Right face edge highlight
    pygame.draw.line(surf, scale_color(color, 0.95), p6, p7, 1)

    # ── Top face (brightest) ──
    top_c = scale_color(color, 1.3)
    pygame.draw.polygon(surf, top_c, [p5, p6, p2, p1])

    # ── Edge lines (neon-tinted) ──
    edge_c = scale_color(color, 1.7)
    # Top diamond outline
    pygame.draw.polygon(surf, edge_c, [p5, p6, p2, p1], 1)
    # Vertical edges (brighter, neon feel)
    vert_c = scale_color(color, 1.4)
    pygame.draw.line(surf, vert_c, p1, p5, 1)
    pygame.draw.line(surf, vert_c, p2, p6, 1)
    # Bottom edges (subtle)
    pygame.draw.line(surf, scale_color(color, 0.35), p4, p8, 1)
    pygame.draw.line(surf, scale_color(color, 0.35), p3, p7, 1)

    # ── Top surface cross detail ──
    mid_top = ((p5[0]+p6[0])//2, (p5[1]+p6[1])//2)
    mid_bot = ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2)
    mid_l = ((p5[0]+p1[0])//2, (p5[1]+p1[1])//2)
    mid_r = ((p6[0]+p2[0])//2, (p6[1]+p2[1])//2)
    pygame.draw.line(surf, scale_color(color, 1.6), mid_top, mid_bot, 1)
    pygame.draw.line(surf, scale_color(color, 1.6), mid_l, mid_r, 1)

    # ── Subtle top-face inner glow line along front edge ──
    glow_c = lerp_color(color, NEON_CYAN, 0.15)
    pygame.draw.line(surf, scale_color(glow_c, 1.8), p1, p2, 1)

    return (x + y + h + z_sort_offset)

# ═══════════════════════════════════════════════════════════════════════════════
# BOX-HEAD CHARACTER  –  Neon Noire Edition
# ═══════════════════════════════════════════════════════════════════════════════
def draw_box_character(surf, cx, cy, body_w, body_h, head_size,
                       body_col, head_col, eye_col, mouth_col,
                       facing_ang, frame, alpha=255,
                       head_offset_y=-2, is_boss=False, boss_state=None):
    s = pygame.Surface((body_w + 24, body_h + head_size * 2 + 14), pygame.SRCALPHA)

    bx = (s.get_width() - body_w) // 2
    by = head_size * 2 + head_offset_y

    # ── BODY ──
    # Main body
    pygame.draw.rect(s, (*body_col, alpha), (bx, by, body_w, body_h))
    # Left highlight strip
    hl_w = max(2, body_w // 4)
    pygame.draw.rect(s, (*scale_color(body_col, 1.35), alpha), (bx, by, hl_w, body_h))
    # Right shadow strip
    sh_w = max(2, body_w // 4)
    pygame.draw.rect(s, (*scale_color(body_col, 0.6), alpha), (bx + body_w - sh_w, by, sh_w, body_h))
    # Center mid-tone
    pygame.draw.rect(s, (*scale_color(body_col, 0.9), alpha), (bx + hl_w, by + body_h//3, body_w - hl_w - sh_w, body_h//3))
    # Outline
    pygame.draw.rect(s, (*scale_color(body_col, 0.35), alpha), (bx, by, body_w, body_h), 2)
    # Belt / detail line
    belt_y = by + body_h * 2 // 3
    pygame.draw.line(s, (*scale_color(body_col, 0.4), alpha), (bx + 1, belt_y), (bx + body_w - 1, belt_y), 1)

    # ── ARMS ──
    arm_w = max(4, body_w // 5)
    arm_h = max(6, body_h // 2)
    arm_swing = math.sin(frame * 0.15) * 3 if not is_boss else math.sin(frame * 0.1) * 2
    # Left arm
    la_y = int(by + 3 + arm_swing)
    pygame.draw.rect(s, (*scale_color(body_col, 0.8), alpha), (bx - arm_w + 2, la_y, arm_w, arm_h))
    pygame.draw.rect(s, (*scale_color(body_col, 1.1), alpha), (bx - arm_w + 2, la_y, max(1, arm_w//2), arm_h))
    pygame.draw.rect(s, (*scale_color(body_col, 0.4), alpha), (bx - arm_w + 2, la_y, arm_w, arm_h), 1)
    # Right arm
    ra_y = int(by + 3 - arm_swing)
    pygame.draw.rect(s, (*scale_color(body_col, 0.8), alpha), (bx + body_w - 2, ra_y, arm_w, arm_h))
    pygame.draw.rect(s, (*scale_color(body_col, 0.4), alpha), (bx + body_w - 2, ra_y, arm_w, arm_h), 1)

    # ── HEAD (the box) ──
    hx = (s.get_width() - head_size) // 2
    bob = math.sin(frame * 0.12) * 2 if not is_boss else math.sin(frame * 0.08) * 1.5
    hy = int(head_offset_y + bob)

    # Head shadow (under head)
    pygame.draw.rect(s, (*scale_color(head_col, 0.4), alpha // 2), (hx + 2, hy + 2, head_size, head_size))
    # Main head face
    pygame.draw.rect(s, (*head_col, alpha), (hx, hy, head_size, head_size))
    # Top-left highlight (3D cube feel)
    hl_w2 = max(2, head_size // 3)
    hl_h2 = max(2, head_size // 3)
    pygame.draw.rect(s, (*scale_color(head_col, 1.3), alpha), (hx, hy, hl_w2, hl_h2))
    # Bottom-right shadow
    sh_w2 = max(2, head_size // 4)
    sh_h2 = max(2, head_size // 4)
    pygame.draw.rect(s, (*scale_color(head_col, 0.65), alpha), (hx + head_size - sh_w2, hy + head_size - sh_h2, sh_w2, sh_h2))
    # Outline
    pygame.draw.rect(s, (*scale_color(head_col, 0.3), alpha), (hx, hy, head_size, head_size), 2)
    # Top edge bright line
    pygame.draw.line(s, (*scale_color(head_col, 1.6), alpha), (hx, hy), (hx + head_size, hy), 1)

    # ── FACE ──
    eye_size = max(2, head_size // 7)
    eye_y = hy + head_size // 3
    ex_off = int(math.cos(facing_ang) * (eye_size // 3))
    ey_off = int(math.sin(facing_ang) * (eye_size // 4))
    le_x = hx + head_size // 3 + ex_off
    le_y = eye_y + ey_off
    re_x = hx + head_size * 2 // 3 + ex_off
    re_y = eye_y + ey_off

    # Eye socket (darker background)
    ew = eye_size + 3
    socket_c = scale_color(eye_col, 0.25)
    pygame.draw.rect(s, (*socket_c, alpha), (le_x - 1, le_y - 1, ew, ew))
    pygame.draw.rect(s, (*socket_c, alpha), (re_x - 1, re_y - 1, ew, ew))
    # Eye glow (soft bloom behind eye)
    if alpha > 100:
        glow_s = pygame.Surface((ew + 4, ew + 4), pygame.SRCALPHA)
        pygame.draw.rect(glow_s, (*eye_col, min(50, alpha // 3)), (0, 0, ew + 4, ew + 4))
        s.blit(glow_s, (le_x - 3, le_y - 3))
        s.blit(glow_s, (re_x - 3, re_y - 3))
    # Pupils
    pygame.draw.rect(s, (*eye_col, alpha), (le_x + ex_off // 2, le_y + ey_off // 2, eye_size, eye_size))
    pygame.draw.rect(s, (*eye_col, alpha), (re_x + ex_off // 2, re_y + ey_off // 2, eye_size, eye_size))
    # Pupil highlight
    if eye_size >= 3:
        pygame.draw.rect(s, (255, 255, 255, min(220, alpha)),
                         (le_x + ex_off // 2, le_y + ey_off // 2, max(1, eye_size // 2), max(1, eye_size // 2)))
        pygame.draw.rect(s, (255, 255, 255, min(220, alpha)),
                         (re_x + ex_off // 2, re_y + ey_off // 2, max(1, eye_size // 2), max(1, eye_size // 2)))

    # Mouth
    mouth_y = hy + head_size * 2 // 3 + 2
    mouth_w = max(4, head_size // 2)
    mouth_h = max(3, head_size // 5)
    mouth_x = hx + (head_size - mouth_w) // 2
    pygame.draw.rect(s, (*mouth_col, alpha), (mouth_x, mouth_y, mouth_w, mouth_h))
    # Teeth
    if mouth_h >= 3 and mouth_w >= 6:
        for tx in range(mouth_x + 2, mouth_x + mouth_w - 1, max(2, mouth_w // 4)):
            pygame.draw.line(s, (220, 215, 200, alpha), (tx, mouth_y), (tx, mouth_y + mouth_h // 2), 1)
    # Mouth outline
    pygame.draw.rect(s, (*scale_color(mouth_col, 0.5), alpha), (mouth_x, mouth_y, mouth_w, mouth_h), 1)

    # Boss crown
    if is_boss:
        cr_y = hy - 7
        cr_x = hx + (head_size - 18) // 2
        pygame.draw.rect(s, (255, 215, 0, alpha), (cr_x, cr_y, 18, 8))
        pygame.draw.rect(s, (255, 240, 100, alpha), (cr_x, cr_y, 18, 3))
        pygame.draw.rect(s, (180, 140, 0, alpha), (cr_x, cr_y, 18, 8), 1)
        for px in [cr_x, cr_x + 6, cr_x + 12, cr_x + 17]:
            pygame.draw.rect(s, (255, 50, 50, alpha), (px - 1, cr_y - 5, 3, 6))
            pygame.draw.rect(s, (255, 150, 50, alpha), (px - 1, cr_y - 5, 3, 2))

    rot_deg = -math.degrees(facing_ang)
    rotated = pygame.transform.rotate(s, rot_deg)
    rect = rotated.get_rect(center=(cx, cy))
    surf.blit(rotated, rect)

# ── Entities ─────────────────────────────────────────────────────────────────────
class Entity:
    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.alive = True
        self.z_sort = 0
    def get_rect(self):
        return pygame.Rect(self.x - self.w/2, self.y - self.h/2, self.w, self.h)

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 28, 28)
        self.hp = 100; self.max_hp = 100; self.speed = 3.8
        self.weapons = ["pistol", "shotgun", "uzi", "grenade"]
        self.cw = 0; self.fcd = 0
        self.ammo = {k: WPN[k]["ammo"] for k in self.weapons}
        self.dashing = False; self.dash_t = 0; self.dash_cd = 0
        self.dash_dx = 0; self.dash_dy = 0; self.dash_trail = []
        self.pu_type = None; self.pu_timer = 0; self.last_hit = 0; self.regen_t = 0
        self.barricade_cd = 0; self.inv = 0; self.ang = 0
        self.vx = 0.0; self.vy = 0.0
        self.accel = 0.6; self.decel = 0.45; self.max_vx = 4.0
        self.sprinting = False; self.stamina = 100; self.max_stamina = 100
        self.move_frame = 0

    @property
    def wk(self): return self.weapons[self.cw]

    def update(self, keys, m_pos_w, game):
        if not self.alive: return
        if self.fcd > 0: self.fcd -= 1
        if self.barricade_cd > 0: self.barricade_cd -= 1
        if self.dash_cd > 0: self.dash_cd -= 1
        if self.pu_timer > 0:
            self.pu_timer -= 1
            if self.pu_timer <= 0: self.pu_type = None
        if game.frame - self.last_hit > 300:
            self.regen_t += 1
            if self.regen_t >= 180: self.regen_t = 0; self.hp = min(self.max_hp, self.hp + 1)
        else: self.regen_t = 0
        if self.inv > 0: self.inv -= 1

        if self.dashing:
            self.dash_t -= 1
            self.x += self.dash_dx * 11; self.y += self.dash_dy * 11
            self.x = max(14, min(WW-14, self.x)); self.y = max(14, min(WH-14, self.y))
            self.dash_trail.append((self.x, self.y, self.ang, 8))
            if self.dash_t <= 0: self.dashing = False
            return

        self.sprinting = keys[pygame.K_LSHIFT] and self.stamina > 0
        sprint_mult = 1.6 if self.sprinting else 1.0
        if self.sprinting:
            self.stamina = max(0, self.stamina - 0.4)
        else:
            self.stamina = min(self.max_stamina, self.stamina + 0.25)
        pu_mult = 1.5 if self.pu_type == "speed" else 1.0
        top_speed = self.speed * sprint_mult * pu_mult

        ix = iy = 0
        if keys[pygame.K_w]: iy -= 1
        if keys[pygame.K_s]: iy += 1
        if keys[pygame.K_a]: ix -= 1
        if keys[pygame.K_d]: ix += 1
        if ix and iy: ix *= 0.7071; iy *= 0.7071

        if ix != 0 or iy != 0:
            self.vx += ix * self.accel
            self.vy += iy * self.accel
            spd = math.hypot(self.vx, self.vy)
            if spd > top_speed:
                self.vx = self.vx / spd * top_speed
                self.vy = self.vy / spd * top_speed
            self.move_frame += 1
            if self.move_frame % 6 == 0 and spd > 1.5:
                game.effects.append(Effect(type="dust", x=self.x + random.uniform(-8, 8),
                                           y=self.y + random.uniform(-4, 8), life=18))
        else:
            if abs(self.vx) > 0.05:
                self.vx *= (1 - self.decel * 0.15)
                if abs(self.vx) < 0.05: self.vx = 0
            else:
                self.vx = 0
            if abs(self.vy) > 0.05:
                self.vy *= (1 - self.decel * 0.15)
                if abs(self.vy) < 0.05: self.vy = 0
            else:
                self.vy = 0

        ox, oy = self.x, self.y
        self.x += self.vx
        if self._hit_walls(game.walls): self.x = ox; self.vx = 0
        self.y += self.vy
        if self._hit_walls(game.walls): self.y = oy; self.vy = 0
        self.x = max(14, min(WW-14, self.x)); self.y = max(14, min(WH-14, self.y))
        self.ang = math.atan2(m_pos_w[1] - self.y, m_pos_w[0] - self.x)
        self.z_sort = self.x + self.y
        self.dash_trail = [(tx, ty, ta, tl - 1) for tx, ty, ta, tl in self.dash_trail if tl > 0]

    def dash(self, keys):
        if self.dashing or self.dash_cd > 0 or not self.alive: return
        dx = dy = 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        if dx == 0 and dy == 0: dx, dy = math.cos(self.ang), math.sin(self.ang)
        d = math.hypot(dx, dy)
        if d > 0: dx /= d; dy /= d
        self.dash_dx, self.dash_dy = dx, dy
        self.dashing = True; self.dash_t = 8; self.dash_cd = 90; self.inv = 10
        self.dash_trail = []

    def shoot(self, m_pos_w, game):
        if self.fcd > 0 or not self.alive: return
        wk = self.wk
        if self.ammo[wk] <= 0: return
        w = WPN[wk]
        if wk != "pistol": self.ammo[wk] -= 1
        rm = 1 - min(0.3, (game.wave-1)*0.01) if game.wave > 1 else 1.0
        if self.pu_type == "rapid": rm *= 0.5
        self.fcd = int(w["rate"] * rm)
        dm = 2.0 if self.pu_type == "damage" else 1.0
        for _ in range(w["n"]):
            a = self.ang + random.uniform(-w["spr"], w["spr"])
            gx = self.x + math.cos(self.ang)*24; gy = self.y + math.sin(self.ang)*24
            game.bullets.append(Bullet(gx, gy, a, wk, w["dmg"] * dm))
        fx = self.x + math.cos(self.ang)*30; fy = self.y + math.sin(self.ang)*30
        game.effects.append(Effect(type="flash", x=fx, y=fy, sz=w["fs"]))
        self.vx -= math.cos(self.ang) * (0.8 if wk == "shotgun" else 0.3)
        self.vy -= math.sin(self.ang) * (0.8 if wk == "shotgun" else 0.3)
        if wk in ("shotgun", "grenade"): game.shake(4 if wk == "shotgun" else 2)

    def take_damage(self, d, frame):
        if self.inv > 0 or self.dashing: return
        if self.pu_type == "shield": self.inv = 10; return
        self.hp -= d; self.inv = 30; self.last_hit = frame
        if self.hp <= 0: self.hp = 0; self.alive = False

    def _hit_walls(self, walls):
        pr = self.get_rect()
        for w in walls:
            if pr.colliderect(w.get_rect()): return True
        return False

    # ═══════════════════════════════════════════════════════════════════════════
    # PLAYER DRAW  –  Neon Noire
    # ═══════════════════════════════════════════════════════════════════════════
    def draw(self, surf, cx, cy):
        # Dash afterimage trail
        for tx, ty, ta, tl in self.dash_trail:
            tsx, tsy = w2s(tx, ty)
            tdx, tdy = tsx - cx, tsy - cy
            a = int(100 * (tl / 8))
            trail_s = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Neon afterimage
            pygame.draw.rect(trail_s, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], a), (2, 2, 28, 28))
            pygame.draw.rect(trail_s, (255, 255, 255, a // 3), (4, 4, 24, 24), 1)
            rotated = pygame.transform.rotate(trail_s, -math.degrees(ta))
            r = rotated.get_rect(center=(int(tdx), int(tdy)))
            surf.blit(rotated, r)

        sx, sy = w2s(self.x, self.y)
        dx, dy = sx - cx, sy - cy
        if not (-50 < dx < WIDTH+50 and -50 < dy < HEIGHT+50): return

        # Shadow
        shadow_s = pygame.Surface((40, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_s, (0, 0, 0, 50), (0, 0, 40, 16))
        pygame.draw.ellipse(shadow_s, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], 15), (2, 2, 36, 12), 1)
        surf.blit(shadow_s, (dx - 20, dy + 10))

        # Player colours
        is_flash = self.inv % 6 >= 3 and self.inv > 0
        col = (160, 210, 255) if is_flash else (40, 140, 220)
        head_col = (190, 225, 255) if is_flash else (60, 170, 250)

        body_w, body_h = 22, 20
        head_sz = 16

        s = pygame.Surface((body_w + 28, body_h + head_sz * 2 + 14), pygame.SRCALPHA)
        bx_off = (s.get_width() - body_w) // 2
        by_off = head_sz * 2 - 2

        # ── Body ──
        pygame.draw.rect(s, (*col, 255), (bx_off, by_off, body_w, body_h))
        # Highlight strip (left)
        sw = max(2, body_w // 4)
        pygame.draw.rect(s, (*scale_color(col, 1.35), 255), (bx_off, by_off, sw, body_h))
        # Shadow strip (right)
        pygame.draw.rect(s, (*scale_color(col, 0.55), 255), (bx_off + body_w - sw, by_off, sw, body_h))
        # Center panel detail
        mid_x = bx_off + sw
        mid_w = body_w - 2 * sw
        if mid_w > 0:
            pygame.draw.rect(s, (*scale_color(col, 0.85), 255), (mid_x, by_off + 2, mid_w, body_h - 4))
        # Outline
        pygame.draw.rect(s, (*scale_color(col, 0.3), 255), (bx_off, by_off, body_w, body_h), 2)
        # Belt line
        belt_y = by_off + body_h * 2 // 3
        pygame.draw.line(s, (*scale_color(col, 0.4), 200), (bx_off + 1, belt_y), (bx_off + body_w - 1, belt_y), 1)
        # Chest emblem (small diamond)
        em_x = bx_off + body_w // 2
        em_y = by_off + body_h // 3
        pts = [(em_x, em_y - 3), (em_x + 3, em_y), (em_x, em_y + 3), (em_x - 3, em_y)]
        pygame.draw.polygon(s, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], 180), pts)
        pygame.draw.polygon(s, (255, 255, 255, 100), pts, 1)

        # ── Arms ──
        aw, ah = 5, 10
        arm_swing = math.sin(self.move_frame * 0.15) * 2
        # Left arm
        la_y = int(by_off + 3 + arm_swing)
        pygame.draw.rect(s, (*scale_color(col, 0.8), 255), (bx_off - 3, la_y, aw, ah))
        pygame.draw.rect(s, (*scale_color(col, 1.1), 255), (bx_off - 3, la_y, max(1, aw//2), ah))
        pygame.draw.rect(s, (*scale_color(col, 0.35), 255), (bx_off - 3, la_y, aw, ah), 1)
        # Right arm + gun
        ra_y = int(by_off + 3 - arm_swing)
        pygame.draw.rect(s, (*scale_color(col, 0.8), 255), (bx_off + body_w - 2, ra_y, aw, ah))
        pygame.draw.rect(s, (*scale_color(col, 0.35), 255), (bx_off + body_w - 2, ra_y, aw, ah), 1)

        # ── Gun ──
        gun_len = 16
        gun_x = bx_off + body_w + 2
        gun_y = by_off + body_h // 2 - 3
        wk_col = WPN_ICON_COL.get(self.wk, (180, 180, 180))
        # Gun body
        pygame.draw.rect(s, (*scale_color(wk_col, 0.85), 255), (gun_x, gun_y, gun_len, 5))
        # Gun highlight
        pygame.draw.rect(s, (*scale_color(wk_col, 1.2), 200), (gun_x, gun_y, gun_len, 2))
        # Gun grip
        pygame.draw.rect(s, (*scale_color(wk_col, 0.65), 255), (gun_x + 4, gun_y + 3, 5, 7))
        # Muzzle tip glow
        pygame.draw.rect(s, (255, 255, 200, 120), (gun_x + gun_len - 2, gun_y, 2, 5))

        # ── Head ──
        hx = (s.get_width() - head_sz) // 2
        hy = 0
        spd = math.hypot(self.vx, self.vy)
        if spd > 0.5:
            hy += int(math.sin(self.move_frame * 0.3) * 2)

        # Head shadow
        pygame.draw.rect(s, (*scale_color(head_col, 0.35), 128), (hx + 2, hy + 2, head_sz, head_sz))
        # Main head
        pygame.draw.rect(s, (*head_col, 255), (hx, hy, head_sz, head_sz))
        # Top-left highlight
        hl = max(2, head_sz // 3)
        pygame.draw.rect(s, (*scale_color(head_col, 1.35), 255), (hx, hy, hl, hl))
        # Bottom-right shadow
        pygame.draw.rect(s, (*scale_color(head_col, 0.6), 255), (hx + head_sz - hl//2, hy + head_sz - hl//2, hl//2, hl//2))
        # Outline
        pygame.draw.rect(s, (*scale_color(head_col, 0.3), 255), (hx, hy, head_sz, head_sz), 2)
        # Top bright edge
        pygame.draw.line(s, (*scale_color(head_col, 1.6), 200), (hx, hy), (hx + head_sz, hy), 1)

        # ── Face ──
        esz = 3
        ey_y = hy + head_sz // 3
        ex_off = int(math.cos(self.ang) * 1)
        # Eye sockets
        pygame.draw.rect(s, (20, 20, 35, 255), (hx + 2 + ex_off, ey_y - 1, esz + 3, esz + 3))
        pygame.draw.rect(s, (20, 20, 35, 255), (hx + head_sz - 6 + ex_off, ey_y - 1, esz + 3, esz + 3))
        # Eye glow
        pygame.draw.rect(s, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], 60),
                         (hx + 2 + ex_off - 1, ey_y - 2, esz + 5, esz + 5))
        pygame.draw.rect(s, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], 60),
                         (hx + head_sz - 6 + ex_off - 1, ey_y - 2, esz + 5, esz + 5))
        # Whites
        pygame.draw.rect(s, (220, 230, 245, 255), (hx + 3 + ex_off, ey_y, esz + 1, esz + 1))
        pygame.draw.rect(s, (220, 230, 245, 255), (hx + head_sz - 5 + ex_off, ey_y, esz + 1, esz + 1))
        # Pupils
        pygame.draw.rect(s, (25, 30, 55, 255), (hx + 4 + ex_off, ey_y + 1, esz - 1, esz - 1))
        pygame.draw.rect(s, (25, 30, 55, 255), (hx + head_sz - 4 + ex_off, ey_y + 1, esz - 1, esz - 1))
        # Pupil highlights
        pygame.draw.rect(s, (255, 255, 255, 255), (hx + 4 + ex_off, ey_y + 1, 1, 1))
        pygame.draw.rect(s, (255, 255, 255, 255), (hx + head_sz - 4 + ex_off, ey_y + 1, 1, 1))

        # Mouth
        my = hy + head_sz * 2 // 3 + 2
        pygame.draw.rect(s, (45, 30, 25, 255), (hx + 4, my, head_sz - 8, 3))
        pygame.draw.rect(s, (30, 20, 15, 255), (hx + 4, my, head_sz - 8, 3), 1)
        for txx in range(hx + 5, hx + head_sz - 5, 3):
            pygame.draw.line(s, (220, 215, 200, 255), (txx, my), (txx, my + 1), 1)

        rotated = pygame.transform.rotate(s, -math.degrees(self.ang))
        rect = rotated.get_rect(center=(int(dx), int(dy)))
        surf.blit(rotated, rect)

        # Powerup aura (neon glow)
        if self.pu_type and self.pu_timer > 0:
            p = 0.5 + 0.5 * math.sin(self.pu_timer * 0.15)
            draw_neon_glow(surf, int(dx), int(dy), 32, PU_I[self.pu_type][0], int(80 * p))

class Zombie(Entity):
    def __init__(self, x, y, zt, wave):
        s = Z_ST[zt]; self.zt = zt; self.sz = s["sz"]
        super().__init__(x, y, s["sz"], s["sz"])
        hm = 60 if zt == "boss" else (12 if zt == "big" else 5)
        self.max_hp = s["hp"] + wave * hm; self.hp = self.max_hp
        self.speed = s["spd"] + wave * (.02 if zt == "boss" else (.05 if zt == "fast" else .03))
        self.dmg = s["dmg"] + wave * (3 if zt == "boss" else 2)
        self.pts = s["pt"]; self.atk_cd = 0; self.dying = False; self.dt = 0
        self.c = s["body"]; self.hc = s["head"]
        self.zz_t = 0 if zt == "fast" else -1
        self.facing = 0; self.walk_t = random.uniform(0, 6.28)
        if zt == "boss": self.bst = "normal"; self.btmr = 200; self.cdx = 0; self.cdy = 0

    def update(self, ppos, walls, zombies, game):
        if self.dying:
            self.dt += 1
            if self.dt >= 25: self.alive = False
            return
        self.z_sort = self.x + self.y
        if self.atk_cd > 0: self.atk_cd -= 1
        dx = ppos[0] - self.x; dy = ppos[1] - self.y; d = math.hypot(dx, dy)
        if d > 0: dx /= d; dy /= d
        self.facing = math.atan2(dy, dx)
        self.walk_t += 0.1 * (2.0 if self.zt == "fast" else 1.0)

        if self.zt == "boss": self._boss_tick(dx, dy, d, ppos, walls, zombies, game); return

        if self.zz_t >= 0:
            self.zz_t += 1; px, py = -dy, dx; zz = math.sin(self.zz_t * 0.2) * 2.5
            dx += px * zz * 0.3; dy += py * zz * 0.3
        sx, sy = 0, 0
        for oz in zombies:
            if oz is self or not oz.alive or oz.dying: continue
            ox = self.x - oz.x; oy = self.y - oz.y; od = math.hypot(ox, oy)
            if 0 < od < (self.sz + oz.sz) * 0.8:
                f = (self.sz + oz.sz - od) * 0.15 / od; sx += ox * f; sy += oy * f
        self._move(dx * self.speed + sx, dy * self.speed + sy, walls, ppos)

    def _boss_tick(self, dx, dy, d, ppos, walls, zombies, game):
        if self.bst == "normal":
            self.btmr -= 1; self._move(dx*self.speed*0.7, dy*self.speed*0.7, walls, ppos)
            if self.btmr <= 0: self.bst = "winding"; self.btmr = 45
        elif self.bst == "winding":
            self.btmr -= 1; self.x += random.uniform(-1,1); self.y += random.uniform(-1,1)
            if self.btmr <= 0: self.bst = "charging"; self.btmr = 28; self.cdx, self.cdy = dx, dy
        elif self.bst == "charging":
            self.btmr -= 1; self._move(self.cdx*6.0, self.cdy*6.0, walls, ppos)
            if self.btmr <= 0: self.bst = "stunned"; self.btmr = 50
        elif self.bst == "stunned":
            self.btmr -= 1
            if self.btmr <= 0: self.bst = "normal"; self.btmr = random.randint(160, 260)

    def _move(self, mx, my, walls, ppos):
        ox, oy = self.x, self.y
        self.x += mx
        if self._hit(walls): self.x = ox
        self.y += my
        if self._hit(walls): self.y = oy
        hs = self.sz/2
        self.x = max(hs, min(WW-hs, self.x)); self.y = max(hs, min(WH-hs, self.y))

    def take_damage(self, dmg, game):
        if self.dying: return False
        if self.zt == "boss" and self.bst == "stunned": dmg *= 1.5
        self.hp -= dmg
        game.effects.append(Effect(type="dmg", x=self.x, y=self.y-20, txt=str(int(dmg)), big=dmg>40))
        if self.hp <= 0:
            self.dying = True; self.dt = 0
            s = Z_ST[self.zt]
            for _ in range(4):
                game.effects.append(Effect(type="head_gib", x=self.x, y=self.y - self.sz * 0.3,
                    vx=random.uniform(-5, 5), vy=random.uniform(-7, -2),
                    col=s["head"], life=45))
            return True
        return False

    def _hit(self, walls):
        pr = self.get_rect()
        for w in walls:
            if pr.colliderect(w.get_rect()): return True
        return False

    # ═══════════════════════════════════════════════════════════════════════════
    # ZOMBIE DRAW  –  Neon Noire
    # ═══════════════════════════════════════════════════════════════════════════
    def draw(self, surf, cx, cy):
        sx, sy = w2s(self.x, self.y)
        dx, dy = sx - cx, sy - cy
        if not (-80 < dx < WIDTH+80 and -80 < dy < HEIGHT+80): return

        s = Z_ST[self.zt]
        scale = max(0.0, 1 - (self.dt / 25.0)) if self.dying else 1.0

        # Shadow (with coloured rim)
        if not self.dying:
            sh_sz = self.sz
            shadow_s = pygame.Surface((sh_sz + 6, (sh_sz + 6) // 3), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_s, (0, 0, 0, 40), (0, 0, sh_sz + 6, (sh_sz + 6) // 3))
            # Coloured rim on shadow for zombie type
            rim_c = s["eye"]
            pygame.draw.ellipse(shadow_s, (*rim_c, 20), (1, 1, sh_sz + 4, (sh_sz + 4) // 3), 1)
            surf.blit(shadow_s, (dx - (sh_sz + 6) // 2, dy + self.sz // 2))

        if scale <= 0.05: return

        body_col = s["body"]
        head_col = s["head"]
        eye_col = s["eye"]
        mouth_col = s["mouth"]
        if self.zt == "boss" and not self.dying:
            if self.bst == "winding":
                body_col = (240, 60, 60); head_col = (255, 85, 70)
                eye_col = (255, 255, 120)
            elif self.bst == "charging":
                body_col = (255, 200, 50); head_col = (255, 225, 70)
            elif self.bst == "stunned":
                eye_col = (255, 255, 220)

        alpha = int(max(0, 255 * scale)) if self.dying else 255
        if self.dying:
            body_col = scale_color(body_col, scale)
            head_col = scale_color(head_col, scale)
            eye_col = scale_color(eye_col, scale)
            mouth_col = scale_color(mouth_col, scale)

        if self.zt == "boss":
            bw = int(self.sz * 0.85); bh = int(self.sz * 0.6)
            head_sz = int(self.sz * 0.55)
        elif self.zt == "big":
            bw = int(self.sz * 0.8); bh = int(self.sz * 0.55)
            head_sz = int(self.sz * 0.5)
        elif self.zt == "fast":
            bw = int(self.sz * 0.7); bh = int(self.sz * 0.5)
            head_sz = int(self.sz * 0.5)
        else:
            bw = int(self.sz * 0.7); bh = int(self.sz * 0.5)
            head_sz = int(self.sz * 0.48)

        head_offset_y = -bh // 2 - head_sz // 2

        if self.dying:
            death_progress = self.dt / 25.0
            head_fly_y = -death_progress * 45
            head_fly_x = math.sin(self.dt * 0.4) * 12
            body_alpha = int(max(0, 255 * (1 - death_progress * 1.5)))

            if body_alpha > 10:
                bs = pygame.Surface((bw + 6, bh + 6), pygame.SRCALPHA)
                pygame.draw.rect(bs, (*body_col, body_alpha), (3, 3, bw, bh))
                pygame.draw.rect(bs, (*scale_color(body_col, 0.4), body_alpha), (3, 3, bw, bh), 1)
                rot = pygame.transform.rotate(bs, -math.degrees(self.facing))
                r = rot.get_rect(center=(int(dx), int(dy + 4)))
                surf.blit(rot, r)

            if alpha > 10:
                hs = head_sz + 6
                head_s = pygame.Surface((hs, hs), pygame.SRCALPHA)
                hsz2 = head_sz
                pygame.draw.rect(head_s, (*head_col, alpha), (3, 3, hsz2, hsz2))
                pygame.draw.rect(head_s, (*scale_color(head_col, 0.35), alpha), (3, 3, hsz2, hsz2), 1)
                esz = max(1, hsz2 // 6)
                ey_off = hsz2 // 3
                for ex_pos in [hsz2 // 3 + 3, hsz2 * 2 // 3]:
                    cx_e, cy_e = ex_pos + 3, ey_off + 3
                    pygame.draw.line(head_s, (*eye_col, alpha), (cx_e - esz, cy_e - esz), (cx_e + esz, cy_e + esz), 2)
                    pygame.draw.line(head_s, (*eye_col, alpha), (cx_e + esz, cy_e - esz), (cx_e - esz, cy_e + esz), 2)
                rot_deg = self.dt * 8
                rot = pygame.transform.rotate(head_s, rot_deg)
                r = rot.get_rect(center=(int(dx + head_fly_x), int(dy + head_offset_y + head_fly_y)))
                surf.blit(rot, r)
                # Trailing particles from flying head
                if self.dt % 3 == 0:
                    pass  # handled by head_gib effects already
        else:
            # Alive: draw full box-head
            # Eye glow behind character
            draw_glow(surf, int(dx), int(dy + head_offset_y * 0.3 - head_sz * 0.3),
                      head_sz, eye_col, 25)

            draw_box_character(surf, int(dx), int(dy + head_offset_y * 0.3),
                               bw, bh, head_sz,
                               body_col, head_col, eye_col, mouth_col,
                               self.facing, int(self.walk_t * 10),
                               alpha=alpha,
                               head_offset_y=head_offset_y,
                               is_boss=(self.zt == "boss"),
                               boss_state=self.bst if self.zt == "boss" else None)

        # HP bar
        if not self.dying and self.hp < self.max_hp:
            bar_w = self.sz + 4
            bar_y_pos = dy + head_offset_y * 0.3 - head_sz - 8
            hps = pygame.Surface((bar_w, 6), pygame.SRCALPHA)
            # Background
            pygame.draw.rect(hps, (15, 5, 5, 200), (0, 0, bar_w, 6), border_radius=2)
            r = max(0, self.hp / self.max_hp)
            if r > .5:
                hpc = NEON_GREEN
            elif r > .25:
                hpc = NEON_AMBER
            else:
                hpc = NEON_RED
            fw = max(0, int((bar_w - 2) * r))
            if fw > 0:
                pygame.draw.rect(hps, (*hpc, 230), (1, 1, fw, 4), border_radius=1)
                # Bright top edge on HP
                pygame.draw.line(hps, (*scale_color(hpc, 1.4), 150), (1, 1), (fw, 1), 1)
            pygame.draw.rect(hps, (0, 0, 0, 140), (0, 0, bar_w, 6), 1, border_radius=2)
            surf.blit(hps, (dx - bar_w // 2, bar_y_pos))

class Bullet(Entity):
    def __init__(self, x, y, a, wk, dmg):
        super().__init__(x, y, 4 if wk != "grenade" else 9, 4 if wk != "grenade" else 9)
        w = WPN[wk]
        self.wk = wk; self.dmg = dmg
        self.vx = math.cos(a) * w["spd"]; self.vy = math.sin(a) * w["spd"]
        self.ang = a; self.life = 160; self.bc = w["bc"]; self.bl = w["bl"]
        self.trail = []

    def update(self, game):
        if self.life % 2 == 0:
            self.trail.append((self.x, self.y))
            if len(self.trail) > 5:
                self.trail.pop(0)
        self.x += self.vx; self.y += self.vy; self.life -= 1
        self.z_sort = self.x + self.y
        if self.life <= 0 or self.x<-80 or self.x>WW+80 or self.y<-80 or self.y>WH+80:
            self.alive = False; return
        br = self.get_rect()
        for wall in game.walls[:]:
            if br.colliderect(wall.get_rect()):
                if self.wk == "grenade": self._explode(game)
                else:
                    if isinstance(wall, (DestWall, SupplyCrate)):
                        wall.take_damage(self.dmg if isinstance(wall, SupplyCrate) else self.dmg * 0.2)
                self.alive = False; return

    def _explode(self, game):
        game.effects.append(Effect(type="explosion", x=self.x, y=self.y))
        for i in range(4):
            game.effects.append(Effect(type="smoke_ring", x=self.x, y=self.y, life=35 + i * 12,
                                       col=(120, 100, 80)))
        game.shake(12); rad = 120
        for z in game.zombies:
            if not z.alive or z.dying: continue
            d = math.hypot(z.x - self.x, z.y - self.y)
            if d < rad: z.take_damage(self.dmg * (1 - d/rad), game)
        for wall in game.walls[:]:
            if isinstance(wall, (DestWall, SupplyCrate)):
                d = math.hypot(wall.x - self.x, wall.y - self.y)
                if d < rad: wall.take_damage(self.dmg * 0.8)
        pl = game.player
        if pl and pl.alive:
            d = math.hypot(pl.x - self.x, pl.y - self.y)
            if d < rad and pl.pu_type != "shield": pl.take_damage(25 * (1 - d/rad), game.frame)
        self.alive = False

    # ═══════════════════════════════════════════════════════════════════════════
    # BULLET DRAW  –  Neon Noire
    # ═══════════════════════════════════════════════════════════════════════════
    def draw(self, surf, cx, cy):
        sx, sy = w2s(self.x, self.y)
        dx, dy = sx - cx, sy - cy
        if not (-20 < dx < WIDTH+20 and -20 < dy < HEIGHT+20): return

        # Trail (fading, colour-matched)
        for i, (tx, ty) in enumerate(self.trail):
            tsx, tsy = w2s(tx, ty)
            tdx, tdy = tsx - cx, tsy - cy
            a = int(60 * (i + 1) / len(self.trail)) if self.trail else 60
            trail_w = max(2, 4 - i)
            ts = pygame.Surface((8, trail_w), pygame.SRCALPHA)
            pygame.draw.rect(ts, (*self.bc, a), (0, 0, 8, trail_w))
            # Bright core on trail
            pygame.draw.line(ts, (255, 255, 255, a // 2), (0, trail_w // 2), (8, trail_w // 2), 1)
            rotated = pygame.transform.rotate(ts, -math.degrees(self.ang))
            r = rotated.get_rect(center=(int(tdx), int(tdy)))
            surf.blit(rotated, r)

        if self.bl > 0:
            # Bullet with outer glow
            s = pygame.Surface((self.bl + 6, 8), pygame.SRCALPHA)
            # Outer glow
            pygame.draw.rect(s, (*scale_color(self.bc, 0.4), 70), (0, -1, self.bl + 6, 10), border_radius=2)
            # Main body
            pygame.draw.rect(s, (*self.bc, 240), (3, 1, self.bl, 6), border_radius=1)
            # Bright core
            pygame.draw.rect(s, (255, 255, 255, 180), (5, 2, self.bl - 2, 4))
            # Hot tip
            pygame.draw.rect(s, (255, 255, 255, 220), (self.bl + 1, 2, 3, 4))
            rotated = pygame.transform.rotate(s, -math.degrees(self.ang))
            rect = rotated.get_rect(center=(int(dx), int(dy)))
            surf.blit(rotated, rect)
        else:
            # Grenade with spin
            spin = self.life * 12
            gs = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Body
            pygame.draw.circle(gs, self.bc, (8, 8), 6)
            pygame.draw.circle(gs, scale_color(self.bc, 1.4), (6, 6), 2)
            pygame.draw.circle(gs, scale_color(self.bc, 0.5), (8, 8), 6, 1)
            # Fuse spark
            spark_a = int(128 + 127 * math.sin(self.life * 0.5))
            pygame.draw.circle(gs, (255, 200, 50, spark_a), (8, 1), 2)
            pygame.draw.circle(gs, (255, 255, 200, spark_a), (8, 1), 1)
            rotated = pygame.transform.rotate(gs, spin)
            r = rotated.get_rect(center=(int(dx), int(dy)))
            surf.blit(rotated, r)

class Wall(Entity):
    def __init__(self, x, y, w, h, z_h=25, color=C_WALL_BASE):
        super().__init__(x, y, w, h)
        self.z_h = z_h; self.color = color
    def get_rect(self): return pygame.Rect(self.x, self.y, self.w, self.h)
    def draw(self, surf, cx, cy): return draw_iso_block(surf, self.color, self.x, self.y, self.w, self.h, self.z_h, self.y + self.h)

class DestWall(Wall):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, 25, C_DEST_WALL)
        self.max_hp = 100; self.hp = 100
    def take_damage(self, d):
        self.hp -= d
        r = max(0, self.hp / self.max_hp)
        self.color = tuple(int(c * r + dc * (1-r)) for c, dc in zip((160,140,100), (50,40,30)))
        if self.hp <= 0: self.alive = False

class Barricade(DestWall):
    def __init__(self, x, y):
        super().__init__(x-15, y-15, 30, 30)
        self.max_hp = 60; self.hp = 60; self.color = C_BARRICADE

class SupplyCrate(Wall):
    def __init__(self, x, y):
        super().__init__(x-15, y-15, 30, 30, 15, C_CRATE)
        self.max_hp = 25; self.hp = 25
    def take_damage(self, d):
        self.hp -= d
        if self.hp <= 0: self.alive = False
    def draw(self, surf, cx, cy):
        r = draw_iso_block(surf, self.color, self.x, self.y, self.w, self.h, self.z_h, self.y + self.h)
        cxx = (self.x + self.w / 2); cyy = (self.y + self.h / 2)
        scx, scy = w2s(cxx, cyy - self.z_h)
        sdx, sdy = scx - cx, scy - cy
        if -30 < sdx < WIDTH+30 and -30 < sdy < HEIGHT+30:
            cs = pygame.Surface((14, 14), pygame.SRCALPHA)
            pygame.draw.line(cs, (NEON_AMBER[0], NEON_AMBER[1], NEON_AMBER[2], 200), (2, 2), (12, 12), 2)
            pygame.draw.line(cs, (NEON_AMBER[0], NEON_AMBER[1], NEON_AMBER[2], 200), (12, 2), (2, 12), 2)
            # Small glow
            pygame.draw.circle(cs, (NEON_AMBER[0], NEON_AMBER[1], NEON_AMBER[2], 40), (7, 7), 6)
            surf.blit(cs, (sdx - 7, sdy - 7))

class Pickup(Entity):
    def __init__(self, x, y, kind="health"):
        super().__init__(x, y, 26, 26)
        self.kind = kind; self.bob = random.uniform(0, 6.28)
    def update(self): self.bob += 0.1; self.y += math.sin(self.bob) * 0.18; self.z_sort = self.x + self.y

    # ═══════════════════════════════════════════════════════════════════════════
    # PICKUP DRAW  –  Neon Noire
    # ═══════════════════════════════════════════════════════════════════════════
    def draw(self, surf, cx, cy):
        sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
        if not (-30 < dx < WIDTH+30 and -30 < dy < HEIGHT+30): return
        glow_col = NEON_RED if self.kind == "health" else NEON_AMBER
        draw_neon_glow(surf, int(dx), int(dy), 22, glow_col, 45)
        bob_off = int(math.sin(self.bob) * 3)
        bs = pygame.Surface((22, 22), pygame.SRCALPHA)
        if self.kind == "health":
            # Red box with white cross
            pygame.draw.rect(bs, (NEON_RED[0], NEON_RED[1], NEON_RED[2], 220), (2, 2, 18, 18), border_radius=2)
            pygame.draw.rect(bs, (255, 100, 100, 180), (2, 2, 9, 9), border_radius=1)  # highlight
            pygame.draw.rect(bs, (180, 20, 30, 250), (2, 2, 18, 18), 2, border_radius=2)
            pygame.draw.rect(bs, (255, 255, 255, 245), (9, 5, 4, 12))
            pygame.draw.rect(bs, (255, 255, 255, 245), (5, 9, 12, 4))
        else:
            # Amber box with bullet
            pygame.draw.rect(bs, (NEON_AMBER[0], NEON_AMBER[1], NEON_AMBER[2], 220), (2, 2, 18, 18), border_radius=2)
            pygame.draw.rect(bs, (255, 230, 80, 180), (2, 2, 9, 9), border_radius=1)
            pygame.draw.rect(bs, (160, 120, 10, 250), (2, 2, 18, 18), 2, border_radius=2)
            pygame.draw.rect(bs, (60, 45, 10, 240), (9, 5, 4, 11))
            pygame.draw.rect(bs, (100, 80, 15, 240), (7, 3, 8, 4))
        rotated = pygame.transform.rotate(bs, self.bob * 0.5)
        r = rotated.get_rect(center=(int(dx), int(dy + bob_off)))
        surf.blit(rotated, r)

class PowerUp(Entity):
    def __init__(self, x, y, kind):
        super().__init__(x, y, 32, 32)
        self.kind = kind; self.bob = random.uniform(0, 6.28)
    def update(self): self.bob += 0.12; self.y += math.sin(self.bob) * 0.22; self.z_sort = self.x + self.y

    # ═══════════════════════════════════════════════════════════════════════════
    # POWERUP DRAW  –  Neon Noire
    # ═══════════════════════════════════════════════════════════════════════════
    def draw(self, surf, cx, cy):
        sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
        if not (-30 < dx < WIDTH+30 and -30 < dy < HEIGHT+30): return
        p = 0.5 + 0.5 * math.sin(self.bob * 1.5)
        r = int(16 + 6 * p)
        col = PU_I[self.kind][0]
        # Outer neon glow
        draw_neon_glow(surf, int(dx), int(dy), r + 14, col, 55)
        # Ring
        ring_s = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(ring_s, (*col, 60), (r+2, r+2), r + 1, 2)
        surf.blit(ring_s, (dx - r - 2, dy - r - 2))
        # Inner
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, 70), (r, r), r)
        pygame.draw.circle(s, (*col, 220), (r, r), 13)
        # Bright highlight
        pygame.draw.circle(s, (*scale_color(col, 1.5), 160), (r - 3, r - 3), 5)
        pygame.draw.circle(s, (255, 255, 255, 80), (r - 4, r - 4), 3)
        surf.blit(s, (dx - r, dy - r))

# ═══════════════════════════════════════════════════════════════════════════════
# EFFECTS  –  Neon Noire
# ═══════════════════════════════════════════════════════════════════════════════
class Effect:
    def __init__(self, **kw):
        self.type = kw.get("type"); self.x = kw.get("x", 0); self.y = kw.get("y", 0)
        self.life = kw.get("life", 30); self.max_life = self.life; self.alive = True
        self.txt = kw.get("txt", ""); self.big = kw.get("big", False)
        self.sz = kw.get("sz", 8); self.col = kw.get("col", (255,255,100))
        self.vx = kw.get("vx", 0); self.vy = kw.get("vy", 0)
        self.z_sort = self.x + self.y
    def update(self):
        self.life -= 1; self.x += self.vx; self.y += self.vy
        if self.vy < 0: self.vy += 0.15
        self.vx *= 0.92; self.vy *= 0.92
        if self.life <= 0: self.alive = False

    def draw(self, surf, cx, cy):
        t = 1 - (self.life / self.max_life)
        alpha = int(255 * (1 - t))

        if self.type == "blood":
            sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
            if -10<dx<WIDTH+10 and -10<dy<HEIGHT+10:
                s = pygame.Surface((12, 12), pygame.SRCALPHA)
                r = random.randint(2, 5)
                rc = random.randint(140, 220)
                pygame.draw.circle(s, (rc, random.randint(0, 20), random.randint(0, 15), alpha), (6, 6), r)
                # Brighter centre
                if r > 2:
                    pygame.draw.circle(s, (min(255, rc+40), 10, 10, alpha // 2), (6, 6), max(1, r // 2))
                surf.blit(s, (dx-6, dy-6))

        elif self.type == "dust":
            sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
            if -10<dx<WIDTH+10 and -10<dy<HEIGHT+10:
                s = pygame.Surface((10, 10), pygame.SRCALPHA)
                r = int(4 * (1 - t))
                pygame.draw.circle(s, (140, 135, 120, int(alpha * 0.4)), (5, 5), r)
                surf.blit(s, (dx-5, dy-5))

        elif self.type == "head_gib":
            sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
            if -20<dx<WIDTH+20 and -20<dy<HEIGHT+20:
                gs = pygame.Surface((12, 12), pygame.SRCALPHA)
                # Box head gib with shading
                pygame.draw.rect(gs, (*scale_color(self.col, 0.6), alpha), (1, 1, 10, 10))  # shadow
                pygame.draw.rect(gs, (*self.col, alpha), (0, 0, 10, 10))
                pygame.draw.rect(gs, (*scale_color(self.col, 1.3), alpha // 2), (0, 0, 4, 4))  # highlight
                pygame.draw.rect(gs, (*scale_color(self.col, 0.4), alpha), (0, 0, 10, 10), 1)
                # X eyes
                pygame.draw.line(gs, (255, 60, 60, alpha), (3, 3), (5, 5), 1)
                pygame.draw.line(gs, (255, 60, 60, alpha), (5, 3), (3, 5), 1)
                rot = pygame.transform.rotate(gs, self.vx * 20)
                r = rot.get_rect(center=(int(dx), int(dy)))
                surf.blit(rot, r)

        elif self.type == "smoke_ring":
            sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
            r = int(25 + 70 * t)
            a = int(alpha * 0.35 * (1 - t))
            if a > 0 and -r<dx<WIDTH+r and -r<dy<HEIGHT+r:
                s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                c = self.col if self.col else (120, 100, 80)
                # Double ring
                pygame.draw.circle(s, (*c, a), (r, r), r, max(1, int(4 * (1 - t))))
                if r > 10:
                    inner_a = a // 2
                    pygame.draw.circle(s, (*scale_color(c, 1.2), inner_a), (r, r), r - 4, max(1, int(2 * (1 - t))))
                surf.blit(s, (dx - r, dy - r))

        elif self.type == "dmg":
            sx, sy = w2s(self.x, self.y - (1-t)*30); dx, dy = sx - cx, sy - cy
            if -20<dx<WIDTH+20 and -20<dy<HEIGHT+10:
                f = font_sm if not self.big else font_md
                col = (NEON_PINK[0], NEON_PINK[1], NEON_PINK[2]) if self.big else (255, 255, 255)
                # Shadow
                ts = f.render(self.txt, True, (0, 0, 0))
                ts.set_alpha(alpha // 2)
                surf.blit(ts, (dx - ts.get_width()//2 + 1, dy - ts.get_height()//2 + 1))
                # Main text
                ts = f.render(self.txt, True, col)
                ts.set_alpha(alpha)
                surf.blit(ts, (dx - ts.get_width()//2, dy - ts.get_height()//2))

        elif self.type == "flash":
            sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
            if -30<dx<WIDTH+30 and -30<dy<HEIGHT+30:
                draw_neon_glow(surf, int(dx), int(dy), self.sz * 2 + 4, (255, 255, 200), int(alpha * 0.7))
                s = pygame.Surface((self.sz*2, self.sz*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 230, alpha), (self.sz, self.sz), self.sz)
                pygame.draw.circle(s, (255, 255, 255, min(255, int(alpha * 1.3))), (self.sz, self.sz), max(1, self.sz // 3))
                # Starburst rays
                for ang_i in range(6):
                    a_rad = ang_i * math.pi / 3 + t * 2
                    ex = int(self.sz + self.sz * 0.8 * t)
                    ey = int(self.sz + math.sin(a_rad) * self.sz * 0.5)
                    px = int(self.sz + math.cos(a_rad) * self.sz * 0.5)
                    pygame.draw.line(s, (255, 255, 200, alpha // 2),
                                     (self.sz + px // 2, self.sz + ey // 2),
                                     (self.sz + px, self.sz + ey), 1)
                surf.blit(s, (dx - self.sz, dy - self.sz))

        elif self.type == "explosion":
            sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
            r = int(35 + 110 * t)
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            if t < 0.12:
                c = (255,255,245,alpha); inner = (255,255,255,alpha)
            elif t < 0.3:
                c = (255,200,60,alpha); inner = (255,240,120,int(alpha*0.7))
            elif t < 0.55:
                c = (220,90,25,alpha); inner = (255,140,50,int(alpha*0.4))
            else:
                c = (90,80,75,alpha); inner = None
            pygame.draw.circle(s, c, (r, r), r)
            if inner and r > 10:
                pygame.draw.circle(s, inner, (r, r), r // 2)
            # Shockwave ring
            if t < 0.5:
                ring_r = int(r * 1.3)
                ring_a = int(alpha * 0.4 * (1 - t * 2))
                if ring_a > 0 and ring_r > 5:
                    pygame.draw.circle(s, (255, 220, 150, ring_a), (r, r), ring_r, max(1, int(3 * (1 - t * 2))))
            surf.blit(s, (dx - r, dy - r))

        elif self.type == "gibs":
            sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
            if -10<dx<WIDTH+10 and -10<dy<HEIGHT+10:
                s = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.rect(s, (*self.col, alpha), (0, 0, 6, 6))
                pygame.draw.rect(s, (*scale_color(self.col, 1.4), alpha), (0, 0, 3, 3))
                pygame.draw.rect(s, (*scale_color(self.col, 0.4), alpha), (0, 0, 6, 6), 1)
                surf.blit(s, (dx-4, dy-4))

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GAME CLASS
# ═══════════════════════════════════════════════════════════════════════════════
class Game:
    def __init__(self):
        self.state = "menu"; self.frame = 0; self.hi_score = 0
        self.kill_feed = []; self.total_kills = 0; self.time_played = 0
        self.reset_game()

    def reset_game(self):
        self.player = Player(WW/2, WH/2)
        self.zombies = []; self.bullets = []; self.walls = []; self.effects = []
        self.pickups = []; self.powerups = []
        self.score = 0; self.wave = 0; self.wave_timer = 120; self.announce = 130
        self.to_spawn = 0; self.spawn_cd = 0; self.wave_start = 0
        self.combo = 0; self.combo_t = 0; self.last_streak = 0
        self.kills = {"normal":0, "fast":0, "big":0, "boss":0}
        self.sx = 0; self.sy = 0; self.dmg_flash = 0
        self.hit_marks = []; self.boss_warn = 0; self.wc_bonus = 0; self.wc_bonus_t = 0
        self.wpn_ann = ""; self.wpn_ann_t = 0
        self.cx = WW/2; self.cy = WH/2
        self.kill_feed = []; self.total_kills = 0; self.time_played = 0
        for i, (x,y,w,h) in enumerate(WALLS_DEF):
            self.walls.append(DestWall(x,y,w,h) if i in DST_SET else Wall(x,y,w,h))

    def shake(self, a):
        self.sx += random.uniform(-a, a); self.sy += random.uniform(-a, a)

    def place_barricade(self):
        pl = self.player
        if not pl or pl.barricade_cd > 0 or self.score < 50: return
        bx = pl.x + math.cos(pl.ang)*45; by = pl.y + math.sin(pl.ang)*45
        b = Barricade(bx, by)
        for w in self.walls:
            if b.get_rect().colliderect(w.get_rect()): return
        self.walls.append(b); pl.barricade_cd = 30; self.score -= 50

    def _add_kill_feed(self, text, color=(255, 255, 255)):
        self.kill_feed.append((text, color, 180))
        if len(self.kill_feed) > 6: self.kill_feed.pop(0)

    def _nw(self):
        self.wave += 1; is_boss = self.wave % 5 == 0
        self.to_spawn = 5 + self.wave*3 + self.wave//3*2 + (0 if not is_boss else 1)
        self.spawn_cd = 0; self.announce = 130; self.wave_start = self.frame
        if is_boss: self.boss_warn = 180
        for _ in range(random.randint(2, 3)):
            cx2, cy2 = random.uniform(150, WW-150), random.uniform(150, WH-150)
            self.walls.append(SupplyCrate(cx2, cy2))

    def _sz(self):
        for _ in range(50):
            side = random.randint(0,3)
            if side==0: x,y = random.uniform(50,WW-50), 25
            elif side==1: x,y = random.uniform(50,WW-50), WH-25
            elif side==2: x,y = 25, random.uniform(50,WH-50)
            else: x,y = WW-25, random.uniform(50,WH-50)
            ok = True
            for w in self.walls:
                if pygame.Rect(x-20, y-20, 40, 40).colliderect(w.get_rect()): ok = False; break
            if ok:
                is_boss = self.wave % 5 == 0 and self.to_spawn == 1
                if is_boss: zt = "boss"
                else:
                    r = random.random()
                    if self.wave >= 4 and r < .10: zt = "big"
                    elif self.wave >= 2 and r < .35: zt = "fast"
                    else: zt = "normal"
                self.zombies.append(Zombie(x, y, zt, self.wave)); return
        self.zombies.append(Zombie(50, 50, "normal", self.wave))

    def update(self, keys, m_pos):
        if self.state != "playing": return
        self.frame += 1; self.time_played += 1; pl = self.player
        if not pl or not pl.alive:
            self.state = "gameover"; self.hi_score = max(self.hi_score, self.score); return
        if self.frame % FPS == 0: self.score += 1
        self.hit_marks = [t-1 for t in self.hit_marks if t > 0]
        if self.dmg_flash > 0: self.dmg_flash = max(0, self.dmg_flash - 4)
        if self.combo_t > 0: self.combo_t -= 1
        else: self.combo = 0
        if self.wpn_ann_t > 0: self.wpn_ann_t -= 1
        if self.wc_bonus_t > 0: self.wc_bonus_t -= 1
        if self.boss_warn > 0: self.boss_warn -= 1
        if self.announce > 0: self.announce -= 1
        self.kill_feed = [(t, c, tmr - 1) for t, c, tmr in self.kill_feed if tmr > 1]

        m_pos_w = s2w(m_pos[0] + self.cx, m_pos[1] + self.cy)
        pl.update(keys, m_pos_w, self)
        if pygame.mouse.get_pressed()[0]: pl.shoot(m_pos_w, self)

        self.sx *= SHD; self.sy *= SHD
        if abs(self.sx) < .1: self.sx = 0
        if abs(self.sy) < .1: self.sy = 0
        tx, ty = w2s(pl.x + self.sx, pl.y + self.sy)
        self.cx += (tx - self.cx) * CAM_L; self.cy += (ty - self.cy) * CAM_L

        if self.wave_timer > 0: self.wave_timer -= 1
        elif self.to_spawn > 0:
            self.spawn_cd -= 1
            if self.spawn_cd <= 0: self._sz(); self.to_spawn -= 1; self.spawn_cd = max(4, 26-self.wave*2)
        elif not any(z.alive and not z.dying for z in self.zombies):
            if self.wave > 0:
                bonus = max(0, (300 - (self.frame - self.wave_start)) * self.wave)
                if bonus > 0: self.score += bonus; self.wc_bonus = bonus; self.wc_bonus_t = 120
            self.wave_timer = 180
            if self.wave > 0 and self.wave % 2 == 0: self.pickups.append(Pickup(random.uniform(120,WW-120), random.uniform(120,WH-120), "health"))
            if self.wave > 0 and self.wave % 3 == 0: self.pickups.append(Pickup(random.uniform(120,WW-120), random.uniform(120,WH-120), "ammo"))
            self._nw()

        ppos = (pl.x, pl.y)
        for z in self.zombies: z.update(ppos, self.walls, self.zombies, self)
        for z in self.zombies:
            if z.alive and not z.dying and z.atk_cd <= 0 and z.get_rect().colliderect(pl.get_rect()):
                cdmg = z.dmg * (1.8 if z.zt == "boss" and z.bst == "charging" else 1.0)
                pl.take_damage(cdmg, self.frame); z.atk_cd = 30
                if cdmg > 0 and pl.pu_type != "shield": self.shake(5)
                self.dmg_flash = 180

        for b in self.bullets: b.update(self)
        for b in self.bullets:
            if not b.alive: continue
            br = b.get_rect()
            for z in self.zombies:
                if not z.alive or z.dying: continue
                if br.colliderect(z.get_rect()):
                    self.hit_marks.append(6)
                    if b.wk == "grenade": b._explode(self)
                    else:
                        killed = z.take_damage(b.dmg, self)
                        for _ in range(3): self.effects.append(Effect(type="blood", x=z.x+random.uniform(-10,10), y=z.y+random.uniform(-10,10), life=140))
                        if killed:
                            self.combo += 1; self.combo_t = 120; mult = 1 + self.combo*0.25
                            pts = int(z.pts * self.wave * mult)
                            self.score += pts; self.kills[z.zt] += 1; self.total_kills += 1
                            for _ in range(7): self.effects.append(Effect(type="blood", x=z.x+random.uniform(-12,12), y=z.y+random.uniform(-12,12), life=220))
                            for _ in range(5): self.effects.append(Effect(type="gibs", x=z.x, y=z.y, vx=random.uniform(-5,5), vy=random.uniform(-5,5), col=Z_ST[z.zt]["body"], life=24))
                            for thresh, txt, col in STREAKS:
                                if self.combo >= thresh and self.combo != self.last_streak:
                                    self.last_streak = self.combo; self.announce = 0
                                    self.effects.append(Effect(type="dmg", x=WW/2, y=WH/2 - 60, txt=txt, life=90, big=True, col=col)); break
                            zt_name = z.zt.upper(); zt_col = Z_ST[z.zt]["head"]
                            feed_txt = f"  {zt_name}  +{pts}"
                            if self.combo > 1: feed_txt += f"  x{self.combo}"
                            self._add_kill_feed(feed_txt, zt_col)
                            if z.zt == "boss":
                                self._add_kill_feed("  BOSS ELIMINATED!", NEON_AMBER)
                                for _ in range(3): self.pickups.append(Pickup(z.x+random.uniform(-30,30), z.y+random.uniform(-30,30), random.choice(["health","ammo"])))
                                for _ in range(3): self.zombies.append(Zombie(z.x+random.uniform(-40,40), z.y+random.uniform(-40,40), "normal", self.wave))
                                self.shake(15)
                            elif random.random() < .18: self.pickups.append(Pickup(z.x, z.y, "health" if random.random() < .55 else "ammo"))
                            elif random.random() < .08: self.powerups.append(PowerUp(z.x, z.y, random.choice(POWERUP_TYPES)))
                    b.alive = False; break

        for pk in self.pickups:
            pk.update()
            if pk.get_rect().colliderect(pl.get_rect()):
                if pk.kind == "health": pl.hp = min(pl.max_hp, pl.hp + 30)
                else:
                    wk = pl.wk
                    if wk != "pistol": pl.ammo[wk] += WPN[wk]["per"]
                pk.alive = False
        for pu in self.powerups:
            pu.update()
            if pu.get_rect().colliderect(pl.get_rect()):
                pl.pu_type = pu.kind; pl.pu_timer = 480; self.wpn_ann = PU_I[pu.kind][1]; self.wpn_ann_t = 60
                pu.alive = False

        for e in self.effects: e.update()
        self.zombies = [z for z in self.zombies if z.alive]
        self.bullets = [b for b in self.bullets if b.alive]
        self.effects = [e for e in self.effects if e.alive][:500]
        self.pickups = [p for p in self.pickups if p.alive]
        self.powerups = [p for p in self.powerups if p.alive]
        self.walls = [w for w in self.walls if w.alive]

    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN DRAW  –  Neon Noire Floor
    # ═══════════════════════════════════════════════════════════════════════════
    def draw(self):
        screen.fill(C_BG)

        # Tiled isometric floor with richer checkerboard
        for gx in range(0, WW + FLOOR_TILE, FLOOR_TILE):
            for gy in range(0, WH + FLOOR_TILE, FLOOR_TILE):
                p1 = w2s(gx, gy); p2 = w2s(gx + FLOOR_TILE, gy)
                p3 = w2s(gx + FLOOR_TILE, gy + FLOOR_TILE); p4 = w2s(gx, gy + FLOOR_TILE)
                pts = [(p1[0]-self.cx, p1[1]-self.cy), (p2[0]-self.cx, p2[1]-self.cy),
                       (p3[0]-self.cx, p3[1]-self.cy), (p4[0]-self.cx, p4[1]-self.cy)]
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                if max(xs) < -10 or min(xs) > WIDTH+10 or max(ys) < -10 or min(ys) > HEIGHT+10:
                    continue
                tx = (gx // FLOOR_TILE) % 2; ty = (gy // FLOOR_TILE) % 2
                if (tx + ty) % 2 == 0:
                    col = C_FLOOR_A
                else:
                    col = C_FLOOR_B
                pygame.draw.polygon(screen, col, pts)
                # Subtle crack/detail lines on some tiles
                if (gx + gy) % 120 == 0:
                    mid1 = ((pts[0][0]+pts[2][0])//2, (pts[0][1]+pts[2][1])//2)
                    mid2 = ((pts[1][0]+pts[3][0])//2, (pts[1][1]+pts[3][1])//2)
                    pygame.draw.line(screen, (48, 50, 58), mid1, mid2, 1)
                # Grid lines
                pygame.draw.polygon(screen, C_FLOOR_LINE, pts, 1)

        if self.state == "menu": self._draw_menu(); return
        if self.state == "gameover": self._draw_go(); return

        drawables = []
        for w in self.walls: drawables.append(('wall', w.z_sort if hasattr(w, 'z_sort') else w.y + w.h, w))
        for p in self.pickups: drawables.append(('pk', p.z_sort, p))
        for p in self.powerups: drawables.append(('pu', p.z_sort, p))
        if self.player and self.player.alive: drawables.append(('pl', self.player.z_sort, self.player))
        for z in self.zombies: drawables.append(('z', z.z_sort, z))
        for b in self.bullets: drawables.append(('b', b.z_sort, b))
        for e in self.effects: drawables.append(('e', e.z_sort, e))
        drawables.sort(key=lambda item: item[1])
        for typ, _, obj in drawables:
            obj.draw(screen, self.cx, self.cy)

        # Vignette post-process
        screen.blit(vignette_surf, (0, 0))

        self._draw_hud()

    # ═══════════════════════════════════════════════════════════════════════════
    # MENU  –  Neon Noire
    # ═══════════════════════════════════════════════════════════════════════════
    def _draw_menu(self):
        # Animated background grid
        t = pygame.time.get_ticks() * 0.001
        for i in range(0, WIDTH, 60):
            a = int(15 + 10 * math.sin(t + i * 0.02))
            pygame.draw.line(screen, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], a), (i, 0), (i, HEIGHT), 1)
        for j in range(0, HEIGHT, 60):
            a = int(15 + 10 * math.sin(t + j * 0.02))
            pygame.draw.line(screen, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], a), (0, j), (WIDTH, j), 1)

        # Vignette on menu too
        screen.blit(vignette_surf, (0, 0))

        # Title glow
        draw_neon_glow(screen, WIDTH//2, HEIGHT//2 - 100, 120, NEON_CYAN, 40)

        # Title text with shadow
        draw_text(screen, "BOX HEAD", (WIDTH//2 + 3, HEIGHT//2 - 97), (0, 0, 0), font_title, True)
        draw_text(screen, "BOX HEAD", (WIDTH//2, HEIGHT//2 - 100), NEON_CYAN, font_title, True)

        # Subtitle
        draw_text(screen, "NEON NOIRE EDITION", (WIDTH//2, HEIGHT//2 - 25), (140, 150, 180), font_md, True)

        # Pulsing start prompt
        pulse = 0.5 + 0.5 * math.sin(t * 3)
        start_col = lerp_color((120, 130, 150), WHITE, pulse)
        draw_text(screen, "[ Click to Start ]", (WIDTH//2, HEIGHT//2 + 35), start_col, font_lg, True)

        # Controls
        ctrls = ["WASD Move  |  Shift Sprint  |  Mouse Aim  |  LMB Shoot  |  Q/E or Scroll Switch",
                 "Space Dash  |  F Barricade (50pts)  |  1-4 Weapon Slots  |  Esc Pause"]
        for i, t in enumerate(ctrls):
            draw_text(screen, t, (WIDTH//2, HEIGHT//2 + 100 + i * 25), (70, 75, 95), font_sm, True)

        if self.hi_score > 0:
            draw_text(screen, f"High Score: {self.hi_score}", (WIDTH//2, HEIGHT - 50), NEON_AMBER, font_md, True)

    # ═══════════════════════════════════════════════════════════════════════════
    # GAME OVER  –  Neon Noire
    # ═══════════════════════════════════════════════════════════════════════════
    def _draw_go(self):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((0, 0, 0, 160))
        screen.blit(ov, (0, 0))

        # Title with neon glow
        draw_neon_glow(screen, WIDTH//2, 150, 80, NEON_PINK, 50)
        draw_text(screen, "GAME OVER", (WIDTH//2 + 3, 153), (0, 0, 0), font_xl, True)
        draw_text(screen, "GAME OVER", (WIDTH//2, 150), NEON_PINK, font_xl, True)

        pw, ph = 380, 270; px, py = (WIDTH - pw) // 2, 200
        panel = _make_glass_panel(pw, ph, border_col=(80, 60, 80, 120), fill_col=(12, 10, 18, 210))
        screen.blit(panel, (px, py))

        stats = [
            (f"Final Score:  {self.score}", (255, 255, 255)),
            (f"Wave Reached:  {self.wave}", (180, 190, 210)),
            (f"Total Kills:  {self.total_kills}", (180, 190, 210)),
            (f"  Normal: {self.kills['normal']}   Fast: {self.kills['fast']}", (130, 140, 160)),
            (f"  Big: {self.kills['big']}   Boss: {self.kills['boss']}", (130, 140, 160)),
            (f"Time Survived:  {self.time_played // FPS}s", (150, 160, 180)),
            (f"Best Combo:  x{self.last_streak}", NEON_AMBER),
        ]
        for i, (txt, col) in enumerate(stats):
            draw_text(screen, txt, (px + 22, py + 18 + i * 35), col, font_md)

        if self.score >= self.hi_score and self.score > 0:
            t = pygame.time.get_ticks() * 0.003
            pulse = 0.7 + 0.3 * math.sin(t)
            c = lerp_color(NEON_AMBER, WHITE, pulse)
            draw_text(screen, "NEW HIGH SCORE!", (WIDTH//2, py + ph + 22), c, font_lg, True)

        draw_text(screen, "[ Click to Restart ]", (WIDTH//2, py + ph + 68), (120, 125, 140), font_md, True)

    # ═══════════════════════════════════════════════════════════════════════════
    # HUD  –  Neon Noire
    # ═══════════════════════════════════════════════════════════════════════════
    def _draw_hud(self):
        pl = self.player
        if not pl: return

        # ── Low HP danger pulse ──
        hp_ratio = max(0, pl.hp / pl.max_hp)
        if hp_ratio < 0.3:
            pulse = 0.5 + 0.5 * math.sin(self.frame * 0.15)
            low_s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            low_s.fill((NEON_RED[0], 0, 0, int(70 * pulse * (1 - hp_ratio / 0.3))))
            screen.blit(low_s, (0, 0))

        # ── Damage flash (red vignette) ──
        if self.dmg_flash > 0:
            vs = vignette_surf.copy()
            vs.fill((NEON_RED[0], 10, 20, min(255, int(self.dmg_flash * 0.9))))
            screen.blit(vs, (0, 0))

        # ── Hit Markers ──
        if self.hit_marks:
            mx, my = pygame.mouse.get_pos()
            hm_a = min(255, max(0, self.hit_marks[0] * 42))
            hm_s = pygame.Surface((24, 24), pygame.SRCALPHA)
            c = (255, 255, 255, hm_a)
            pygame.draw.line(hm_s, c, (2, 2), (9, 9), 3)
            pygame.draw.line(hm_s, c, (22, 2), (15, 9), 3)
            pygame.draw.line(hm_s, c, (2, 22), (9, 15), 3)
            pygame.draw.line(hm_s, c, (22, 22), (15, 15), 3)
            # Glow behind
            pygame.draw.circle(hm_s, (255, 255, 255, hm_a // 3), (12, 12), 8)
            screen.blit(hm_s, (mx - 12, my - 12))

        # ══════ LEFT PANEL ══════
        screen.blit(_hud_left_panel, (10, 10))

        # HP Bar
        r = max(0, pl.hp / pl.max_hp)
        if r > .5: hc = NEON_GREEN
        elif r > .25: hc = NEON_AMBER
        else: hc = NEON_RED
        draw_rounded_bar(screen, 20, 20, 238, 22, r, hc, (30, 12, 12))
        draw_text(screen, "+", (24, 19), hc, font_hud_num)
        hp_txt = f"{int(pl.hp)}/{pl.max_hp}"
        draw_text(screen, hp_txt, (258 - font_hud_sm.size(hp_txt)[0] - 4, 24), (200, 210, 230), font_hud_sm)

        # Stamina
        st_r = pl.stamina / pl.max_stamina
        st_col = NEON_CYAN if pl.stamina > 20 else NEON_PINK
        draw_rounded_bar(screen, 20, 46, 238, 10, st_r, st_col, (18, 18, 30))
        lbl_col = (140, 200, 240) if pl.stamina > 20 else (200, 100, 120)
        draw_text(screen, f"STAMINA [{'SPRINT' if pl.sprinting else 'SHIFT'}]", (24, 44), lbl_col, font_hud_sm)

        # Dash CD
        dr = 1 - pl.dash_cd / 90 if pl.dash_cd > 0 else 1
        dash_col = NEON_CYAN if dr >= 1 else (50, 90, 140)
        draw_rounded_bar(screen, 20, 60, 238, 10, dr, dash_col, (18, 22, 35))
        dash_txt = "READY" if dr >= 1 else f"{pl.dash_cd // FPS + 1}s"
        draw_text(screen, f"DASH  [SPACE]  {dash_txt}", (24, 59), (170, 215, 255) if dr >= 1 else (70, 80, 100), font_hud_sm)

        # Barricade CD
        br2 = 1 - pl.barricade_cd / 30 if pl.barricade_cd > 0 else 1
        bar_col = (120, 125, 150) if br2 >= 1 else (60, 62, 75)
        draw_rounded_bar(screen, 20, 74, 238, 10, br2, bar_col, (18, 18, 28))
        if br2 >= 1:
            draw_text(screen, "BARRICADE  [F]  (-50pts)", (24, 73), (150, 155, 175), font_hud_sm)
        else:
            draw_text(screen, f"BARRICADE  [F]  {pl.barricade_cd // FPS + 1}s", (24, 73), (70, 72, 85), font_hud_sm)

        # Powerup timer
        if pl.pu_type and pl.pu_timer > 0:
            pr = pl.pu_timer / 480
            col = PU_I[pl.pu_type][0]
            draw_rounded_bar(screen, 20, 88, 238, 12, pr, col, (18, 18, 22))
            draw_text(screen, f"{PU_I[pl.pu_type][1]}  {pl.pu_timer // FPS + 1}s", (24, 86), col, font_hud_sm)

        # ══════ RIGHT PANEL ══════
        screen.blit(_hud_right_panel, (WIDTH - 248, 10))

        # Score
        draw_text(screen, "SCORE", (WIDTH - 232, 16), (110, 115, 140), font_hud_sm)
        draw_text(screen, f"{self.score:,}", (WIDTH - 232, 30), WHITE, font_hud_num)

        # Wave
        draw_text(screen, "WAVE", (WIDTH - 232, 56), (110, 115, 140), font_hud_sm)
        draw_text(screen, f"{self.wave}", (WIDTH - 148, 56), NEON_AMBER, font_hud_num)

        # Wave progress
        rem = self.to_spawn + sum(1 for z in self.zombies if z.alive and not z.dying)
        total_for_wave = 5 + self.wave * 3 + self.wave // 3 * 2 + (1 if self.wave % 5 == 0 else 0)
        wp_ratio = max(0, 1 - rem / max(1, total_for_wave)) if self.wave > 0 else 0
        draw_rounded_bar(screen, WIDTH - 232, 78, 218, 10, wp_ratio, NEON_GREEN, (22, 22, 28), 3)
        rem_col = NEON_RED if rem > 0 else NEON_GREEN
        draw_text(screen, f"{rem} left", (WIDTH - 232, 77), rem_col, font_hud_sm)

        # Time & kills
        secs = self.time_played // FPS; mins = secs // 60
        draw_text(screen, f"{mins}:{secs % 60:02d}", (WIDTH - 232, 94), (100, 105, 125), font_hud_sm)
        draw_text(screen, f"Kills: {self.total_kills}", (WIDTH - 148, 94), (100, 105, 125), font_hud_sm)

        # ══════ KILL FEED ══════
        kf_x = WIDTH - 248; kf_y = 116
        for i, (txt, col, timer) in enumerate(self.kill_feed):
            a = min(255, timer * 3)
            # Background strip
            ts = font_kf.render(txt, True, col)
            strip = pygame.Surface((ts.get_width() + 8, ts.get_height() + 2), pygame.SRCALPHA)
            strip.fill((10, 10, 15, min(140, a // 2)))
            strip.blit(ts, (4, 1))
            strip.set_alpha(a)
            screen.blit(strip, (kf_x + 2, kf_y + i * 18))

        self._draw_weapon_bar(pl)

        # ══════ COMBO ══════
        if self.combo > 1:
            scale_t = min(1.0, self.combo_t / 15.0)
            base_size = min(50, 34 + self.combo); sz = int(base_size * scale_t)
            if sz > 10:
                cf = pygame.font.SysFont("Impact", sz, bold=True)
                # Shadow
                draw_text(screen, f"x{self.combo} COMBO", (WIDTH//2+2, 32), (30, 25, 0), cf, True)
                # Main
                cc = lerp_color(NEON_GREEN, NEON_PINK, min(1, self.combo / 20))
                draw_text(screen, f"x{self.combo} COMBO", (WIDTH//2, 30), cc, cf, True)
                # Glow
                if self.combo >= 5:
                    draw_neon_glow(screen, WIDTH//2, 30, sz, cc, 30)

        # ══════ ANNOUNCEMENTS ══════
        if self.announce > 0:
            a_alpha = min(255, self.announce * 5)
            a_scale = min(1.0, (130 - self.announce + 1) / 15.0)
            if a_scale > 0.1:
                af = pygame.font.SysFont("Impact", int(60 * a_scale), bold=True)
                # Shadow
                ts = af.render(f"WAVE {self.wave}", True, (0, 0, 0)); ts.set_alpha(a_alpha // 2)
                screen.blit(ts, ts.get_rect(center=(WIDTH//2 + 2, HEIGHT//2 + 2)))
                # Main
                ts = af.render(f"WAVE {self.wave}", True, NEON_CYAN); ts.set_alpha(a_alpha)
                screen.blit(ts, ts.get_rect(center=(WIDTH//2, HEIGHT//2)))
                # Glow
                draw_neon_glow(screen, WIDTH//2, HEIGHT//2, int(80 * a_scale), NEON_CYAN, int(30 * a_alpha / 255))

        if self.boss_warn > 0:
            bw_a = min(255, self.boss_warn * 4)
            p = 0.7 + 0.3 * math.sin(self.boss_warn * 0.3)
            col = (int(255*p), int(30*p), int(30*p))
            ts = font_lg.render("!! BOSS INCOMING !!", True, col)
            ts.set_alpha(bw_a)
            screen.blit(ts, ts.get_rect(center=(WIDTH//2, HEIGHT//2 + 60)))
            if self.boss_warn % 30 < 15:
                draw_neon_glow(screen, WIDTH//2, HEIGHT//2 + 60, 60, NEON_RED, 40)

        if self.wc_bonus_t > 0:
            ts = font_md.render(f"WAVE CLEAR! +{self.wc_bonus}", True, NEON_GREEN)
            ts.set_alpha(min(255, self.wc_bonus_t * 4))
            screen.blit(ts, ts.get_rect(center=(WIDTH//2, HEIGHT//2 + 30)))

        if self.wpn_ann_t > 0:
            ts = font_md.render(self.wpn_ann, True, (180, 185, 200))
            ts.set_alpha(min(255, self.wpn_ann_t * 6))
            screen.blit(ts, ts.get_rect(center=(WIDTH//2, HEIGHT - 100)))

        self._draw_minimap(pl)
        self._draw_crosshair(pl)

    # ═══════════════════════════════════════════════════════════════════════════
    # WEAPON BAR  –  Neon Noire
    # ═══════════════════════════════════════════════════════════════════════════
    def _draw_weapon_bar(self, pl):
        n = len(pl.weapons); slot_w, slot_h = 104, 52; gap = 4
        total_w = n * slot_w + (n - 1) * gap
        bar_x = (WIDTH - total_w) // 2; bar_y = HEIGHT - slot_h - 14

        # Background panel
        bg = _make_glass_panel(total_w + 14, slot_h + 14)
        screen.blit(bg, (bar_x - 7, bar_y - 7))

        for i, wk in enumerate(pl.weapons):
            sx = bar_x + i * (slot_w + gap); is_active = (i == pl.cw)
            w = WPN[wk]; ic = WPN_ICON_COL[wk]

            if is_active:
                sb = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
                sb.fill((*ic, 25))
                # Top accent line (brighter)
                pygame.draw.rect(sb, (*ic, 200), (0, 0, slot_w, 3))
                # Border with rounded corners
                pygame.draw.rect(sb, (*ic, 180), (0, 0, slot_w, slot_h), 2, border_radius=5)
                # Inner glow at top
                for gy in range(6):
                    a = int(15 * (1 - gy / 6))
                    pygame.draw.line(sb, (*ic, a), (2, gy + 3), (slot_w - 2, gy + 3), 1)
                screen.blit(sb, (sx, bar_y))
            else:
                sb = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
                sb.fill((16, 16, 22, 160))
                pygame.draw.rect(sb, (45, 48, 60, 110), (0, 0, slot_w, slot_h), 1, border_radius=5)
                screen.blit(sb, (sx, bar_y))

            # Weapon icon
            ix, iy = sx + 8, bar_y + 9
            if wk == "pistol":
                pygame.draw.rect(screen, ic, (ix, iy + 4, 18, 6))
                pygame.draw.rect(screen, scale_color(ic, 1.2), (ix, iy + 4, 18, 2))  # highlight
                pygame.draw.rect(screen, scale_color(ic, 0.65), (ix + 4, iy + 8, 6, 10))
            elif wk == "shotgun":
                pygame.draw.rect(screen, ic, (ix, iy + 3, 22, 8))
                pygame.draw.rect(screen, scale_color(ic, 1.2), (ix, iy + 3, 22, 3))
                pygame.draw.rect(screen, scale_color(ic, 0.65), (ix + 6, iy + 9, 8, 12))
            elif wk == "uzi":
                pygame.draw.rect(screen, ic, (ix, iy + 2, 20, 7))
                pygame.draw.rect(screen, scale_color(ic, 1.2), (ix, iy + 2, 20, 3))
                pygame.draw.rect(screen, scale_color(ic, 0.65), (ix + 2, iy + 7, 5, 14))
            elif wk == "grenade":
                pygame.draw.circle(screen, ic, (ix + 10, iy + 10), 8)
                pygame.draw.circle(screen, scale_color(ic, 1.3), (ix + 8, iy + 7), 3)
                pygame.draw.circle(screen, scale_color(ic, 0.6), (ix + 10, iy + 10), 8, 1)

            nc = WHITE if is_active else (75, 78, 92)
            draw_text(screen, w["nm"], (sx + 36, bar_y + 7), nc, font_hud_sm)
            if wk == "pistol":
                draw_text(screen, "INF", (sx + 36, bar_y + 24), (70, 75, 90) if not is_active else (NEON_GREEN[0], NEON_GREEN[1], NEON_GREEN[2]), font_hud_sm)
            else:
                ammo = pl.ammo[wk]; ac = (170, 175, 190) if is_active else (70, 75, 90)
                if ammo == 0: ac = NEON_RED
                draw_text(screen, f"{ammo}", (sx + 36, bar_y + 24), ac, font_hud_sm)

            # Slot key
            draw_text(screen, WPN_SLOT_KEY.get(i, ""), (sx + slot_w - 16, bar_y + slot_h - 18),
                      ic if is_active else (50, 52, 62), font_hud_sm)

    # ═══════════════════════════════════════════════════════════════════════════
    # MINIMAP  –  Neon Noire
    # ═══════════════════════════════════════════════════════════════════════════
    def _draw_minimap(self, pl):
        mm = 154; mmx, mmy = WIDTH - mm - 14, HEIGHT - mm - 80
        panel = _make_glass_panel(mm + 6, mm + 24, border_col=(50, 55, 80, 100))
        screen.blit(panel, (mmx - 3, mmy - 3))

        ms = pygame.Surface((mm, mm), pygame.SRCALPHA); ms.fill((10, 10, 16, 210))
        sxr, syr = mm / WW, mm / WH

        # Walls
        for w in self.walls:
            if isinstance(w, DestWall): c = (110, 90, 50, 170)
            elif isinstance(w, SupplyCrate): c = (NEON_AMBER[0], NEON_AMBER[1], NEON_AMBER[2], 190)
            elif isinstance(w, Barricade): c = (90, 95, 115, 190)
            else: c = (55, 58, 72, 170)
            pygame.draw.rect(ms, c, (w.x*sxr, w.y*syr, max(1, w.w*sxr), max(1, w.h*syr)))

        # Pickups
        for pk in self.pickups:
            c = (NEON_RED[0], NEON_RED[1], NEON_RED[2], 230) if pk.kind == "health" else (NEON_AMBER[0], NEON_AMBER[1], NEON_AMBER[2], 230)
            pygame.draw.circle(ms, c, (int(pk.x*sxr), int(pk.y*syr)), 2)

        # Powerups
        for pu in self.powerups:
            pygame.draw.circle(ms, (*PU_I[pu.kind][0], 250), (int(pu.x*sxr), int(pu.y*syr)), 3)

        # Zombies
        for z in self.zombies:
            if z.alive and not z.dying:
                if z.zt == "boss":
                    pygame.draw.rect(ms, (NEON_AMBER[0], NEON_AMBER[1], NEON_AMBER[2], 255),
                                     (int(z.x*sxr)-3, int(z.y*syr)-3, 6, 6))
                else:
                    c = (NEON_RED[0], NEON_RED[1], NEON_RED[2], 210) if z.zt != "fast" else (255, 120, 120, 210)
                    pygame.draw.rect(ms, c, (int(z.x*sxr)-1, int(z.y*syr)-1, 3, 3))

        # Player FOV cone
        pmx, pmy = int(pl.x*sxr), int(pl.y*syr)
        fov_s = pygame.Surface((mm, mm), pygame.SRCALPHA)
        a1 = pl.ang - 0.4; a2 = pl.ang + 0.4; fl = 28
        pts = [(pmx, pmy), (pmx+int(math.cos(a1)*fl), pmy+int(math.sin(a1)*fl)),
               (pmx+int(math.cos(a2)*fl), pmy+int(math.sin(a2)*fl))]
        pygame.draw.polygon(fov_s, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], 30), pts)
        ms.blit(fov_s, (0, 0))

        # Player dot with glow
        glow_s = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], 60), (6, 6), 6)
        ms.blit(glow_s, (pmx - 6, pmy - 6))
        pygame.draw.rect(ms, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], 255), (pmx-3, pmy-3, 6, 6))

        screen.blit(ms, (mmx, mmy))
        draw_text(screen, "MAP", (mmx + 5, mmy + mm + 5), (70, 75, 95), font_hud_sm)

    # ═══════════════════════════════════════════════════════════════════════════
    # CROSSHAIR  –  Neon Noire
    # ═══════════════════════════════════════════════════════════════════════════
    def _draw_crosshair(self, pl):
        mx, my = pygame.mouse.get_pos()
        wk = pl.wk; col = WPN_ICON_COL.get(wk, WHITE)
        gap = 6
        if pl.fcd > 0:
            ratio = pl.fcd / max(1, WPN[wk]["rate"])
            gap = int(6 + 10 * ratio)
            # Dim colour when on cooldown
            col = lerp_color(col, (100, 100, 100), ratio * 0.5)

        arm_len = 16
        arm_w = 2

        # Outer glow ring
        rs = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(rs, (*col, 40), (15, 15), 13, 1)
        pygame.draw.circle(rs, (*col, 20), (15, 15), 15, 1)
        screen.blit(rs, (mx - 15, my - 15))

        # Crosshair arms
        pygame.draw.line(screen, col, (mx - gap - arm_len, my), (mx - gap, my), arm_w)
        pygame.draw.line(screen, col, (mx + gap, my), (mx + gap + arm_len, my), arm_w)
        pygame.draw.line(screen, col, (mx, my - gap - arm_len), (mx, my - gap), arm_w)
        pygame.draw.line(screen, col, (mx, my + gap), (mx, my + gap + arm_len), arm_w)

        # Centre dot
        pygame.draw.circle(screen, col, (mx, my), 2)
        pygame.draw.circle(screen, (255, 255, 255, 200), (mx, my), 1)

        # Small tick marks at gap ends
        tick = 3
        for dx2, dy2 in [(gap, 0), (-gap, 0), (0, gap), (0, -gap)]:
            pygame.draw.line(screen, (*scale_color(col, 0.6), 150),
                             (mx + dx2, my + dy2 - tick), (mx + dx2, my + dy2 + tick), 1)

# ── Main Loop ───────────────────────────────────────────────────────────────────
def main():
    game = Game()
    running = True
    while running:
        keys = pygame.key.get_pressed()
        m_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.state in ("menu", "gameover"): game.reset_game(); game.state = "playing"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.state == "playing": game.state = "paused"
                    elif game.state == "paused": game.state = "playing"
                if game.state == "playing":
                    if event.key == pygame.K_SPACE: game.player.dash(keys)
                    if event.key == pygame.K_f: game.place_barricade()
                    if event.key == pygame.K_q: game.player.cw = (game.player.cw - 1) % 4
                    if event.key == pygame.K_e: game.player.cw = (game.player.cw + 1) % 4
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                        idx = event.key - pygame.K_1
                        if 0 <= idx < len(game.player.weapons): game.player.cw = idx
            if event.type == pygame.MOUSEWHEEL and game.state == "playing":
                game.player.cw = (game.player.cw + (1 if event.y > 0 else -1)) % 4
        if game.state == "playing": game.update(keys, m_pos)
        game.draw()
        if game.state == "paused":
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0, 0, 0, 170))
            screen.blit(s, (0, 0))
            draw_neon_glow(screen, WIDTH//2, HEIGHT//2, 100, NEON_CYAN, 30)
            draw_text(screen, "PAUSED", (WIDTH//2, HEIGHT//2), NEON_CYAN, font_xl, True)
            draw_text(screen, "Press ESC to resume", (WIDTH//2, HEIGHT//2 + 60), (140, 145, 165), font_md, True)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()