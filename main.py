import curses

import tcod.path
import tcod.map
import tcod.constants

from procgen import generate_dungeon

from data import Buffer, Level

import numpy as np

GAMENAME = "Ethereal Collapse"

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

    def main_menu():
        return True

    def main_game():
        game_screen = Buffer(gameplay_width - 2, gameplay_height - 2)

        level, x, y = generate_dungeon(
            15, 4, 6, width, height
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

        cam_x = x - gameplay_width // 2
        cam_y = y - gameplay_height // 2

        show_text = False

        title = ""
        contents = ""

        while True:
            generate_solids()
            fov = tcod.map.compute_fov(solids, (y, x), 4, algorithm=tcod.constants.FOV_DIAMOND)
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
            screen.set_text(gameplay_width + 1, 0, "Inventory", Colors.WHITE)
            screen.set_rect(0, gameplay_height, gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(1, gameplay_height, "Messages", Colors.WHITE)
            screen.set_rect(gameplay_width, gameplay_height, width - gameplay_width, height - gameplay_height, Colors.WHITE)
            screen.set_text(gameplay_width + 1, gameplay_height, "???", Colors.WHITE)

            game_screen.blit_level(active_visibility, level, -cam_x, -cam_y, Colors.BLUE)

            for entity in level.entities:
                if active_visibility[entity.y * level.width + entity.x]:
                    game_screen.set_at(entity.x - cam_x, entity.y - cam_y, entity.char, entity.color)

            game_screen.set_at(x - cam_x, y - cam_y, '@', Colors.YELLOW)
            
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
                ox, oy = x, y

                if key == curses.KEY_UP:
                    y = max(0, y - 1)
                elif key == curses.KEY_DOWN:
                    y = min(height - 1, y + 1)
                elif key == curses.KEY_LEFT:
                    x = max(0, x - 1)
                elif key == curses.KEY_RIGHT:
                    x = min(width - 1, x + 1)
                elif key == ord('l'):
                    for n in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        for entity in level.entities:
                            if entity.x == x + n[0] and entity.y == y + n[1]:
                                show_text = True
                                title = entity.name
                                contents = entity.description
                                break
                elif key == 27:
                    break

                if not solids[y, x]:
                    for entity in level.entities:
                        if entity.x == x and entity.y == y:
                            interaction_type, interaction_data = entity.interact()

                            match interaction_type:
                                case "description":
                                    show_text = True
                                    title = entity.name
                                    contents = entity.description
                                case "dialogue":
                                    show_text = True
                                    title = entity.name
                                    contents = interaction_data
                    x, y = ox, oy

            cam_x = x - gameplay_width // 2
            cam_y = y - gameplay_height // 2

    while True:
        if not main_menu():
            break
        main_game()

if __name__ == '__main__':
    curses.wrapper(main)
