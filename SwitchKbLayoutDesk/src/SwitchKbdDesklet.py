#! /usr/bin/env python

import adesklets
from time import time
from os.path import dirname, join, abspath
from KbdLayout import KbdLayout

class Config(adesklets.ConfigFile):
    cfg_default = { 'layouts' : [('us.gif','us'),('de.gif','de')],
                   'width'   : 50,
                   'height'  : 30 ,
                   'click_delay' : 2,
                   'refreshrate' : 2}
    



    def __init__(self,id,filename):
        adesklets.ConfigFile.__init__(self,id,filename)



class SwitchKbdEvent(adesklets.Events_handler):

    def __init__(self,basedir=None):
        print "arg: "+basedir
        if not basedir:
            print "basedir is empty"
            self._basedir = ".."
        else:
            self._basedir = basedir
               
        #self.logfile = open('/home/hardik/pythonScripts/SwitchKbLayoutDesk/src/log','w')
        print "basedir: "+self._basedir
        adesklets.Events_handler.__init__(self)



    def __del__(self):
        adesklets.Events_handler.__del__(self)

    def ready(self):
        # real initialization takes place here
        #
        #self.logfile.write("Entering Ready")
        print self._basedir
        self.config = Config(adesklets.get_id(),join(self._basedir,"config.txt"))
        self._layout = ""
        self.lastClickTime = time()
        
        adesklets.window_resize(self.config['width'],self.config['height'])
        adesklets.window_set_transparency(True)
        

        self.renderFlag()
        

        adesklets.window_show()
        #self.logfile.write("\nExit Ready")
        
    
    def renderFlag(self):
        
        lKbdLayout = KbdLayout()
        #self.logfile.write("\nEntering renderFlag")
        try:
            lCurLayout = lKbdLayout.getCurrentLayout()
        except:
            print "\nsome error occured in KbdLayout\n";
        print lCurLayout+", Prev: "+self._layout
        if lCurLayout == self._layout:
            return

        self._layout = lCurLayout

        # Find Flag image for the current layout

        # Load the image files for the flags
        lFound = False
        for lFlag, lLayout in self.config['layouts']:
            if lCurLayout == lLayout:
                self._flag = adesklets.load_image(
                                        join(self._basedir,"img/"+lFlag))
                #print lFlag+" img: "+str(self._flag)
                lFound = True
                break
        
        
 
        adesklets.context_set_image(self._flag)
        self.flagWidth  = adesklets.image_get_width()
        self.flagHeight = adesklets.image_get_height()
        adesklets.context_set_image(0)
        adesklets.blend_image_onto_image(self._flag, 1, 0, 0,
                        self.flagWidth,self.flagHeight,
                        0, 0, self.config['width'],self.config['height'])

        #self.logfile.write("\nEntering renderFlag")
        
    def quit(self):
        print "Quitting..."

    def alarm(self):
        self.block()
        self.renderFlag()
        self.unblock()
        return self.config['refreshrate']

    def button_press(self, delayed, x, y, button):
        if button == 1:
            lNow = time()
            if (lNow - self.lastClickTime) < self.config['click_delay']:
                self.lastClickTime = lNow
                return
            self.lastClickTime = lNow
            lKbdLayout = KbdLayout()
            lKbdLayout.switchKbdLayout()
            self.renderFlag()

    def background_grab(self,delayed):
        self.renderFlag()
                
      
 
print abspath(dirname(__file__))
SwitchKbdEvent(dirname(abspath(dirname(__file__)))).pause()

