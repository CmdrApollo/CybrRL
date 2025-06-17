import curses

import tcod.path
import tcod.map
import tcod.constants

from procgen import generate_dungeon
from data import *
from items import MagicalConsumibleItem

status_texts = {
    Status.ONFIRE: "`rBurning`",
    Status.FROZEN: "`cFrozen`",
    Status.SHOCKED: "`yShocked`",
    Status.POISONED: "`mPoisoned`"
}

import numpy as np
import random
import math
import time

GAMENAME = "Aether Collapse"

end_text = "[ENTER] to continue"

print("If the program hangs for a second and does not boot, it is because your terminal doesn't meet the minimum size requirements of 100 columns by 40 rows.")

# i = input("Window width (leave empty for recommended of 100)? ").lower().strip()
# try:
#     width = int(i)
# except ValueError:
width = 100
        
# i = input("Window height (leave empty for recommended of 40)? ").lower().strip()
# try:
#     height = int(i)
# except ValueError:
height = 40

class GameScene:
    MAIN_MENU = 0
    PLAYING = 1

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def main(stdscr):
    level_size = (64, 23)

    gameplay_width, gameplay_height = int(width * (2 / 3)), int(height * (3 / 4))

    curses.start_color()

    # Clear screen
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Don't wait for user input (animations etc)
    stdscr.keypad(True)  # Enable arrow keys
    stdscr.resize(height + 2, width + 2)

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK    )
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK  )
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK   )
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK )
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK   )
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(7, 244, curses.COLOR_BLACK)

    class Colors:
        WHITE = curses.color_pair(0)
        RED = curses.color_pair(1)
        GREEN = curses.color_pair(2)
        BLUE = curses.color_pair(3)
        YELLOW = curses.color_pair(4)
        CYAN = curses.color_pair(5)
        MAGNETA = curses.color_pair(6)
        GRAY = curses.color_pair(7) if curses.can_change_color() and curses.COLORS > 0xff else curses.color_pair(3)

    def split_up(text, size_x=width, size_y=height):
        final = [""]
        for word in text.split():
            if len(final[-1]) + len(word) + 1 >= size_x:
                final.append("")
            final[-1] += word + " "
        return "\n".join(final[:size_y])

    def text_box(x, y, w, h, title, contents, scr):
        text = split_up(contents, w - 2, h) + f"\n{' ' * (w - len(end_text) - 2)}{end_text}"

        scr.set_rect_filled(x, y, w, min(h, len(text.splitlines()) + 2), ' ', Colors.WHITE)
        scr.set_rect(x, y, w, min(h, len(text.splitlines()) + 2), Colors.WHITE)
        scr.set_text(x + w // 2 - len(title) // 2, y, title, Colors.WHITE)
        scr.set_text(x + 1, y + 1, text, Colors.WHITE)

    screen = Buffer(width, height)

    messages = [f"Welcome to {GAMENAME}!"]
    message_colors = [Colors.YELLOW]

    def add_message(text, color='white'):
        carry_color = None
        for line in split_up(": " + text, gameplay_width - 2).splitlines():
            if carry_color:
                line = f'`{carry_color}' + line
                carry_color = None

            has_color = False
            for k, char in enumerate(line):
                if char == '`':
                    has_color = not has_color

                    if has_color:
                        try:
                            carry_color = line[k + 1]
                        except IndexError:
                            pass
            
            if has_color:
                line += '`'

            messages.append(line)
            message_colors.append(color)

        while len(messages) > height - gameplay_height - 2:
            messages.pop(0)
            message_colors.pop(0)

    def main_menu(start_ticks: int):
        choice = 0
        attributes_size = 5
        game_screen = Buffer(gameplay_width - 2, gameplay_height - attributes_size - 2)

        titles = ["Menu", "Choices", "", "", ""]

        while True:
            elapsed_ticks = int(time.time() * 4) - start_ticks
            
            stdscr.clear()
            screen.clear()

            stdscr.subwin(height + 2, width + 2, 0, 0).box()
            stdscr.addstr(0, 1, GAMENAME)

            screen.set_rect(0, 0, game_screen.width + 2, game_screen.height + 2, Colors.WHITE)
            screen.set_text(2, 0, titles[0], Colors.GRAY)

            ay = game_screen.height + 2
            screen.set_rect(0, ay, game_screen.width + 2, attributes_size, Colors.WHITE)
            screen.set_text(2, ay, titles[2], Colors.GRAY)
            ay += 1

            screen.set_rect(gameplay_width, 0, width - gameplay_width, gameplay_height, Colors.WHITE)
            screen.set_text(gameplay_width + 2, 0, titles[1], Colors.GRAY)

            screen.set_rect(0, gameplay_height, gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(2, gameplay_height, titles[3], Colors.GRAY)

            screen.set_rect(gameplay_width, gameplay_height, width - gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(gameplay_width + 2, gameplay_height, titles[4], Colors.GRAY)

            t = "\n".join([
                "   ***********************************   ",
                " *************************************** ",
                "*****        `wAether Collapse`        *****",
                " *************************************** ",
                "   ***********************************   ",
            ])
            tx, ty = game_screen.width // 2 - len(t.splitlines()[0]) // 2, game_screen.height // 2 - len(t.splitlines()) // 2
            game_screen.set_text(tx, ty, t, Colors.CYAN if elapsed_ticks & 4 else Colors.BLUE)

            screen.blit(game_screen, 1, 1)

            ptext = "> Play" if choice == 0 else "  Play"
            screen.set_text(gameplay_width + 1, 1, ptext, Colors.YELLOW if choice == 0 else Colors.WHITE)
            ptext = "> Quit" if choice == 1 else "  Quit"
            screen.set_text(gameplay_width + 1, 2, ptext, Colors.YELLOW if choice == 1 else Colors.WHITE)

            screen.put(stdscr, 1, 1, Colors)

            stdscr.refresh()

            # Get user input
            key = stdscr.getch()
            
            if key == ord('\n'):
                match choice:
                    case 0:
                        return True
                    case 1:
                        return False
            elif key == curses.KEY_UP or key == curses.KEY_DOWN:
                choice = 1 - choice

    def main_game(start_ticks: int):
        attributes_size = 5

        game_screen = Buffer(gameplay_width - 2, gameplay_height - attributes_size - 2)

        level, player = generate_dungeon(
            15, 4, 6, *level_size
        )

        level.wallify(Colors.WHITE)

        active_visibility = level.visibility.copy()

        solids = None
        empty_solids = None

        titles = ["Floor 1", "Backpack", "Stats", "Messages", "Gear"]

        def generate_solids():
            nonlocal solids
            nonlocal empty_solids

            # used for pathfinding and fov
            solids = np.array([[ 1 for _ in range(level.width) ] for _ in range(level.height)])

            empty_solids = solids.copy()

            for x in range(level.width):
                for y in range(level.height):
                    if level.buffer.get(x, y)[0] == '#' or any([e.solid and e.x == x and e.y == y for e in level.entities]):
                        solids[y, x] = 0

        cam_x = 0#player.x - gameplay_width // 2
        cam_y = 0#player.y - (gameplay_height - attributes_size) // 2

        show_text = False

        menu = False

        title = ""
        contents = ""

        cursor = Point(0, 0)
        
        menu_options = [
            "Save & Quit",
            "Quit"
        ]
        menu_choice = 0

        inventory_choice = 0

        gear_choice = 0

        equipping = False
        item_to_equip = None

        examining_entity = None

        replace_player = False

        def interact_with(entity, interaction_type, interaction_data):
            nonlocal show_text, title, contents, replace_player
            match interaction_type:
                case "description":
                    show_text = True
                    title = '`c' + entity.name + '`'
                    contents = entity.description + f" The `c{entity.name}` has `g{entity.health}`/`g{entity.max_health}` Hp."
                    add_message(f"You examine the `c{entity.name}`.")
                case "dialogue":
                    show_text = True
                    title = entity.name
                    contents = interaction_data
                    add_message(f"You speak to the `c{entity.name}`.")
                case "attack":
                    if roll_against(player.calculate_melee_chance()):
                        dmg = player.strength + random.randint(-1, 1)
                        entity.health = max(0, entity.health - (dmg))
                        if entity.health == 0:
                            level.entities.remove(entity)
                            add_message(f"You `yattack` the `c{entity.name}` for `g{dmg}` `aHp`, `rkilling it`!")
                        else:
                            add_message(f"You `yattack` the `c{entity.name}` for `g{dmg}` `aHp`.")
                    else:
                        add_message(f"You `ymiss` the `c{entity.name}`!")
                case "swap":
                    tx, ty = ox, oy
                    player.x, player.y = entity.x, entity.y
                    entity.x, entity.y = tx, ty
                    replace_player = False
                    add_message(f"You swap places with the `c{entity.name}`.")
                case "pickup":
                    add_message(f"You pick up the `c{entity.item.name}`.")
                case "goldpickup":
                    add_message(f"You pick up the `y{entity.amount}` `aGold`.")
                case "pickupfail":
                    add_message(f"You can't pick up the `c{entity.item.name}`!")
                case "dooropen" | "doorclose":
                    return True
                case _:
                    return False
            return True

        identifying = False
        using = False

        def cast_blink(player, target, level, tier):
            distance = [4, 2, 6][tier]

            options = []

            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    if dx == 0 and dy == 0: continue

                    try:
                        if solids[target.y + dy, target.x + dx]:
                            options.append((target.x + dx, target.y + dy))
                    except IndexError:
                        continue
            t = random.choice(options) if len(options) else (target.x, target.y)
            tx, ty = t
            d = abs(tx - target.x) + abs(ty - target.y)
            if (tx, ty) == (target.x, target.y):
                add_message(f"There is nowhere for them to blink to!", 'white')
            else:
                target.x, target.y = tx, ty
                add_message(f"They blink `g{d}` tiles!", 'white')

        def cast_confuse(player, target, level, tier):
            pass

        def cast_cure_wounds(player, target, level, tier):
            amount = [2, 1, 4][tier]
            new_health = min(target.max_health, target.health + amount)
            add_message(f"You cure `g{new_health - target.health}` of their `aHp`.")

        def cast_endurance(player, target, level, tier):
            pass

        def cast_flame(player, target, level, tier):
            pass

        def cast_focus(player, target, level, tier):
            pass

        def cast_freeze(player, target, level, tier):
            pass

        def cast_magic_missile(player, target, level, tier):
            pass

        def cast_poison(player, target, level, tier):
            pass

        def cast_satiate(player, target, level, tier):
            pass

        def cast_shield(player, target, level, tier):
            pass

        def cast_zap(player, target, level, tier):
            pass

        spellbook = {
            "Blink": cast_blink,
            "Confuse": cast_confuse,
            "Cure Wounds": cast_cure_wounds,
            "Endurance": cast_endurance,
            "Flame": cast_flame,
            "Focus": cast_focus,
            "Freeze": cast_freeze,
            "Magic Missile": cast_magic_missile,
            "Poison": cast_poison,
            "Satiate": cast_satiate,
            "Shield": cast_shield,
            "Zap": cast_zap
        }

        def cast_spell(player, target, level, spell_name, tier):
            cast = False
            for k, v in spellbook.items():
                if k in spell_name:
                    add_message(f"You cast `m{k}` on {'the' if target != player else ''} {'`cyourself`' if target == player else f'`c{target.name}`'}!")
                    v(player, target, level, tier)
                    cast = True
            if not cast:
                add_message("Nothing happens...", 'gray')

        while True:
            elapsed_ticks = int(time.time() * 4) - start_ticks

            generate_solids()
            fov = tcod.map.compute_fov(solids, (player.y, player.x), player.vision, algorithm=tcod.constants.FOV_DIAMOND)
            for j in range(level.height):
                for i in range(level.width):
                    if fov[j, i]:
                        active_visibility[j * level.width + i] = True
                        level.set_visibility(i, j, True)
                    else:
                        active_visibility[j * level.width + i] = False

            stdscr.clear()
            screen.clear()
            game_screen.clear()

            stdscr.subwin(height + 2, width + 2, 0, 0).box()
            stdscr.addstr(0, 1, GAMENAME)

            screen.set_rect(0, 0, game_screen.width + 2, game_screen.height + 2, Colors.WHITE)
            screen.set_text(2, 0, titles[0], Colors.GRAY)

            ay = game_screen.height + 2
            screen.set_rect(0, ay, game_screen.width + 2, attributes_size, Colors.WHITE)
            screen.set_text(2, ay, titles[2], Colors.GRAY)
            ay += 1

            screen.set_text(
                1,
                ay,
                "\n".join([
                    f"`aHp`: `g{player.health}`/`g{player.max_health}` `aMp`: `g{player.magic}`/`g{player.max_magic}` `aHg`: `g{player.hunger}` `aCap`: `g{player.capacity}`/`g{player.max_capacity}` `yGold`: `g{player.gold}` `yVision`: `g{player.vision}`",
                    f"`aMelee`: `g{player.calculate_melee_chance()}%` `aBlock`: `g{player.calculate_block_chance()}%` `aRanged`: `g{player.calculate_ranged_chance()}%` `aStealth`: `g{player.calculate_stealth_chance()}%`",
                    " ".join(status_texts[s] for s in sorted(player.statuses))
                ]),
                Colors.WHITE)

            screen.set_rect(gameplay_width, 0, width - gameplay_width, gameplay_height, Colors.WHITE)
            screen.set_text(gameplay_width + 2, 0, titles[1], Colors.GRAY)

            screen.set_rect(0, gameplay_height, gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(2, gameplay_height, titles[3], Colors.GRAY)
            if examining_entity:
                screen.set_text(1, gameplay_height + 1, title + "\n" + split_up(contents, game_screen.width), Colors.WHITE)
            else:
                titles[3] = "Messages"
                y = height - 2
                for i, msg in enumerate(messages[::-1]):
                    s = msg
                    screen.set_text(1, y, s, message_colors[::-1][i])
                    y -= 1

            screen.set_rect(gameplay_width, gameplay_height, width - gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(gameplay_width + 2, gameplay_height, titles[4], Colors.GRAY)
    
            screen.set_text(gameplay_width + 1, gameplay_height + 1, "\n".join([
                f"{"> " if equipping and item_to_equip and gear_choice == 0 else "  "}head: {player.head_equipment.name if player.head_equipment else "none"}",
                f"{"> " if equipping and item_to_equip and gear_choice == 1 else "  "}body: {player.body_equipment.name if player.body_equipment else "none"}",
                f"{"> " if equipping and item_to_equip and gear_choice == 2 else "  "}feet: {player.foot_equipment.name if player.foot_equipment else "none"}",
                "",
                f"{"> " if equipping and item_to_equip and gear_choice == 3 else "  "}ring: {player.left_ring.name if player.left_ring else "none"}",
                f"{"> " if equipping and item_to_equip and gear_choice == 4 else "  "}hand: {player.left_hand_equipment.name if player.left_hand_equipment else "none"}",
                f"{"> " if equipping and item_to_equip and gear_choice == 5 else "  "}ring: {player.right_ring.name if player.right_ring else "none"}",
                f"{"> " if equipping and item_to_equip and gear_choice == 6 else "  "}hand: {player.right_hand_equipment.name if player.right_hand_equipment else "none"}"
            ]), Colors.WHITE)


            if not menu:
                game_screen.blit_level(active_visibility, level, -cam_x, -cam_y, Colors.GRAY)

                for entity in level.entities:
                    if active_visibility[entity.y * level.width + entity.x]:
                        game_screen.set_at(entity.x - cam_x, entity.y - cam_y, entity.char, entity.color)
                    elif isinstance(entity, Door) and level.visibility[entity.y * level.width + entity.x]:
                        game_screen.set_at(entity.x - cam_x, entity.y - cam_y, entity.char, Colors.GRAY)
                    
                game_screen.set_at(player.x - cam_x, player.y - cam_y, '@', Colors.YELLOW)

                if examining_entity:
                    if examining_entity.health >= examining_entity.max_health * (2 / 3): c = Colors.GREEN
                    elif examining_entity.health >= examining_entity.max_health / 3: c = Colors.YELLOW
                    else: c = Colors.RED
                    game_screen.set_rect(cursor.x - cam_x - 1, cursor.y - cam_y - 1, 3, 3, c)

                for i, item in enumerate(player.backpack):
                    text = ("> " if i == inventory_choice and (identifying or using or equipping) else "  ") + item.name + (f' [`y{item.id_cost}` Mp]' if not item.identified else '')
                    screen.set_text(gameplay_width + 1, 1 + i, text, Colors.YELLOW if i == inventory_choice and (identifying or using or equipping) else Colors.WHITE)
            else:
                t = "\n".join([
                    "   ***********************************   ",
                    " *************************************** ",
                    "*****        `wAether Collapse`        *****",
                    " *************************************** ",
                    "   ***********************************   ",
                ])
                tx, ty = game_screen.width // 2 - len(t.splitlines()[0]) // 2, game_screen.height // 2 - len(t.splitlines()) // 2
                game_screen.set_text(tx, ty, t, Colors.CYAN if int(time.time()) & 1 else Colors.BLUE)

                for i, option in enumerate(menu_options):
                    text = ("> " if i == menu_choice else "  ") + option
                    screen.set_text(gameplay_width + 1, 1 + i, text, Colors.YELLOW if i == menu_choice else Colors.WHITE)

            if show_text:
                if examining_entity:
                    titles[3] = "Description"
                else:
                    text_box(0, 0, game_screen.width, game_screen.height, title, contents, game_screen)

            screen.blit(game_screen, 1, 1)

            screen.put(stdscr, 1, 1, Colors)

            stdscr.refresh()

            # Get user input
            key = stdscr.getch()

            entities_can_go = False

            if menu or identifying or using or equipping:
                if identifying or using or (equipping and not item_to_equip):
                    if key == curses.KEY_UP:
                        inventory_choice -= 1
                        if inventory_choice < 0: inventory_choice += len(player.backpack)
                    elif key == curses.KEY_DOWN:
                        inventory_choice = (inventory_choice + 1) % len(player.backpack)
                    elif key == ord('\n'):
                        if identifying:
                            if player.backpack[inventory_choice].identified:
                                add_message(f"The `c{player.backpack[inventory_choice].name}` has already been identified!")
                            else:
                                if player.magic >= player.backpack[inventory_choice].id_cost:
                                    player.magic -= player.backpack[inventory_choice].id_cost
                                    player.backpack[inventory_choice].identify()
                                    add_message(f"You realize that the `c{player.backpack[inventory_choice].name.split()[0]}` is a `m{player.backpack[inventory_choice].name}`!")
                                else:
                                    add_message("You lack the required `aMp` to identify that!")
                            entities_can_go = True
                            identifying = False
                        elif using:
                            # use item

                            item = player.backpack[inventory_choice]

                            if isinstance(item, MagicalConsumibleItem):
                                # cast spell
                                cast_spell(player, examining_entity, level, item.name, item.intensity)
                                show_text = False
                                examining_entity = None
                                player.take_away(item)

                            entities_can_go = True
                            using = False
                        elif equipping:
                            item_to_equip = player.backpack[inventory_choice]
                else:
                    if equipping:
                        if key == curses.KEY_UP:
                            gear_choice -= 1
                            if gear_choice < 0: gear_choice += 7
                        elif key == curses.KEY_DOWN:
                            gear_choice = (gear_choice + 1) % 7
                        elif key == ord('\n'):
                            msg = player.put_gear_in_slot(item_to_equip, gear_choice)
                            if msg:
                                add_message(msg)
                            equipping = False
                    else:
                        if key == curses.KEY_UP:
                            menu_choice -= 1
                            if menu_choice < 0: menu_choice += len(menu_options)
                        elif key == curses.KEY_DOWN:
                            menu_choice = (menu_choice + 1) % len(menu_options)
                        elif key == ord('\n'):
                            pass
            else:
                if show_text:
                    if key == ord('\n'):
                        show_text = False
                        examining_entity = None

                    if examining_entity:
                        exam_list = [player] + list(filter(lambda e: active_visibility[e.y * level.width + e.x], level.entities))
                        exam_index = exam_list.index(examining_entity)

                        if key == curses.KEY_LEFT:
                            exam_index -= 1
                            if exam_index < 0: exam_index += len(exam_list)
                            examining_entity = exam_list[exam_index]
                            title = '`c' + examining_entity.name + '`'
                            contents = examining_entity.description + f" The `c{examining_entity.name}` has `g{examining_entity.health}`/`g{examining_entity.max_health}` Hp."
                            add_message(f"You examine the `c{examining_entity.name}`.")
                        elif key == curses.KEY_RIGHT:
                            exam_index += 1
                            if exam_index >= len(exam_list): exam_index -= len(exam_list)
                            examining_entity = exam_list[exam_index]
                            title = '`c' + examining_entity.name + '`'
                            contents = examining_entity.description + f" The `c{examining_entity.name}` has `g{examining_entity.health}`/`g{examining_entity.max_health}` Hp."
                            add_message(f"You examine the `c{examining_entity.name}`.")
                        elif key == ord('u'):
                            # use
                            if len(player.backpack) and not identifying and not equipping:
                                using = True
                                inventory_choice = 0
                        elif key == ord('x'):
                            show_text = False
                            examining_entity = None
                else:
                    ox, oy = player.x, player.y

                    if key == curses.KEY_UP:
                        player.y = max(0, player.y - 1)
                    elif key == curses.KEY_DOWN:
                        player.y = min(level_size[1] - 1, player.y + 1)
                    elif key == curses.KEY_LEFT:
                        player.x = max(0, player.x - 1)
                    elif key == curses.KEY_RIGHT:
                        player.x = min(level_size[0] - 1, player.x + 1)
                    elif key == ord(' '):
                        # wait
                        entities_can_go = True
                    elif key == ord('x'):
                        # examine
                        if not examining_entity:
                            closest_distance = 0xffff
                            closest_entity = None
                            for entity in level.entities:
                                d = math.sqrt(pow(entity.x - player.x, 2) + pow(entity.y - player.y, 2))
                                if active_visibility[entity.y * level.width + entity.x] and d < closest_distance:
                                    closest_distance = d
                                    closest_entity = entity
                                
                            if closest_entity:
                                show_text = True
                                title = '`c' + closest_entity.name + '`'
                                contents = closest_entity.description + f" The `c{closest_entity.name}` has `g{closest_entity.health}`/`g{closest_entity.max_health}` Hp."
                                add_message(f"You examine the `c{closest_entity.name}`.")
                                examining_entity = closest_entity
                                cursor.x = examining_entity.x
                                cursor.y = examining_entity.y
                            else:
                                show_text = True
                                examining_entity = player
                                cursor.x = examining_entity.x
                                cursor.y = examining_entity.y
                                title = '`c' + examining_entity.name + '`'
                                contents = examining_entity.description + f" The `c{examining_entity.name}` has `g{examining_entity.health}`/`g{examining_entity.max_health}` Hp."
                                add_message(f"You examine the `c{examining_entity.name}`.")
                    elif key == ord('i'):
                        # identify
                        if len(player.backpack) and not using and not equipping:
                            identifying = True
                            inventory_choice = 0
                    elif key == ord('e'):
                        # equip
                        if len(player.backpack) and not identifying and not using:
                            equipping = True
                            item_to_equip = None
                            gear_choice = 0
                    else:
                        for entity in level.entities:
                            for n in [
                                (0, -1),
                                (0, 1),
                                (-1, 0),
                                (1, 0)
                            ]:
                                if entity.x == player.x + n[0] and entity.y == player.y + n[1]:
                                    interaction_type, interaction_data = entity.key_interact(key, player)

                                    if interact_with(entity, interaction_type, interaction_data):
                                        entities_can_go = True
                                        break

                            if entity.x == player.x and entity.y == player.y:
                                interaction_type, interaction_data = entity.direct_key_interact(key, player)

                                if interact_with(entity, interaction_type, interaction_data):
                                    entities_can_go = True
                                    break

                    if not solids[player.y, player.x]:
                        replace_player = True
                        for entity in level.entities[::-1]:
                            if entity.x == player.x and entity.y == player.y:
                                interaction_type, interaction_data = entity.interact(player)

                                if interact_with(entity, interaction_type, interaction_data):
                                    entities_can_go = True
                                    break
                        if replace_player:
                            player.x, player.y = ox, oy
                    elif (ox, oy) != (player.x, player.y):
                        entities_can_go = True

            if key == 27:
                if examining_entity:
                    show_text = False
                    examining_entity = None
                elif identifying or using or equipping:
                    identifying = False
                    using = False
                    equipping = False
                else:
                    menu = not menu

                    if menu:
                        old_titles = titles.copy()
                        titles[0] = "Menu"
                        titles[1] = "Choices"
                    else:
                        titles = old_titles

            if entities_can_go:
                for entity in level.entities[::-1]:
                    entity.on_my_turn(player, solids)
                    
                    if entity.remove:
                        level.entities.remove(entity)
            
            if examining_entity:
                cursor.x = examining_entity.x
                cursor.y = examining_entity.y

    start_ticks = int(time.time() * 4)

    while True:
        if not main_menu(start_ticks):
            break
        main_game(start_ticks)
    
    print("Thank you for playing Aether Collapse!")

if __name__ == '__main__':
    curses.wrapper(main)
