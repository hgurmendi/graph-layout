#! /usr/bin/python

'''
Complementos de Matematica I
Trabajo practico de laboratorio
Graph Layout usando el metodo de Fruchterman-Reingold

Dependencias:
 * pyeuclid     https://code.google.com/p/pyeuclid/
 * pygame       http://www.pygame.org/

'''

import sys, pygame, random, math, os
from pygame.locals import *
from euclid import *

def read_graph(input_file=""):
    V = []
    E = []
    
    f = open(input_file, "r")
    
    count = int(f.readline())
    
    print "Leyendo " + input_file
    
    for i in range(count):
        V.append(f.readline().strip())
        
    for line in f:
        E.append(line.strip().split(" ", 2))
    
    return (V, E)

class LayoutGraph():

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    
    START_TEMPERATURE = 100
    
    MAX_FPS = 60
    TICKS_PER_FRAME = 1000 / MAX_FPS
    TICKS_PER_SECOND = 1000
    
    NODE_RADIUS = 8
    
    FONT_SIZE = 20

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    FONT_COLOR = (255, 255, 0)
    NODE_COLOR = (255, 0, 0)
    EDGE_COLOR = (255, 255, 255)
    
    TEMPERATURE_FACTOR = 0.95
    
    INITIAL_TEMPERATURE = SCREEN_WIDTH / 10

    def __init__(self, filename, grafo, iters, refresh, c_a, c_r):
        self.filename = filename
        
        self.grafo = grafo
        
        # Posiciones de los vertices.
        self.pos = {}
        
        self.temperature = self.INITIAL_TEMPERATURE
        
        self.iters = iters
        self.refresh = refresh
        
        # Constante de atraccion.
        self.c_a = c_a
        
        # Constante de repulsion.
        self.c_r = c_r
        
        # Variables para calculo y control de los fps.
        self.fps_count = 0
        self.fps_timer = 0
        self.fps_last = 0
        self.fps = 0
        
        self.step_timer = 0
        self.iters_counter = 0
        
        # Inicializa pygame.
        pygame.init()
        
        # Inicializa la pantalla.
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Graph Layout")
        
        V, E = self.grafo
        
        # Inicializa las etiquetas de los nodos.
        self.label = {}
        self.font = pygame.font.Font(None, self.FONT_SIZE)
        for node in V:
            self.label[node] = self.font.render(node, 1, self.FONT_COLOR)
        
        self.reset()
        
    # Distribuye los nodos aleatoriamente en la pantalla y reinicia la temperatura del sistema.
    def reset(self):
        V, E = self.grafo
        
        for node in V:
            x = random.randint(0, self.SCREEN_WIDTH)
            y = random.randint(0, self.SCREEN_HEIGHT)
            self.pos[node] = Vector2(x, y)
        
        self.temperature = self.INITIAL_TEMPERATURE
        self.step_timer = pygame.time.get_ticks()
        self.iters_counter = 0

    # Maneja apropiadamente los eventos de teclado.
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                elif event.key == K_r:
                    self.reset()
                    self.draw_frame()
                elif event.key == K_RETURN:
                    self.step()
    
    def draw_frame(self):
        V, E = self.grafo
        
        self.screen.fill(self.BLACK)
        
        # Dibuja texto 
        text_title = self.font.render("Complementos de Matematica I - Graph Layout", 1, self.WHITE)
        text_file = self.font.render("file: " + os.path.realpath(self.filename), 1, self.WHITE)
        text_fps = self.font.render("fps: " + str(self.fps) + " (max " + str(self.MAX_FPS) + ")", 1, self.WHITE)
        text_iters = self.font.render("iteraciones: " + str(self.iters_counter) + "/" + str(self.iters), 1, self.WHITE)
        text_temp = self.font.render("temperatura: " + str(self.temperature), 1, self.WHITE)

        text_commands = self.font.render("Comandos: ", 1, self.WHITE)
        text_r_key = self.font.render("R - Reiniciar layout", 1, self.WHITE)
        text_esc_key = self.font.render("ESC - Salir", 1, self.WHITE)
        text_enter_key = self.font.render("ENTER - Realizar una iteracion", 1, self.WHITE)
        
        next_line = 5
        self.screen.blit(text_title, (5, next_line))
        
        next_line += 10 + text_title.get_height()
        self.screen.blit(text_file, (5, next_line))
        
        next_line += text_file.get_height()
        self.screen.blit(text_fps, (5, next_line))
        
        next_line += text_fps.get_height()
        self.screen.blit(text_iters, (5, next_line))
        
        next_line += text_iters.get_height()
        self.screen.blit(text_temp, (5, next_line))
        
        next_line = self.SCREEN_HEIGHT - 5 - text_r_key.get_height()
        self.screen.blit(text_r_key, (5, next_line))
        
        next_line -= text_esc_key.get_height()
        self.screen.blit(text_esc_key, (5, next_line))
        
        next_line -= text_enter_key.get_height()
        self.screen.blit(text_enter_key, (5, next_line))

        next_line -= text_commands.get_height()
        self.screen.blit(text_commands, (5, next_line))
        
        # Dibuja el centro de la pantalla.
        pygame.draw.aaline(self.screen,
            self.BLUE,
            (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 - 10),
            (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 10))
        
        pygame.draw.aaline(self.screen,
            self.BLUE,
            (self.SCREEN_WIDTH / 2 - 10, self.SCREEN_HEIGHT / 2),
            (self.SCREEN_WIDTH / 2 + 10, self.SCREEN_HEIGHT / 2))
            
        # Dibuja las aristas.
        for edge in E:
            node1 = edge[0]
            node2 = edge[1]
            
            pygame.draw.aaline(self.screen,
                self.EDGE_COLOR,
                (self.pos[node1].x, self.pos[node1].y),
                (self.pos[node2].x, self.pos[node2].y))
        
        # Dibuja los vertices
        for node in V:
            pygame.draw.circle(self.screen,
                self.NODE_COLOR,
                (int(self.pos[node].x), int(self.pos[node].y)),
                self.NODE_RADIUS,
                0
                )
            
            label_pos = self.label[node].get_rect()
            label_pos.centerx = self.pos[node].x
            label_pos.centery = self.pos[node].y
            self.screen.blit(self.label[node], label_pos)
            
        pygame.display.flip()
        
    def layout(self):
        while True:
            self.handle_events()
            
            # Limitar los cuadros dibujados por segundo.
            if pygame.time.get_ticks() - self.fps_last >= self.TICKS_PER_FRAME:
                # Dibuja el cuadro
                self.draw_frame()
                
                self.fps_count += 1
                
                # Actualizar contador de fps.
                tmp = pygame.time.get_ticks()
                if tmp - self.fps_timer > self.TICKS_PER_SECOND:
                    self.fps = self.fps_count
                    self.fps_count = 0
                    self.fps_timer = tmp
                
                # Realizar una iteracion adicional.
                if self.iters_counter < self.iters:
                    tmp = pygame.time.get_ticks()
                    if tmp - self.step_timer > self.refresh:
                        self.step()
                        self.step_timer = tmp
                
                self.fps_last = pygame.time.get_ticks()
    
    # Realiza una iteracion del algoritmo
    def step(self):
        V, E = self.grafo

        # Desplazamiento de los vertices.
        disp = {}
        
        # Inicializacion del desplazamiento de los vertices en 0.
        for node in V:
            disp[node] = Vector2(0, 0)
        
        # Fuerza de repulsion ejercida SOBRE node1 POR node2
        for node1 in V:
            for node2 in V:
                if node1 != node2:  
                    # Vector node1->node2.
                    vec = self.pos[node2] - self.pos[node1]
                    
                    # Distancia entre ambos vertices.
                    dist = vec.magnitude()
                    
                    # Calculo de la fuerza de repulsion.
                    fz_r = self.c_r / dist

                    vec.normalize()
                    
                    # Calculo del vector de repulsion.
                    vec = vec * fz_r * -1
                    
                    # Se agrega al desplazamiento del vertices.
                    disp[node1] += vec
     
        
        # Las fuerzas de atraccion se dan entre los vertices adyacentes.
        for edge in E:
            node1 = edge[0]
            node2 = edge[1]
            
            # Vector node1->node2.
            vec = self.pos[node2] - self.pos[node1]
            
            # Distancia entre ambos vertices.
            dist = vec.magnitude()
            
            # Calculo de la fuerza de atraccion.
            fz_a = self.c_a * dist**2
            
            vec.normalize()
            
            # Calculo del vector de atraccion.
            vec *= fz_a
            
            # Se agrega al desplazamiento de cada uno de los vertices involucrados.
            disp[node1] += vec
            disp[node2] -= vec

        # La fuerza de gravedad afecta a todos los vertices, atrayendolos
        # al centro de la pantalla con una fuerza relativamente leve.
        center = Vector2(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2)
        
        for node in V:
            # Vector node->center.
            vec = center - self.pos[node]
            
            # Distancia entre el centro y el vertice.
            dist = vec.magnitude()
            
            # Calculo de la fuerza de atraccion gravitatoria.
            fz_gr = self.c_a / 8 * dist**2
            
            vec.normalize()
            
            # Calculo del vector de atraccion gravitatoria.
            vec *= fz_gr
            
            # Se agrega al desplazamiento del vertice.
            disp[node] += vec

        # Los vertices se mueven de acuerdo con el desplazamiento.
        for node in V:
            # Limito el desplazamiento con la temperatura.
            if disp[node].magnitude() > self.temperature:

                disp[node].normalize()
                disp[node] *= self.temperature
            
            self.pos[node] += disp[node]
            
            # Los vertices no se pueden dibujar fuera de la pantalla.
            if self.pos[node].x >= self.SCREEN_WIDTH:
                self.pos[node].x = self.SCREEN_WIDTH
                
            if self.pos[node].x < 0:
                self.pos[node].x = 0
            
            if self.pos[node].y >= self.SCREEN_HEIGHT:
                self.pos[node].y = self.SCREEN_HEIGHT
            
            if self.pos[node].y < 0:
                self.pos[node].y = 0
            
        # Baja la temperatura luego de cada iteracion.
        self.temperature *= self.TEMPERATURE_FACTOR
        
        self.iters_counter += 1
            
def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        print "USAGE: " + sys.argv[0] + " <graph-file>"
        sys.exit(1)
    
    G = read_graph(input_file)
    
    # Las constantes de atraccion y repulsion fueron determinadas empiricamente.
    layout_gr = LayoutGraph(filename=input_file,
        grafo=G,
        iters=150,
        refresh=100,
        c_a=0.01,
        c_r=3500.0
        )
    
    layout_gr.layout()

if __name__ == "__main__":
    main()
