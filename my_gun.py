from random import randrange as rnd, choice
from abc import ABCMeta, abstractmethod
import tkinter as tk
import math as m
from globasl_vars import *


def main():
    global root, canvas, canvas_objects, gun  # FIXME: make locals

    root = tk.Tk()
    root.geometry(str(CANVAS_WIDTH) + 'x' + str(CANVAS_HEIGHT))
    canvas = tk.Canvas(root)
    canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
    canvas_objects, gun = init_game_objects()
    canvas.bind('<Button-1>', mouse_1_clicked_handler)
    canvas.bind('<Button-2>', mouse_2_clicked_handler)
    canvas.bind('<Button-3>', mouse_3_clicked_handler)
    canvas.bind('<ButtonRelease-1>', mouse_1_release_handler)
    canvas.bind('<ButtonRelease-2>', mouse_2_release_handler)
    canvas.bind('<Motion>', mouse_motion_handler)
    canvas.pack(fill=tk.BOTH, expand=1)

    tick()
    root.mainloop()
    pass


def init_game_objects():
    """Inits game objects to be handled after"""
    canvas_objects = list()
    gun = Gun()
    canvas_objects.append(Shell())
    canvas_objects.append(Target())
    return canvas_objects, gun


def tick():
    """Moves and reshows everything on canvas."""
    global root, BUTTON_1_HOLD, gun, canvas_objects  # FIXME: make root local
    power_up_handler()
    gun.show()
    for obj in canvas_objects:
        obj.move()
        obj.show()
    collision_handler(canvas_objects)  # if shells and targets intersects, then targets die

    root.after(TIME_REFRESH, tick)


def mouse_1_clicked_handler(event):
    global BUTTON_1_HOLD
    BUTTON_1_HOLD = True


def mouse_1_release_handler(event):
    global BUTTON_1_HOLD
    BUTTON_1_HOLD = False
    gun.fire()


def mouse_motion_handler(event):
    gun.move(event.x, event.y)


def mouse_3_clicked_handler(event):
    global canvas_objects
    canvas_objects.append(Target())  # initing
    canvas_objects[-1]._set_shell_params()  # creating


def mouse_2_clicked_handler(event):
    global BUTTON_2_HOLD
    BUTTON_2_HOLD = True


def mouse_2_release_handler(event):
    global BUTTON_2_HOLD
    BUTTON_2_HOLD = False
    gun.fire2()


def power_up_handler():
    global BUTTON_1_HOLD, BUTTON_2_HOLD, canvas_objects, gun
    gun.target_and_increase_power()


def collision_handler(canvas_objects):
    """Checks if collision occurs, comparing objects in list
    :param canvas_objects: list of collisionable objects on canvas
    """
    for i in range(len(canvas_objects)):
        for j in range(i + 1, len(canvas_objects)):
            if collision_check(canvas_objects[i], canvas_objects[j]):
                if type(canvas_objects[i]) != type(canvas_objects[j]):  # if target and shell intersects
                    if isinstance(canvas_objects[j], Target):
                        canvas_objects[j].die()
                    else:
                        canvas_objects[i].die()
                else:  # objects are of the same type
                    canvas_objects[j].rebound(canvas_objects[i])
                    canvas_objects[i].rebound(canvas_objects[j])
                    canvas_objects[j].pop_out(canvas_objects[i])


def collision_check(obj1, obj2):
    """Checks if two round object intersects."""
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


def count_angle(x0, y0, x1, y1):
    """Counts angle in radians between vector (x1, y1) (x0, y0) and horizontal axis (CW) in canvas coordinate system
        :returns  0 if x0 == y0 == x1 == y1 == 0
                  [0.. +3.14] if vectors points down
                  (-3.14.. 0] if vectors points up
    """
    if x0 == y0 == x1 == y1 == 0:
        return 0

    if x1 - x0 > 0:  # pointing to the right semi-plane
        angle = m.atan((y1 - y0) / (x1 - x0))
    elif x1 - x0 < 0 and y1 - y0 >= 0:  # adding pi if pointing to the left-bottom quart
        angle = m.pi + m.atan((y1 - y0) / (x1 - x0))
    elif x1 - x0 < 0 and y1 - y0 < 0:  # subtract pi if pointing to the left-upper quart
        angle = -m.pi + m.atan((y1 - y0) / (x1 - x0))
    else:  # zerodevision handle
        if y1 - y0 > 0:  # pointing down
            angle = m.pi / 2
        else:  # pointing up
            angle = -m.pi / 2

    return angle


def vector_reflection(x0, y0, x1, y1, xv0, yv0, xv1, yv1):
    """ Returns new vector with coordinates[new_xv0, new_yv0, new_xv1, new_yv1] reflecting current vector
    [xv0, yv0, xv1, yv1]  from border defined by two points [x0, y0, x1, y1]
    :param x0, y0:the first point of the line which defines the border of reflection
    :param x1, y1: the second point of the line which defines the border of reflection
    :param xv0, yv0: beginning point of the vector to reflect
    :param xv1, yv1: ending point of the vector to reflect
    :return: coordinates of a new vector as a list, or [0, 0, 0, 0] if vector points out of the border or intersects it
    """

    # Find border and vector slope, intercept and point of intersection -- xC, yC.
    if xv0 != xv1 and x0 != x1:
        vector_slope = (yv1 - yv0) / (xv1 - xv0)
        vector_intercept = yv1 - vector_slope * xv1
        border_slope = (y1 - y0) / (x1 - x0)
        if border_slope == vector_slope:
            return [0, 0, 0, 0]  # border and vector are collinear
        border_angle = m.atan(border_slope)
        border_intercept = y1 - border_slope * x1
        xC = (border_intercept - vector_intercept) / (vector_slope - border_slope)  # coordinates of intersection of
        yC = border_slope * xC + border_intercept  # a vector-line and border-line
    elif xv0 == xv1 and x0 != x1:  # avoiding zerodevision -- vector is vertical
        vector_slope = m.inf
        vector_intercept = m.inf
        border_slope = (y1 - y0) / (x1 - x0)
        border_angle = m.atan(border_slope)
        border_intercept = y1 - border_slope * x1
        xC = xv0
        yC = border_slope * xC + border_intercept
    elif xv0 != xv1 and x0 == x1:  # avoiding zerodevision -- border is vertical
        border_slope = m.inf
        border_angle = m.pi / 2
        border_intercept = m.inf
        vector_slope = (yv1 - yv0) / (xv1 - xv0)
        vector_intercept = yv1 - vector_slope * xv1
        xC = x0
        yC = vector_slope * xC + vector_intercept
    else:  # border and vector are vertical and collinear
        return [0, 0, 0, 0]

    # R = ((xC - xv1) ** 2 + (yC - yv1) ** 2) ** 0.5  # distance between intersection and ending of the vector
    # S = ((xC - xv0) ** 2 + (yC - yv0) ** 2) ** 0.5  # distance between intersection and beginning of the vector

    # if S <= R:  # vector is pointing out of the border
    #     return [0, 0, 0, 0]
    # elif min(xv0, xv1) < xC < max(xv0, xv1) and min(yv0, yv1) < yC < max(yv0, yv1):  # vector intersects the border
    #     return [0, 0, 0, 0]

    # Translation of canvas coordinates to xC, yC intersection point
    pv0 = xv0 - xC
    qv0 = yv0 - yC
    pv1 = xv1 - xC
    qv1 = yv1 - yC

    # Rotation of canvas coordinates
    p_rotated_v0 = pv0 * m.cos(border_angle) + qv0 * m.sin(border_angle)
    q_rotated_v0 = -pv0 * m.sin(border_angle) + qv0 * m.cos(border_angle)
    p_rotated_v1 = pv1 * m.cos(border_angle) + qv1 * m.sin(border_angle)
    q_rotated_v1 = -pv1 * m.sin(border_angle) + qv1 * m.cos(border_angle)

    # Reflecting vector relatively y-axis. New ending is old beginning, new beginning is old ending
    new_p_rotated_v0 = -p_rotated_v1
    new_q_rotated_v0 = q_rotated_v1
    new_p_rotated_v1 = -p_rotated_v0
    new_q_rotated_v1 = q_rotated_v0

    # Rotating coordinates back
    new_pv0 = new_p_rotated_v0 * m.cos(-border_angle) + new_q_rotated_v0 * m.sin(-border_angle)
    new_qv0 = -new_p_rotated_v0 * m.sin(-border_angle) + new_q_rotated_v0 * m.cos(-border_angle)
    new_pv1 = new_p_rotated_v1 * m.cos(-border_angle) + new_q_rotated_v1 * m.sin(-border_angle)
    new_qv1 = -new_p_rotated_v1 * m.sin(-border_angle) + new_q_rotated_v1 * m.cos(-border_angle)
    # Translating coordinates back
    new_xv0 = new_pv0 + xC
    new_yv0 = new_qv0 + yC
    new_xv1 = new_pv1 + xC
    new_yv1 = new_qv1 + yC

    return new_xv0, new_yv0, new_xv1, new_yv1


def from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code."""
    return "#%02x%02x%02x" % rgb


class IGameActor:
    __metaclass__ = ABCMeta

    @abstractmethod
    def move(self):
        raise NotImplementedError

    @abstractmethod
    def show(self):
        raise NotImplementedError

    @abstractmethod
    def die(self):
        raise NotImplementedError


class Gun(IGameActor):
    def __init__(self, x=GUN_INIT_POS_X, y=GUN_INIT_POS_Y, angle=0,
                 power=GUN_INIT_POWER, color=GUN_INIT_COLOR):
        """Inits the gun with initial pos, angle, power and color.
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
        """Creates gun pointing on  mouse position
        :param x_mouse_pointer, y_mouse_pointr: mouse coordinates on canvas
        """
        if self.live:
            self.angle = count_angle(GUN_INIT_POS_X, GUN_INIT_POS_Y, x_mouse_pointer, y_mouse_pointer)
            self._set_gun_params(self.x1, self.y1, self.angle, self.power, self.color)

    def _set_gun_params(self, x, y, angle, power, color):
        """Creates the gun with defined pos, angle, power and color.
        x1, y1 -- fixed end of the gun; x2, y2 -- moving end of the gun
        """
        if self.live:
            self.x1 = x
            self.y1 = y
            self.angle = angle
            self.power = power
            self.color = color
            self.x2 = self.x1 + m.cos(self.angle) * self.power
            self.y2 = self.y1 + m.sin(self.angle) * self.power

    def target_and_increase_power(self):
        """Increases/decreases gun power while targeting, recreates itself."""
        if self.live:
            if BUTTON_1_HOLD or BUTTON_2_HOLD:
                if self.power <= GUN_MAX_POWER:
                    self.power += GUN_INCREASE_RATE
            else:
                if self.power >= GUN_INIT_POWER:
                    self.power -= GUN_DECREASE_RATE
            r = int(254 * self.power / GUN_MAX_POWER)
            g = int(0 * self.power / GUN_MAX_POWER)
            b = int(0 * self.power / GUN_MAX_POWER)
            self.color = from_rgb((r, g, b))
            self._set_gun_params(self.x1, self.y1, self.angle, self.power, self.color)

    def fire(self):
        """Creates a shell on guns end with power / const velocity. Appends shell to global list."""
        if self.live:
            x = self.x2
            y = self.y2
            dx = m.cos(self.angle) * self.power / GUN_FIRING_RATIO
            dy = m.sin(self.angle) * self.power / GUN_FIRING_RATIO
            canvas_objects.append(Shell())
            canvas_objects[-1]._set_shell_params(x, y, dx, dy)

    def fire2(self):
        """Creates a target on guns end with power / const velocity. Appends shell to global list."""
        if self.live:
            x = self.x2
            y = self.y2
            dx = m.cos(self.angle) * self.power / GUN_FIRING_RATIO
            dy = m.sin(self.angle) * self.power / GUN_FIRING_RATIO
            canvas_objects.append(Target())  # inits as an object
            canvas_objects[-1].create2(x, y, dx, dy)  # creates defined objects

    def show(self):
        """Make all physical changes visible"""
        if self.live:
            canvas.coords(self.id, self.x1, self.y1, self.x2, self.y2)
            canvas.itemconfig(self.id, fill=self.color)
        else:
            canvas.delete(self.id)
            self.id = 0

    def print_yourself(self):
        print('x1 = ', self.x1, 'y1 = ', self.y1)
        print('x2 = ', self.x2, 'y2 = ', self.y2)
        print('angle = ', self.angle, 'power = ', self.power)
        print('color = ', self.color)

    def die(self):
        canvas.delete(self.id)
        self.id = 0
        self.live = False


class Target(IGameActor):
    def __init__(self, x=0, y=0, dx=0, dy=0, r=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.r = r
        self.color = TARGET_INIT_COLOR
        self.id = 0  # id == 0, target shouldn't to be drawn
        self.life_time = TARGET_LIFETIME
        self.angle = count_angle(0, 0, self.dx, self.dy)

    def create(self):
        """Creates round target in random place, of random radius."""
        self.r = rnd(TARGET_APPEAR_RADIUS_INTERVAL[0], TARGET_APPEAR_RADIUS_INTERVAL[1])
        self.x = rnd(TARGET_APPEAR_WIDTH_INTERVAL[0], TARGET_APPEAR_WIDTH_INTERVAL[1])
        self.y = rnd(TARGET_APPEAR_HEIGHT_INTERVAL[0], TARGET_APPEAR_HEIGHT_INTERVAL[1])
        self.life_time = TARGET_LIFETIME

    def create2(self, x, y, dx, dy):
        """Creates Target object in defined place x, y w/ defined velocity dx, dy."""
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.r = rnd(TARGET_APPEAR_RADIUS_INTERVAL[0], TARGET_APPEAR_RADIUS_INTERVAL[1])
        self.angle = count_angle(0, 0, self.dx, self.dy)
        self.life_time = SHELL_LIFETIME

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
        """Move itself by one tick, recalculates angle"""
        if self.life_time > 0:
            # For x coordinate far of border:
            if 0 + self.r < self.x + self.dx < CANVAS_WIDTH - self.r:
                self.x += self.dx
                self.angle = count_angle(0, 0, self.dx, self.dy)
            else:  # each vertical border collision
                self.angle = count_angle(0, 0, self.dx, self.dy)
                self.dx = -self.dx * FRICTION_CONSTANT
                self.dy *= FRICTION_CONSTANT
                self.x += self.dx
            if -0.3 <= self.dx <= 0.3:
                self.dx = 0
                self.angle = count_angle(0, 0, self.dx, self.dy)
            # For y coordinate:
            if 0 + self.r < self.y + self.dy < CANVAS_HEIGHT - self.r:
                self.y += self.dy
                self.dy += GRAVITY_CONSTANT
                self.angle = count_angle(0, 0, self.dx, self.dy)
            else:  # each horizontal border collision
                self.angle = count_angle(0, 0, self.dx, self.dy)
                self.dy = -self.dy * FRICTION_CONSTANT
                self.dx *= FRICTION_CONSTANT
                self.y += self.dy
                self.dy += GRAVITY_CONSTANT

            if self.y + self.dy >= CANVAS_HEIGHT - self.r and -3 <= self.dy <= 3:
                self.dy = 0
                self.angle = count_angle(0, 0, self.dx, self.dy)

            self.life_time -= 1
        else:
            self.die()

    def rebound(self, target):
        x2 = target.x
        x = x1 = self.x
        y2 = target.y
        y = y1 = self.y
        r2 = target.r
        r1 = self.r
        dx = self.dx
        dy = self.dy

        # touching point
        xc = (x2 - x1) * (r1 / (r1 + r2)) + x1
        yc = (y2 - y1) * (r1 / (r1 + r2)) + y1

        # slopes of line connecting centers and normal-line to it
        if x2 != x1:
            center_slope = (y2 - y1) / (x2 - x1)
            if center_slope == 0:
                normal_slope = m.inf
            else:
                normal_slope = 1 / center_slope
        else:
            center_slope = m.inf
            normal_slope = 0

        # need to get the second point on tangency
        if normal_slope != m.inf:
            normal_intercept = yc - xc * normal_slope
            xc2 = 0
            yc2 = normal_intercept
        else:
            xc2 = xc
            yc2 = 0

        new_vector = vector_reflection(xc, yc, xc2, yc2, x, y, x + dx, y + dy)

        self.dx = (new_vector[2] - new_vector[0])
        self.dy = (new_vector[3] - new_vector[1])

    def pop_out(self, target):
        x2 = target.x
        x = x1 = self.x
        y2 = target.y
        y = y1 = self.y
        r2 = target.r
        r1 = self.r
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        self.x = x1 - (x2 - x1) * (L / (r1 + r2)) * (r1 / (r1 + r2))
        self.y = y1 - (y2 - y1) * (L / (r1 + r2)) * (r1 / (r1 + r2))

        target.x = x2 + (x2 - x1) * (L / (r1 + r2)) * (r2/(r1+r2))
        target.y = y2 + (y2 - y1) * (L / (r1 + r2)) * (r2/(r1+r2))
        new_L = ((target.x - self.x) ** 2 + (target.y - self.y) ** 2) ** 0.5

    def print_yourself(self):
        print('x = ', self.x, 'y = ', self.y)
        print('r = ', self.r, 'id = ', self.id)


class Shell(IGameActor):
    def __init__(self, x=0, y=0, dx=0, dy=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.angle = count_angle(0, 0, self.dx, self.dy)
        self.color = from_rgb((rnd(0, 255), rnd(0, 255), rnd(0, 255)))
        self.life_time = SHELL_LIFETIME
        self.r = SHELL_INIT_RADIUS
        self.id = 0  # id == 0, shell hasn't been drawn

    def _set_shell_params(self, x, y, dx, dy):
        """Creates a ball of random color in defined pos and velocity, and random color."""
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.angle = count_angle(0, 0, self.dx, self.dy)
        self.color = from_rgb((rnd(0, 255), rnd(0, 255), rnd(0, 255)))
        self.life_time = SHELL_LIFETIME

    def die(self):
        self.life_time = 0
        canvas.delete(self.id)  # delete from canvas
        self.id = 0  # delete from physics, shell shouldn't be moved

    def kill_target(self, target):
        """Twiches die method of target"""
        target.die()

    def move(self):
        """Moves itself by one tick"""
        if self.life_time > 0:  # at each tick physics done:
            if 0 + self.r < self.x + self.dx < CANVAS_WIDTH - self.r:
                self.x += self.dx
                self.angle = count_angle(0, 0, self.dx, self.dy)
            else:  # each vertical border collision
                self.angle = count_angle(0, 0, self.dx, self.dy)
                self.dx = -self.dx * FRICTION_CONSTANT
                self.dy *= FRICTION_CONSTANT
                self.x += self.dx
            if -0.3 <= self.dx <= 0.3:
                self.dx = 0
                self.angle = count_angle(0, 0, self.dx, self.dy)
            if 0 + self.r < self.y + self.dy < CANVAS_HEIGHT - self.r:
                self.y += self.dy
                self.dy += GRAVITY_CONSTANT
                self.angle = count_angle(0, 0, self.dx, self.dy)
            else:  # each horizontal border collision
                self.angle = count_angle(0, 0, self.dx, self.dy)
                self.dy = -self.dy * FRICTION_CONSTANT
                self.dx *= FRICTION_CONSTANT
                self.y += self.dy
                self.dy += GRAVITY_CONSTANT

            if self.y + self.dy >= CANVAS_HEIGHT - self.r and -3 <= self.dy <= 3:
                self.dy = 0
                self.angle = count_angle(0, 0, self.dx, self.dy)

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

    def rebound(self, shell):
        x2 = shell.x
        x = x1 = self.x
        y2 = shell.y
        y = y1 = self.y
        r2 = shell.r
        r1 = self.r
        dx = self.dx
        dy = self.dy

        # touching point
        xc = (x2 - x1) * (r1 / (r1 + r2)) + x1
        yc = (y2 - y1) * (r1 / (r1 + r2)) + y1

        # slopes of line connecting centers and normal-line to it
        if x2 != x1:
            center_slope = (y2 - y1) / (x2 - x1)
            if center_slope == 0:
                normal_slope = m.inf
            else:
                normal_slope = 1 / center_slope

        else:
            center_slope = m.inf
            normal_slope = 0

        # need to get the second point on tangency
        if normal_slope != m.inf:
            normal_intercept = yc - xc * normal_slope
            xc2 = 0
            yc2 = normal_intercept
        else:
            xc2 = xc
            yc2 = 0
        new_vector = vector_reflection(xc, yc, xc2, yc2, x, y, x + dx, y + dy)

        self.dx = (new_vector[2] - new_vector[0])
        self.dy = (new_vector[3] - new_vector[1])

    def pop_out(self, shell):
        x2 = shell.x
        x = x1 = self.x
        y2 = shell.y
        y = y1 = self.y
        r2 = shell.r
        r1 = self.r
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        self.x = x1 - (x2 - x1) * (L / (r1 + r2)) * (r1 / (r1 + r2))
        self.y = y1 - (y2 - y1) * (L / (r1 + r2)) * (r1 / (r1 + r2))

        shell.x = x2 + (x2 - x1) * (L / (r1 + r2)) * (r2 / (r1 + r2))
        shell.y = y2 + (y2 - y1) * (L / (r1 + r2)) * (r2 / (r1 + r2))
        new_L = ((shell.x - self.x) ** 2 + (shell.y - self.y) ** 2) ** 0.5

    def print_yourself(self):
        print('x =', self.x, 'y =', self.y)
        print('dx =', self.dx, 'dy =', self.dy)
        print('color =', self.color, 'id =', self.id)


if __name__ == '__main__':
    main()
