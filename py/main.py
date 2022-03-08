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
    hwalls: List['Pos']
    vwalls: List['Pos']
    robots: List['Robot']
    robot_positions: Dict['Robot', 'Pos']
    history: List[Tuple['Robot', 'Dir']]

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.hwalls = []
        self.vwalls = []
        self.robots = []
        self.robot_positions = {}
        self.history = []


    def put_walls_from_ascii_art(self, text: str) -> None:
        lines = dedent(text).splitlines()

        assert len(lines) >= 1
        assert len(lines[0]) % 2 == 1

        # w = (len(lines[0]) - 1) // 2
        # h = len(lines) - 1

        for i, line in enumerate(lines):
            assert len(line) == len(lines[0])
            for j, col in enumerate(line):
                if j % 2 == 0:
                    x, y = j // 2, i - 1
                    if col == '|':
                        self.put_vwall(x, y)
                    elif col == '.':
                        pass
                    else:
                        raise ValueError()
                else:
                    x, y = (j - 1) // 2, i
                    if col == '_':
                        self.put_hwall(x, y)
                    elif col == ' ':
                        pass
                    else:
                        raise ValueError()


    def put_walls(self, points: List[int]) -> None:
        assert len(points) % 2 == 0
        for i in range(len(points) - 2):
            x1, y1, x2, y2 = points[i:i+4]
            # TODO

    def put_hwall(self, x: int, y: int) -> None:
        self.hwalls.append((x, y))

    def put_vwall(self, x: int, y: int) -> None:
        self.vwalls.append((x, y))

    def put(self, robot: 'Robot', x: int, y: int) -> None:
        self.robots.append(robot)
        self.robot_positions[robot] = (x, y)

    def move(self, robot: 'Robot', dir: 'Dir') -> None:
        self.history.append((robot, dir))


class Board(Component):
    def put_component(self, component: 'Component', x: int, y: int) -> None:
        self.hwalls.extend([(x0 + x, y0 + y) for x0, y0 in component.hwalls])
        self.vwalls.extend([(x0 + x, y0 + y) for x0, y0 in component.vwalls])
        self.robots.extend(component.robots)
        self.robot_positions.update((r, (x0 + x, y0 + y)) for r, (x0, y0) in component.robot_positions.items())
        component.history = self.history


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


    def save(self, path: str) -> None:
        images = self.render_all()
        dur = 40
        durations = [dur] * len(images)
        durations[0] = dur * 10
        durations[-1] = dur * 10
        images[0].save(path, save_all=True, append_images=images[1:], optimize=False, duration=durations, loop=0)


class Robot:
    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name


class HalfAdder(Component):
    r0: Robot
    r1: Robot
    r2: Robot
    rc: Robot
    r3: Robot
    rs: Robot

    def __init__(self) -> None:
        super().__init__(0, 0)

        self.put_walls_from_ascii_art("""\
            . ._. .
            ._| |_.
            | . | |
            . | | |
            |_. . |
            | . | |
            . | | |
            |_. . |
            |_._. .
            . . |_.
        """)

        self.r0 = Robot()
        self.put(self.r0, 0, 1)
        self.r1 = Robot()
        self.put(self.r1, 0, 4)
        self.r2 = Robot()
        self.put(self.r2, 1, 0)
        self.rc = Robot('C')
        self.put(self.rc, 2, 2)
        self.r3 = Robot()
        self.put(self.r3, 2, 1)
        self.rs = Robot('S')
        self.put(self.rs, 0, 7)


    def execute(self) -> None:
        self.move(self.r0, DOWN)
        self.move(self.r0, RIGHT)
        self.move(self.r1, DOWN)
        self.move(self.r1, RIGHT)
        self.move(self.r2, DOWN)
        self.move(self.rc, DOWN)
        self.move(self.r3, DOWN)
        self.move(self.rs, RIGHT)
        self.move(self.rc, RIGHT)


def half_adder():
    board = Board(9, 11)

    board.put_walls_from_ascii_art("""\
        . . . . . . . . . .
        . . . . . . . . . .
        . . . . . . . . . .
        . . ._. . . . . . .
        . . ._. . . . . . .
        . . . . . . . . . .
        . . ._. . . . . . .
        . . ._. . . . . . .
        . . . . . . ._. . .
        . . . . . . ._. | .
        . . . . . . ._. | .
        . . . . . . . . . .
    """)

    ra = Robot('A')
    board.put(ra, 1, 3)
    rb = Robot('B')
    board.put(rb, 1, 6)

    ha0 = HalfAdder()
    board.put_component(ha0, 3, 1)

    board.move(ra, RIGHT)
    board.move(rb, RIGHT)
    ha0.execute()

    board.save('images/half_adder.gif')


def full_adder():
    board = Board(14, 17)

    board.put_walls_from_ascii_art("""\
        . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . .
        . . . . . . . . . . . . . . .
        . . ._. . . . . . . . . . . .
        . . ._. . . . . . . ._. . . .
        . . . . . . ._._._._| | . . .
        . . ._. . . . . . . . | . . .
        . . ._. . . . . . . . | . . .
        . . . . . . . . . . . | . . .
        . . . . . . . . . . . | . . .
        . . . . . . ._. . . . | . . .
        . . . . . . ._. . . . | . . .
        . . . . . . ._. . . . | . . .
        . . . . . . . . . . . |_. . .
        . . . . . . . . . . . ._. | .
        . . . . . . . . . . . |_. . .
        . . . . . . . . . |_._._. | .
        . . . . . . . . . . . . . . .
    """)

    ra = Robot('A')
    board.put(ra, 1, 3)
    rb = Robot('B')
    board.put(rb, 1, 6)
    rx = Robot('X')
    board.put(rx, 5, 11)
    r0 = Robot()
    board.put(r0, 10, 4)
    rc = Robot('C')
    board.put(rc, 9, 15)

    ha0 = HalfAdder()
    board.put_component(ha0, 3, 1)

    ha1 = HalfAdder()
    board.put_component(ha1, 7, 6)

    board.move(ra, RIGHT)
    board.move(rb, RIGHT)
    board.move(rx, RIGHT)
    ha0.execute()
    board.move(ha0.rc, UP)
    board.move(ha0.rc, RIGHT)
    ha1.execute()
    board.move(r0, DOWN)
    board.move(rc, RIGHT)

    board.save('images/full_adder.gif')


def main():
    full_adder()


if __name__ == '__main__':
    main()
