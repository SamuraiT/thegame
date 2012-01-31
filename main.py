# ------------------------------------------------------------------
# main.py
# 
# Initialise stuff, handle events, main loop
# ------------------------------------------------------------------

import pygame
import pygtk
import gtk
import threading
import os
import sys
import traceback

from vec2d import Vec2d
import shared
import gui
import objects
import player

window_pos = (150, 100) #from top-left
window_size = (800, 600)
gtk_pos = (150, 100) #from bottom-right
gtk_size = (640, 480)

background_color = (0,0,0) #black
fps = 40.0

shared.stop_game = False

def init():
    # set WM_CLASS under X
    os.environ['SDL_VIDEO_X11_WMCLASS'] = "thegame"
    gtk.gdk.set_program_class("thegame")

    # initialise gtk
    gtk.threads_init()

    shared.gtkwin = gtk.Window(gtk.WINDOW_TOPLEVEL)
    shared.gtkwin.show()
    gtkscreen = shared.gtkwin.get_screen()
    shared.gtkwin.move(gtkscreen.get_width() - gtk_size[0] - gtk_pos[0],
            gtkscreen.get_height() - gtk_size[1] - gtk_pos[0])
    shared.gtkwin.resize(*gtk_size)

    shared.gui = gui.Gui()
    shared.gui.init()

    # initialise pygame
    pygame.init()
    global clock
    clock = pygame.time.Clock()
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % window_pos
    shared.canvas = pygame.display.set_mode(window_size)

    # set window titles
    shared.gtkwin.set_title("thegame - code editor")
    pygame.display.set_caption("thegame - world", "thegame")

    # create player
    p = objects.create(player._Player, Vec2d(window_size) / 2)
    shared.userspace['player'] = p.proxy

    # set keybindings
    resetKeybindings()

def resetKeybindings():
    # set default keybindings
    shared.userspace['keybindings'] = {
        pygame.K_LEFT: "player.walk('left')",
        pygame.K_RIGHT: "player.walk('right')",
        pygame.K_UP: "player.walk('up')",
        pygame.K_DOWN: "print 'x'; import shared; print shared.userspace;",
    }

def safe_exec(code):
    exec(code, shared.userspace, shared.userspace)

def handleEvents():
    # pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False

            if 'keybindings' not in shared.userspace or type(shared.userspace['keybindings']) is not dict:
                resetKeybindings()
            if event.key in shared.userspace['keybindings']:
                code = shared.userspace['keybindings'][event.key]
                safe_exec(code)

    return True

def loop():
    # run gtk main loop in separate thread
    class GtkLoop(threading.Thread):
        def run(self):
            gtk.main()
    gtkLoop = GtkLoop()
    gtkLoop.start()

    # game loop
    while not shared.stop_game:
        # events
        if not handleEvents():
            break

        # action!
        # TODO: fix elapsed time handling!
        elapsed = 1 / fps
        map(lambda o: o.step(elapsed), objects.world)
        shared.gui.step(elapsed)

        # draw pretty things
        shared.canvas.fill(background_color)
        map(lambda o: o.draw(), objects.world)
        pygame.display.update()

        # not so fast
        clock.tick(fps)

def end():
    objects.destroy_all()

    shared.gui.quit()

    gtk.threads_enter()
    gtk.main_quit()
    gtk.threads_leave()

    pygame.quit()

# play the game!
try:
    init()
    loop()
except Exception, e:
    tb = sys.exc_info()[2]
    traceback.print_exception(e.__class__, e, tb)
end()
