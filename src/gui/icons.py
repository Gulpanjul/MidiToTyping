import math
import tkinter as tk


def plus(c, color, size=16, tag='icon'):
    m, p = size / 2, size / 4
    c.create_line(p, m, size-p, m, fill=color, width=1.5, capstyle='round', tags=tag)
    c.create_line(m, p, m, size-p, fill=color, width=1.5, capstyle='round', tags=tag)


def minus(c, color, size=16, tag='icon'):
    m, p = size / 2, size / 4
    c.create_line(p, m, size-p, m, fill=color, width=1.5, capstyle='round', tags=tag)


def arrow_left(c, color, size=16, tag='icon'):
    m = size / 2
    p = size * 0.22
    c.create_line(p, m, size-p, m, fill=color, width=1.5, capstyle='round', tags=tag)
    c.create_line(p, m, p+size*0.25, m-size*0.25, fill=color, width=1.5, capstyle='round', tags=tag)
    c.create_line(p, m, p+size*0.25, m+size*0.25, fill=color, width=1.5, capstyle='round', tags=tag)


def sun(c, color, size=16, tag='icon'):
    m = size / 2
    r = size * 0.19
    c.create_oval(m-r, m-r, m+r, m+r, outline=color, width=1.3, tags=tag)
    r1, r2 = size * 0.30, size * 0.42
    for ang in range(0, 360, 45):
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        c.create_line(m+dx*r1, m+dy*r1, m+dx*r2, m+dy*r2,
                      fill=color, width=1.3, capstyle='round', tags=tag)


def moon(c, color, size=16, tag='icon'):
    pad = size * 0.16
    c.create_arc(pad, pad, size-pad, size-pad, start=50, extent=260,
                 outline=color, width=1.5, style='arc', tags=tag)


def info(c, color, size=16, tag='icon'):
    pad = size * 0.14
    m = size / 2
    c.create_oval(pad, pad, size-pad, size-pad, outline=color, width=1.3, tags=tag)
    r = size * 0.05
    c.create_oval(m-r, pad+size*0.17, m+r, pad+size*0.17+r*2,
                  fill=color, outline='', tags=tag)
    c.create_line(m, m-size*0.04, m, size-pad-size*0.17,
                  fill=color, width=1.4, capstyle='round', tags=tag)


def play(c, color, size=16, tag='icon'):
    p = size * 0.22
    c.create_polygon(p, p, p, size-p, size-p, size/2,
                     fill=color, outline=color, tags=tag)


def x_mark(c, color, size=16, tag='icon'):
    p = size / 4
    c.create_line(p, p, size-p, size-p, fill=color, width=1.5, capstyle='round', tags=tag)
    c.create_line(size-p, p, p, size-p, fill=color, width=1.5, capstyle='round', tags=tag)


def search(c, color, size=16, tag='icon'):
    pad = size * 0.15
    r = size * 0.28
    c.create_oval(pad, pad, pad+r*2, pad+r*2, outline=color, width=1.3, tags=tag)
    c.create_line(pad+r*1.55, pad+r*1.55, size-pad*0.5, size-pad*0.5,
                  fill=color, width=1.5, capstyle='round', tags=tag)


def make_icon_button(parent, icon_fn, cmd, bg, color, hover, size=16, pad_x=8, pad_y=5):
    w, h = size + pad_x*2, size + pad_y*2
    c = tk.Canvas(parent, width=w, height=h, bg=bg, highlightthickness=0, bd=0, cursor='hand2')
    c._icon_fn, c._icon_size, c._icon_pad = icon_fn, size, (pad_x, pad_y)
    c._icon_color, c._bg, c._hov = color, bg, hover
    _paint(c)
    c.bind('<Button-1>', lambda _: cmd())
    c.bind('<Enter>', lambda _: c.configure(bg=hover))
    c.bind('<Leave>', lambda _: c.configure(bg=c._bg))
    return c


def _paint(c):
    c.delete('icon')
    c._icon_fn(c, c._icon_color, c._icon_size, 'icon')
    c.move('icon', *c._icon_pad)


def retint(c, color, bg=None, hover=None):
    c._icon_color = color
    if bg is not None:   c._bg = bg; c.configure(bg=bg)
    if hover is not None: c._hov = hover
    _paint(c)
