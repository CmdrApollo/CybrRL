import curses

import tcod.path
import tcod.map
import tcod.constants

from procgen import generate_dungeon

from data import Buffer, Level

import numpy as np
import random
import math
import time

GAMENAME = "Aether Collapse"

end_text = "[ENTER] to continue"

i = input("Window width (leave empty for recommended of 100)? ").lower().strip()
try:
    width = int(i)
except ValueError:
    width = 100
        
i = input("Window height (leave empty for recommended of 40)? ").lower().strip()
try:
    height = int(i)
except ValueError:
    height = 40

class GameScene:
    MAIN_MENU = 0
    PLAYING = 1

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def main(stdscr):
    level_size = (59, 21)

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
        messages.append(": " + text)
        message_colors.append(color)

        while len(messages) > height - gameplay_height - 2:
            messages.pop(0)
            message_colors.pop(0)

    def main_menu():
        choice = 0
        attributes_size = 5
        game_screen = Buffer(gameplay_width - 2, gameplay_height - attributes_size - 2)

        titles = ["Title", "Menu", "", "", ""]

        while True:
            stdscr.clear()
            screen.clear()

            stdscr.subwin(height + 2, width + 2, 0, 0).box()
            stdscr.addstr(0, 1, GAMENAME)

            screen.set_rect(0, 0, game_screen.width + 2, game_screen.height + 2, Colors.WHITE)
            screen.set_text(2, 0, titles[0], Colors.WHITE)

            ay = game_screen.height + 2
            screen.set_rect(0, ay, game_screen.width + 2, attributes_size, Colors.WHITE)
            screen.set_text(2, ay, titles[2], Colors.WHITE)
            ay += 1

            screen.set_rect(gameplay_width, 0, width - gameplay_width, gameplay_height, Colors.WHITE)
            screen.set_text(gameplay_width + 2, 0, titles[1], Colors.WHITE)

            screen.set_rect(0, gameplay_height, gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(2, gameplay_height, titles[3], Colors.WHITE)

            screen.set_rect(gameplay_width, gameplay_height, width - gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(gameplay_width + 2, gameplay_height, titles[4], Colors.WHITE)

            t = "\n".join([
                "   ***********************************   ",
                " *************************************** ",
                "*****        `wAether Collapse`        *****",
                " *************************************** ",
                "   ***********************************   ",
            ])
            tx, ty = game_screen.width // 2 - len(t.splitlines()[0]) // 2, game_screen.height // 2 - len(t.splitlines()) // 2
            game_screen.set_text(tx, ty, t, Colors.CYAN if int(time.time()) & 1 else Colors.BLUE)

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

    def main_game():
        attributes_size = 5

        game_screen = Buffer(gameplay_width - 2, gameplay_height - attributes_size - 2)

        level, player = generate_dungeon(
            15, 4, 6, *level_size
        )

        level.wallify(Colors.WHITE)

        active_visibility = level.visibility.copy()

        solids = None
        empty_solids = None

        titles = ["Floor 1", "Inventory", "Stats", "Messages", "Exploration"]

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

        examining_entity = None

        while True:
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
            screen.set_text(2, 0, titles[0], Colors.WHITE)

            ay = game_screen.height + 2
            screen.set_rect(0, ay, game_screen.width + 2, attributes_size, Colors.WHITE)
            screen.set_text(2, ay, titles[2], Colors.WHITE)
            ay += 1

            screen.set_text(
                1,
                ay,
                "\n".join([
                    f"`aHp`: `g{player.health}`/`g{player.max_health}` `aMp`: `g{player.magic}`/`g{player.max_magic}` `aHg`: `g{player.hunger}` `aInv`: `g{player.capacity}`/`g{player.max_capacity}`",
                    f"`yGold`: `g{player.gold}` `yVision`: `g{player.vision}`",
                ]),
                Colors.WHITE)

            screen.set_rect(gameplay_width, 0, width - gameplay_width, gameplay_height, Colors.WHITE)
            screen.set_text(gameplay_width + 2, 0, titles[1], Colors.WHITE)

            screen.set_rect(0, gameplay_height, gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(2, gameplay_height, titles[3], Colors.WHITE)
            y = 0
            for i, msg in enumerate(messages[::-1]):
                s = split_up(msg, game_screen.width)
                screen.set_text(1, height - 2 - y, s, message_colors[::-1][i])
                y += len(s.splitlines())

            screen.set_rect(gameplay_width, gameplay_height, width - gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(gameplay_width + 2, gameplay_height, titles[4], Colors.WHITE)

            if not menu:
                game_screen.blit_level(active_visibility, level, -cam_x, -cam_y, Colors.GRAY)

                for entity in level.entities:
                    if active_visibility[entity.y * level.width + entity.x]:
                        game_screen.set_at(entity.x - cam_x, entity.y - cam_y, entity.char, entity.color)

                game_screen.set_at(player.x - cam_x, player.y - cam_y, '@', Colors.YELLOW)

                if examining_entity:
                    if examining_entity.health >= examining_entity.max_health * (2 / 3): c = Colors.GREEN
                    elif examining_entity.health >= examining_entity.max_health / 3: c = Colors.YELLOW
                    else: c = Colors.RED
                    game_screen.set_rect(cursor.x - cam_x - 1, cursor.y - cam_y - 1, 3, 3, c)
            
            if show_text:
                text_box(0, 0, game_screen.width, game_screen.height, title, contents, game_screen)

            screen.blit(game_screen, 1, 1)

            screen.put(stdscr, 1, 1, Colors)

            stdscr.refresh()

            # Get user input
            key = stdscr.getch()

            entities_can_go = False

            if menu:
                pass
            else:
                if show_text:
                    if key == ord('\n'):
                        show_text = False
                        examining_entity = None

                    if examining_entity:
                        exam_list = list(filter(lambda e: active_visibility[e.y * level.width + e.x], level.entities))
                        exam_index = exam_list.index(examining_entity)

                        if key == curses.KEY_LEFT:
                            exam_index -= 1
                            if exam_index < 0: exam_index += len(exam_list)
                            examining_entity = exam_list[exam_index]
                            title = examining_entity.name
                            contents = examining_entity.description + f" The {examining_entity.name} has {examining_entity.health}/{examining_entity.max_health} HP."
                            add_message(f"You examine the {examining_entity.name}.")
                        elif key == curses.KEY_RIGHT:
                            exam_index += 1
                            if exam_index >= len(exam_list): exam_index -= len(exam_list)
                            examining_entity = exam_list[exam_index]
                            title = examining_entity.name
                            contents = examining_entity.description + f" The {examining_entity.name} has {examining_entity.health}/{examining_entity.max_health} HP."
                            add_message(f"You examine the {examining_entity.name}.")
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
                    elif key == ord('5'):
                        entities_can_go = True
                    elif key == ord('l'):
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
                                title = closest_entity.name
                                contents = closest_entity.description + f" The {closest_entity.name} has {closest_entity.health}/{closest_entity.max_health} HP."
                                add_message(f"You examine the {closest_entity.name}.")
                                examining_entity = closest_entity
                                cursor.x = examining_entity.x
                                cursor.y = examining_entity.y
                            else:
                                add_message("Alas, there is nothing to examine here.", 'red')
                        else:
                            examining_entity = None

                    if not solids[player.y, player.x]:
                        replace_player = True
                        for entity in level.entities[::-1]:
                            if entity.x == player.x and entity.y == player.y:
                                interaction_type, interaction_data = entity.interact(player)

                                match interaction_type:
                                    case "description":
                                        show_text = True
                                        title = '`c' + entity.name + '`'
                                        contents = entity.description + f" The `c{entity.name}` has `g{entity.health}`/`g{entity.max_health}` HP."
                                        add_message(f"You examine the `c{entity.name}`.")
                                    case "dialogue":
                                        show_text = True
                                        title = entity.name
                                        contents = interaction_data
                                        add_message(f"You speak to the `c{entity.name}`.")
                                    case "attack":
                                        dmg = player.strength + random.randint(-1, 1)
                                        entity.health = max(0, entity.health - (dmg))
                                        if entity.health == 0:
                                            level.entities.remove(entity)
                                            add_message(f"You attack the `c{entity.name}` for `y{dmg}` Hp, killing it!")
                                        else:
                                            add_message(f"You attack the `c{entity.name}` for `y{dmg}` Hp.")
                                    case "swap":
                                        tx, ty = ox, oy
                                        player.x, player.y = entity.x, entity.y
                                        entity.x, entity.y = tx, ty
                                        replace_player = False

                        if replace_player:
                            player.x, player.y = ox, oy
                    elif (ox, oy) != (player.x, player.y):
                        entities_can_go = True

            if key == 27:
                menu = not menu

            if entities_can_go:
                for entity in level.entities:
                    entity.on_my_turn(player, solids)
            
            if examining_entity:
                cursor.x = examining_entity.x
                cursor.y = examining_entity.y

    while True:
        if not main_menu():
            break
        main_game()

if __name__ == '__main__':
    curses.wrapper(main)
