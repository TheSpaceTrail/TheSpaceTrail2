import pygame
import random
import math

def huntinga(screen, font, inp, database, player, bar, prompt):

    W, H = screen.get_size()
    TEXT = (220, 220, 220)

    clock = pygame.time.Clock()

    # PLAYER

    px, py = W // 2, H // 2
    facing_x, facing_y = 0, -1
    player_speed = 150

    shots = 20

    start_time = pygame.time.get_ticks()
    TIME_LIMIT = 80  # seconds

    game_over = False
    survived = False

    # ASTEROIDS

    asteroids = []
    spawn_timer = 0

    bullet_list = []

    def dist(ax, ay, bx, by):
        return math.hypot(bx - ax, by - ay)

    # MAIN LOOP

    while True:

        dt = clock.tick(60) / 1000.0
        inp.update(screen, font, inp, database, player, bar, prompt)

        elapsed = (pygame.time.get_ticks() - start_time) / 1000
        time_left = max(0, TIME_LIMIT - elapsed)

        # WIN CONDITION

        if time_left <= 0:
            survived = True
            game_over = True

        # EXIT

        if inp.pressed(pygame.K_ESCAPE):
            return

        # GAME OVER SCREEN

        if game_over:

            while True:

                inp.update(screen, font, inp, database, player, bar, prompt)

                screen.fill((0, 0, 0))

                if survived:
                    msg = font.render("Mission Complete", True, TEXT)
                else:
                    msg = font.render("Destroyed", True, TEXT)

                sub = font.render("ESC to exit", True, TEXT)

                screen.blit(
                    msg,
                    msg.get_rect(center=(W // 2, H // 2 - 20))
                )

                screen.blit(
                    sub,
                    sub.get_rect(center=(W // 2, H // 2 + 20))
                )

                pygame.display.flip()

                if inp.pressed(pygame.K_ESCAPE):
                    return

        # PLAYER MOVEMENT

        dx = dy = 0

        if inp.down(pygame.K_w):
            dy -= 1

        if inp.down(pygame.K_s):
            dy += 1

        if inp.down(pygame.K_a):
            dx -= 1

        if inp.down(pygame.K_d):
            dx += 1

        if dx or dy:

            length = math.hypot(dx, dy)

            dx /= length
            dy /= length

            facing_x = dx
            facing_y = dy

        px += dx * player_speed * dt
        py += dy * player_speed * dt

        px = max(10, min(W - 10, px))
        py = max(10, min(H - 10, py))

        # SHOOT

        if inp.pressed(pygame.K_SPACE) and shots > 0:

            bullet_list.append([
                px,
                py,
                facing_x * 500,
                facing_y * 500
            ])

            shots -= 1

        # BULLETS MOVE

        new_bullets = []

        for b in bullet_list:

            b[0] += b[2] * dt
            b[1] += b[3] * dt

            if -20 < b[0] < W + 20 and -20 < b[1] < H + 20:
                new_bullets.append(b)

        bullet_list = new_bullets

        # ASTEROID SPAWNING

        spawn_timer += dt

        if spawn_timer >= 0.8:

            spawn_timer = 0

            side = random.randint(0, 3)

            if side == 0:
                x = random.randint(0, W)
                y = -30

            elif side == 1:
                x = W + 30
                y = random.randint(0, H)

            elif side == 2:
                x = random.randint(0, W)
                y = H + 30

            else:
                x = -30
                y = random.randint(0, H)

            angle = math.atan2(py - y, px - x)

            speed = random.randint(120, 220)

            asteroids.append([
                x,
                y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.randint(12, 24)
            ])

        # ASTEROID MOVEMENT

        for a in asteroids:

            a[0] += a[2] * dt
            a[1] += a[3] * dt

        # BULLET ↔ ASTEROID COLLISION

        new_asteroids = asteroids[:]
        new_bullets = []

        for b in bullet_list:

            hit = False

            for a in new_asteroids[:]:

                if dist(b[0], b[1], a[0], a[1]) < a[4]:

                    new_asteroids.remove(a)
                    hit = True
                    break

            if not hit:
                new_bullets.append(b)

        bullet_list = new_bullets
        asteroids = new_asteroids

        # PLAYER ↔ ASTEROID COLLISION

        for a in asteroids:

            if dist(px, py, a[0], a[1]) < a[4] + 10:

                survived = False
                game_over = True
                break

        # CLEAN UP FAR AWAY ASTEROIDS

        asteroids = [
            a for a in asteroids
            if -100 < a[0] < W + 100 and -100 < a[1] < H + 100
        ]

        # DRAW

        screen.fill((5, 5, 15))

        # PLAYER

        pygame.draw.rect(
            screen,
            (0, 255, 0),
            (px - 10, py - 10, 20, 20)
        )

        pygame.draw.rect(
            screen,
            (0, 180, 255),
            (
                px + facing_x * 18 - 3,
                py + facing_y * 18 - 3,
                6,
                6
            )
        )

        # ASTEROIDS

        for a in asteroids:

            pygame.draw.circle(
                screen,
                (180, 180, 180),
                (int(a[0]), int(a[1])),
                a[4]
            )

        # BULLETS

        for b in bullet_list:

            pygame.draw.rect(
                screen,
                (255, 230, 0),
                (b[0] - 2, b[1] - 2, 4, 4)
            )

        # UI

        screen.blit(
            font.render(f"Shots: {shots}", True, TEXT),
            (20, 20)
        )

        screen.blit(
            font.render(f"Time: {int(time_left)}", True, TEXT),
            (20, 50)
        )

        screen.blit(
            font.render(
                "WASD move | SPACE shoot | Survive 80s",
                True,
                TEXT
            ),
            (20, H - 40)
        )

        pygame.display.flip()