import random

class Buffer:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self._buf = [(' ', 0) for _ in range(self.width * self.height)]

    def clear(self):
        self._buf = [(' ', 0) for _ in range(self.width * self.height)]

    def get(self, x, y):
        try:
            return self._buf[y * self.width + x]
        except IndexError:
            pass

    def set_at(self, x, y, char, color):
        try:
            if x > -1 and y > -1 and x < self.width and y < self.height:
                self._buf[y * self.width + x] = (char, color)
        except IndexError:
            pass
    
    def set_text(self, x, y, text, color):
        i = j = 0
        for char in text:
            if char == '\n':
                j += 1
                i = 0
                continue
            self.set_at(x + i, y + j, char, color)
            i += 1

    def set_col(self, x, y, color):
        char = self._buf[y * self.width + x][0]
        self._buf[y * self.width + x] = (char, color)

    def set_rect(self, x, y, w, h, color):
        for i in range(w):
            for j in range(h):
                if (i, j) in [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]:
                    self.set_at(x + i, y + j, '+', color)
                elif i == 0 or i == w - 1:
                    self.set_at(x + i, y + j, '|', color)
                elif j == 0 or j == h - 1:
                    self.set_at(x + i, y + j, '-', color)

    def set_rect_filled(self, x, y, w, h, char, color):
        for i in range(w):
            for j in range(h):
                self.set_at(x + i, y + j, char, color)

    def blit(self, other, x, y):
        for i in range(other.width):
            for j in range(other.height):
                self.set_at(x + i, y + j, *other._buf[j * other.width + i])

    def blit_level(self, active_vis, level, x, y, invisible_color=None):
        for i in range(level.width):
            for j in range(level.height):
                char, color = level.buffer._buf[j * level.width + i]
                if level.visibility[j * level.width + i] and not active_vis[j * level.width + i]:
                    color = invisible_color

                if level.visibility[j * level.width + i]:
                    self.set_at(x + i, y + j, char, color)

    def put(self, stdscr, x, y, colors):
        for j in range(self.height):
            for i in range(self.width):
                c = self._buf[j * self.width + i]
                stdscr.addch(y + j, x + i, c[0], c[1] if type(c[1]) != str else {
                    'white': colors.WHITE,
                    'red': colors.RED,
                    'green': colors.GREEN,
                    'blue': colors.BLUE,
                    'yellow': colors.YELLOW,
                    'cyan': colors.CYAN,
                    'magenta': colors.MAGNETA,
                    'inverse': colors.INVERSE,
                }[c[1]])

class Level:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.buffer = Buffer(width, height)
        self.visibility = [False for _ in range(width * height)]
        self.entities = []
    
    def set_visibility(self, x, y, value):
        self.visibility[y * self.width + x] = value
    
    def wallify(self, color):
        for x in range(self.width):
            for y in range(self.height):
                for n in [(0, -1), (1, -1), (-1, -1), (0, 1), (1, 1), (-1, 1), (-1, 0), (1, 0)]:
                    if 0 <= x + n[0] < self.width and 0 <= y + n[1] < self.height:
                        if self.buffer.get(x + n[0], y + n[1])[0] == '.' and self.buffer.get(x, y)[0] == ' ':
                            self.buffer.set_at(x, y, '#', color)
                            break

class Entity:
    def __init__(self, x, y, name, description, char, color, solid=True, health=1000, max_health=1000):
        self.x = x
        self.y = y
        self.name = name
        self.description = description
        self.char = char
        self.color = color
        self.solid = solid
        
        self.health = health
        self.max_health = max_health

    def interact(self):
        # default interaction
        # tells what the player
        # should do when it bump
        # attacks this entity,
        # in this case, show its
        # description
        return ("description", None)

class NPC(Entity):
    def __init__(self, x, y, name, description, dialogue, char, color):
        super().__init__(x, y, name, description, char, color)
        self.dialogue = dialogue
    
    def interact(self):
        return ("dialogue", self.dialogue)

class MangledKobold(NPC):
    def __init__(self, x, y):
        super().__init__(x, y, "Mangled Kobold", "Before you, you see a Kobold who has been mangled by cybernetic enhancments; almost to the point of no recognition. You wonder if the poor creature is still whole beneath all of the technology that engulfs its small body. They grunt at you annoyedly.", "The kobold groans to life, machines sputtering as they do so. \"Go away,\" they tell you in a dry voice.", 'k', 'cyan')

class Enemy(Entity):
    def __init__(self, x, y, name, description, health, damage, char, color):
        super().__init__(x, y, name, description, char, color, health, health)
        self.damage = damage
    
    def interact(self):
        x = self.damage + random.randint(-1, 1)
        return ("attack", f"{self.name} attacks you for {x} damage!")
    
class Kobold(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "Kobold", "This small, draconic creature bears striking resemblence to the dragons of the days of yore. Or so you've been told.", 10, 3, 'k', 'red')