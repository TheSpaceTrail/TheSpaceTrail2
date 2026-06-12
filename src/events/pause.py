import time, json
import pygame

WIDTH = 1280
HEIGHT = 720
TEXT = (235, 235, 235)

bar = None

font_small = pygame.font.SysFont("segoeuiemoji", 22)

class PauseState:
    def __init__(self, database, player):
        self.database = database
        self.player = player
        self.sequence = None
        self.index = None

    def save(self, player, sequence, index):

        with open("./savestate.json", "w") as save:

            json.dump({
                "database": self.database, 
                "player": self.player, 
                "sequence": sequence, 
                "index": index
            }, save)

    def load(self):

        with open("./savestate.json", "w") as save:

            v = json.load(save)

            self.player = v["player"]
            self.database = v["database"]
            self.sequence = v["sequence"]
            self.index = v["index"]

    def reset(self):
        self.dialog_index = 0
        self.buffer = ""


def pause(screen, font, inp, database, player, bar, prompt):

    state = PauseState(database, player)
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



        if inp.confirm():

            return

        if inp.pressed(pygame.K_ESCAPE):
    
            state.save()
            
            return
