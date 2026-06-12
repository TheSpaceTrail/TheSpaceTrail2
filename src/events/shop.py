import time
import pygame

WIDTH = 1280
HEIGHT = 720
TEXT = (235, 235, 235)

bar = None

font_small = pygame.font.SysFont("segoeuiemoji", 22)

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


def shop(screen, font, inp, data, player, bar):

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

        inp.update(screen, font, inp, database, player, bar, prompt)
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
