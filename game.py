import pygame
import sys
import random
import math

from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle

#Increase to decrease spanw chance
PARTICLE_SPAWN_RATE = 35000

# This is the main game class. It contains all the game logic.
class Game:
    def __init__(self):
    
        pygame.init()

        self.screen = pygame.display.set_mode((640,480))

        pygame.display.set_caption("Ninja Game")

        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_duration=6),
            'player/run': Animation(load_images('entities/player/run'), img_duration=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_duration=20, loop=False)
        }

        self.player = Player(self, (50,50), (8,15))

        self.tilemap = Tilemap(self, tile_size=16)

        self.tilemap.load('map.json')

        self.scroll = [0, 0]

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep = True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        
        self.particles = []

    # This is the main game loop.
    def run(self):
        while True:

            self.display.blit(self.assets['background'], (0,0))

            self.scroll[0] += (self.player.rect().centerx -  self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery -  self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.leaf_spawners:
                #Control the spawn chance. Bigger spawners have a greater spawn chance
                if random.random() * PARTICLE_SPAWN_RATE < rect.width * rect.height:
                    spawn_pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', spawn_pos, [-0.1, 0.3], frame=random.randint(0, 20)))

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)

            self.tilemap.render(self.display, offset=render_scroll)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
        
                #Particle movement following a sin curve while falling
                if particle.p_type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                    
                #Remove the particle once the animation is complete
                if kill:
                    self.particles.remove(particle)
                

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        self.player.jump()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False


            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))

            # This is the code that makes the game run at 60 frames per second.
            pygame.display.update()
            self.clock.tick(60)

Game().run()
