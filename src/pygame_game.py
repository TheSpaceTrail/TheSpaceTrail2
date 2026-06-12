from numpy import isin
import pygame; pygame.init();
import re, random
import time, math

from . import parser

from .events.roulette import roulette
from .events.shop import shop
from .events.hunting import hunting
from .events.asteroid import huntinga
from .events.pause import pause

WIDTH, HEIGHT = 1280, 720
BAR_H = 60

BG = (12, 12, 12)
TEXT = (235, 235, 235)

dist_to_saturn = ""

font_small = pygame.font.SysFont("segoeuiemoji", 22)

class Input:
    def __init__(self):
        self.prev = set()
        self.now = set()
        self.held = set()

    def update(self):
        self.prev = self.now
        self.now = set()

        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                raise SystemExit

            if e.type == pygame.KEYDOWN and e.key == pygame.K_q:
                
                pause()
                

            if e.type == pygame.KEYDOWN:
                self.now.add(e.key)
                self.held.add(e.key)

            if e.type == pygame.KEYUP:
                if e.key in self.held:
                    self.held.remove(e.key)

    def pressed(self, k):
        return k in self.now and k not in self.prev

    def down(self, k):
        return k in self.held

    def confirm(self):
        return (
            self.pressed(pygame.K_SPACE)
            or self.pressed(pygame.K_RETURN)
        )


COLOR_MAP = {
    "red3": (255, 40, 40),
    "red": (255, 80, 80),
    "cyan1": (135, 206, 255),
    "cyan2": (100, 200, 255),
    "green": (120, 255, 120),
    "yellow": (255, 255, 140),
    "orange_red1": (255, 100, 60),
    "deep_sky_blue1": (0, 191, 255),
    "dark_cyan": (0, 139, 139),
}


TAG_RE = re.compile(r"(\[/?[^\]]+\])")


def parse_formatted(text: str):

    tokens = TAG_RE.split(text)

    stack = []
    buffer = []
    out = []

    def flush():
        nonlocal buffer
        if buffer:
            out.append({"text": "".join(buffer), "fmt": stack.copy()})
            buffer = []

    for t in tokens:

        if not t:
            continue

        if t.startswith("["):

            flush()
            tag = t[1:-1].strip()

            if tag.startswith("/"):
                name = tag[1:]
                for i in range(len(stack) - 1, -1, -1):
                    if stack[i] == name:
                        stack = stack[:i]
                        break
            else:
                stack.append(tag)

        else:
            buffer.append(t)

    flush()
    return out


def resolve_style(fmt):
    color = TEXT
    bold = False

    for f in fmt:
        if f == "bold":
            bold = True
        elif f in COLOR_MAP:
            color = COLOR_MAP[f]

    return color, bold

def wrap(font, segments, max_width):

    lines = []
    line = []
    width = 0

    for seg in segments:

        words = seg["text"].split(" ")

        for w in words:

            if w == "":
                continue

            token = w + " "
            w_w = font.size(token)[0]

            if width + w_w > max_width and line:
                lines.append(line)
                line = []
                width = 0

            line.append((token, seg["fmt"]))
            width += w_w

    if line:
        lines.append(line)

    return lines


class Buffer:
    def __init__(self):
        self.messages = []

    def add(self, segments):
        self.messages.append(segments)

def render(screen, font, buf):

    screen.fill(BG)

    max_width = WIDTH - 40
    line_h = 28

    all_lines = []
    for msg in buf.messages:
        all_lines.extend(wrap(font, msg, max_width))

    visible = (HEIGHT - BAR_H - 40) // line_h
    start = max(0, len(all_lines) - visible)

    y = 20

    for line in all_lines[start:]:

        x = 20

        for text, fmt in line:

            color, bold = resolve_style(fmt)

            f = font
            f.set_bold(bold)

            surf = f.render(text, True, color)
            screen.blit(surf, (x, y))

            x += surf.get_width()

        y += line_h

def prompt(screen, font, inp, question, choices, buf):
    small = pygame.font.SysFont("segoeuiemoji", 20)

    q_segments = parse_formatted(question)
    selected = 0

    while True:

        inp.update()
        render(screen, font, buf)

        box = pygame.Rect(WIDTH//2 - 360, HEIGHT//2 - 180, 720, 360)
        pygame.draw.rect(screen, (30, 30, 30), box)

        max_w = box.width - 40

        lines = []
        current_line = ""

        def flush():
            nonlocal current_line
            if current_line:
                lines.append(current_line)
                current_line = ""

        for seg in q_segments:
            words = seg["text"].split(" ")

            for w in words:
                if w == "":
                    continue

                test = current_line + w + " "

                if small.size(test)[0] > max_w:
                    flush()
                    current_line = w + " "
                else:
                    current_line = test

        flush()

        y = box.y + 20

        for text in lines:
            screen.blit(
                small.render(text, True, TEXT),
                (box.x + 20, y)
            )
            y += 22

        y += 26

        for i, c in enumerate(choices):

            prefix = "> " if i == selected else "  "
            surf = small.render(prefix + c, True, TEXT)

            screen.blit(surf, (box.x + 20, y))
            y += 26

        bar(screen, small, "[SPACE/ENTER] Select")
        pygame.display.flip()

        if inp.pressed(pygame.K_UP):
            selected = max(0, selected - 1)

        if inp.pressed(pygame.K_DOWN):
            selected = min(len(choices) - 1, selected + 1)

        if inp.confirm():
            return choices[selected]

def bar(screen, font, text):

    global dist_to_saturn

    pygame.draw.rect(
        screen,
        (18, 18, 18),
        (0, HEIGHT - BAR_H, WIDTH, BAR_H)
    )

    display_text = (
        f"DISTANCE TO SATURN: {dist_to_saturn} | {text}"
        if dist_to_saturn
        else text
    )

    screen.blit(
        font.render(display_text, True, (120, 200, 255)),
        (20, HEIGHT - 40)
    )

shop.bar = bar

# MAIN LOOP (FIXED SLOW PRINT HERE)


def run():

    global dist_to_saturn

    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    font = pygame.font.SysFont("segoeuiemoji", 26)

    inp = Input()
    buf = Buffer()

    state = "intro"

    SLOW_RE = re.compile(r"^!slow\s+(\d+)\s+(.*)$")

    # Load title image
    title_image = pygame.image.load("./assets/TheSpaceTrail.png").convert_alpha()
    title_image = pygame.transform.scale_by(title_image, (0.7, 0.7))

    title_surface = font.render("PRESS ANY KEY TO BEGIN", True, (255, 255, 255))

    waiting_for_key = True
    
    while waiting_for_key:

        screen.fill((0, 0, 0))

        title_rect = title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        prompt_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 250))

        screen.blit(title_image, title_rect)
        screen.blit(title_surface, prompt_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("quit")
                pygame.quit()

            elif event.type == pygame.KEYDOWN:
                waiting_for_key = False

    while True:

        gen = parser.run_sequence(parser.storyline[state])
        send = None

        try:
            while True:

                for event in pygame.event.get():

                    if event.type == pygame.KEYDOWN:
                        waiting_for_key = False

                inp.update()

                ev = gen.send(send)
                send = None

                if isinstance(ev, parser.Roulette):

                    result = roulette(screen, font_small, inp, parser.player)

                if isinstance(ev, parser.Asteroid):

                    result = huntinga(screen, font_small, inp, parser.player)
                
                if isinstance(ev, parser.Hunting):

                    result = hunting(screen, font_small, inp, parser.player)

                if isinstance(ev, parser.Print):

                    if "DISTANCE" in ev.text: 
                        dist_to_saturn = " ".join(ev.text.split(" ")[3:])
    
                    buf.add(parse_formatted(ev.text))
                    render(screen, font, buf)
                    bar(screen, font_small, "[SPACE/ENTER] Continue")
                    pygame.display.flip()
                    while not inp.confirm():
                        inp.update()
                        
                elif isinstance(ev, parser.SlowPrint):

                    speed = ev.speed
                    raw = ev.text

                    i = 0
                    last = time.time()
                    delay = 0.03 / max(speed, 1)

                    temp = ""

                    while i < len(raw):

                        inp.update()
                        now = time.time()

                        # skip
                        if inp.confirm():
                            temp = raw
                            buf.messages = []
                            buf.add(parse_formatted(temp))
                            render(screen, font, buf)
                            pygame.display.flip()
                            break

                        if now - last >= delay:

                            ch = raw[i]
                            temp += ch
                            i += 1
                            last = now

                            # ONLY re-render full parsed text
                            buf.messages = []
                            buf.add(parse_formatted(temp))

                        render(screen, font, buf)
                        pygame.display.flip()

                elif isinstance(ev, parser.Prompt):
                    send = prompt(screen, font, inp, ev.question, ev.choices, buf)

                elif isinstance(ev, parser.Shop):
                    shop(screen, font, inp, ev.shop_data, parser.player, bar)

                elif isinstance(ev, parser.Jump):
                    state = ev.target
                    break

                elif isinstance(ev, parser.End):
                    pygame.quit()
                    return

        except StopIteration:
            pass


if __name__ == "__main__":
    run()