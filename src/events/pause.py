import time, json
import pygame
from .. import parser

WIDTH = 1280
HEIGHT = 720
TEXT = (235, 235, 235)

bar = None

font_small = pygame.font.SysFont("segoeuiemoji", 22)

class PauseState:
    def __init__(self, database, player):
        self.database = database
        self.player = player

    def save(self, player):

        print("You tried to save the file")

        with open("./savestate.json", "w") as save:

            print({
                "database": self.database, 
                "player": self.player, 
                })

            json.dump({
                "database": self.database, 
                "player": self.player
            }, save)

    def load(self):

        with open("./savestate.json", "r") as save:

            v = json.load(save)

            self.player = v["player"]
            self.database = v["database"]

            parser.player = self.player
            parser.database = self.database
            

    def reset(self):
        self.dialog_index = 0
        self.buffer = ""


def pause(screen, font, inp, database, player, bar, prompt):

    state = PauseState(database, player)
    i = 0

    print("Du Bist Gut Genug")

    while True:

        inp.update(screen, font, inp, database, player, bar, prompt)
        # state.slow_update()

        screen.fill((18, 18, 18))

        # pygame.draw.rect(screen, (30, 30, 30), (20, 20, WIDTH - 40, 160))
        # pygame.draw.rect(screen, (80, 80, 80), (40, 40, 110, 110))

        bar(screen, font, "PAUSE MENU")

        result = prompt(
            screen, 
            font, 
            inp, 
            "What would you like to do", 
            ["SAVE GAME", "LOAD GAME", "RESUME", "QUIT"],
            None, 
            database, 
            player, 
            bar, 
            (lambda x: ...)
        )

        match result:
            case "SAVE GAME":
                state.save(player)
                bar(screen, font, "Game saved successfully!")
                time.sleep(1)
                return

            case "LOAD GAME":
                state.load()
                bar(screen, font, "Game loaded successfully!")
                time.sleep(1)
                return

            case "RESUME":
                bar(screen, font, "Resuming")
                return

            case "QUIT":
                raise SystemExit

        pygame.display.flip()



        if inp.confirm():

            return

        if inp.pressed(pygame.K_ESCAPE):
    
            state.save()
            
            return
