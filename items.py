from spells import SpellEffects

class MagicalConsumibleItem:
    def __init__(self, name, char, color, description, effect, intensity):
        self.effect = effect
        self.intensity = intensity

        self.id_cost = [2, 1, 3][self.intensity]

        self.name = name
        self.char = char
        self.color = color
        self.description = description

        self.identified = False
    
    def identify(self):
        if not self.identified:
            self.identified = True
            self.name = self.get_fancy_name()
    
    def get_fancy_name(self):
        return f"{self.name} of {
            [
                "", "Lesser ", "Major "
            ][self.intensity]
            }{
                [
                    "Nothingness",
                    "Blink",
                    "Confuse",
                    "Cure Wounds",
                    "Endurance",
                    "Flame",
                    "Focus",
                    "Freeze",
                    "Magic Missile",
                    "Poison",
                    "Satiate",
                    "Shield",
                    "Summon",
                    "Zap",
                ][self.effect]
            }"

class Scroll(MagicalConsumibleItem):
    def __init__(self, effect, intensity):
        super().__init__("Scroll", '?', 'white', "A paper scroll inscribed with some runes.", effect, intensity)

class Potion(MagicalConsumibleItem):
    def __init__(self, effect, intensity):
        super().__init__("Potion", '!', 'cyan', "A magical potion.", effect, intensity)

class Wand(MagicalConsumibleItem):
    def __init__(self, charges, effect, intensity):
        super().__init__("Wand", '/', 'magenta', "A magic wand.", effect, intensity)
        self.charges = charges
    
def generate_random_magical_item():
    import random

    i = random.randint(0, 2)
    item_type = [Scroll, Potion, Wand][i]
    
    effect = random.randint(0, 12)
    intensity = random.randint(0, 2)

    if item_type == Wand:
        item = item_type(random.randint(2, 4), effect, intensity)
    else:
        item = item_type(effect, intensity)

    return item

class Item:
    def __init__(self, name, description, char, color):
        self.name = name
        self.description = description
        self.char = char
        self.color = color

class HeadArmor(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, '*', color)

class BodyArmor(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, '%', color)

class FootArmor(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, '_', color)

class Ring(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, '=', color)