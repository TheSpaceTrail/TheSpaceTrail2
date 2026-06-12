import pygame
import random

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

    W, H = screen.get_size()
    TEXT = (220, 220, 220)

    CURRENCY = "S¥"

    clock = pygame.time.Clock()

    
    # WHEEL (ACCURATE ODDS)
    
    wheel_colors = ["Red", "Black"] * 7 + ["Green"]

    wheel = pygame.image.load("./assets/roulette_wheel.jpg").convert_alpha()
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