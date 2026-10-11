#!/usr/bin/env python3
"""Box Head – Ultimate 2.5D Isometric Edition (Native Pygame Port) – Improved HUD."""

import pygame
import math
import random
import sys

# ── Initialization ─────────────────────────────────────────────────────────────
pygame.init()
WIDTH, HEIGHT = 1024, 768
FPS = 60
WW, WH = 1600, 1200
COS30 = math.cos(math.radians(30))
SIN30 = math.sin(math.radians(30))

# Camera constants (were missing – caused NameError)
SHD = 0.85          # shake decay
CAM_L = 0.08        # camera lerp speed

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GRAY = (130, 130, 130)
DARK_GRAY = (60, 60, 60)

# ── Isometric Math ─────────────────────────────────────────────────────────────
def w2s(wx, wy):
    return ((wx - wy) * COS30, (wx + wy) * SIN30)

def s2w(sx, sy):
    wx = (sx / COS30 + sy / SIN30) / 2
    wy = (sy / SIN30 - sx / COS30) / 2
    return wx, wy

# ── Game Data ──────────────────────────────────────────────────────────────────
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
    "normal": dict(hp=50, spd=1.3, dmg=10, c=(75,160,50), hc=(100,185,70), sz=26, pt=10),
    "fast":   dict(hp=30, spd=2.6, dmg=8,  c=(190,50,50), hc=(215,85,85),  sz=22, pt=15),
    "big":    dict(hp=160,spd=.75, dmg=25, c=(115,75,160),hc=(150,110,190), sz=38, pt=25),
    "boss":   dict(hp=400,spd=1.0, dmg=35, c=(180,20,20), hc=(220,60,60),  sz=56, pt=100),
}
PU_I = {
    "speed":  ((0,200,255), "SPEED UP!"),
    "damage": ((255,120,0), "DAMAGE x2!"),
    "shield": ((100,200,255),"SHIELD!"),
    "rapid":  ((255,255,0), "RAPID FIRE!"),
}
POWERUP_TYPES = list(PU_I.keys())
STREAKS = [
    (3,"DOUBLE KILL",(255,255,100)),(5,"TRIPLE KILL",(255,200,50)),
    (8,"MULTI KILL",(255,150,0)),(12,"MEGA KILL",(255,100,0)),
    (16,"ULTRA KILL",(255,50,50)),(20,"UNSTOPPABLE!",(255,0,255)),
    (25,"GODLIKE!",(255,220,0)),(30,"MASSACRE!",(255,0,0)),
]

# Weapon icon colors for HUD
WPN_ICON_COL = {
    "pistol":  (200, 200, 210),
    "shotgun": (255, 170, 50),
    "uzi":     (180, 220, 255),
    "grenade": (255, 80, 60),
}
WPN_SLOT_KEY = {0: "1", 1: "2", 2: "3", 3: "4"}

# ── Drawing Helpers ────────────────────────────────────────────────────────────
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Box Head – Pygame 2.5D Isometric")
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

vignette_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for i in range(100, 0, -1):
    alpha = int(255 * (1 - (i / 100.0)) * 0.6)
    pygame.draw.circle(vignette_surf, (0, 0, 0, alpha), (WIDTH//2, HEIGHT//2), int(WIDTH*0.6 * (i/100.0)))

# Pre-build HUD panel background
_hud_left_panel = pygame.Surface((250, 210), pygame.SRCALPHA)
_hud_left_panel.fill((10, 10, 15, 160))
pygame.draw.rect(_hud_left_panel, (60, 60, 80, 100), (0, 0, 250, 210), 1, border_radius=6)

_hud_right_panel = pygame.Surface((230, 90), pygame.SRCALPHA)
_hud_right_panel.fill((10, 10, 15, 160))
pygame.draw.rect(_hud_right_panel, (60, 60, 80, 100), (0, 0, 230, 90), 1, border_radius=6)

def draw_text(surf, text, pos, color, font=font_md, center=False):
    txt_surf = font.render(text, True, color)
    if center:
        rect = txt_surf.get_rect(center=pos)
        surf.blit(txt_surf, rect)
    else:
        surf.blit(txt_surf, pos)

def draw_bar(surf, x, y, w, h, ratio, col_full, col_empty, border_col):
    pygame.draw.rect(surf, col_empty, (x, y, w, h))
    pygame.draw.rect(surf, col_full, (x+1, y+1, int((w-2)*ratio), h-2))
    pygame.draw.rect(surf, border_col, (x, y, w, h), 2)

def scale_color(color, factor):
    return tuple(min(255, int(c * factor)) for c in color)

def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def draw_rounded_bar(surf, x, y, w, h, ratio, col_full, col_empty, radius=4):
    """Draw a bar with rounded ends and a subtle gradient."""
    # Background
    bg_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(bg_surf, (*col_empty, 200), (0, 0, w, h), border_radius=radius)
    # Fill
    fw = max(0, int((w - 2) * ratio))
    if fw > 0:
        # Gradient fill: lighter at top, darker at bottom
        fill_surf = pygame.Surface((fw, h - 2), pygame.SRCALPHA)
        top_col = tuple(min(255, c + 40) for c in col_full)
        bot_col = tuple(max(0, c - 30) for c in col_full)
        for row in range(h - 2):
            t = row / max(1, h - 3)
            c = lerp_color(top_col, bot_col, t)
            pygame.draw.line(fill_surf, (*c, 230), (0, row), (fw, row))
        bg_surf.blit(fill_surf, (1, 1))
    # Highlight line at top
    if fw > 2:
        pygame.draw.line(bg_surf, (*[min(255, c + 80) for c in col_full], 90),
                         (2, 1), (fw, 1), 1)
    surf.blit(bg_surf, (x, y))
    # Border
    pygame.draw.rect(surf, (80, 80, 100, 120), (x, y, w, h), 1, border_radius=radius)

def draw_iso_block(surf, color, x, y, w, h, z_h=25, z_sort_offset=0):
    p1 = w2s(x, y); p2 = w2s(x+w, y); p3 = w2s(x+w, y+h); p4 = w2s(x, y+h)
    p5 = w2s(x, y-z_h); p6 = w2s(x+w, y-z_h); p7 = w2s(x+w, y+h-z_h); p8 = w2s(x, y+h-z_h)
    pygame.draw.polygon(surf, scale_color(color, 0.8), [p1, p4, p8, p5])
    pygame.draw.polygon(surf, color, [p2, p3, p7, p6])
    pygame.draw.polygon(surf, scale_color(color, 1.4), [p5, p6, p2, p1])
    pygame.draw.polygon(surf, scale_color(color, 0.5), [p1, p4, p8, p5], 1)
    pygame.draw.polygon(surf, scale_color(color, 0.5), [p2, p3, p7, p6], 1)
    pygame.draw.polygon(surf, scale_color(color, 0.5), [p5, p6, p2, p1], 1)
    return (x + y + h + z_sort_offset)

# ── Entities ───────────────────────────────────────────────────────────────────
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
        self.dashing = False; self.dash_t = 0; self.dash_cd = 0; self.dash_dx = 0; self.dash_dy = 0
        self.pu_type = None; self.pu_timer = 0; self.last_hit = 0; self.regen_t = 0
        self.barricade_cd = 0; self.inv = 0; self.ang = 0

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
            if self.dash_t <= 0: self.dashing = False
            return
        spd = self.speed * (1.5 if self.pu_type == "speed" else 1.0)
        dx = dy = 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        if dx and dy: dx *= 0.7071; dy *= 0.7071
        ox, oy = self.x, self.y
        self.x += dx * spd
        if self._hit_walls(game.walls): self.x = ox
        self.y += dy * spd
        if self._hit_walls(game.walls): self.y = oy
        self.x = max(14, min(WW-14, self.x)); self.y = max(14, min(WH-14, self.y))
        self.ang = math.atan2(m_pos_w[1] - self.y, m_pos_w[0] - self.x)
        self.z_sort = self.x + self.y

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

    def draw(self, surf, cx, cy):
        sx, sy = w2s(self.x, self.y)
        dx, dy = sx - cx, sy - cy
        if not (-50 < dx < WIDTH+50 and -50 < dy < HEIGHT+50): return
        # Shadow
        shadow_s = pygame.Surface((32, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_s, (0, 0, 0, 50), (0, 0, 32, 12))
        surf.blit(shadow_s, (dx - 16, dy + 8))
        # Body
        s = pygame.Surface((28, 28), pygame.SRCALPHA)
        col = (50, 150, 255) if self.inv % 6 >= 3 or self.inv == 0 else (150, 200, 255)
        pygame.draw.rect(s, col, (0, 0, 28, 28))
        pygame.draw.rect(s, (30, 110, 200), (0, 0, 28, 28), 2)
        pygame.draw.rect(s, (225, 205, 175), (16, 4, 12, 12))
        pygame.draw.rect(s, (75, 75, 80), (20, 11, 16, 5))
        rotated = pygame.transform.rotate(s, -math.degrees(self.ang))
        rect = rotated.get_rect(center=(dx, dy))
        surf.blit(rotated, rect)
        if self.pu_type and self.pu_timer > 0:
            p = 0.5 + 0.5 * math.sin(self.pu_timer * 0.15)
            aura_col = (*PU_I[self.pu_type][0], int(80 * p))
            aura_s = pygame.Surface((48, 48), pygame.SRCALPHA)
            pygame.draw.circle(aura_s, aura_col, (24, 24), 24)
            surf.blit(aura_s, (dx - 24, dy - 24))

class Zombie(Entity):
    def __init__(self, x, y, zt, wave):
        s = Z_ST[zt]; self.zt = zt; self.sz = s["sz"]
        super().__init__(x, y, s["sz"], s["sz"])
        hm = 60 if zt == "boss" else (12 if zt == "big" else 5)
        self.max_hp = s["hp"] + wave * hm; self.hp = self.max_hp
        self.speed = s["spd"] + wave * (.02 if zt == "boss" else (.05 if zt == "fast" else .03))
        self.dmg = s["dmg"] + wave * (3 if zt == "boss" else 2)
        self.pts = s["pt"]; self.atk_cd = 0; self.dying = False; self.dt = 0
        self.c = s["c"]; self.hc = s["hc"]; self.zz_t = 0 if zt == "fast" else -1
        if zt == "boss": self.bst = "normal"; self.btmr = 200; self.cdx = 0; self.cdy = 0

    def update(self, ppos, walls, zombies, game):
        if self.dying:
            self.dt += 1
            if self.dt >= 20: self.alive = False
            return
        self.z_sort = self.x + self.y
        if self.atk_cd > 0: self.atk_cd -= 1
        dx = ppos[0] - self.x; dy = ppos[1] - self.y; d = math.hypot(dx, dy)
        if d > 0: dx /= d; dy /= d
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
            self.dying = True; self.dt = 0; return True
        return False

    def _hit(self, walls):
        pr = self.get_rect()
        for w in walls:
            if pr.colliderect(w.get_rect()): return True
        return False

    def draw(self, surf, cx, cy):
        sx, sy = w2s(self.x, self.y)
        dx, dy = sx - cx, sy - cy
        if not (-60 < dx < WIDTH+60 and -60 < dy < HEIGHT+60): return
        scale = max(0.1, 1 - (self.dt / 20.0)) if self.dying else 1.0
        s = pygame.Surface((self.sz, self.sz), pygame.SRCALPHA)
        col = self.c
        if self.zt == "boss":
            if self.bst == "winding": col = (255, 60, 60)
            elif self.bst == "charging": col = (255, 200, 50)
            elif self.bst == "stunned": col = (180, 20, 20)
        alpha = int(max(0, 255 * scale)) if self.dying else 255
        c = (*col, alpha)
        pygame.draw.rect(s, c, (0, 0, self.sz, self.sz))
        pygame.draw.rect(s, (*scale_color(col, 0.6), alpha), (0, 0, self.sz, self.sz), 2)
        hs = int(self.sz * 0.55)
        pygame.draw.rect(s, (*self.hc, alpha), (self.sz//2, self.sz//2 - hs//2, hs, hs))
        if scale > 0.5:
            es = max(2, hs // 4)
            pygame.draw.circle(s, (255, 20, 20, alpha), (self.sz//2 + hs//2, self.sz//2 - hs//4), es)
            pygame.draw.circle(s, (255, 20, 20, alpha), (self.sz//2 + hs//2, self.sz//2 + hs//4), es)
            if self.zt == "boss" and not self.dying:
                pygame.draw.rect(s, (255, 215, 0, alpha), (self.sz//2, self.sz//2 - hs//2 - 8, 14, 8))
                pygame.draw.rect(s, (80, 0, 0, alpha), (self.sz//4 - 2, self.sz//2 - hs//2 - 12, 5, 12))
                pygame.draw.rect(s, (80, 0, 0, alpha), (self.sz*3//4 - 2, self.sz//2 - hs//2 - 12, 5, 12))
            if not self.dying:
                bw = self.sz
                pygame.draw.rect(s, (60, 0, 0, 200), (0, -8, bw, 4))
                r = max(0, self.hp / self.max_hp)
                hpc = (0,200,0,200) if r>.5 else (255,200,0,200) if r>.25 else (255,0,0,200)
                pygame.draw.rect(s, hpc, (0, -8, int(bw * r), 4))
        if scale != 1.0:
            s = pygame.transform.scale(s, (int(self.sz * scale), int(self.sz * scale)))
        rect = s.get_rect(center=(dx, dy))
        surf.blit(s, rect)

class Bullet(Entity):
    def __init__(self, x, y, a, wk, dmg):
        super().__init__(x, y, 4 if wk != "grenade" else 9, 4 if wk != "grenade" else 9)
        w = WPN[wk]
        self.wk = wk; self.dmg = dmg
        self.vx = math.cos(a) * w["spd"]; self.vy = math.sin(a) * w["spd"]
        self.ang = a; self.life = 160; self.bc = w["bc"]; self.bl = w["bl"]

    def update(self, game):
        self.x += self.vx; self.y += self.vy; self.life -= 1
        self.z_sort = self.x + self.y
        if self.life <= 0 or self.x<-80 or self.x>WW+80 or self.y<-80 or self.y>WH+80:
            self.alive = False; return
        br = self.get_rect()
        for wall in game.walls[:]:
            if br.colliderect(wall.get_rect()):
                if self.wk == "grenade": self._explode(game)
                else:
                    if isinstance(wall, (DestWall, SupplyCrate)): wall.take_damage(self.dmg if isinstance(wall, SupplyCrate) else self.dmg * 0.2)
                self.alive = False; return

    def _explode(self, game):
        game.effects.append(Effect(type="explosion", x=self.x, y=self.y))
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

    def draw(self, surf, cx, cy):
        sx, sy = w2s(self.x, self.y)
        dx, dy = sx - cx, sy - cy
        if not (-20 < dx < WIDTH+20 and -20 < dy < HEIGHT+20): return
        if self.bl > 0:
            s = pygame.Surface((self.bl, 4), pygame.SRCALPHA)
            pygame.draw.rect(s, self.bc, (0, 0, self.bl, 4))
            rotated = pygame.transform.rotate(s, -math.degrees(self.ang))
            rect = rotated.get_rect(center=(dx, dy))
            surf.blit(rotated, rect)
        else:
            pygame.draw.circle(surf, self.bc, (int(dx), int(dy)), 5)

class Wall(Entity):
    def __init__(self, x, y, w, h, z_h=25, color=(82,82,92)):
        super().__init__(x, y, w, h)
        self.z_h = z_h; self.color = color
    def get_rect(self): return pygame.Rect(self.x, self.y, self.w, self.h)
    def draw(self, surf, cx, cy): return draw_iso_block(surf, self.color, self.x, self.y, self.w, self.h, self.z_h, self.y + self.h)

class DestWall(Wall):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, 25, (130,110,75))
        self.max_hp = 100; self.hp = 100
    def take_damage(self, d):
        self.hp -= d
        r = max(0, self.hp / self.max_hp)
        self.color = tuple(int(c * r + dc * (1-r)) for c, dc in zip((160,140,100), (60,50,35)))
        if self.hp <= 0: self.alive = False

class Barricade(DestWall):
    def __init__(self, x, y):
        super().__init__(x-15, y-15, 30, 30)
        self.max_hp = 60; self.hp = 60; self.color = (120, 120, 130)

class SupplyCrate(Wall):
    def __init__(self, x, y):
        super().__init__(x-15, y-15, 30, 30, 15, (140, 100, 50))
        self.max_hp = 25; self.hp = 25
    def take_damage(self, d):
        self.hp -= d
        if self.hp <= 0: self.alive = False

class Pickup(Entity):
    def __init__(self, x, y, kind="health"):
        super().__init__(x, y, 26, 26)
        self.kind = kind; self.bob = random.uniform(0, 6.28)
    def update(self): self.bob += 0.1; self.y += math.sin(self.bob) * 0.18; self.z_sort = self.x + self.y
    def draw(self, surf, cx, cy):
        sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
        if not (-20 < dx < WIDTH+20 and -20 < dy < HEIGHT+20): return
        col = (220, 40, 40) if self.kind == "health" else (255, 220, 50)
        pygame.draw.circle(surf, col, (int(dx), int(dy)), 13)
        if self.kind == "health":
            pygame.draw.line(surf, WHITE, (int(dx)-7, int(dy)), (int(dx)+7, int(dy)), 2)
            pygame.draw.line(surf, WHITE, (int(dx), int(dy)-7), (int(dx), int(dy)+7), 2)

class PowerUp(Entity):
    def __init__(self, x, y, kind):
        super().__init__(x, y, 32, 32)
        self.kind = kind; self.bob = random.uniform(0, 6.28)
    def update(self): self.bob += 0.12; self.y += math.sin(self.bob) * 0.22; self.z_sort = self.x + self.y
    def draw(self, surf, cx, cy):
        sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
        if not (-20 < dx < WIDTH+20 and -20 < dy < HEIGHT+20): return
        p = 0.5 + 0.5 * math.sin(self.bob * 1.5)
        r = int(16 + 6 * p)
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        col = (*PU_I[self.kind][0], 100)
        pygame.draw.circle(s, col, (r, r), r)
        col2 = (*PU_I[self.kind][0], 220)
        pygame.draw.circle(s, col2, (r, r), 16)
        surf.blit(s, (dx - r, dy - r))

class Effect:
    def __init__(self, **kwargs):
        self.type = kwargs.get("type"); self.x = kwargs.get("x", 0); self.y = kwargs.get("y", 0)
        self.life = kwargs.get("life", 30); self.max_life = self.life; self.alive = True
        self.txt = kwargs.get("txt", ""); self.big = kwargs.get("big", False)
        self.sz = kwargs.get("sz", 8); self.col = kwargs.get("col", (255,255,100))
        self.vx = kwargs.get("vx", 0); self.vy = kwargs.get("vy", 0)
        self.z_sort = self.x + self.y

    def update(self):
        self.life -= 1; self.x += self.vx; self.y += self.vy
        if self.vy < 0: self.vy += 0.1
        self.vx *= 0.9; self.vy *= 0.9
        if self.life <= 0: self.alive = False

    def draw(self, surf, cx, cy):
        t = 1 - (self.life / self.max_life)
        alpha = int(255 * (1 - t))
        if self.type == "blood":
            sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
            if -10<dx<WIDTH+10 and -10<dy<HEIGHT+10:
                s = pygame.Surface((10, 10), pygame.SRCALPHA)
                pygame.draw.circle(s, (random.randint(120,200), 0, 0, alpha), (5, 5), random.randint(3, 6))
                surf.blit(s, (dx-5, dy-5))
        elif self.type == "dmg":
            sx, sy = w2s(self.x, self.y - (1-t)*30); dx, dy = sx - cx, sy - cy
            if -20<dx<WIDTH+20 and -20<dy<HEIGHT+10:
                f = font_sm if not self.big else font_md
                col = (255, 80, 80, alpha) if self.big else (255, 255, 255, alpha)
                ts = f.render(self.txt, True, col[:3])
                ts.set_alpha(alpha)
                surf.blit(ts, (dx - ts.get_width()//2, dy - ts.get_height()//2))
        elif self.type == "flash":
            sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
            if -20<dx<WIDTH+20 and -20<dy<HEIGHT+20:
                s = pygame.Surface((self.sz*2, self.sz*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 180, alpha), (self.sz, self.sz), self.sz)
                surf.blit(s, (dx - self.sz, dy - self.sz))
        elif self.type == "explosion":
            sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
            r = int(30 + 100 * t)
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            if t < 0.25: c = (255,255,220,alpha)
            elif t < 0.5: c = (255,150,40,alpha)
            elif t < 0.75: c = (180,80,20,alpha)
            else: c = (80,80,80,alpha)
            pygame.draw.circle(s, c, (r, r), r)
            surf.blit(s, (dx - r, dy - r))
        elif self.type == "gibs":
            sx, sy = w2s(self.x, self.y); dx, dy = sx - cx, sy - cy
            if -10<dx<WIDTH+10 and -10<dy<HEIGHT+10:
                s = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.rect(s, (*self.col, alpha), (0, 0, 6, 6))
                surf.blit(s, (dx-3, dy-3))

# ── Main Game Class ────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.state = "menu"; self.frame = 0; self.hi_score = 0
        self.kill_feed = []  # list of (text, color, timer)
        self.total_kills = 0
        self.time_played = 0  # frames spent playing
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
        self.kill_feed = []
        self.total_kills = 0
        self.time_played = 0
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
        self.kill_feed.append((text, color, 180))  # 3 seconds
        if len(self.kill_feed) > 6:
            self.kill_feed.pop(0)

    def _nw(self):
        self.wave += 1; is_boss = self.wave % 5 == 0
        self.to_spawn = 5 + self.wave*3 + self.wave//3*2 + (0 if not is_boss else 1)
        self.spawn_cd = 0; self.announce = 130; self.wave_start = self.frame
        if is_boss: self.boss_warn = 180
        for _ in range(random.randint(2, 3)):
            cx, cy = random.uniform(150, WW-150), random.uniform(150, WH-150)
            self.walls.append(SupplyCrate(cx, cy))

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

        # Kill feed timers
        self.kill_feed = [(t, c, tmr - 1) for t, c, tmr in self.kill_feed if tmr > 1]

        m_pos_w = s2w(m_pos[0] + self.cx, m_pos[1] + self.cy)
        pl.update(keys, m_pos_w, self)
        if pygame.mouse.get_pressed()[0]: pl.shoot(m_pos_w, self)

        # Camera & Shake
        self.sx *= SHD; self.sy *= SHD
        if abs(self.sx) < .1: self.sx = 0
        if abs(self.sy) < .1: self.sy = 0
        tx, ty = w2s(pl.x + self.sx, pl.y + self.sy)
        self.cx += (tx - self.cx) * CAM_L; self.cy += (ty - self.cy) * CAM_L

        # Waves
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

        # Zombies
        ppos = (pl.x, pl.y)
        for z in self.zombies: z.update(ppos, self.walls, self.zombies, self)
        for z in self.zombies:
            if z.alive and not z.dying and z.atk_cd <= 0 and z.get_rect().colliderect(pl.get_rect()):
                cdmg = z.dmg * (1.8 if z.zt == "boss" and z.bst == "charging" else 1.0)
                pl.take_damage(cdmg, self.frame); z.atk_cd = 30
                if cdmg > 0 and pl.pu_type != "shield": self.shake(5)
                self.dmg_flash = 180

        # Bullets
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
                        for _ in range(2): self.effects.append(Effect(type="blood", x=z.x+random.uniform(-10,10), y=z.y+random.uniform(-10,10), life=120))
                        if killed:
                            self.combo += 1; self.combo_t = 120; mult = 1 + self.combo*0.25
                            pts = int(z.pts * self.wave * mult)
                            self.score += pts; self.kills[z.zt] += 1
                            self.total_kills += 1
                            for _ in range(6): self.effects.append(Effect(type="blood", x=z.x+random.uniform(-10,10), y=z.y+random.uniform(-10,10), life=200))
                            for _ in range(4): self.effects.append(Effect(type="gibs", x=z.x, y=z.y, vx=random.uniform(-5,5), vy=random.uniform(-5,5), col=Z_ST[z.zt]["c"], life=20))
                            for thresh, txt, col in STREAKS:
                                if self.combo >= thresh and self.combo != self.last_streak:
                                    self.last_streak = self.combo; self.announce = 0
                                    self.effects.append(Effect(type="dmg", x=WW/2, y=WH/2 - 60, txt=txt, life=90, big=True, col=col)); break
                            # Kill feed entry
                            zt_name = z.zt.upper()
                            zt_col = Z_ST[z.zt]["hc"]
                            feed_txt = f"  {zt_name}  +{pts}"
                            if self.combo > 1:
                                feed_txt += f"  x{self.combo}"
                            self._add_kill_feed(feed_txt, zt_col)
                            if z.zt == "boss":
                                self._add_kill_feed("  BOSS ELIMINATED!", (255, 215, 0))
                                for _ in range(3): self.pickups.append(Pickup(z.x+random.uniform(-30,30), z.y+random.uniform(-30,30), random.choice(["health","ammo"])))
                                for _ in range(3): self.zombies.append(Zombie(z.x+random.uniform(-40,40), z.y+random.uniform(-40,40), "normal", self.wave))
                                self.shake(15)
                            elif random.random() < .18: self.pickups.append(Pickup(z.x, z.y, "health" if random.random() < .55 else "ammo"))
                            elif random.random() < .08: self.powerups.append(PowerUp(z.x, z.y, random.choice(POWERUP_TYPES)))
                    b.alive = False; break

        # Pickups & PowerUps
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

        # Effects
        for e in self.effects: e.update()

        # Cleanup
        self.zombies = [z for z in self.zombies if z.alive]
        self.bullets = [b for b in self.bullets if b.alive]
        self.effects = [e for e in self.effects if e.alive][:500]
        self.pickups = [p for p in self.pickups if p.alive]
        self.powerups = [p for p in self.powerups if p.alive]
        self.walls = [w for w in self.walls if w.alive]

    # ── Drawing ─────────────────────────────────────────────────────────────────
    def draw(self):
        screen.fill((35, 35, 40))

        # Draw Floor Grid
        for x in range(0, WW+1, 40):
            p1 = w2s(x, 0); p2 = w2s(x, WH)
            pygame.draw.line(screen, (44,44,49), (p1[0]-self.cx, p1[1]-self.cy), (p2[0]-self.cx, p2[1]-self.cy))
        for y in range(0, WH+1, 40):
            p1 = w2s(0, y); p2 = w2s(WW, y)
            pygame.draw.line(screen, (44,44,49), (p1[0]-self.cx, p1[1]-self.cy), (p2[0]-self.cx, p2[1]-self.cy))

        if self.state == "menu": self._draw_menu(); return
        if self.state == "gameover": self._draw_go(); return

        # Gather and Z-Sort
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

        self._draw_hud()

    def _draw_menu(self):
        draw_text(screen, "BOX HEAD", (WIDTH//2, HEIGHT//2 - 100), (50,180,255), font_title, True)
        draw_text(screen, "2.5D Isometric Pygame Edition", (WIDTH//2, HEIGHT//2 - 20), GRAY, font_md, True)
        draw_text(screen, "[ Click to Start ]", (WIDTH//2, HEIGHT//2 + 40), WHITE, font_lg, True)
        ctrls = ["WASD Move | Mouse Aim | LMB Shoot | Q/E or Scroll Switch",
                 "Space Dash | F Barricade (50pts) | 1-4 Weapon Slots | Esc Pause"]
        for i, t in enumerate(ctrls): draw_text(screen, t, (WIDTH//2, HEIGHT//2 + 100 + i*25), DARK_GRAY, font_sm, True)
        if self.hi_score > 0: draw_text(screen, f"High Score: {self.hi_score}", (WIDTH//2, HEIGHT - 50), (255,220,80), font_md, True)

    def _draw_go(self):
        # Darken background
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((0, 0, 0, 140))
        screen.blit(ov, (0, 0))
        draw_text(screen, "GAME OVER", (WIDTH//2, 150), RED, font_xl, True)

        # Stats panel
        pw, ph = 360, 260
        px, py = (WIDTH - pw) // 2, 200
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((15, 15, 20, 200))
        pygame.draw.rect(panel, (80, 80, 100, 150), (0, 0, pw, ph), 1, border_radius=8)
        screen.blit(panel, (px, py))

        stats = [
            (f"Final Score:  {self.score}", (255, 255, 255)),
            (f"Wave Reached:  {self.wave}", (200, 200, 200)),
            (f"Total Kills:  {self.total_kills}", (200, 200, 200)),
            (f"  Normal: {self.kills['normal']}   Fast: {self.kills['fast']}", (160, 160, 160)),
            (f"  Big: {self.kills['big']}   Boss: {self.kills['boss']}", (160, 160, 160)),
            (f"Time Survived:  {self.time_played // FPS}s", (180, 180, 180)),
            (f"Best Combo:  x{self.last_streak}", (255, 200, 50)),
        ]
        for i, (txt, col) in enumerate(stats):
            draw_text(screen, txt, (px + 20, py + 15 + i * 33), col, font_md)

        if self.score >= self.hi_score and self.score > 0:
            draw_text(screen, "NEW HIGH SCORE!", (WIDTH//2, py + ph + 20), (255, 215, 0), font_lg, True)

        draw_text(screen, "[ Click to Restart ]", (WIDTH//2, py + ph + 65), GRAY, font_md, True)

    # ── IMPROVED HUD ────────────────────────────────────────────────────────────
    def _draw_hud(self):
        pl = self.player
        if not pl: return

        # ── Damage vignette (low-HP pulse) ──────────────────────────────────
        hp_ratio = max(0, pl.hp / pl.max_hp)
        if hp_ratio < 0.3:
            pulse = 0.5 + 0.5 * math.sin(self.frame * 0.15)
            low_hp_alpha = int(60 * pulse * (1 - hp_ratio / 0.3))
            low_s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            low_s.fill((180, 0, 0, low_hp_alpha))
            screen.blit(low_s, (0, 0))

        if self.dmg_flash > 0:
            vs = vignette_surf.copy()
            vs.fill((255, 0, 0, min(255, int(self.dmg_flash * 0.8))))
            screen.blit(vs, (0, 0))

        # ── Hit Markers ─────────────────────────────────────────────────────
        if self.hit_marks:
            mx, my = pygame.mouse.get_pos()
            hm_s = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.line(hm_s, (255, 255, 255, 220), (2, 2), (8, 8), 3)
            pygame.draw.line(hm_s, (255, 255, 255, 220), (18, 2), (12, 8), 3)
            pygame.draw.line(hm_s, (255, 255, 255, 220), (2, 18), (8, 12), 3)
            pygame.draw.line(hm_s, (255, 255, 255, 220), (18, 18), (12, 12), 3)
            screen.blit(hm_s, (mx - 10, my - 10))

        # ── LEFT PANEL: HP / Dash / Barricade / Powerup ─────────────────────
        screen.blit(_hud_left_panel, (10, 10))

        # HP Bar
        r = max(0, pl.hp / pl.max_hp)
        hc = (40, 220, 60) if r > .5 else (255, 200, 0) if r > .25 else (255, 40, 40)
        draw_rounded_bar(screen, 20, 20, 230, 22, r, hc, (40, 10, 10))
        # HP icon + text
        draw_text(screen, "+", (24, 20), hc, font_hud_num)
        hp_txt = f"{int(pl.hp)}/{pl.max_hp}"
        draw_text(screen, hp_txt, (250 - font_hud_sm.size(hp_txt)[0] - 4, 24), WHITE, font_hud_sm)

        # Dash CD bar
        dr = 1 - pl.dash_cd / 90 if pl.dash_cd > 0 else 1
        dash_col = (40, 180, 255) if dr >= 1 else (60, 100, 160)
        draw_rounded_bar(screen, 20, 48, 230, 12, dr, dash_col, (20, 25, 40))
        dash_txt = "SPACE" if dr >= 1 else f"SPACE  {pl.dash_cd // FPS + 1}s"
        dash_col_t = (180, 220, 255) if dr >= 1 else (80, 90, 110)
        draw_text(screen, f"DASH  [{dash_txt}]", (24, 47), dash_col_t, font_hud_sm)

        # Barricade CD bar  (bug fixed: string concat)
        br = 1 - pl.barricade_cd / 30 if pl.barricade_cd > 0 else 1
        bar_col = (130, 130, 145) if br >= 1 else (70, 70, 80)
        draw_rounded_bar(screen, 20, 66, 230, 12, br, bar_col, (20, 20, 30))
        if br >= 1:
            draw_text(screen, f"BARRICADE  [F]  (-50pts)", (24, 65), (160, 160, 175), font_hud_sm)
        else:
            draw_text(screen, f"BARRICADE  [F]  {pl.barricade_cd // FPS + 1}s", (24, 65), (80, 80, 95), font_hud_sm)

        # Powerup bar
        py_off = 86
        if pl.pu_type and pl.pu_timer > 0:
            pr = pl.pu_timer / 480
            col = PU_I[pl.pu_type][0]
            draw_rounded_bar(screen, 20, 86, 230, 14, pr, col, (20, 20, 25))
            secs = pl.pu_timer // FPS + 1
            draw_text(screen, f"{PU_I[pl.pu_type][1]}  {secs}s", (24, 84), col, font_hud_sm)
            py_off = 106

        # ── RIGHT PANEL: Score / Wave / Enemies / Time ──────────────────────
        screen.blit(_hud_right_panel, (WIDTH - 240, 10))

        draw_text(screen, f"SCORE", (WIDTH - 224, 16), (140, 140, 150), font_hud_sm)
        draw_text(screen, f"{self.score:,}", (WIDTH - 224, 30), WHITE, font_hud_num)

        draw_text(screen, f"WAVE", (WIDTH - 224, 55), (140, 140, 150), font_hud_sm)
        draw_text(screen, f"{self.wave}", (WIDTH - 140, 55), (255, 200, 80), font_hud_num)

        # Wave progress bar (under score panel)
        rem = self.to_spawn + sum(1 for z in self.zombies if z.alive and not z.dying)
        total_for_wave = 5 + self.wave * 3 + self.wave // 3 * 2
        if self.wave % 5 == 0:
            total_for_wave += 1
        wp_ratio = max(0, 1 - rem / max(1, total_for_wave)) if self.wave > 0 else 0
        draw_rounded_bar(screen, WIDTH - 224, 78, 210, 10, wp_ratio, (100, 200, 120), (25, 25, 30), 3)
        draw_text(screen, f"{rem} left", (WIDTH - 224, 77), (200, 120, 120) if rem > 0 else (100, 200, 120), font_hud_sm)

        # Time survived
        secs = self.time_played // FPS
        mins = secs // 60
        time_str = f"{mins}:{secs % 60:02d}"
        draw_text(screen, time_str, (WIDTH - 224, 93), (120, 120, 130), font_hud_sm)

        # Total kills
        draw_text(screen, f"Kills: {self.total_kills}", (WIDTH - 140, 93), (120, 120, 130), font_hud_sm)

        # ── KILL FEED (top-right, below score panel) ────────────────────────
        kf_x = WIDTH - 240
        kf_y = 110
        for i, (txt, col, timer) in enumerate(self.kill_feed):
            alpha = min(255, timer * 3)
            ts = font_kf.render(txt, True, col)
            ts.set_alpha(alpha)
            screen.blit(ts, (kf_x + 4, kf_y + i * 18))

        # ── BOTTOM-CENTER WEAPON BAR ────────────────────────────────────────
        self._draw_weapon_bar(pl)

        # ── COMBO COUNTER ───────────────────────────────────────────────────
        if self.combo > 1:
            # Animated scale
            scale_t = min(1.0, self.combo_t / 15.0)  # pop in
            base_size = min(48, 32 + self.combo)
            sz = int(base_size * scale_t)
            if sz > 10:
                combo_font = pygame.font.SysFont("Impact", sz, bold=True)
                # Shadow
                draw_text(screen, f"x{self.combo}", (WIDTH // 2 + 2, 32), (40, 30, 0), combo_font, True)
                # Main
                combo_col = lerp_color((255, 200, 50), (255, 80, 30), min(1, self.combo / 20))
                draw_text(screen, f"x{self.combo} COMBO", (WIDTH // 2, 30), combo_col, combo_font, True)

        # ── ANNOUNCEMENTS (center, with fade) ───────────────────────────────
        if self.announce > 0:
            a_alpha = min(255, self.announce * 5)
            a_scale = min(1.0, (130 - self.announce + 1) / 15.0)  # zoom in over first 15 frames
            if a_scale > 0.1:
                a_font = pygame.font.SysFont("Impact", int(56 * a_scale), bold=True)
                ts = a_font.render(f"WAVE {self.wave}", True, (255, 255, 100))
                ts.set_alpha(a_alpha)
                r = ts.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(ts, r)

        if self.boss_warn > 0:
            bw_alpha = min(255, self.boss_warn * 4)
            pulse = 0.7 + 0.3 * math.sin(self.boss_warn * 0.3)
            ts = font_lg.render("!! BOSS INCOMING !!", True,
                                (int(255 * pulse), int(30 * pulse), int(30 * pulse)))
            ts.set_alpha(bw_alpha)
            r = ts.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            screen.blit(ts, r)

        if self.wc_bonus_t > 0:
            wc_alpha = min(255, self.wc_bonus_t * 4)
            ts = font_md.render(f"WAVE CLEAR! +{self.wc_bonus}", True, (100, 255, 100))
            ts.set_alpha(wc_alpha)
            r = ts.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(ts, r)

        if self.wpn_ann_t > 0:
            wa_alpha = min(255, self.wpn_ann_t * 6)
            ts = font_md.render(self.wpn_ann, True, GRAY)
            ts.set_alpha(wa_alpha)
            r = ts.get_rect(center=(WIDTH // 2, HEIGHT - 100))
            screen.blit(ts, r)

        # ── MINIMAP ─────────────────────────────────────────────────────────
        self._draw_minimap(pl)

        # ── CROSSHAIR ───────────────────────────────────────────────────────
        self._draw_crosshair(pl)

    def _draw_weapon_bar(self, pl):
        """Draw the bottom-center weapon selection bar."""
        n = len(pl.weapons)
        slot_w, slot_h = 100, 50
        gap = 4
        total_w = n * slot_w + (n - 1) * gap
        bar_x = (WIDTH - total_w) // 2
        bar_y = HEIGHT - slot_h - 14

        # Bar background
        bg = pygame.Surface((total_w + 12, slot_h + 12), pygame.SRCALPHA)
        bg.fill((10, 10, 15, 170))
        pygame.draw.rect(bg, (60, 60, 80, 100), (0, 0, total_w + 12, slot_h + 12), 1, border_radius=6)
        screen.blit(bg, (bar_x - 6, bar_y - 6))

        for i, wk in enumerate(pl.weapons):
            sx = bar_x + i * (slot_w + gap)
            is_active = (i == pl.cw)
            w = WPN[wk]
            icon_col = WPN_ICON_COL[wk]

            # Slot background
            if is_active:
                slot_bg = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
                slot_bg.fill((*icon_col, 30))
                pygame.draw.rect(slot_bg, (*icon_col, 180), (0, 0, slot_w, slot_h), 2, border_radius=4)
                # Active highlight line at top
                pygame.draw.line(slot_bg, (*icon_col, 220), (4, 1), (slot_w - 4, 1), 2)
                screen.blit(slot_bg, (sx, bar_y))
            else:
                slot_bg = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
                slot_bg.fill((20, 20, 25, 150))
                pygame.draw.rect(slot_bg, (50, 50, 60, 100), (0, 0, slot_w, slot_h), 1, border_radius=4)
                screen.blit(slot_bg, (sx, bar_y))

            # Weapon icon (simple colored rectangle representing the gun)
            icon_x = sx + 8
            icon_y = bar_y + 8
            if wk == "pistol":
                pygame.draw.rect(screen, icon_col, (icon_x, icon_y + 4, 18, 6))
                pygame.draw.rect(screen, scale_color(icon_col, 0.7), (icon_x + 4, icon_y + 8, 6, 10))
            elif wk == "shotgun":
                pygame.draw.rect(screen, icon_col, (icon_x, icon_y + 3, 22, 8))
                pygame.draw.rect(screen, scale_color(icon_col, 0.7), (icon_x + 6, icon_y + 9, 8, 12))
                pygame.draw.line(screen, scale_color(icon_col, 0.5), (icon_x + 2, icon_y + 5), (icon_x + 20, icon_y + 5), 1)
                pygame.draw.line(screen, scale_color(icon_col, 0.5), (icon_x + 2, icon_y + 9), (icon_x + 20, icon_y + 9), 1)
            elif wk == "uzi":
                pygame.draw.rect(screen, icon_col, (icon_x, icon_y + 2, 20, 7))
                pygame.draw.rect(screen, scale_color(icon_col, 0.7), (icon_x + 2, icon_y + 7, 5, 14))
                # Bullet indicator lines
                for bl in range(3):
                    pygame.draw.rect(screen, scale_color(icon_col, 0.5), (icon_x + 14 + bl * 3, icon_y + 10, 2, 8))
            elif wk == "grenade":
                pygame.draw.circle(screen, icon_col, (icon_x + 10, icon_y + 10), 8)
                pygame.draw.circle(screen, scale_color(icon_col, 1.3), (icon_x + 8, icon_y + 7), 3)
                pygame.draw.line(screen, (80, 80, 80), (icon_x + 10, icon_y + 2), (icon_x + 10, icon_y - 2), 2)

            # Weapon name
            nm_col = WHITE if is_active else (90, 90, 100)
            draw_text(screen, w["nm"], (sx + 34, bar_y + 6), nm_col, font_hud_sm)

            # Ammo
            if wk == "pistol":
                draw_text(screen, "INF", (sx + 34, bar_y + 22), (80, 80, 90) if not is_active else (180, 180, 100), font_hud_sm)
            else:
                ammo = pl.ammo[wk]
                ammo_col = (180, 180, 190) if is_active else (80, 80, 90)
                if ammo == 0:
                    ammo_col = (255, 50, 50)
                draw_text(screen, f"{ammo}", (sx + 34, bar_y + 22), ammo_col, font_hud_sm)

            # Key binding number
            key_str = WPN_SLOT_KEY.get(i, "")
            key_col = icon_col if is_active else (60, 60, 70)
            draw_text(screen, key_str, (sx + slot_w - 16, bar_y + slot_h - 18), key_col, font_hud_sm)

            # Fire rate indicator dots
            if is_active:
                rate_val = w["rate"]
                dot_y = bar_y + slot_h - 8
                for d in range(5):
                    dx = sx + 34 + d * 10
                    filled = (self.frame % max(1, rate_val)) > d * (rate_val // 5) if rate_val > 0 else False
                    dc = icon_col if filled else (40, 40, 50)
                    pygame.draw.circle(screen, dc, (dx, dot_y), 3)

    def _draw_minimap(self, pl):
        mm = 150
        mmx, mmy = WIDTH - mm - 14, HEIGHT - mm - 80
        mm_s = mm  # keep for label spacing

        # Background panel
        panel = pygame.Surface((mm + 4, mm + 22), pygame.SRCALPHA)
        panel.fill((10, 10, 15, 180))
        pygame.draw.rect(panel, (60, 60, 80, 120), (0, 0, mm + 4, mm + 22), 1, border_radius=4)
        screen.blit(panel, (mmx - 2, mmy - 2))

        # Map surface
        ms = pygame.Surface((mm, mm), pygame.SRCALPHA)
        ms.fill((15, 15, 20, 200))
        sx_r, sy_r = mm / WW, mm / WH

        # Walls
        for w in self.walls:
            if isinstance(w, DestWall):
                col = (120, 100, 60, 180)
            elif isinstance(w, SupplyCrate):
                col = (160, 120, 50, 200)
            elif isinstance(w, Barricade):
                col = (110, 110, 120, 200)
            else:
                col = (60, 60, 65, 180)
            pygame.draw.rect(ms, col, (w.x * sx_r, w.y * sy_r, max(1, w.w * sx_r), max(1, w.h * sy_r)))

        # Pickups
        for pk in self.pickups:
            c = (255, 60, 60, 220) if pk.kind == "health" else (255, 220, 50, 220)
            pygame.draw.circle(ms, c, (int(pk.x * sx_r), int(pk.y * sy_r)), 2)

        # Powerups
        for pu in self.powerups:
            pygame.draw.circle(ms, (*PU_I[pu.kind][0], 240), (int(pu.x * sx_r), int(pu.y * sy_r)), 3)

        # Zombies
        for z in self.zombies:
            if z.alive and not z.dying:
                if z.zt == "boss":
                    pygame.draw.circle(ms, (255, 200, 0, 255), (int(z.x * sx_r), int(z.y * sy_r)), 4)
                    pygame.draw.circle(ms, (255, 255, 100, 200), (int(z.x * sx_r), int(z.y * sy_r)), 6, 1)
                else:
                    c = (255, 40, 40, 220) if z.zt != "fast" else (255, 100, 100, 220)
                    pygame.draw.circle(ms, c, (int(z.x * sx_r), int(z.y * sy_r)), 2)

        # Player FOV cone
        pl_mx, pl_my = int(pl.x * sx_r), int(pl.y * sy_r)
        fov_len = 25
        fov_spread = 0.4
        fov_s = pygame.Surface((mm, mm), pygame.SRCALPHA)
        a1 = pl.ang - fov_spread
        a2 = pl.ang + fov_spread
        pts = [(pl_mx, pl_my),
               (pl_mx + int(math.cos(a1) * fov_len), pl_my + int(math.sin(a1) * fov_len)),
               (pl_mx + int(math.cos(a2) * fov_len), pl_my + int(math.sin(a2) * fov_len))]
        pygame.draw.polygon(fov_s, (50, 150, 255, 35), pts)
        ms.blit(fov_s, (0, 0))

        # Player dot
        pygame.draw.circle(ms, (50, 150, 255, 255), (pl_mx, pl_my), 4)
        pygame.draw.circle(ms, (150, 200, 255, 200), (pl_mx, pl_my), 6, 1)

        screen.blit(ms, (mmx, mmy))

        # Label
        draw_text(screen, "MAP", (mmx + 4, mmy + mm + 4), (80, 80, 100), font_hud_sm)

    def _draw_crosshair(self, pl):
        mx, my = pygame.mouse.get_pos()
        wk = pl.wk
        col = WPN_ICON_COL.get(wk, WHITE)
        gap = 6
        length = 14
        thick = 2

        # Dynamic gap: expand when fire cooldown active
        if pl.fcd > 0:
            ratio = pl.fcd / max(1, WPN[wk]["rate"])
            gap = int(6 + 8 * ratio)

        # Lines
        pygame.draw.line(screen, col, (mx - gap - length, my), (mx - gap, my), thick)
        pygame.draw.line(screen, col, (mx + gap, my), (mx + gap + length, my), thick)
        pygame.draw.line(screen, col, (mx, my - gap - length), (mx, my - gap), thick)
        pygame.draw.line(screen, col, (mx, my + gap), (mx, my + gap + length), thick)

        # Center dot
        pygame.draw.circle(screen, col, (mx, my), 2)

        # Outer ring
        ring_s = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(ring_s, (*col, 60), (12, 12), 10, 1)
        screen.blit(ring_s, (mx - 12, my - 12))

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
                    # Number keys for direct weapon select
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                        idx = event.key - pygame.K_1
                        if 0 <= idx < len(game.player.weapons):
                            game.player.cw = idx
            if event.type == pygame.MOUSEWHEEL and game.state == "playing":
                game.player.cw = (game.player.cw + (1 if event.y > 0 else -1)) % 4

        if game.state == "playing": game.update(keys, m_pos)

        game.draw()
        if game.state == "paused":
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0, 0, 0, 160))
            screen.blit(s, (0, 0))
            draw_text(screen, "PAUSED", (WIDTH // 2, HEIGHT // 2), WHITE, font_xl, True)
            draw_text(screen, "Press ESC to resume", (WIDTH // 2, HEIGHT // 2 + 60), GRAY, font_md, True)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()