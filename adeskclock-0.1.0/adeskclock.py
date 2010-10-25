#! /usr/bin/env python

"""
Copyright (C) 2005 Jon McCormack <jonmack@users.sourceforge.net>

Released under the GPL, version 2. Except the artwork, which is released
pursuant to the restrictions imposed by their authors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies of the Software and its documentation and acknowledgment shall be
given in the documentation and software packages that this Software was
used.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

========

# adeskclock - simple analogue desktop clock (adesklet)
# version 0.1.0

Thanks
======

Thanks go to Sylvain Fourmanoit and Mike Pirnat for their adesklets
(see adesklets.sourceforge.net) to study from :)

Feature list
============

- Configurable skin                         DONE
- Clock hand rotation pivot points          DONE
- Clockface graphic on separate layer
- Skin configuration files
- General configuration files
- Resizable

Known Bugs:
===========

# FIXME: Second hand anchor point moves when in 9-3 half of clock
#    Related wierdness of all hands in this sector perhaps?
#    (DOES NOT APPLY TO RASTER IMAGES)
"""

import adesklets
import math
import time
from os.path import dirname

class ADeskClock(adesklets.Events_handler):
    # The main class for this desk-top analogue clock

    # default configuration to fall back on
    defaultConfig = {
        'skin' : 'sidux',
        'height' : 128,
        'width' : 128,
        'showSecondHand' : True,
        'refreshRate' : 1
    }

    defaultSkinConfig = {
        'hourPivotX' : 2,
        'hourPivotY' : 16,
        'minutePivotX' : 2,
        'minutePivotY' : 16,
        'secondPivotX' : 1,
        'secondPivotY' : 16
    }

    # constants
    SKINS_SUBDIR = '/skins/'
    CLOCK_FACE_IMAGE = 'clockface.png'
    HOUR_HAND_IMAGE = 'hourhand.png'
    MINUTE_HAND_IMAGE = 'minutehand.png'
    SECOND_HAND_IMAGE = 'secondhand.png'

    # TODO: Eventually loadable
    config = defaultConfig
    skinConfig = defaultSkinConfig
    currentHour = 0
    currentMinute = 0
    currentSecond = 0

    def __init__(self, basedir):
        # need one of these for adesklets

        # if we're not here, then where are we?!
        if len(basedir) == 0:
            self.basedir = '.'
        else:
            self.basedir = basedir

        # ready to go!
        adesklets.Events_handler.__init__(self)

    def __del__(self):
        # need this when adesklets kills us

        adesklets.Events_handler.__del__(self)

    def quit(self):
        # just being polite

        print("Quitting adeskclock...")

    def ready(self):
        # need this when adesklets is ready for me

        # I have an ID?
        self.ID = adesklets.get_id()

        # width and height of the window
        self.w = self.config['width']
        self.h = self.config['height']

        # set up a custom right-click menu
        adesklets.menu_add_separator()
        adesklets.menu_add_submenu('Configure')
        adesklets.menu_add_item('EditConfigFile')
        adesklets.menu_add_item('ToggleSecondHand')
        adesklets.menu_end_submenu()

        # set up the initial display window
        adesklets.context_set_image(0)
        #adesklets.context_set_color(0,0,0,0)
        #adesklets.context_set_blend(False)
        adesklets.window_resize(self.w, self.h)
        adesklets.window_set_transparency(True)

        # get a buffer for later
        self.buffer = adesklets.create_image(self.w, self.h)

        # load skin from config file (+ render refresh)
        self.loadSkin(self.config['skin'])

        # cross your fingers!
        adesklets.window_show()

    def loadSkin(self, skinName):
        # load images from a given skin at adeskclock/skins/<skinName>

        # load clock face
        self.clockFace = \
                adesklets.load_image(self.basedir + self.SKINS_SUBDIR +
                self.config['skin'] + '/' + self.CLOCK_FACE_IMAGE)
        adesklets.context_set_image(self.clockFace)
        self.faceWidth = adesklets.image_get_width()
        self.faceHeight = adesklets.image_get_height()

        # hour hand
        self.hourHand = \
                adesklets.load_image(self.basedir + self.SKINS_SUBDIR +
                self.config['skin'] + '/' + self.HOUR_HAND_IMAGE)
        adesklets.context_set_image(self.hourHand)
        self.hourWidth = adesklets.image_get_width()
        self.hourHeight = adesklets.image_get_height()

        # minute hand
        self.minuteHand = \
                adesklets.load_image(self.basedir + self.SKINS_SUBDIR +
                self.config['skin'] + '/' + self.MINUTE_HAND_IMAGE)
        adesklets.context_set_image(self.minuteHand)
        self.minuteWidth = adesklets.image_get_width()
        self.minuteHeight = adesklets.image_get_height()

        # second hand
        self.secondHand = \
                adesklets.load_image(self.basedir + self.SKINS_SUBDIR +
                self.config['skin'] + '/' + self.SECOND_HAND_IMAGE)
        adesklets.context_set_image(self.secondHand)
        self.secondWidth = adesklets.image_get_width()
        self.secondHeight = adesklets.image_get_height()

        # force full refresh
        self.renderBackground()
        self.renderForeground()

        # DEBUGGING
        print adesklets.images_info()
        print self.buffer
        self.quit()
        '''
        print self.faceWidth
        print self.faceHeight
        print self.hourWidth
        print self.hourHeight
        print self.minuteWidth
        print self.minuteHeight
        print self.secondWidth
        print self.secondHeight
        '''

    def alarm(self):
        # need this to tell adesklets to update me

        self.block()
        # just get the time once, and only when we just need it
        self.refreshTime()
        self.renderForeground()
        self.unblock()

        return self.config['refreshRate']

    def menu_fire(self, delayed, menu_id, item, something=0):
        if item == "ToggleSecondHand":
            self.config['showSecondHand'] = not self.config['showSecondHand']        
        #elif item == "EditConfigFile":
        #    editor = getenv('EDITOR')
        #    if editor:
        #        system('xterm -e %s %s/config.txt &' % (editor, self.basedir))

    def background_grab(self, delayed):
        self.loadSkin(self.config['skin'])
        #if not delayed:
        #    self.loadSkin(self.config['skin'])

    def refreshTime(self):
        # refresh time variables to be used anywhere else

        currentTime = time.localtime(time.time())
        #  0     1   2   3   4   5   ...
        # (YYYY, MM, DD, HH, MM, SS, ...)
        self.currentHour = currentTime[3]
        self.currentMinute = currentTime[4]
        self.currentSecond = currentTime[5]

        # DEBUGGING
        #print self.currentHour
        #print self.currentMinute
        #print self.currentSecond

    def renderBackground(self):
        # draws the clock face to a background layer
        print 'background'

        # clear the canvas
        #adesklets.context_set_image(self.buffer)
        #adesklets.context_set_blend(False)
        #adesklets.context_set_color(0, 0, 0, 0)
        adesklets.image_fill_rectangle(0, 0, self.w, self.h)
        adesklets.context_set_blend(True)

        # render background to buffer
        # D'oh! Make sure it's self.buffer, not self.bugger ;)
        adesklets.context_set_image(1)
        adesklets.blend_image_onto_image(self.clockFace, 1,
                0, 0, self.faceWidth, self.faceHeight,
                0, 0, self.w, self.h)
        

    def renderForeground(self):
        # draws the clock hands to a foreground layer

        # clear the canvas
        adesklets.context_set_image(self.buffer)
        adesklets.context_set_blend(False)
        adesklets.context_set_color(0, 0, 0, 0)
        adesklets.image_fill_rectangle(0, 0, self.w, self.h)
        adesklets.context_set_blend(True)

        # hands rotate around middle of the window
        #a = self.pivotX
        #b = self.pivotY
        a = self.w / 2
        b = self.h / 2

        """
        Pivoting:

        Pivot vector p has origin at top-left corner of graphic (0,0) and points
        to pivot point (x increasing to the right, y increasing downwards).

        Rotation matrix for this coordinate system (angles defined from 3
        o'clock increasing clockwise) given by

            R = | cos(theta)    -sin(theta) |
                | sin(theta)     cos(theta) |

        Therefore, new position r' translated by rotated p

            r' = r - Rp

        Or,

            rx' = rx - ( px*cos(theta) - py*sin(theta) )
            py' = ry - ( px*sin(theta) + py*cos(theta) )
        """

        # hour hand
        ang = self.getHourAngle()
        sina = math.sin(ang)
        cosa = math.cos(ang)
        px = self.skinConfig['hourPivotX']
        py = self.skinConfig['hourPivotY']
        rx = a - (px*cosa - py*sina)
        ry = b - (px*sina + py*cosa)
        #adesklets.blend_image_onto_image_at_angle(self.hourHand, 1,
        #        0, 0, self.hourWidth, self.hourHeight, rx, ry,
        #        self.hourWidth*cosa, self.hourWidth*sina)
        adesklets.blend_image_onto_image_at_angle(self.hourHand, 1,
                0, 0, self.w, self.h, rx, ry,
                self.w*cosa, self.w*sina)

        # minute hand
        ang = self.getMinuteAngle()
        sina = math.sin(ang)
        cosa = math.cos(ang)
        px = self.skinConfig['minutePivotX']
        py = self.skinConfig['minutePivotY']
        rx = a - (px*cosa - py*sina)
        ry = b - (px*sina + py*cosa)
        #adesklets.blend_image_onto_image_at_angle(self.minuteHand, 1,
        #        0, 0, self.minuteWidth, self.minuteHeight, rx, ry,
        #        self.minuteWidth*cosa, self.minuteWidth*sina)
        adesklets.blend_image_onto_image_at_angle(self.minuteHand, 1,
                0, 0, self.w, self.h, rx, ry,
                self.w*cosa, self.w*sina)

        # second hand
        if (self.config['showSecondHand']):
            ang = self.getSecondAngle()
            sina = math.sin(ang)
            cosa = math.cos(ang)
            px = self.skinConfig['secondPivotX'] #print px
            py = self.skinConfig['secondPivotY'] #print py
            rx = a - (px*cosa - py*sina) #print rx
            ry = b - (px*sina + py*cosa) #print ry
            #adesklets.blend_image_onto_image_at_angle(self.secondHand, 1,
            #        0, 0, self.secondWidth, self.secondHeight, rx, ry,
            #        self.secondWidth*cosa, self.secondWidth*sina)
            adesklets.blend_image_onto_image_at_angle(self.secondHand, 1,
                    0, 0, self.w, self.h, rx, ry,
                    self.w*cosa, self.w*sina)

        # render buffer to screen
        adesklets.context_set_image(0)
        adesklets.context_set_blend(False)
        adesklets.blend_image_onto_image(self.buffer, 1,
                0, 0, self.w, self.h,
                0, 0, self.w, self.h)        
        adesklets.context_set_blend(True)

    def getHourAngle(self):
        # calculates the angle for the current hour

        # work out the which fifth of the hour we are in
        f = math.floor(self.currentMinute / 12.0)

        # get the angle of the current hour
        ang = self.calcAngle(self.currentHour, 12.0)

        # add on 6 degrees for every fifth of an hour
        ang += (f * math.pi/24.0)

        return ang

    def getMinuteAngle(self):
        # calculates the angle in radians for the current minute

        return self.calcAngle(self.currentMinute, 60.0)

    def getSecondAngle(self):
        # calculates the angle in radians for the current second

        return self.calcAngle(self.currentSecond, 60.0)

    def calcAngle(self, frac, total):
        # calculates the angle in radians for a frac of the total

        #return ((-math.pi/2) - (2*math.pi*frac/total))
        f = 2*math.pi*frac/total - math.pi
        #print f
        return f

# apparently this starts this whole thing off...
ADeskClock(dirname(__file__)).pause()
