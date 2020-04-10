from random import randrange as rnd, choice
import tkinter as tk
import math as m
import time

TIME_REFRESH = 50  # tick time in milliseconds
INIT_GUN_POWER = 30
INIT_GUN_POS_X = 100
INIT_GUN_POS_Y = 0
INIT_GUN_COLOR = 'blue'
MAX_GUN_POWER = 100
GUN_INCREASE_RATE = 1  # per tick
GUN_DECREASE_RATE = 2
INIT_TARGET_COLOR = 'red'
INIT_SHELL_RADIUS = 5
SHELL_LIFETIME = 2 * 1000 / TIME_REFRESH  # seconds
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

button_1_hold = False


def main():
    global root, canvas, gun, shell  # FIXME: make locals

    root = tk.Tk()
    root.geometry(str(CANVAS_WIDTH) + 'x' + str(CANVAS_HEIGHT))
    canvas = tk.Canvas(root)
    [gun, target, shell] = init_game_objects()
    canvas.bind('<Button-1>', mouse_1_clicked_handler)
    canvas.bind('<ButtonRelease-1>', mouse_1_release_handler)
    canvas.bind('<Motion>', mouse_motion_handler)
    canvas.pack(fill=tk.BOTH, expand=1)

    tick()
    root.mainloop()
    pass


def mouse_1_clicked_handler(event):
    global button_1_hold
    button_1_hold = True


def mouse_1_release_handler(event):
    global button_1_hold
    button_1_hold = False
    gun.fire()


def mouse_motion_handler(event):
    gun.move(event.x, event.y)


def power_up_handler():
    global button_1_hold
    gun.target_and_increase_power()


def tick():
    """
    Moves and reshows everything on canvas.
    """
    global root, button_1_hold, gun, shell  # FIXME: make root local
    # TODO:move_everything
    # TODO:show_everything
    gun.show()  # gun moves in mainloop with MouseMotion  event
    shell.move()
    shell.show()
    power_up_handler()
    root.after(TIME_REFRESH, tick)


def init_game_objects():
    """Inits game objects to be handled after"""
    gun = Gun()
    shell = Shell()
    target = Target()
    target.create()
    return gun, target, shell


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
        self.x2 = self.x1 + m.sin(self.angle) * self.power
        self.y2 = self.y1 + m.cos(self.angle) * self.power
        self.live = True
        if self.live:
            self.id = canvas.create_line(self.x1, self.y1, self.x2, self.y2, width=10)
        else:
            self.id = 0

    def move(self, x_mouse_pointer, y_mouse_pointer):
        """
        Creates gun pointing on  mouse position
        :param x_mouse_pointer, y_mouse_pointr: mouse coordinates on canvas
        """
        if y_mouse_pointer == 0:
            y_mouse_pointer += 1
        self.angle = m.atan((x_mouse_pointer - INIT_GUN_POS_X) / (y_mouse_pointer - INIT_GUN_POS_Y))
        self.create(self.x1, self.y1, self.angle, self.power, self.color)

    def create(self, x, y, angle, power, color):
        """
        Creates the gun with defined pos, angle, power and color.
        x1, y1 -- fixed end of the gun; x2, y2 -- moving end of the gun
        """
        self.live = True
        self.x1 = x
        self.y1 = y
        self.angle = angle
        self.power = power
        self.color = color
        self.x2 = self.x1 + m.sin(self.angle) * self.power
        self.y2 = self.y1 + m.cos(self.angle) * self.power

    def target_and_increase_power(self):
        """
        Increases gun power while targeting, recreates itself
        """
        global button_1_hold
        if button_1_hold:
            if self.power <= MAX_GUN_POWER:
                self.power += GUN_INCREASE_RATE
                self.create(self.x1, self.y1, self.angle, self.power, self.color)
        else:
            if self.power >= INIT_GUN_POWER:
                self.power -= GUN_DECREASE_RATE
                self.create(self.x1, self.y1, self.angle, self.power, self.color)

    def fire(self):
        """Creates shell on guns end with power / 10 velocity"""
        x = self.x2
        y = self.y2
        dx = m.sin(m.atan(self.angle)) * self.power / 10
        dy = m.cos(m.atan(self.angle)) * self.power / 10
        shell.create(x, y, dx, dy)

    def show(self):
        if self.live:
            canvas.coords(self.id, self.x1, self.y1, self.x2, self.y2)
            # TODO: make color depending of power
        else:
            print('Gun hasnt called gun.create')  # FIXME

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
        print('r = ', self.R, 'live = ', self.live)


class Shell:
    def __init__(self, x=0, y=0, dx=0, dy=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.r = INIT_SHELL_RADIUS
        self.color = 'green'
        self.live = 0
        if self.live:
            self.id = canvas.create_oval(
                self.x - self.r,
                self.y - self.r,
                self.x + self.r,
                self.y + self.r,
                fill=self.color
            )

    def create(self, x, y, dx, dy):
        """
        Creates a ball of random color in defined pos and velocity, and random color
        """
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = choice(['blue', 'green', 'red', 'brown'])
        self.live = SHELL_LIFETIME

    def die(self):
        self.live = False

    def kill_target(self, target):
        """Twiches die method of target"""
        target.die()

    def move(self):
        """Move itself by one tick"""
        if self.live:
            self.x += self.dx
            self.y += self.dy
            self.live -= 1

    def show(self):
        if self.live != 0:
            canvas.coords(
                self.id,
                self.x - self.r,
                self.y - self.r,
                self.x + self.r,
                self.y + self.r
            )
        else:
            self.id = canvas.create_oval(
                self.x - self.r,
                self.y - self.r,
                self.x + self.r,
                self.y + self.r,
                fill=self.color
            )

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
