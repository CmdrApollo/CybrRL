import curses

import tcod.path
import tcod.map
import tcod.constants

from procgen import generate_dungeon

from data import Buffer, Level

import numpy as np

import random

GAMENAME = "Aether Collapse"

end_text = "[ENTER] to continue"

BIG_WINDOW = None

while True:
    i = input("Big or Small Terminal (0=Big, 1=Small)? ").lower().strip()
    if i == '0':
        BIG_WINDOW = True
        break
    elif i == '1':
        BIG_WINDOW = False
        break

class GameScene:
    MAIN_MENU = 0
    PLAYING = 1

def main(stdscr):
    level_size = (100, 50)

    if BIG_WINDOW:
        width, height = 120, 35
        gameplay_width, gameplay_height = 80, 25
    else:
        width, height = 80, 25
        gameplay_width, gameplay_height = 60, 18

    curses.start_color()

    # Clear screen
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(False)  # Wait for user input
    stdscr.keypad(True)  # Enable arrow keys
    stdscr.resize(height + 2, width + 2)

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    class Colors:
        WHITE = curses.color_pair(0)
        RED = curses.color_pair(1)
        GREEN = curses.color_pair(2)
        BLUE = curses.color_pair(3)
        YELLOW = curses.color_pair(4)
        CYAN = curses.color_pair(5)
        MAGNETA = curses.color_pair(6)
        INVERSE = curses.color_pair(7)

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

        while True:
            stdscr.clear()
            screen.clear()

            stdscr.subwin(height + 2, width + 2, 0, 0).box()
            stdscr.addstr(0, 1, GAMENAME)

            t = "\n".join([
                "   ***********************************   ",
                " *************************************** ",
                "*****        Aether Collapse        *****",
                " *************************************** ",
                "   ***********************************   ",
            ])
            tx, ty = width // 2 - len(t.splitlines()[0]) // 2, height // 4 - len(t.splitlines()) // 2
            screen.set_text(tx, ty, t, Colors.WHITE)

            ptext = "> Play" if choice == 0 else "  Play"
            screen.set_text(width // 2 - len(ptext) // 2, height // 2, ptext, Colors.WHITE)
            ptext = "> Quit" if choice == 1 else "  Quit"
            screen.set_text(width // 2 - len(ptext) // 2, height // 2 + 1, ptext, Colors.WHITE)

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
        game_screen = Buffer(gameplay_width - 2, gameplay_height - 2)

        level, player = generate_dungeon(
            15, 4, 6, *level_size
        )

        level.wallify(Colors.WHITE)

        active_visibility = level.visibility.copy()

        solids = None
        empty_solids = None

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

        cam_x = player.x - gameplay_width // 2
        cam_y = player.y - gameplay_height // 2

        show_text = False

        title = ""
        contents = ""

        while True:
            generate_solids()
            fov = tcod.map.compute_fov(solids, (player.y, player.x), 4, algorithm=tcod.constants.FOV_DIAMOND)
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

            screen.set_rect(0, 0, gameplay_width, gameplay_height, Colors.WHITE)
            screen.set_text(1, 0, "Game", Colors.WHITE)
            screen.set_rect(gameplay_width, 0, width - gameplay_width, gameplay_height, Colors.WHITE)
            screen.set_text(gameplay_width + 1, 0, "Stats", Colors.WHITE)
            screen.set_text(gameplay_width + 1, 1, f"HP: {player.health}/{player.max_health}", Colors.WHITE)

            screen.set_rect(0, gameplay_height, gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(1, gameplay_height, "Messages", Colors.WHITE)
            y = 0
            for i, msg in enumerate(messages[::-1]):
                s = split_up(msg, game_screen.width)
                screen.set_text(1, height - 2 - y, s, message_colors[::-1][i])
                y += len(s.splitlines())

            screen.set_rect(gameplay_width, gameplay_height, width - gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(gameplay_width + 1, gameplay_height, "???", Colors.WHITE)

            game_screen.blit_level(active_visibility, level, -cam_x, -cam_y, Colors.BLUE)

            for entity in level.entities:
                if active_visibility[entity.y * level.width + entity.x]:
                    game_screen.set_at(entity.x - cam_x, entity.y - cam_y, entity.char, entity.color)

            game_screen.set_at(player.x - cam_x, player.y - cam_y, '@', Colors.YELLOW)
            
            if show_text:
                text_box(0, 0, game_screen.width, game_screen.height, title, contents, game_screen)

            screen.blit(game_screen, 1, 1)

            screen.put(stdscr, 1, 1, Colors)

            stdscr.refresh()

            # Get user input
            key = stdscr.getch()

            if show_text:
                if key == ord('\n'):
                    show_text = False
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
                elif key == ord('l'):
                    for n in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        for entity in level.entities:
                            if entity.x == player.x + n[0] and entity.y == player.y + n[1]:
                                show_text = True
                                title = entity.name
                                contents = entity.description
                                add_message(f"You examine the {entity.name}.")
                                break
                elif key == 27:
                    break

                if not solids[player.y, player.x]:
                    for entity in level.entities[::-1]:
                        if entity.x == player.x and entity.y == player.y:
                            interaction_type, interaction_data = entity.interact()

                            match interaction_type:
                                case "description":
                                    show_text = True
                                    title = entity.name
                                    contents = entity.description
                                    add_message(f"You examine the {entity.name}.")
                                case "dialogue":
                                    show_text = True
                                    title = entity.name
                                    contents = interaction_data
                                    add_message(f"You speak to the {entity.name}.")
                                case "attack":
                                    entity.health = max(0, entity.health - (player.strength + random.randint(-1, 1)))
                                    if entity.health == 0:
                                        level.entities.remove(entity)
                                        add_message(F"You attack the {entity.name}, killing it!")
                                    else:
                                        add_message(F"You attack the {entity.name}.")
                    player.x, player.y = ox, oy

            cam_x = player.x - gameplay_width // 2
            cam_y = player.y - gameplay_height // 2

    while True:
        if not main_menu():
            break
        main_game()

if __name__ == '__main__':
    curses.wrapper(main)
