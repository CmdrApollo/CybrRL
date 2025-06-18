import random
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
                "", "Lesser ", "Greater "
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
                    "Poison",
                    "Satiate",
                    "Shield",
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
    i = random.randint(0, 2)
    item_type = [Scroll, Potion, Wand][i]
    
    effect = random.randint(0, 11)
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

        self.identified = True

class HeadArmor(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, '^', color)

class LeatherHelmet(HeadArmor):
    def __init__(self):
        super().__init__("Leather Helmet", "A simple helmet made of animal hide.", 'red')

class BodyArmor(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, '%', color)

class LeatherArmor(BodyArmor):
    def __init__(self):
        super().__init__("Leather Armor", "A simple set of armor made of animal hide.", 'red')

class FootArmor(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, '_', color)

class LeatherBoots(FootArmor):
    def __init__(self):
        super().__init__("Leather Boots", "A simple pair of boots made of animal hide.", 'red')

class Ring(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, '=', color)

class MeleeWeapon(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, ']', color)

class IronStaff(MeleeWeapon):
    def __init__(self):
        super().__init__("Iron Staff", "A simple metal rod, used for smacking things.", 'gray')

class Shortsword(MeleeWeapon):
    def __init__(self):
        super().__init__("Shortsword", "A commonplace sword for adventurers.", 'white')

class WoodenStaff(MeleeWeapon):
    def __init__(self):
        super().__init__("Wooden Staff", "A simple wooden rod, used for smacking things.", 'red')

class RangedWeapon(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, ')', color)

class Slingshot(RangedWeapon):
    def __init__(self):
        super().__init__("Slingshot", "A simple device used for launching crude projectiles.", 'magenta')

class Sling(RangedWeapon):
    def __init__(self):
        super().__init__("Sling", "A simple device used since ancient times for launching crude projectiles.", 'gray')

class WoodenBow(RangedWeapon):
    def __init__(self):
        super().__init__("Wooden Bow", "A fairly crude bow. It gets the job done.", 'red')

class WoodenCrossbow(RangedWeapon):
    def __init__(self):
        super().__init__("Wooden Crossbow", "A true feat of modern engineering. Uses a spring mechanism to launch projectiles with significant force.", 'red')

class Ammunition(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, '*', color)

class Rock(Ammunition):
    def __init__(self):
        super().__init__("Rock", "A rock.", 'gray')

class WoodenArrow(Ammunition):
    def __init__(self):
        super().__init__("Wooden Arrow", "A simple wooden arrow.", 'red')

class FoodItem(Item):
    def __init__(self, name, description, color):
        super().__init__(name, description, '"', color)

def generate_random_nonmagical_item():
    all_items = [
        LeatherHelmet, LeatherArmor, LeatherBoots,
        IronStaff, Shortsword, WoodenStaff,
        Slingshot, Sling, WoodenBow, WoodenCrossbow,
        Rock, WoodenArrow
    ]

    return random.choice(all_items)()