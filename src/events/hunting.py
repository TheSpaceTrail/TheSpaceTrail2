import pygame
import random
import math

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
    
    foliage_img = pygame.image.load("./assets/foliage.png").convert_alpha()
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