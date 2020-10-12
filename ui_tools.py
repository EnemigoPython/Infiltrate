import pygame

# define colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PURPLE = (204, 0, 102)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)
DARK_GREY = (108, 108, 108)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 200, 240)
LIGHT_GREEN = (102, 255, 102)
YELLOW = (255, 255, 54)


class Button:
    def __init__(self, colour, x, y, width, height, text='', txt_size=40, font_type='ariel', shape='rect',
                 sub_shape=None):
        self.colour = colour
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.txt_size = txt_size
        self.font_type = font_type
        self.shape = shape
        self.sub_shape = sub_shape

    def draw(self, screen, outline=None):
        if outline:
            if self.shape == 'rect':
                pygame.draw.rect(screen, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)
            elif self.shape == 'tri':
                if self.sub_shape == 'up':
                    pygame.draw.polygon(screen, outline, (
                        (self.x - 5, self.y + self.height + 2), (self.x + self.width + 5, self.y + self.height + 2),
                        (self.x + (round(self.width / 2)), self.y - 4)), 0)
                elif self.sub_shape == 'down':
                    pygame.draw.polygon(screen, outline, (
                        (self.x - 5, self.y - 2), (self.x + self.width + 5, self.y - 2),
                        (self.x + (round(self.width / 2)), self.y + self.height + 4)), 0)
        if self.shape == 'rect':
            pygame.draw.rect(screen, self.colour, (self.x, self.y, self.width, self.height), 0)
        elif self.shape == 'tri':
            if self.sub_shape == 'up':
                pygame.draw.polygon(screen, self.colour, (
                    (self.x, self.y + self.height), (self.x + self.width, self.y + self.height),
                    (self.x + (round(self.width / 2)), self.y)), 0)
            elif self.sub_shape == 'down':
                pygame.draw.polygon(screen, self.colour, ((self.x, self.y), (self.x + self.width, self.y),
                                                          (self.x + (round(self.width / 2)), self.y + self.height)), 0)
        if self.text != '':
            font = pygame.font.SysFont(self.font_type, self.txt_size)
            text = font.render(self.text, True, BLACK)
            if self.shape == 'rect':
                screen.blit(text, (self.x + round((self.width / 2 - text.get_width() / 2)),
                                   self.y + round((self.height / 2 - text.get_height() / 2))))
            elif self.shape == 'tri':
                if self.sub_shape == 'up':
                    screen.blit(text, (self.x + round((self.width / 2 - text.get_width() / 2)),
                                       self.y + round((self.height / 1.25 - text.get_height() / 2))))
                elif self.sub_shape == 'down':
                    screen.blit(text, (self.x + round((self.width / 2 - text.get_width() / 2)),
                                       self.y + round((self.height / 4 - text.get_height() / 2))))

    def is_over(self, pos):
        if self.shape == 'rect':
            if pos[0] > self.x and pos[0] < self.x + self.width:
                if pos[1] > self.y and pos[1] < self.y + self.height:
                    return True
            return False

        elif self.shape == 'tri':
            if self.sub_shape == 'up':
                if pos[0] > self.x and pos[0] < self.x + self.width:
                    if pos[1] > self.y and pos[1] < self.y + self.height:
                        if abs(self.x + (self.width / 2) - pos[0]) < abs(self.y - pos[1]):
                            return True
                return False
            if self.sub_shape == 'down':
                if pos[0] > self.x and pos[0] < self.x + self.width:
                    if pos[1] > self.y and pos[1] < self.y + self.height:
                        if abs(self.x + (self.width / 2) - pos[0]) < abs(self.y + self.height - pos[1]):
                            return True
                return False


class Scroller:
    def __init__(self, colour, x, y_down, y_up, width, height, min_val=0, max_val=100, adjust=6):
        self.colour = colour
        self.x = x
        self.y_down = y_down
        self.y_up = y_up
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.y = y_up
        self.adjust = adjust

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, (self.x, self.y, self.width, self.height), 0)
        pygame.draw.line(screen, BLACK, (self.x, self.y_down), (self.x, self.y_up), self.adjust)
        pygame.draw.line(screen, BLACK, (self.x + self.width, self.y_down), (self.x + self.width, self.y_up),
                         self.adjust)
        pygame.draw.line(screen, BLACK, (self.x, self.y_down), (self.x + self.width, self.y_down), self.adjust)
        pygame.draw.line(screen, BLACK, (self.x, self.y_up), (self.x + self.width, self.y_up), self.adjust)

    def is_over(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y_up and pos[1] < self.y_down:
                return True
        return False

    def scroll(self, mouseY):
        value = round((self.y + self.adjust - self.y_up) / (self.y_down / self.max_val)) + self.min_val
        if self.y_down - self.height + self.adjust > mouseY > self.y_up + self.adjust:
            self.y = mouseY - self.adjust
        elif mouseY > self.y_down - self.height:
            self.y = self.y_down - self.height
            value = self.max_val
        elif mouseY <= self.y_up:
            self.y = self.y_up
        return value

    def update_y(self, y):
        new_y = int(y * (self.y_down / self.max_val))
        if new_y > self.y_down - self.height:
            self.y = self.y_down - self.height
        elif new_y < self.y_up:
            self.y = self.y_up
        else:
            self.y = new_y
