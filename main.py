import sys
import random
import pygame
from pygame.locals import *

# Inisialisasi Pygame dan mixer (untuk musik/suara)
pygame.init()
pygame.mixer.init()

# === MEMUAT GAMBAR ===
# File gambar karakter dan peluru
player_ship = 'plyship.png'
enemy_ship = 'enemyship.png'
ufo_ship = 'ufo.png'
player_bullet = 'pbullet.png'
enemy_bullet = 'enemybullet.png'
ufo_bullet = 'enemybullet.png'

# === MEMUAT SUARA ===
laser_sound = pygame.mixer.Sound('laser.wav')
explosion_sound = pygame.mixer.Sound('low_expl.wav')
go_sound = pygame.mixer.Sound('go.wav')
game_over_sound = pygame.mixer.Sound('game_over.wav')
start_screen_music = 'cyberfunk.mp3'
game_over_music = 'illusoryrealm.mp3'
pygame.mixer.music.load('epicsong.mp3')

# === MENGATUR LAYAR (FULLSCREEN) ===
screen = pygame.display.set_mode((0, 0), FULLSCREEN)
s_width, s_height = screen.get_size()
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
FPS = 60  # Frame Per Second

# === GRUP SPRITE ===
# Mengelompokkan objek agar mudah dikelola dan ditampilkan
background_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
playerbullet_group = pygame.sprite.Group()
enemybullet_group = pygame.sprite.Group()
ufobullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()
sprite_group = pygame.sprite.Group()

# === DATA SOAL MATEMATIKA ===
# Soal dan jawaban benar/salah
questions_and_answers = [
    ("2 + 2 = 4?", True),
    ("5 * 3 = 15?", True),
    ("10 / 2 = 6?", False),
    # ...
]

# === KELAS BACKGROUND BINTANG / PARTICLE ===
class Background(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([x, y])
        self.image.fill((255, 255, 255))  # Putih
        self.image.set_colorkey((0, 0, 0))  # Transparansi
        self.rect = self.image.get_rect()

    def update(self):
        # Partikel bergerak diagonal
        self.rect.y += 1
        self.rect.x += 1
        if self.rect.y > s_height:
            # Reset posisi partikel
            self.rect.y = random.randrange(-10, 0)
            self.rect.x = random.randrange(-400, s_width)

# Versi lebih kecil & acak dari Background
class Particle(Background):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.rect.x = random.randrange(0, s_width)
        self.rect.y = random.randrange(0, s_height)
        self.image.fill((128, 128, 128))  # Abu-abu
        self.vel = random.randint(3, 8)

    def update(self):
        self.rect.y += self.vel
        if self.rect.y > s_height:
            self.rect.x = random.randrange(0, s_width)
            self.rect.y = random.randrange(0, s_height)

# === KELAS PEMAIN ===
class Player(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img).convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey((0, 0, 0))  # Transparansi
        self.alive = True
        self.count_to_live = 0
        self.activate_bullet = True
        self.alpha_duration = 0  # Efek transparan saat respawn

    def update(self):
        if self.alive:
            # Efek transparan saat respawn
            self.image.set_alpha(80 if self.alpha_duration <= 170 else 255)
            self.alpha_duration += 1
            mouse = pygame.mouse.get_pos()
            self.rect.x = mouse[0] - 20
            self.rect.y = mouse[1] + 40
        else:
            # Saat mati, tampilkan ledakan
            self.alpha_duration = 0
            explosion = Explosion(self.rect.x + 20, self.rect.y + 40)
            explosion_group.add(explosion)
            sprite_group.add(explosion)
            pygame.time.delay(22)  # Delay sejenak
            self.rect.y = s_height + 200  # Sembunyikan
            self.count_to_live += 1
            if self.count_to_live > 100:
                self.alive = True
                self.count_to_live = 0
                self.activate_bullet = True

    def shoot(self):
        if self.activate_bullet:
            bullet = PlayerBullet(player_bullet)
            mouse = pygame.mouse.get_pos()
            bullet.rect.x = mouse[0]
            bullet.rect.y = mouse[1]
            playerbullet_group.add(bullet)
            sprite_group.add(bullet)

    def dead(self):
        explosion_sound.play()
        self.alive = False
        self.activate_bullet = False

# === KELAS MUSUH ===
class Enemy(Player):
    def __init__(self, img):
        super().__init__(img)
        self.rect.x = random.randrange(80, s_width - 80)
        self.rect.y = random.randrange(-500, 0)
        self.question, self.answer = random.choice(questions_and_answers)

    def update(self):
        self.rect.y += 1
        if self.rect.y > s_height:
            self.rect.x = random.randrange(80, s_width - 50)
            self.rect.y = random.randrange(-2000, 0)
            self.question, self.answer = random.choice(questions_and_answers)
        self.shoot()

    def shoot(self):
        # Menembak saat di posisi tertentu
        if self.rect.y in (0, 300, 700):
            bullet = EnemyBullet(enemy_bullet)
            bullet.rect.x = self.rect.x + 20
            bullet.rect.y = self.rect.y + 50
            enemybullet_group.add(bullet)
            sprite_group.add(bullet)

# === KELAS UFO (BOS) ===
class Ufo(Enemy):
    def __init__(self, img):
        super().__init__(img)
        self.rect.x = -200
        self.rect.y = 200
        self.move = 1

    def update(self):
        self.rect.x += self.move
        if self.rect.x > s_width + 200 or self.rect.x < -200:
            self.move *= -1
        self.shoot()

    def shoot(self):
        if self.rect.x % 50 == 0:
            bullet = EnemyBullet(ufo_bullet)
            bullet.rect.x = self.rect.x + 50
            bullet.rect.y = self.rect.y + 70
            ufobullet_group.add(bullet)
            sprite_group.add(bullet)

# === KELAS PELURU PEMAIN ===
class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img).convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y -= 18  # Bergerak ke atas
        if self.rect.y < 0:
            self.kill()

# === KELAS PELURU MUSUH ===
class EnemyBullet(PlayerBullet):
    def __init__(self, img):
        super().__init__(img)
        self.image.set_colorkey((255, 255, 255))

    def update(self):
        self.rect.y += 3  # Bergerak ke bawah
        if self.rect.y > s_height:
            self.kill()

# === KELAS LEDAKAN ===
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.img_list = [pygame.transform.scale(pygame.image.load(f'exp{i}.png').convert(), (120, 120)) for i in range(1, 6)]
        for img in self.img_list:
            img.set_colorkey((0, 0, 0))
        self.index = 0
        self.image = self.img_list[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.count_delay = 0

    def update(self):
        self.count_delay += 1
        if self.count_delay >= 12:
            if self.index < len(self.img_list) - 1:
                self.index += 1
                self.image = self.img_list[self.index]
                self.count_delay = 0
            else:
                self.kill()

# === KELAS UTAMA GAME ===
class Game:
    def __init__(self):
        self.count_hit = 0
        self.count_hit2 = 0
        self.lives = 3
        self.score = 0
        self.init_create = True
        self.start_screen()

    def handle_collisions(self):
        # Cek tabrakan peluru dengan musuh
        hits = pygame.sprite.groupcollide(enemy_group, playerbullet_group, False, True)
        for enemy in hits:
            if enemy.answer:
                self.count_hit += 1
                if self.count_hit == 3:
                    self.score += 10
                    explosion = Explosion(enemy.rect.x + 20, enemy.rect.y + 40)
                    explosion_group.add(explosion)
                    sprite_group.add(explosion)
                    enemy.rect.y = random.randrange(-3000, -100)
                    self.count_hit = 0
                    explosion_sound.play()
            else:
                self.score -= 5
                explosion = Explosion(enemy.rect.x + 20, enemy.rect.y + 40)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                enemy.rect.y = random.randrange(-3000, -100)
                explosion_sound.play()

        # Cek tabrakan peluru ke UFO (bos)
        hits2 = pygame.sprite.groupcollide(ufo_group, playerbullet_group, False, True)
        for ufo in hits2:
            self.count_hit2 += 1
            if self.count_hit2 == 5:
                self.score += 20
                explosion = Explosion(ufo.rect.x + 20, ufo.rect.y + 40)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                ufo.rect.x = -200
                self.count_hit2 = 0
                explosion_sound.play()

        # Cek pemain terkena peluru musuh
        if pygame.sprite.spritecollide(self.player, enemybullet_group, True) and self.player.alive:
            self.lives -= 1
            self.player.dead()
            if self.lives == 0:
                self.game_over()

        # Cek pemain terkena peluru UFO
        if pygame.sprite.spritecollide(self.player, ufobullet_group, True) and self.player.alive:
            self.lives -= 1
            self.player.dead()
            if self.lives == 0:
                self.game_over()

    def draw_enemy_questions(self):
        # Menampilkan soal di atas musuh
        font = pygame.font.SysFont('Calibri', 20)
        for enemy in enemy_group:
            question_text = font.render(enemy.question, True, (255, 255, 0))
            screen.blit(question_text, (enemy.rect.x, enemy.rect.y - 25))

    def start_screen(self):
        # Tampilan awal
        pygame.mixer.music.stop()
        pygame.mixer.music.load(start_screen_music)
        pygame.mixer.music.play(-1)
        while True:
            screen.fill((0, 0, 0))
            font = pygame.font.SysFont('Calibri', 50)
            text = font.render('SPACE WAR', True, (0, 0, 255))
            screen.blit(text, text.get_rect(center=(s_width/2, s_height/2)))
            font2 = pygame.font.SysFont('Calibri', 20)
            text2 = font2.render('PROJECT GAME KELOMPOK 7', True, (255, 255, 255))
            screen.blit(text2, text2.get_rect(center=(s_width/2, s_height/2 + 60)))
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_RETURN:
                    self.run_game()
            pygame.display.update()

    def game_over(self):
        # Tampilan ketika game selesai
        pygame.mixer.music.stop()
        game_over_sound.play()
        pygame.mixer.music.load(game_over_music)
        pygame.mixer.music.play(-1)
        font = pygame.font.SysFont('Calibri', 50)
        font_score = pygame.font.SysFont('Calibri', 30)
        while True:
            screen.fill((0, 0, 0))
            text = font.render('GAME OVER', True, (255, 0, 0))
            screen.blit(text, text.get_rect(center=(s_width/2, s_height/2 - 40)))
            score_text = font_score.render(f'Score Akhir: {self.score}', True, (255, 255, 255))
            screen.blit(score_text, score_text.get_rect(center=(s_width/2, s_height/2 + 20)))
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_RETURN:
                    self.__init__()
                    return
            pygame.display.update()

    def run_game(self):
        # Jalankan permainan utama
        pygame.mixer.music.stop()
        go_sound.play()
        pygame.mixer.music.load('epicsong.mp3')
        pygame.mixer.music.play(-1)
        if self.init_create:
            for _ in range(50):
                background_group.add(Background(3, 3))
                particle_group.add(Particle(2, 2))
            self.player = Player(player_ship)
            player_group.add(self.player)
            sprite_group.add(self.player)
            for _ in range(15):
                enemy = Enemy(enemy_ship)
                enemy_group.add(enemy)
                sprite_group.add(enemy)
            ufo = Ufo(ufo_ship)
            ufo_group.add(ufo)
            sprite_group.add(ufo)

        while True:
            screen.fill((0, 0, 0))
            self.handle_collisions()
            sprite_group.draw(screen)
            self.draw_enemy_questions()
            sprite_group.update()
            # HUD (lives dan score)
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, s_width, 30))
            font = pygame.font.SysFont('Calibri', 20)
            screen.blit(font.render(f'Lives: {self.lives}', True, (255, 255, 255)), (20, 0))
            screen.blit(font.render(f'Score: {self.score}', True, (255, 255, 255)), (s_width - 120, 0))
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    laser_sound.play()
                    self.player.shoot()
                    if event.key == K_SPACE:
                        self.init_create = False
                        return
            pygame.display.update()
            clock.tick(FPS)

# === EKSEKUSI PROGRAM ===
if __name__ == "__main__":
    Game()
