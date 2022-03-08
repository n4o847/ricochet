from enum import Enum, auto
from textwrap import dedent
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

images = []

size = 70
robot_size = size * 0.8


Pos = Tuple[int, int]

class Dir(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    def get(self) -> 'Pos':
        if self == Dir.UP:
            return (0, -1)
        elif self == Dir.DOWN:
            return (0, 1)
        elif self == Dir.LEFT:
            return (-1, 0)
        elif self == Dir.RIGHT:
            return (1, 0)

UP = Dir.UP
DOWN = Dir.DOWN
LEFT = Dir.LEFT
RIGHT = Dir.RIGHT

class Component:
    pass


class Board(Component):
    hwalls: List['Pos'] = []
    vwalls: List['Pos'] = []
    robots: List['Robot'] = []
    robot_positions: Dict['Robot', 'Pos'] = {}
    history: List[Tuple['Robot', 'Dir']] = []

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    @staticmethod
    def from_ascii_art(text: str) -> 'Board':
        lines = dedent(text).splitlines()

        assert len(lines) >= 1
        assert len(lines[0]) % 2 == 1

        w = (len(lines[0]) - 1) // 2
        h = len(lines) - 1

        board = Board(w, h)

        for i, line in enumerate(lines):
            assert len(line) == len(lines[0])
            for j, col in enumerate(line):
                if j % 2 == 0:
                    x, y = j // 2, i - 1
                    if col == '|':
                        board.vwall(x, y)
                    elif col == '.':
                        pass
                    else:
                        raise ValueError()
                else:
                    x, y = (j - 1) // 2, i
                    if col == '_':
                        board.hwall(x, y)
                    elif col == ' ':
                        pass
                    else:
                        raise ValueError()

        return board

    def wall(self, points: List[int]) -> None:
        assert len(points) % 2 == 0
        for i in range(len(points) - 2):
            x1, y1, x2, y2 = points[i:i+4]
            # TODO

    def hwall(self, x: int, y: int) -> None:
        self.hwalls.append((x, y))

    def vwall(self, x: int, y: int) -> None:
        self.vwalls.append((x, y))

    def put(self, robot: 'Robot', x: int, y: int) -> None:
        self.robots.append(robot)
        self.robot_positions[robot] = (x, y)

    def move(self, robot: 'Robot', dir: 'Dir') -> None:
        self.history.append((robot, dir))

    def render(self) -> Image.Image:
        w = self.width
        h = self.height
        width = w * size + 2
        height = h * size + 2

        # Note: RGB mode is too slow
        im = Image.new('P', (width, height), '#F5F5DB')
        draw = ImageDraw.Draw(im)

        # Render grids
        for x in range(0, w + 1):
            draw.line([(x * size, 0), (x * size, height)], fill='#808080', width=2)
        for y in range(0, h + 1):
            draw.line([(0, y * size), (width, y * size)], fill='#808080', width=2)

        # Render walls
        for x, y in self.vwalls:
            border = 5
            draw.line([(x * size, y * size - border + 1), (x * size, (y + 1) * size + border)], fill='#38382D', width=border * 2)
        for x, y in self.hwalls:
            border = 5
            draw.line([(x * size - border + 1, y * size), ((x + 1) * size + border, y * size)], fill='#38382D', width=border * 2)

        # Render robots
        font = ImageFont.truetype('DejaVuSans', size=int(size * 0.5) & -2)
        for robot, pos in self.robot_positions.items():
            x, y = pos
            padding = (size - robot_size) / 2
            draw.ellipse([(x * size + padding, y * size + padding), ((x + 1) * size - padding, (y + 1) * size - padding)], fill='#FFFFFF', outline='#000000', width=1)
            if robot.name:
                # tw, th = draw.textsize(robot.name, font=font)
                draw.text(((x + 0.5) * size + 1, (y + 0.5) * size + 1), robot.name, fill='#000000', font=font, anchor='mm')
                # draw.text(((x + 0.5) * size - tw / 2, (y + 0.5) * size - th / 2), robot.name, fill='#000000', font=font)

        return im


    def render_all(self) -> List[Image.Image]:
        w = self.width
        h = self.height

        images: List[Image.Image] = []
        images.append(self.render())

        for robot, dir in self.history:
            rx, ry = self.robot_positions[robot]
            if dir == Dir.UP:
                while True:
                    if ry - 1 < 0:
                        break
                    if (rx, ry) in self.hwalls:
                        break
                    if (rx, ry - 1) in self.robot_positions.values():
                        break
                    self.robot_positions[robot] = (rx, ry - 0.5)
                    images.append(self.render())
                    self.robot_positions[robot] = (rx, ry - 1)
                    images.append(self.render())
                    ry -= 1
            elif dir == Dir.DOWN:
                while True:
                    if ry + 1 >= h:
                        break
                    if (rx, ry + 1) in self.hwalls:
                        break
                    if (rx, ry + 1) in self.robot_positions.values():
                        break
                    self.robot_positions[robot] = (rx, ry + 0.5)
                    images.append(self.render())
                    self.robot_positions[robot] = (rx, ry + 1)
                    images.append(self.render())
                    ry += 1
            elif dir == Dir.LEFT:
                while True:
                    if rx - 1 < 0:
                        break
                    if (rx, ry) in self.vwalls:
                        break
                    if (rx - 1, ry) in self.robot_positions.values():
                        break
                    self.robot_positions[robot] = (rx - 0.5, ry)
                    images.append(self.render())
                    self.robot_positions[robot] = (rx - 1, ry)
                    images.append(self.render())
                    rx -= 1
            elif dir == Dir.RIGHT:
                while True:
                    if rx + 1 >= w:
                        break
                    if (rx + 1, ry) in self.vwalls:
                        break
                    if (rx + 1, ry) in self.robot_positions.values():
                        break
                    self.robot_positions[robot] = (rx + 0.5, ry)
                    images.append(self.render())
                    self.robot_positions[robot] = (rx + 1, ry)
                    images.append(self.render())
                    rx += 1

        return images


class Robot:
    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name


def half_adder():
    board = Board.from_ascii_art("""\
        . . . . . . . . . .
        . . . . ._. . . . .
        . . . ._| |_. . . .
        . . ._| . | | . . .
        . . ._. | | | . . .
        . . . |_. . | . . .
        . . ._| . | | . . .
        . . ._. | | | . . .
        . . . |_. . |_. . .
        . . . |_._. ._. | .
        . . . . . |_._. | .
        . . . . . . . . . .
    """)
    ra = Robot('A')
    board.put(ra, 1, 3)
    rb = Robot('B')
    board.put(rb, 1, 6)
    r0 = Robot()
    board.put(r0, 3, 2)
    r1 = Robot()
    board.put(r1, 3, 5)
    r2 = Robot()
    board.put(r2, 4, 1)
    rc = Robot('C')
    board.put(rc, 5, 3)
    r3 = Robot()
    board.put(r3, 5, 2)
    rs = Robot('S')
    board.put(rs, 3, 8)

    board.move(ra, RIGHT)
    board.move(rb, RIGHT)

    board.move(r0, DOWN)
    board.move(r0, RIGHT)
    board.move(r1, DOWN)
    board.move(r1, RIGHT)
    board.move(r2, DOWN)
    board.move(rc, DOWN)
    board.move(r3, DOWN)
    board.move(rs, RIGHT)
    board.move(rc, RIGHT)

    images = board.render_all()
    dur = 40
    durations = [dur] * len(images)
    durations[0] = dur * 10
    durations[-1] = dur * 10
    images[0].save('half_adder.gif', save_all=True, append_images=images[1:], optimize=False, duration=durations, loop=0)


half_adder()


def main():
    # board = Board(12, 12)
    # board.vwall(11, 1)
    # board.hwall(10, 11)
    board = Board.from_ascii_art("""\
        . . . . . . . . . . . . .
        . . . . . . . . . . . . .
        . . . . . . . . . . . | .
        . . . . . . . . . . . . .
        . . . . . . . . . . . . .
        . . . . . . . . . . . . .
        . . . . . . . . . . . . .
        . . . . . . . . . . . . .
        . . . . . . . . . . . . .
        . . . . . . . . . . . . .
        . . . . . . . . . . . . .
        . . . . . . . . . . ._. .
        . . . . . . . . . . . . .
    """)
    r0 = Robot()
    board.put(r0, 1, 1)
    r1 = Robot()
    board.put(r1, 1, 10)
    board.move(r0, Dir.RIGHT)
    board.move(r0, Dir.DOWN)
    board.move(r0, Dir.LEFT)

    images = board.render_all()
    dur = 40
    durations = [dur] * len(images)
    durations[0] = dur * 10
    durations[-1] = dur * 10
    images[0].save('image.gif', save_all=True, append_images=images[1:], optimize=False, duration=durations, loop=0)


# main()
