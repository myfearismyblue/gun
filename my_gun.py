from random import randrange as rnd, choice
import tkinter as tk
import math as m
import time
from globasl_vars import *


def main():
    global root, canvas, canvas_objects, gun  # FIXME: make locals

    root = tk.Tk()
    root.geometry(str(CANVAS_WIDTH) + 'x' + str(CANVAS_HEIGHT))
    canvas = tk.Canvas(root)
    canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
    canvas_objects, gun = init_game_objects()
    canvas.bind('<Button-1>', mouse_1_clicked_handler)
    canvas.bind('<Button-3>', mouse_3_clicked_handler)
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


def mouse_3_clicked_handler(event):
    global canvas_objects
    canvas_objects.append(Target())  # initing
    canvas_objects[-1].create()  # creating


def power_up_handler():
    global button_1_hold, canvas_objects, gun
    gun.target_and_increase_power()


def collision_handler(canvas_objects):
    """
    Check if collision occurs, comparing objects in list
    :param canvas_objects: list of collisionable objects on canvas
    """
    for i in range(len(canvas_objects)):
        for j in range(i + 1, len(canvas_objects)):
            if type(canvas_objects[i]) != type(canvas_objects[j]):  # if target and shell intersects
                if collision_check(canvas_objects[i], canvas_objects[j]):
                    if isinstance(canvas_objects[j], Target):
                        canvas_objects[j].die()
                    else:
                        canvas_objects[i].die()
            else:
                pass


def collision_check(obj1, obj2):
    """Checks if two round object intersects"""
    x1 = obj1.x
    y1 = obj1.y
    r1 = obj1.r
    x2 = obj2.x
    y2 = obj2.y
    r2 = obj2.r
    if obj1.life_time and obj2.life_time:
        if (x2 - x1) ** 2 + (y2 - y1) ** 2 < (r1 + r2) ** 2:
            return True
    else:
        return False


def tick():
    """
    Moves and reshows everything on canvas.
    """
    global root, button_1_hold, gun, canvas_objects  # FIXME: make root local
    # TODO:move_everything
    # TODO:show_everything
    power_up_handler()
    gun.show()
    for obj in canvas_objects:
        obj.move()
        obj.show()
    collision_handler(canvas_objects)  # if shells and targets intersects, then targets die

    root.after(TIME_REFRESH, tick)


def init_game_objects():
    """Inits game objects to be handled after"""
    canvas_objects = list()
    gun = Gun()
    canvas_objects.append(Shell())
    canvas_objects.append(Target())
    canvas_objects[1].create()
    return canvas_objects, gun


class Gun:
    def __init__(self, x=GUN_INIT_POS_X, y=GUN_INIT_POS_Y, angle=0,
                 power=GUN_INIT_POWER, color=GUN_INIT_COLOR):
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

    def move(self, x_mouse_pointer=0, y_mouse_pointer=0):
        """
        Creates gun pointing on  mouse position
        :param x_mouse_pointer, y_mouse_pointr: mouse coordinates on canvas
        """
        self.count_angle(x_mouse_pointer, y_mouse_pointer)
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
        self.x2 = self.x1 + m.cos(self.angle) * self.power
        self.y2 = self.y1 + m.sin(self.angle) * self.power

    def target_and_increase_power(self):
        """
        Increases/decreases gun power while targeting, recreates itself
        """
        global button_1_hold
        if button_1_hold:
            if self.power <= GUN_MAX_POWER:
                self.power += GUN_INCREASE_RATE
                self.create(self.x1, self.y1, self.angle, self.power, self.color)
        else:
            if self.power >= GUN_INIT_POWER:
                self.power -= GUN_DECREASE_RATE
                self.create(self.x1, self.y1, self.angle, self.power, self.color)

    def fire(self):
        """Creates shell on guns end with power / const velocity"""
        x = self.x2
        y = self.y2
        dx = m.cos(self.angle) * self.power / 1
        dy = m.sin(self.angle) * self.power / 1
        canvas_objects.append(Shell())
        canvas_objects[-1].create(x, y, dx, dy)

    def show(self):
        if self.live:
            canvas.coords(self.id, self.x1, self.y1, self.x2, self.y2)
            canvas.itemconfig(self.id, fill=GUN_INIT_COLOR)
            # TODO: make color depending of power
        else:
            print('Gun hasn\'t called gun.create')  # FIXME

    def count_angle(self, x_mouse_pointer, y_mouse_pointer):
        if x_mouse_pointer - GUN_INIT_POS_X:
            self.angle = m.atan((y_mouse_pointer - GUN_INIT_POS_Y) /
                                (x_mouse_pointer - GUN_INIT_POS_X))
        else:  # zerodevision handle
            self.angle = m.pi / 2

    def print_yourself(self):
        print('x1 = ', self.x1, 'y1 = ', self.y1)
        print('x2 = ', self.x2, 'y2 = ', self.y2)
        print('angle = ', self.angle, 'power = ', self.power)
        print('color = ', self.color)


class Target:
    def __init__(self, x=0, y=0, dx=0, dy=0, r=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.r = r
        self.color = TARGET_INIT_COLOR
        self.id = 0  # id == 0, target shouldn't to be drawn
        self.life_time = TARGET_LIFETIME
        self.count_angle()

    def create(self):
        """
        Creates round target in random place, of random radius
        """
        self.r = rnd(TARGET_APPEAR_RADIUS_INTERVAL[0], TARGET_APPEAR_RADIUS_INTERVAL[1])
        self.x = rnd(TARGET_APPEAR_WIDTH_INTERVAL[0], TARGET_APPEAR_WIDTH_INTERVAL[1])
        self.y = rnd(TARGET_APPEAR_HEIGHT_INTERVAL[0], TARGET_APPEAR_HEIGHT_INTERVAL[1])
        self.life_time = TARGET_LIFETIME

    def show(self):
        if self.life_time > 0:  # if a target have to live
            if self.id:  # lets check, if it has been drawn
                canvas.coords(self.id,  # if so, then redraw coords
                              self.x - self.r,
                              self.y - self.r,
                              self.x + self.r,
                              self.y + self.r
                              )

            else:  # if it hasn't been drawn, then draw
                self.id = canvas.create_oval(self.x - self.r,
                                             self.y - self.r,
                                             self.x + self.r,
                                             self.y + self.r,
                                             fill=self.color
                                             )

    def die(self):
        self.life_time = 0
        canvas.delete(self.id)  # delete from canvas
        self.id = 0  # delete from physics, target shouldn't be moved

    def move(self):
        """Move itself by one tick"""
        if self.life_time > 0:  # at each tick physics done:
            if 0 + self.r < self.x + self.dx < CANVAS_WIDTH - self.r:
                self.x += self.dx
                self.count_angle()
            else:  # each vertical border collision
                self.count_angle()
                self.dx = -self.dx * FRICTION_CONSTANT
                self.dy *= FRICTION_CONSTANT
                self.x += self.dx
            if -1 <= self.dx <= 1:
                self.dx = 0
                self.count_angle()
            if 0 + self.r < self.y + self.dy < CANVAS_HEIGHT - self.r:
                self.y += self.dy
                self.dy += GRAVITY_CONSTANT
                self.count_angle()
            else:  # each horizontal border collision
                self.count_angle()
                self.dy = -self.dy * FRICTION_CONSTANT
                self.dx *= FRICTION_CONSTANT
                self.y += self.dy
                self.dy += GRAVITY_CONSTANT

            if self.y + self.dy >= CANVAS_HEIGHT - self.r and -3 <= self.dy <= 3:
                self.dy = 0
                self.count_angle()

            self.life_time -= 1
        else:
            self.die()

    def count_angle(self):
        if self.dx != 0:
            self.angle = m.atan(self.dy / self.dx)
        else:
            self.angle = m.pi / 2

    def print_yourself(self):
        print('x = ', self.x, 'y = ', self.y)
        print('r = ', self.r, 'id = ', self.id)


class Shell:
    def __init__(self, x=0, y=0, dx=0, dy=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.angle = None
        self.r = SHELL_INIT_RADIUS
        self.color = 'green'
        self.id = 0  # id == 0, shell hasn't been drawn
        self.life_time = 0

    def create(self, x, y, dx, dy):
        """
        Creates a ball of random color in defined pos and velocity, and random color
        """
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.count_angle()
        self.color = choice(['blue', 'green', 'red', 'brown'])
        self.life_time = SHELL_LIFETIME

    def die(self):
        self.life_time = 0
        canvas.delete(self.id)  # delete from canvas
        self.id = 0  # delete from physics, shell shouldn't be moved

    def kill_target(self, target):
        """Twiches die method of target"""
        target.die()

    def move(self):
        """Move itself by one tick"""
        if self.life_time > 0:  # at each tick physics done:
            if 0 + self.r < self.x + self.dx < CANVAS_WIDTH - self.r:
                self.x += self.dx
                self.count_angle()
            else:  # each vertical border collision
                self.count_angle()
                self.dx = -self.dx * FRICTION_CONSTANT
                self.dy *= FRICTION_CONSTANT
                self.x += self.dx
            if -1 <= self.dx <= 1:
                self.dx = 0
                self.count_angle()
            if 0 + self.r < self.y + self.dy < CANVAS_HEIGHT - self.r:
                self.y += self.dy
                self.dy += GRAVITY_CONSTANT
                self.count_angle()
            else:  # each horizontal border collision
                self.count_angle()
                self.dy = -self.dy * FRICTION_CONSTANT
                self.dx *= FRICTION_CONSTANT
                self.y += self.dy
                self.dy += GRAVITY_CONSTANT

            if self.y + self.dy >= CANVAS_HEIGHT - self.r and -3 <= self.dy <= 3:
                self.dy = 0
                self.count_angle()

            self.life_time -= 1
        else:
            self.die()

    def show(self):
        if self.life_time > 0:  # if a shell have to live
            if self.id:  # lets check, if it has been drawn
                canvas.coords(self.id,  # if so, then redraw coords
                              self.x - self.r,
                              self.y - self.r,
                              self.x + self.r,
                              self.y + self.r
                              )

            else:  # if it hasn't been drawn, then draw
                self.id = canvas.create_oval(self.x - self.r,
                                             self.y - self.r,
                                             self.x + self.r,
                                             self.y + self.r,
                                             fill=self.color
                                             )

    def count_angle(self):
        if self.dx != 0:
            self.angle = m.atan(self.dy / self.dx)
        else:
            self.angle = m.pi / 2

    def print_yourself(self):
        print('x =', self.x, 'y =', self.y)
        print('dx =', self.dx, 'dy =', self.dy)
        print('color =', self.color, 'id =', self.id)


if __name__ == '__main__':
    main()
