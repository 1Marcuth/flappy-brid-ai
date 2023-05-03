import pygame, random, neat

ai_playing = True
generation = 0

SCREEN = {
    "width": 500,
    "height": 800
}

imgs = {
    "pipe": pygame.transform.scale2x(pygame.image.load("assets/img/pipe.png")),
    "bg": pygame.transform.scale2x(pygame.image.load("assets/img/bg.png")),
    "base": pygame.transform.scale2x(pygame.image.load("assets/img/base.png")),
    "brid": [
        pygame.transform.scale2x(pygame.image.load("assets/img/bird1.png")),
        pygame.transform.scale2x(pygame.image.load("assets/img/bird2.png")),
        pygame.transform.scale2x(pygame.image.load("assets/img/bird3.png"))
    ]
}

pygame.font.init()
font = pygame.font.Font("assets/fonts/carbon-droid.ttf", 20)

class Bird:
    img = imgs["brid"]
    MAX_ROTATION = 25
    rotation_speed = 20
    annimation_time = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.counter_img = 0
        self.image = self.img[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y
    
    def move(self):
        # Cacular o deslocamento
        self.time += 1
        displacement = 1.5 * (self.time**2) + self.speed * self.time
        # Renstringir o deslocamento
        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -=2
        self.y += displacement
        # Ângulo do pássaro
        if displacement < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.rotation_speed
    def draw(self, screen):
        # Definir imagem
        self.counter_img += 1
        if self.counter_img < self.annimation_time:
            self.image = self.img[0]
        elif self.counter_img < self.annimation_time*2:
            self.image = self.img[1]
        elif self.counter_img < self.annimation_time*3:
            self.image = self.img[2]
        elif self.counter_img < self.annimation_time*4:
            self.image = self.img[1]
        elif self.counter_img >= self.annimation_time*4+1:
            self.image = self.img[0]
            self.counter_img = 0
        # Se o pássaro estiver caindo, ele não pode bater asas
        if self.angle <= -80:
            self.image = self.img[1]
            self.counter_img = self.annimation_time*2
        # Desenhar imagem
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        img_center_position = self.image.get_rect(topleft=(self.x, self.y)).center
        retcangle = rotated_image.get_rect(center=img_center_position)
        screen.blit(rotated_image, retcangle.topleft)
    def get_mask(self):
        return pygame.mask.from_surface(self.image)
class Pipe:
    DISTANCE = 200
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_position = 0
        self.base_position = 0
        self.PIPE_TOP = pygame.transform.flip(imgs["pipe"], False, True)
        self.PIPE_BASE = imgs["pipe"]
        self.passed = False
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top_position = self.height - self.PIPE_TOP.get_height()
        self.base_position = self.height + self.DISTANCE
    
    def move(self):
        self.x -= self.SPEED
    
    def draw(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.top_position))
        screen.blit(self.PIPE_BASE, (self.x, self.base_position))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        base_mask = pygame.mask.from_surface(self.PIPE_BASE)

        top_distance = (self.x - round(bird.x), self.top_position - round(bird.y))
        base_distance = (self.x - round(bird.x), self.base_position - round(bird.y))

        top_point = bird_mask.overlap(top_mask, top_distance)
        base_point = bird_mask.overlap(base_mask, base_distance)

        if top_point or base_point:
            return True
        else:
            return False
class Base:
    SPEED = 5
    WIDTH = imgs["base"].get_width()
    IMAGE = imgs["base"]

    def __init__(self, y):
        self.y = y
        self.x_1 = 0
        self.x_2 = self.WIDTH
    
    def move(self):
        self.x_1 -= self.SPEED
        self.x_2 -= self.SPEED
        #-#-#
        
        if self.x_1 + self.WIDTH < 0:
            self.x_1 = self.x_2 + self.WIDTH
        if self.x_2 + self.WIDTH < 0:
            self.x_2 = self.x_1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x_1, self.y))
        screen.blit(self.IMAGE, (self.x_2, self.y))

def draw_screen(screen, birds, pipes, base, points):
    screen.blit(imgs["bg"], (0, 0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)
    
    points_text = font.render(f"Points: {points}", 1, (255, 255, 255))
    screen.blit(points_text, (SCREEN["width"] - 10 - points_text.get_width(), 10))

    if ai_playing:
        generation_text = font.render(f"Generation: {generation}", 1, (255, 255, 255))
        screen.blit(generation_text, (10, 10))

    base.draw(screen)
    pygame.display.update()

def main(genomes, config): # Fitness Function
    global generation
    generation +=1

    if ai_playing:
        networks = []
        genomes_list = []
        birds = []

        for _, genome in genomes:
            network = neat.nn.FeedForwardNetwork.create(genome, config)
            networks.append(network)
            genome.fitness = 0
            genomes_list.append(genome)
            birds.append(Bird(230, 350))
    else:
        birds = [Bird(230, 350)]

    base = Base(730)
    pipes = [Pipe(600)]
    screen = pygame.display.set_mode((SCREEN["width"], SCREEN["height"]))
    points = 0
    clock = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird")
    pygame.display.set_icon(pygame.image.load("assets/img/bird1.png"))

    running = True
    while running:
        clock.tick(30)
        # Interação com o usuário
        for event in pygame.event.get():
            if not ai_playing:
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or pygame.K_UP:
                        for bird in birds:
                            bird.jump()

        index_pipe = 0
        # Descobrir qual cano olhar
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                index_pipe = 1
        else:
            running = False
            break
        # Mover Objetos
        for i, bird in enumerate(birds):
            bird.move()
            # Aumentar um pouquinho a fintess do pássaro
            genomes_list[i].fitness += 0.1
            output = networks[i].activate((
                bird.y,
                abs(bird.y - pipes[index_pipe].height),
                abs(bird.y - pipes[index_pipe].base_position)))
            # -1 e 1 -> se o output for > 0.5 então o pássaro pula
            if output[0] > 0.5:
                bird.jump()
        base.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                    if ai_playing:
                        genomes_list[i].fitness -= 1
                        genomes_list.pop(i)
                        networks.pop(i)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipes.append(pipe)
        if add_pipe:
            points +=1
            pipes.append(Pipe(random.randint(450, 700)))

        for pipe in remove_pipes:
            pipes.remove(pipe)

            for genome in genomes_list:
                genome.fitness +=5
        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > base.y or bird.y < 0:
                birds.pop(i)
                if ai_playing:
                    genomes_list.pop(i)
                    networks.pop(i)

        draw_screen(screen, birds, pipes, base, points)

def run(file_path_config):
    config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            file_path_config
        )
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    if ai_playing:
        population.run(main, 50)
    else:
        main(None, None)

if __name__ == "__main__":
    run("assets/files/config.txt")