import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Point, GraphicException
from random import random
from math import sqrt

from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.spread import pb
from twisted.internet import reactor



def calculate_points(x1, y1, x2, y2, steps=5):
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt(dx * dx + dy * dy)
    if dist < steps:
        return None
    o = []
    m = dist / steps
    for i in xrange(1, int(m)):
        mi = i / m
        lastx = x1 + dx * mi
        lasty = y1 + dy * mi
        o.extend([lastx, lasty])
    return o



class Tracker(FloatLayout):
    def connect(self):
        win = self.get_parent_window()
        self.real_start_x = 10
        self.real_start_y = 10
        self.real_height = self.height - 20
        self.real_width = self.width - 20

        print self.real_height, self.real_width

        self._ready = False;
        self._corners = [];
        pass

    def _init_corner(self, touch):
        self._corners.append(touch)
        if len(self._corners) == 4:
            self._init_keystone()
            self._ready = True

    def _init_keystone(self):
        self._corners.sort(key = lambda touch: touch.y)

        if self._corners[0].x > self._corners[1].x:
            temp = self._corners[0]
            self._corners[0] = self._corners[1]
            self._corners[1] = temp

        if self._corners[2].x > self._corners[3].x:
            temp = self._corners[2]
            self._corners[2] = self._corners[3]
            self._corners[3] = temp

        self.start_y = self._corners[0].y
        self.height1 = self._corners[2].y - self.start_y

        self.start_x1 = self._corners[0].x
        self.start_x2 = self._corners[2].x
        self.width1 = self._corners[1].x - self._corners[0].x
        self.width2 = self._corners[3].x - self._corners[2].x

        print (self._corners[0].x, self._corners[0].y)
        print (self._corners[1].x, self._corners[1].y)
        print (self._corners[2].x, self._corners[2].y)
        print (self._corners[3].x, self._corners[3].y)


    def rectify(self, touch):
        field_percent = (touch.y - self.start_y) / self.height1
        y = self.real_start_y + (self.real_height * field_percent)

        start_x = (1 - field_percent) * self.start_x1 + field_percent * self.start_x2
        width = (1 - field_percent) * self.width1 + field_percent * self.width2
        x = self.real_start_x + (self.real_width * ((touch.x - start_x) / width))

        print (touch.x, touch.y)
        print x, y
        return x, y


    def on_touch_down(self, touch):
        ud = touch.ud
        ud['group'] = g = str(touch.uid)

        if not self._ready:
            self._init_corner(touch)
            return;

        x, y = self.rectify(touch)

        ud = touch.ud
        ud['group'] = g = str(touch.uid)
        with self.canvas:
            ud['color'] = Color(random(), 1, 1, mode='hsv', group=g)
            ud['lines'] = Point(
                points = (x, y),
                source = 'particle.png',
                pointsize = 5,
                group=g)

    def on_touch_move(self, touch):
        return

        if not self._ready:
            return

        x, y = self.rectify(touch)

        ud = touch.ud

        try:
            ud['lines'] = Point(
                points = (x, y),
                source = 'particle.png',
                pointsize = 5,
                group=ud['group'])
        except GraphicException:
            pass

    def on_touch_up(self, touch):
        ud = touch.ud
        #self.canvas.remove_group(ud['group'])

    def update_touch_label(self, label, touch):
        label.text = 'ID: %s\nPos: (%d, %d)\nClass: %s' % (
            touch.id, touch.x, touch.y, touch.__class__.__name__)
        label.texture_update()
        label.pos = touch.pos
        label.size = label.texture_size[0] + 20, label.texture_size[1] + 20


class TrackerApp(App):
    title = 'Touchtracer'
    icon = 'icon.png'

    def build(self):
        return Tracker()

    def on_start(self):
        pass
        self.root.connect()
#        reactor.run()

if __name__ in ('__main__', '__android__'):
    TrackerApp().run()
