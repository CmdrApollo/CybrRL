from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING

import tcod

from data import *
from items import generate_random_magical_item

class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True if this room overlaps with another RectangularRoom."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def tunnel_between(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:  # 50% chance.
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int
) -> Level:
    """Generate a new dungeon map."""
    dungeon = Level(map_width, map_height)

    rooms: List[RectangularRoom] = []

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # "RectangularRoom" class makes rectangles easier to work with
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Dig out this rooms inner area.
        dungeon.buffer.set_rect_filled(new_room.inner[0].start, new_room.inner[1].start, new_room.inner[0].stop - new_room.inner[0].start, new_room.inner[1].stop - new_room.inner[1].start, '.', 0)

        if len(rooms) == 0:
            # The first room, where the player starts.
            px, py = new_room.center
            dungeon.entities.append(MangledKobold(px + 1, py))
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            ex, ey = new_room.center
            if roll_against(100):
                # magical item
                dungeon.entities.append(ItemHolder(ex + random.randint(-1, 1), ey + random.randint(-1, 1), generate_random_magical_item()))
            elif roll_against(50):
                dungeon.entities.append(random.choice([Goblin, Kobold, Bat])(ex, ey))
            
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.buffer._buf[y * dungeon.width + x] = ('.', 0)

        # Finally, append the new room to the list.
        rooms.append(new_room)
    
    for x in range(dungeon.width):
        for y in range(dungeon.height):
            if dungeon.buffer.get(x, y)[0] == '.':
                neighbors = [False] * 8
                walls = [False] * 8
                for i, n in enumerate([(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]):
                    if dungeon.buffer.get(x + n[0], y + n[1])[0] == '.':
                        neighbors[i] = True
                    if dungeon.buffer.get(x + n[0], y + n[1])[0] == ' ':
                        walls[i] = True
                if (neighbors[0] and neighbors[1] and neighbors[2] and walls[3] and walls[4] and neighbors[6]):# or (neighbors[2] and neighbors[4] and neighbors[7] and neighbors[3]):
                    # cursed
                    dungeon.entities.append(Door(x, y))

    return dungeon, Player(px, py)
