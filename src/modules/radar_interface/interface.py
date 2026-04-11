import pygame
import math

class LineTarget:
    COLOR = (80, 0, 0)

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.alpha = 255

    def is_visible(self):
        return self.alpha > 0

    def decrease_alpha(self):
        self.alpha -= 1

    def draw(self, surface):
        if self.alpha <= 0:
            return

        line_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        color = (*self.COLOR, self.alpha)
        pygame.draw.line(
            line_surf, color,
            (self.x1, self.y1),
            (self.x2, self.y2),
            4
        )
        surface.blit(line_surf, (0, 0))

class RadarInterface:
    def __init__(self):
        self.TITLE        = "Radar Interface"
        self.SCREEN_W     = 1200
        self.SCREEN_H     = self.SCREEN_W // 2
        self.FPS          = 60
        self.PADDING      = 50

        self.CL_BACKGROUND = ( 22,  37,  26)
        self.CL_RADAR      = ( 27,  65,  37)
        self.CL_SWEEP      = (  0, 143,  57)
        self.CL_TARGET     = ( 80,   0,   0)

        self.FADE_LVL  = 25
        self.FADE_DIST = 0.01
        self.THICKNESS = 4

        self.TARGET_SAMPLES = 314
        self.MAX_DISTANCE   = 400

        pygame.init()
        pygame.display.set_caption(self.TITLE)

        self.screen = pygame.display.set_mode(
            (self.SCREEN_W, self.SCREEN_H + self.PADDING)
        )
        self.clock = pygame.time.Clock()

        self.sweep_pos = math.pi / 2
        self.dist = -1

        self.targets = [None] * self.TARGET_SAMPLES

    def update(self, pos, dist):
        self.sweep_pos = pos
        self.dist = dist

    def _draw_radar(self):
        # Arcs
        for i in range(4, 0, -1):
            arc_w = (self.SCREEN_W - self.PADDING * 2) * i // 4
            arc_h = (self.SCREEN_H * 2 - self.PADDING * 2) * i // 4
            rect = pygame.Rect(
                self.SCREEN_W // 2 - arc_w // 2,
                self.SCREEN_H - arc_h // 2,
                arc_w,
                arc_h
            )
            pygame.draw.arc(
                self.screen, self.CL_RADAR,
                rect,
                0, math.pi,
                self.THICKNESS
            )

        # Lines: 0, 30, 60, 90, 120, 150, 180 degrees
        radius = self.SCREEN_H - self.PADDING // 2
        for i in range(0, 210, 30):
            rad = math.radians(i)
            pygame.draw.line(
                self.screen, self.CL_RADAR,
                (self.SCREEN_W // 2, self.SCREEN_H),
                (
                    self.SCREEN_W // 2 + math.cos(rad) * radius,
                    self.SCREEN_H - math.sin(rad) * radius
                ),
                self.THICKNESS
            )

    def _draw_scanner(self):
        radius = self.SCREEN_H - self.PADDING // 2

        # Draw and update target lines
        for i in range(len(self.targets)):
            if self.targets[i] is None:
                continue

            self.targets[i].draw(self.screen)
            self.targets[i].decrease_alpha()

            if not self.targets[i].is_visible():
                self.targets[i] = None

        # Set target line based on radar position
        if 0 <= self.dist <= self.MAX_DISTANCE:
            length = self.dist / self.MAX_DISTANCE * radius
            idx = int(self.sweep_pos * 100)

            if 0 <= idx < self.TARGET_SAMPLES:
                self.targets[idx] = LineTarget(
                    self.SCREEN_W // 2 + math.cos(self.sweep_pos) * radius,
                    self.SCREEN_H - math.sin(self.sweep_pos) * radius,
                    self.SCREEN_W // 2 + math.cos(self.sweep_pos) * length,
                    self.SCREEN_H - math.sin(self.sweep_pos) * length,
                )

        # Draw scanner line with fade effect
        fade_surf = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        for i in range(-self.FADE_LVL // 2, self.FADE_LVL // 2):
            alpha = 255 // self.FADE_LVL * (self.FADE_LVL - abs(i * 2))
            alpha = max(0, min(255, alpha))
            color = (*self.CL_SWEEP, alpha)
            angle = self.sweep_pos - self.FADE_DIST * i
            pygame.draw.line(
                fade_surf, color,
                (self.SCREEN_W // 2, self.SCREEN_H),
                (
                    self.SCREEN_W // 2 + math.cos(angle) * radius,
                    self.SCREEN_H - math.sin(angle) * radius
                ),
                self.THICKNESS
            )
        self.screen.blit(fade_surf, (0, 0))

    def draw(self):
        self.screen.fill(self.CL_BACKGROUND)
        self._draw_radar()
        self._draw_scanner()

    def execute(self, pos, dist=-1):
        self.clock.tick(self.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True

        self.update(pos, dist)
        self.draw()
        pygame.display.flip()

        return False
