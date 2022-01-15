from enum import Enum, auto
from textwrap import dedent
from typing import Dict, List, Tuple
from PIL import Image, ImageDraw

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


class Board:
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
        width = w * size
        height = h * size

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
            draw.line([(x * size, y * size - border), (x * size, (y + 1) * size + border)], fill='#38382D', width=border * 2)
        for x, y in self.hwalls:
            border = 5
            draw.line([(x * size - border, y * size), ((x + 1) * size + border, y * size)], fill='#38382D', width=border * 2)

        # Render robots
        for robot, pos in self.robot_positions.items():
            x, y = pos
            padding = (size - robot_size) / 2
            draw.ellipse([(x * size + padding, y * size + padding), ((x + 1) * size - padding, (y + 1) * size - padding)], fill='#FFFFFF', outline='#000000', width=1)

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
    def __init__(self) -> None:
        pass


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


main()
