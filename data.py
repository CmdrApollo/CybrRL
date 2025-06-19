import random
from items import *

class Status:
    ONFIRE = "fire"
    FROZEN = "ice"
    SHOCKED = "shock"
    POISONED = "poison"
    CONFUSED = "confuse"

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
        c = color
        cont = True
        for char in text:
            if char == '`':
                if c == color:
                    cont = False
                c = color
                continue
            if cont:
                if char == '\n':
                    j += 1
                    i = 0
                    continue
                self.set_at(x + i, y + j, char, c)
                i += 1
            else:
                if char in {
                    'w': 'white',
                    'r': 'red',
                    'g': 'green',
                    'b': 'blue',
                    'y': 'yellow',
                    'c': 'cyan',
                    'm': 'magenta',
                    'a': 'gray'
                }:
                    c = {
                        'w': 'white',
                        'r': 'red',
                        'g': 'green',
                        'b': 'blue',
                        'y': 'yellow',
                        'c': 'cyan',
                        'm': 'magenta',
                        'a': 'gray'
                    }[char]
                else:
                    c = 'white'
                cont = True

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
                    'magenta': colors.MAGENTA,
                    'gray': colors.GRAY,
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

        self.remove = False

        self.statuses = []
        self.resistances = {
            Status.ONFIRE: False, # fire
            Status.FROZEN: False, # ice
            Status.SHOCKED: False, # shock
            Status.POISONED: False, # poison
            Status.CONFUSED: False, # confuse
        }

        self.can_move = False
    
    def add_status(self, status: str, amount: int):
        if not self.resistances[status]:
            self.statuses.append((status, amount))
            return None
        return f"The `c{self.name}` resists that status effect!"

    def has_status(self, s: str):
        for status in self.statuses:
            if s == status[0]:
                return True
        return False
    
    def on_my_turn(self, player, solids):
        pass

    def direct_key_interact(self, key, player):
        return ("none", None)

    def key_interact(self, key, player):
        return ("none", None)

    def interact(self, player):
        # default interaction
        # tells what the player
        # should do when it bump
        # attacks this entity,
        # in this case, show its
        # description
        return ("description", None)

class Door(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, "Door", "A simple wooden door.", '+', 'red', True, 10, 10)
        self.open = False

        self.resistances = {
            Status.ONFIRE: False, # fire
            Status.FROZEN: True, # ice
            Status.SHOCKED: True, # shock
            Status.POISONED: True, # poison
            Status.CONFUSED: True, # confuse
        }

    def key_interact(self, key, player):
        if key == ord('c'):
            self.open = False
            self.solid = not self.open
            self.char = '+' if not self.open else '/'
            return ("doorclose", None)
        return ("none", None)
    
    def interact(self, player):
        self.open = True
        self.solid = not self.open
        self.char = '+' if not self.open else '/'
        
        return ("dooropen", None)

class SpellTarget(Entity):
    def __init__(self, x, y, name, description, char, color, solid=True, health=1000, max_health=1000):
        super().__init__(x, y, name, description, char, color, solid, health, max_health)
        self.magic = self.max_magic = 10
        self.capacity, self.max_capacity = 0, 16

        self.hunger = 0

        self.vision = 5

        self.gold = 0

        self.melee = 5
        self.block = 0
        self.ranged = 5
        self.stealth = 0

        self.modifiers = []

        self.backpack = []

        self.can_move = True

        self.statuses = []

class Player(SpellTarget):
    def __init__(self, x, y):
        super().__init__(x, y, "You", "Yourself.", '@', 'yellow', health=10, max_health=10)
        self.strength = 2
    
        self.head_equipment = None
        self.body_equipment = None
        self.foot_equipment = None

        self.left_ring = None
        self.left_hand_equipment = None
        self.right_ring = None

        self.right_hand_equipment = None

        self.can_move = True

    def calculate_melee_chance(self):
        return self.melee * 10

    def calculate_block_chance(self):
        return self.block * 10

    def calculate_ranged_chance(self):
        return self.ranged * 10

    def calculate_stealth_chance(self):
        return self.stealth * 10

    def give(self, item):
        if self.capacity < self.max_capacity:
            self.backpack.append(item)
            self.capacity += 1
            return True
        return False

    def take_away(self, item):
        self.backpack.remove(item)
        self.capacity -= 1

    def put_gear_in_slot(self, item, slot):
        fail_message = "You can't equip that item in that slot."
        match slot:
            case 0:
                if isinstance(item, HeadArmor):
                    if self.head_equipment:
                        self.backpack.append(self.head_equipment)
                    self.head_equipment = item
                else:
                    return fail_message
            case 1:
                if isinstance(item, BodyArmor):
                    if self.body_equipment:
                        self.backpack.append(self.body_equipment)
                    self.body_equipment = item
                else:
                    return fail_message
            case 2:
                if isinstance(item, FootArmor):
                    if self.foot_equipment:
                        self.backpack.append(self.foot_equipment)
                    self.foot_equipment = item
                else:
                    return fail_message
            case 3:
                if isinstance(item, Ring):
                    if self.left_ring:
                        self.backpack.append(self.left_ring)
                    self.left_ring = item
                else:
                    return fail_message
            case 4:
                if self.left_hand_equipment:
                    self.backpack.append(self.left_hand_equipment)
                self.left_hand_equipment = item
            case 5:
                if isinstance(item, Ring):
                    if self.right_ring:
                        self.backpack.append(self.right_ring)
                    self.right_ring = item
                else:
                    return fail_message
            case 6:
                if self.right_hand_equipment:
                    self.backpack.append(self.right_hand_equipment)
                self.right_hand_equipment = item
        
        self.backpack.remove(item)

class NPC(SpellTarget):
    def __init__(self, x, y, name, description, dialogue, char, color):
        super().__init__(x, y, name, description, char, color, health=5, max_health=5)
        self.dialogue = dialogue
    
    def on_my_turn(self, player, solids):
        if self.has_status(Status.FROZEN) or self.has_status(Status.SHOCKED):
            return
        
        n = random.choice([
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0)
        ])

        self.x += n[0]
        self.y += n[1]

        if not solids[self.y, self.x] or (self.x == player.x and self.y == player.y):
            self.x -= n[0]
            self.y -= n[1]
    
    def interact(self, player):
        return ("swap", None)

class MangledKobold(NPC):
    def __init__(self, x, y):
        super().__init__(x, y, "Mangled Kobold", "Before you, you see a Kobold who has been mangled by cybernetic enhancments; almost to the point of no recognition. You wonder if the poor creature is still whole beneath all of the technology that engulfs its small body. They grunt at you annoyedly.", "The kobold groans to life, machines sputtering as they do so. \"Go away,\" they tell you in a dry voice.", 'k', 'cyan')

class Enemy(SpellTarget):
    def __init__(self, x, y, name, description, health, damage, char, color):
        super().__init__(x, y, name, description, char, color, True, health, health)
        self.damage = damage
    
    def interact(self, player):
        return ("attack", None)
    
class HumanoidEnemy(Enemy):
    def __init__(self, x, y, name, description, health, damage, color):
        super().__init__(x, y, name, description, health, damage, '@', color)
    
class Goblin(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "Goblin", "A medium-sized, green, humanoid creature. Generally known for their hostility and shady business tactics.", 6, 2, 'g', 'green')
        
class Kobold(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "Kobold", "This small, draconic creature bears striking resemblence to the dragons of the days of yore. Or so you've been told.", 5, 2, 'k', 'red')

class Bat(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "Bat", "This blood-sucking creature flies silently throughout the dungeon, awaiting its next victim.", 4, 1, 'b', 'magenta')

class Skeleton(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "Skeleton", "This undead creature roams the halls of the dungeon searching for revenge.", 6, 3, 'Z', 'white')

        self.resistances = {
            Status.ONFIRE: False, # fire
            Status.FROZEN: False, # ice
            Status.SHOCKED: False, # shock
            Status.POISONED: True, # poison
            Status.CONFUSED: False, # confuse
        }

class ItemHolder(Entity):
    def __init__(self, x, y, item: Item):
        super().__init__(x, y, item.name, item.description, item.char, item.color, False, 10, 10)
        self.item = item

    def direct_key_interact(self, key, player):
        if key == ord('g'):
            if player.give(self.item):
                self.remove = True
                return ("pickup", None)
            return ("pickupfail", None)
        return ("none", None)
    
class GoldPickup(Entity):
    def __init__(self, x, y, amount: int):
        super().__init__(x, y, "Gold", "Gold nugget(s) that act as the common currency for societies throughout the world.", '$', 'yellow', False, 10, 10)
        self.amount = amount

    def direct_key_interact(self, key, player):
        if key == ord('g'):
            player.gold += self.amount
            self.remove = True
            return ("goldpickup", None)
        return ("none", None)

def roll_against(x: int) -> bool:
    return random.randint(1, 100) <= x