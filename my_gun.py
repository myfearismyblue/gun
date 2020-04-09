from random import randrange as rnd, choice
import tkinter as tk
import math as m
import time

TIME_REFRESH = 50  # tick time in milliseconds
INIT_GUN_POWER = 10
INIT_GUN_POS_X = 0
INIT_GUN_POS_Y = 0
INIT_GUN_COLOR = 'blue'
MAX_GUN_POWER = 50
GUN_INCREASE_RATE = 0.5  # per tick
INIT_TARGET_COLOR = 'red'
INIT_SHELL_RADIUS = 5

def main():
    global root, gun  # FIXME: make root local
    root = tk.Tk()
    canvas = tk.Canvas(root)
    canvas.bind('<Button-1>', mouse_1_clicked_handler)
    canvas.bind('<ButtonRelease-1>', mouse_1_release_handler)
    canvas.bind('<Motion>', mouse_motion_handler)
    canvas.pack(fill=tk.BOTH, expand=1)
    init_game_objects()
    # tick()
    root.mainloop()
    pass


def mouse_1_clicked_handler(event):
    print('Mouse clicked. Power is', gun.power)
    # gun.increase_power(event)



def mouse_1_release_handler(event):
    gun.fire()


def mouse_motion_handler(event):
    gun.move(event.x, event.y)


def tick():
    """
    Moves and reshows everything on canvas
    """
    global root, TIME_REFRESH  # FIXME: make root local
    # TODO:move_everything
    # TODO:show_everything
    root.after(TIME_REFRESH, tick)


def init_game_objects():
    global gun
    gun = Gun()
    target = Target()
    target.create()


class Gun:
    def __init__(self, x=INIT_GUN_POS_X, y=INIT_GUN_POS_Y, angle=0,
                 power=INIT_GUN_POWER, color=INIT_GUN_COLOR):
        """
        Inits the gun with initial pos, angle, power and color.
        x1, y1 -- fixed end of the gun; x2, y2 -- moving end of the gun
        """
        self.x1 = x
        self.y1 = y
        self.angle = angle
        self.power = power
        self.color = color
        self.x2 = self.x1 + m.cos(self.angle) * self.power
        self.y2 = self.y1 + m.sin(self.angle) * self.power

    def move(self, x_mouse_pointer, y_mouse_pointer):
        """
        Creates gun pointing on  mouse position
        :param x_mouse_pointer, y_mouse_pointr: mouse coordinates on canvas
        """
        if y_mouse_pointer == 0:
            y_mouse_pointer += 1
        self.angle = x_mouse_pointer / y_mouse_pointer
        self.create(self.x1, self.y1, self.angle, self.power, self.color)

    def create(self, x, y, angle, power, color):
        """
        Creates the gun with defined pos, angle, power and color.
        x1, y1 -- fixed end of the gun; x2, y2 -- moving end of the gun
        """
        self.x1 = x
        self.y1 = y
        self.angle = angle
        self.power = power
        self.color = color
        self.x2 = self.x1 + m.cos(m.atan(self.angle)) * self.power
        self.y2 = self.y1 + m.sin(m.atan(self.angle)) * self.power

    def increase_power(self, event):
        """
        Increases gun power while targeting
        """
        if event == '<Button-1>':
            while event and self.power <= MAX_GUN_POWER:
                self.power += GUN_INCREASE_RATE
        self.create(self.x1, self.y1, self.angle, self.power, self.color)

    def fire(self):
        """Creates shell on guns end with power / 10 velocity"""
        x = self.x2
        y = self.y2
        dx = m.cos(m.atan(self.angle)) * self.power / 10
        dy = m.sin(m.atan(self.angle)) * self.power / 10
        shell = Shell()
        shell.create(x, y, dx, dy)

    def show(self):
        pass    #tkinter show

    def print_yourself(self):
        print('x1 = ', self.x1, 'y1 = ', self.y1)
        print('x2 = ', self.x2, 'y2 = ', self.y2)
        print('angle = ', self.angle, 'power = ', self.power)
        print('color = ', self.color)


class Target:
    def __init__(self, x=0, y=0, R=0, color=INIT_TARGET_COLOR, live=False):
        self.x = x
        self.y = y
        self.R = R
        self.color = color
        self.live = live

    def create(self):
        """
        Crates round target in random place, of random radius
        """
        self.R = rnd(2, 50)
        self.x = rnd(600, 780)
        self.y = rnd(300, 550)
        self.live = True

    def die(self):
        self.live = False

    def print_yourself(self):
        print('x = ', self.x, 'y = ', self.y)
        print('R = ', self.R, 'live = ', self.live)


class Shell:
    def __init__(self, x=0, y=0, dx=0, dy=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.R = INIT_SHELL_RADIUS
        self.color = 'green'
        self.live = True

    def create(self, x, y, dx, dy):
        """
        Creates a ball of random color in defined pos and velocity, and random color
        """
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = choice(['blue', 'green', 'red', 'brown'])
        self.live = True

    def die(self):
        self.live = False

    def kill_target(self, target):
        """Twiches die method of target"""
        target.die()

    def move(self):
        """Move itself by one tick"""
        self.x += self.dx
        self.y += self.dy

    def print_yourself(self):
        print('x = ', self.x, 'y = ', self.y)
        print('dx = ', self.dx, 'dy = ', self.dy)
        print('color = ', self.color, 'live = ', self.live)

if __name__ == '__main__':
    DEBUG = 0
    if DEBUG:
        [print('DEBUG!') for _ in range(5)]
        gun = Gun()
        ball = Shell()
        target = Target()
        target.create()
        gun.move(10, 10)
        target.print_yourself()
        print('---------------')
        gun.fire(ball)
        ball.print_yourself()
        print('---------------')
        ball.kill_target(target)

        target.print_yourself()
        for obj in [gun, ball, target]:
            obj.print_yourself()
            print('---------------')
    else:
        main()
