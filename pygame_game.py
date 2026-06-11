from numpy import isin
import pygame; pygame.init();
import parser
import re, random
import time, math

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


class ShopState:
    def __init__(self, data):
        self.data = data
        self.dialog_index = 0
        self.last_update = time.time()
        self.buffer = ""

    def get_dialog(self):
        return self.data.get("store_keeper_msg", "")

    def slow_update(self, speed=1):
        dialog = self.get_dialog()

        if self.dialog_index >= len(dialog):
            return

        now = time.time()

        delay = 0.03 / max(speed, 1)

        if now - self.last_update > delay:
            self.buffer += dialog[self.dialog_index]
            self.dialog_index += 1
            self.last_update = now

    def reset(self):
        self.dialog_index = 0
        self.buffer = ""


def shop(screen, font, inp, data, player):

    items = data["items"]

    for it in items:
        try:
            it["price"] = int(it["price"])
        except:
            it["price"] = 0

        if "description" not in it:
            it["description"] = f"{it.get('emoji','')} {it.get('name','')}"

    state = ShopState(data)
    i = 0

    while True:

        inp.update()
        state.slow_update()

        screen.fill((18, 18, 18))

        pygame.draw.rect(screen, (30, 30, 30), (20, 20, WIDTH - 40, 160))
        pygame.draw.rect(screen, (80, 80, 80), (40, 40, 110, 110))

        name = data.get("store_keeper_name", "Shopkeep")
        screen.blit(font_small.render(name, True, TEXT), (170, 40))

        screen.blit(font_small.render(state.buffer, True, TEXT), (170, 80))

        y = 220

        for idx, it in enumerate(items):

            prefix = "> " if idx == i else "  "

            screen.blit(
                font_small.render(
                    f"{prefix}{it['emoji']} {it['name']} ({it['price']})",
                    True,
                    TEXT
                ),
                (60, y)
            )

            y += 35

        sx = WIDTH - 300
        sy = 220

        for k, v in player.items():
            screen.blit(font_small.render(f"{k}: {v}", True, TEXT), (sx, sy))
            sy += 25

        bar(screen, font_small, "[SPACE/ENTER] Buy | [ESC] Exit")
        pygame.display.flip()

        if inp.pressed(pygame.K_UP):
            i = max(0, i - 1)

        if inp.pressed(pygame.K_DOWN):
            i = min(len(items) - 1, i + 1)

        if inp.confirm():
            it = items[i]

            if player["credits"] >= it["price"]:
                player["credits"] -= it["price"]

                if it["id"] in player:
                    player[it["id"]] += 1

        if inp.pressed(pygame.K_ESCAPE):
            state.reset()
            return



# DEALER NPC

class RouletteKeeper:
    def __init__(self):
        self.name = "The Dealer"
        self.full_text = "Lets go gambling!" if random.randint(1, 256) == 1 else "Yo yo yo spin the hwheel and get a deal of.. yen.... ... Space.. yen..."
        self.visible_text = ""
        self.index = 0
        self.timer = 0
        self.streak = 0

        self.avatar = pygame.Surface((90, 90), pygame.SRCALPHA)

    def set(self, text):
        self.full_text = text
        self.visible_text = ""
        self.index = 0
        self.timer = 0

    def update(self):
        if self.index < len(self.full_text):
            self.timer += 1
            if self.timer % 2 == 0:
                self.visible_text += self.full_text[self.index]
                self.index += 1

    def on_spin(self):

        self.set("SPIN IT!")

    def on_win(self, winnings):
        if winnings > 0:
            self.streak += 1

            if self.streak >= 10:
                self.set(random.choice(["Are you cheating?", "wow", "uhh", "ugh!"]))
            elif self.streak >= 3:
                self.set(random.choice(["Lucky lucky lucky.", "Even crazier space dust.", "Stop winning!", "My boss implemented this thing he calls \"reverse commisions\". So.. like you know... stop?"]))
            else:
                self.set(random.choice([
                    "Ok, I hear you!", 
                    "Winner winner space chicken dinner.", 
                    "Space dust.",
                    "Ding ding ding.",
                    "Breaking News: Moron *ACTUALLY* thinks they might win!",
                    "Totally space awesome."
                ]))
        else:
            self.streak = 0
            self.set(random.choice([
                "You know, when amortized, the likelyhood of you winning is basically zero right?",
                "The first step to recovery is admiting you have a problem.",
                "I hate windows, you know? Like it dark.",
                "I make commission off of this you know?",
                "I was thinking of buying some kind of speed boat? Maybe a star crusier?",
                "I could totally smash a diamond with a hammer.",
                "Keep rolling, maybe you'll win.",
                "Breaking News: World's smartest gambler keeps rolling even though they lost!",
                "Might buy a puppy with that money.",
                "I hear they need work over at the factory.",
                "I can give you loan if you want...",
                "Gonna go zero out the corpos or whatever?",
                "It listens, feels, calls......",
                "Come on Pinky Malinky RUN YOU DUMB HORSE!!"
            ]))

    def on_green(self):
        self.streak += 2
        self.set("...")


def roulette(screen, font, inp, player):

    import pygame
    import random

    W, H = screen.get_size()
    TEXT = (220, 220, 220)

    CURRENCY = "S¥"

    clock = pygame.time.Clock()

    
    # WHEEL (ACCURATE ODDS)
    
    wheel_colors = ["Red", "Black"] * 7 + ["Green"]

    wheel = pygame.image.load("roulette_wheel.jpg").convert_alpha()
    wheel = pygame.transform.smoothscale(wheel, (450, 450))

    colors = ["Red", "Black", "Green"]

    selected_color = 0
    bet_step = 0

    
    # DEALER NPC
    

    keeper = RouletteKeeper()

    
    # DRAW DEALER
    
    def draw_dealer():
        pygame.draw.rect(screen, (35, 35, 35), (40, 40, W - 80, 160))

        pygame.draw.rect(screen, (60, 60, 60), (50, 60, 100, 100))
        screen.blit(keeper.avatar, (55, 65))

        screen.blit(font.render(keeper.name, True, (255, 255, 255)), (170, 60))
        screen.blit(font.render(keeper.visible_text, True, (220, 220, 220)), (170, 110))

    
    # DRAW WHEEL
    
    def draw_wheel(img):
        rect = img.get_rect(center=(W // 2, H // 2))
        screen.blit(img, rect)

    
    # BANKRUPTCY SCREEN
    
    def bankruptcy_screen():
        keeper.set("You've lost everything. The house thanks you for your donation.")

        while True:
            inp.update()
            keeper.update()

            screen.fill((10, 10, 10))
            draw_dealer()

            msg = font.render("YOU ARE BANKRUPT", True, (255, 80, 80))
            screen.blit(msg, msg.get_rect(center=(W // 2, H // 2 - 40)))

            sub = font.render("The house always wins.", True, (200, 200, 200))
            screen.blit(sub, sub.get_rect(center=(W // 2, H // 2)))

            cont = font.render("ENTER/ESC = Exit", True, (180, 180, 180))
            screen.blit(cont, cont.get_rect(center=(W // 2, H // 2 + 60)))

            pygame.display.flip()

            if inp.pressed(pygame.K_ESCAPE):
                return False

            if inp.confirm():
                return False

    
    # MAIN LOOP
    
    while True:

        while True:
            dt = clock.tick(60) / 1000.0
            inp.update()
            keeper.update()

            if inp.pressed(pygame.K_ESCAPE):
                return

            credits = player["credits"]

            bet_percent = (bet_step + 1) * 0.25
            bet_amount = max(1, round(credits * bet_percent))

            screen.fill((20, 20, 20))

            draw_dealer()

            screen.blit(font.render(f"Space Yen: {credits} {CURRENCY}", True, TEXT), (50, 220))
            screen.blit(font.render(f"Bet: {bet_amount} {CURRENCY} ({int(bet_percent*100)}%)", True, TEXT), (50, 260))
            screen.blit(font.render(f"Color: {colors[selected_color]}", True, TEXT), (50, 300))

            screen.blit(
                font.render("LEFT/RIGHT bet | UP/DOWN color | ENTER spin | ESC exit", True, (180, 180, 180)),
                (50, H - 60)
            )

            draw_wheel(wheel)

            pygame.display.flip()

            if inp.pressed(pygame.K_LEFT):
                bet_step = max(0, bet_step - 1)

            if inp.pressed(pygame.K_RIGHT):
                bet_step = min(3, bet_step + 1)

            if inp.pressed(pygame.K_UP):
                selected_color = (selected_color - 1) % len(colors)

            if inp.pressed(pygame.K_DOWN):
                selected_color = (selected_color + 1) % len(colors)

            if inp.confirm():
                if player["credits"] <= 0:
                    if not bankruptcy_screen():
                        return
                    else:
                        break

                keeper.on_spin()
                break

        angle = 0
        spin_speed = random.uniform(25, 35)

        while spin_speed > 0.15:
            inp.update()
            keeper.update()

            if inp.pressed(pygame.K_ESCAPE):
                return

            angle += spin_speed
            spin_speed *= 0.985

            screen.fill((20, 20, 20))

            draw_dealer()
            screen.blit(font.render("SPINNING...", True, (255, 215, 0)), (50, 220))

            draw_wheel(pygame.transform.rotozoom(wheel, angle, 1))

            pygame.display.flip()

        sector_size = 360 / len(wheel_colors)
        sector = int((angle % 360) / sector_size)

        winning_color = wheel_colors[sector]

        credits = player["credits"]
        bet_percent = (bet_step + 1) * 0.25
        bet_amount = max(1, round(credits * bet_percent))

        player["credits"] -= bet_amount

        winnings = 0
        bet_color = colors[selected_color]

        
        # GREEN RULE
        
        if winning_color == "Green":
            if bet_color == "Green":
                winnings = bet_amount * 10
                keeper.on_green()
            else:
                winnings = 0
                keeper.set("Oooh green... you would've won big if you'd picked it.")

        elif winning_color == bet_color:
            winnings = bet_amount * 2
            keeper.on_win(winnings)

        else:
            keeper.on_win(0)

        player["credits"] += winnings

        if player["credits"] <= 0:
            if not bankruptcy_screen():
                return
            continue

        while True:
            inp.update()
            keeper.update()

            if inp.pressed(pygame.K_ESCAPE):
                return

            screen.fill((20, 20, 20))

            draw_dealer()

            if winning_color == "Red":
                win_color = (255, 80, 80)
            elif winning_color == "Black":
                win_color = (200, 200, 200)
            else:
                win_color = (80, 255, 120)

            result = font.render(f"Winner: {winning_color}", True, win_color)
            screen.blit(result, result.get_rect(center=(W // 2, H // 2 - 60)))

            if winnings > 0:
                msg = f"You won {winnings} Space Yen!"
                color = (120, 255, 120)
            else:
                msg = f"You lost {bet_amount} Space Yen!"
                color = (255, 120, 120)

            payout = font.render(msg, True, color)
            screen.blit(payout, payout.get_rect(center=(W // 2, H // 2)))

            cont = font.render("ENTER = Play again | ESC = Exit", True, (180, 180, 180))
            screen.blit(cont, cont.get_rect(center=(W // 2, H // 2 + 80)))

            pygame.display.flip()

            if inp.confirm():
                keeper.set(random.choice([
                    "Weeeeeeellll.....",
                    "Bet bet bet!",
                    "Feind!",
                    "You have a problem dude!",
                    "Ha! Look at this idiot.",
                    "Wanna bet your eye?"
                ]))
                break


def hunting(screen, font, inp, player):

    W, H = screen.get_size()
    TEXT = (220, 220, 220)

    clock = pygame.time.Clock()

    
    # PLAYER
    
    px, py = W // 2, H // 2
    facing_x, facing_y = 0, -1
    player_speed = 150

    bullets = 5
    meat = player.get("food", 0)

    game_over = False

    
    # FOLIAGE
    
    foliage_img = pygame.image.load("foliage.png").convert_alpha()
    foliage = []

    for _ in range(25):
        scale = random.uniform(0.5, 1.2)
        img = pygame.transform.smoothscale(
            foliage_img,
            (int(60 * scale), int(60 * scale))
        )
        foliage.append([random.randint(0, W), random.randint(0, H), img])

    
    # BISON
    
    enemies = []
    for _ in range(20):
        enemies.append([
            random.uniform(0, W),
            random.uniform(0, H),
            random.uniform(-5, 5),
            random.uniform(-5, 5),
            0
        ])

    bullet_list = []

    BOUND = 120

    def dist(ax, ay, bx, by):
        return math.hypot(bx - ax, by - ay)

    
    # MAIN LOOP
    
    while True:
        dt = clock.tick(60) / 1000.0
        inp.update()

        
        # EXIT → GAME OVER (same as bullets = 0)
        
        if inp.pressed(pygame.K_ESCAPE):
            game_over = True

        if bullets <= 0:
            game_over = True

        
        # GAME OVER SCREEN
        
        if game_over:
            while True:
                inp.update()
                screen.fill((0, 0, 0))

                msg = font.render("Hunt Complete", True, (80, 80, 80))
                sub = font.render(f"Meat collected: {meat}", True, TEXT)
                cont = font.render("ESC to exit", True, TEXT)

                screen.blit(msg, msg.get_rect(center=(W//2, H//2 - 40)))
                screen.blit(sub, sub.get_rect(center=(W//2, H//2)))
                screen.blit(cont, cont.get_rect(center=(W//2, H//2 + 40)))

                pygame.display.flip()

                if inp.pressed(pygame.K_ESCAPE):
                    player["food"] = meat
                    return

        
        # PLAYER MOVEMENT
        
        dx = dy = 0

        if inp.down(pygame.K_w): dy -= 1
        if inp.down(pygame.K_s): dy += 1
        if inp.down(pygame.K_a): dx -= 1
        if inp.down(pygame.K_d): dx += 1

        if dx or dy:
            l = math.hypot(dx, dy)
            dx /= l
            dy /= l
            facing_x, facing_y = dx, dy

        px += dx * player_speed * dt
        py += dy * player_speed * dt

        px = max(0, min(W, px))
        py = max(0, min(H, py))

        
        # SHOOT
        
        if inp.pressed(pygame.K_SPACE) and bullets > 0:
            bullet_list.append([
                px + 10, py + 10,
                facing_x * 500,
                facing_y * 500
            ])
            bullets -= 1

        
        # BULLETS MOVE
        
        for b in bullet_list:
            b[0] += b[2] * dt
            b[1] += b[3] * dt

        
        # BISON MOVEMENT (FAST + CHAOTIC HERD)
        
        MAX_SPEED = 55

        for i, e in enumerate(enemies):
            if e[4] == 1:
                continue

            ax, ay, vx, vy, _ = e

            cx = cy = avx = avy = 0
            count = 0

            for j, o in enumerate(enemies):
                if i == j or o[4] == 1:
                    continue

                ox, oy, ovx, ovy, _ = o
                d = dist(ax, ay, ox, oy)

                if d < 100:
                    cx += ox
                    cy += oy
                    avx += ovx
                    avy += ovy
                    count += 1

                if d < 55:
                    vx -= (ox - ax) * 0.06
                    vy -= (oy - ay) * 0.06

            if count > 0:
                cx /= count
                cy /= count
                avx /= count
                avy /= count

                vx += (cx - ax) * 0.0012
                vx += avx * 0.008
                vy += avy * 0.008

            vx += random.uniform(-1.6, 1.6)
            vy += random.uniform(-1.6, 1.6)

            if random.random() < 0.03:
                vx += random.uniform(-8, 8)
                vy += random.uniform(-8, 8)

            if ax < BOUND: vx += 30
            if ax > W - BOUND: vx -= 30
            if ay < BOUND: vy += 30
            if ay > H - BOUND: vy -= 30

            vx *= 0.97
            vy *= 0.97

            speed = math.hypot(vx, vy)
            if speed > MAX_SPEED:
                vx = vx / speed * MAX_SPEED
                vy = vy / speed * MAX_SPEED

            ax += vx * dt
            ay += vy * dt

            e[0], e[1], e[2], e[3] = ax, ay, vx, vy

        
        # BULLET COLLISION (BIGGER HITBOX)
        
        new_bullets = []

        for b in bullet_list:
            hit = False

            for e in enemies:
                if e[4] == 1:
                    continue

                if dist(b[0], b[1], e[0], e[1]) < 28:
                    e[4] = 1
                    meat += 1
                    hit = True
                    break

            if not hit:
                new_bullets.append(b)

        bullet_list = new_bullets

        
        # PLAYER ↔ BISON COLLISION (BIGGER HITBOX)
        
        for e in enemies:
            if e[4] == 1:
                continue

            d = dist(px, py, e[0], e[1])

            if 0 < d < 45:
                px += (px - e[0]) / d * 120 * dt
                py += (py - e[1]) / d * 120 * dt

        
        # DRAW
        
        screen.fill((10, 10, 10))

        for fx, fy, img in foliage:
            screen.blit(img, (fx, fy))

        pygame.draw.rect(screen, (0, 255, 0), (px, py, 20, 20))

        pygame.draw.rect(
            screen,
            (0, 180, 255),
            (px + facing_x * 20, py + facing_y * 20, 6, 6)
        )

        for e in enemies:
            if e[4] == 0:
                pygame.draw.rect(screen, (255, 80, 80), (e[0], e[1], 30, 30))

        for b in bullet_list:
            pygame.draw.rect(screen, (255, 230, 0), (b[0], b[1], 5, 5))

        
        # UI
        
        screen.blit(font.render(f"Bullets: {bullets}", True, TEXT), (20, 20))
        screen.blit(font.render(f"Meat: {meat}", True, TEXT), (20, 50))
        screen.blit(font.render("WASD move | SPACE shoot | ESC exit", True, TEXT), (20, H - 40))

        pygame.display.flip()



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
    title_image = pygame.image.load("TheSpaceTrail.png").convert_alpha()
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
                pygame.quit()

            elif event.type == pygame.KEYDOWN:
                waiting_for_key = False

    while True:

        gen = parser.run_sequence(parser.storyline[state])
        send = None

        try:
            while True:

                inp.update()
                ev = gen.send(send)
                send = None

                if isinstance(ev, parser.Roulette):

                    result = roulette(screen, font_small, inp, parser.player)
                
                
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
                    shop(screen, font, inp, ev.shop_data, parser.player)

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