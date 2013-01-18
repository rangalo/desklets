#! /usr/bin/env python

import subprocess, shlex


class KbdLayout:
    def __init__(self,aIndFile=None,aLayoutFile=None):
        self._layout     = "us"
        self._index      = 0
        if not aIndFile:
            self._indexFile = "/home/hardik/.xkbSwitch/index"
        else:
            self._indexFile = aIndFile
        if not aLayoutFile:
            self._layoutFile = "/home/hardik/.xkbSwitch/xkb_layouts"
        else:
            self._layoutFile = aLayoutFile

    def update(self):
        try:
            lIndexFile = open(self._indexFile,"r")
            lIndex = int(lIndexFile.read())
        except:
            lIndexFile = open(self._indexFile,"w")
            lIndexFile.write(str(self._index))
            lIndex = self._index

        lIndexFile.close()

        self._index = lIndex

        try:
            lLayoutFile = open(self._layoutFile,"r")
            lLayouts    = lLayoutFile.readlines()
        except:
            lLayoutFile = open(self._layoutFile,"w")
            lLayoutFile.write(self._layout)
            lLayouts = [self._layout]
        lLayoutFile.close()

        self._layout = (lLayouts[lIndex]).strip()

        # increment
        lIndex = lIndex + 1

        lMax = len(lLayouts)
        if lIndex == lMax:
            lIndex = 0

        self._nextIndex  = lIndex
        self._nextLayout = (lLayouts[lIndex]).strip()


    def getNextLayout(self):
        self.update()
        return self._nextLayout

    def getCurrentLayout(self):
        self.update()
        return self._layout

    def switchKbdLayout(self):
        self.update()
        lCmd = "setxkbmap -layout " + self._nextLayout
        # print(lCmd)
        args = shlex.split(lCmd)
        process  = subprocess.Popen(args)
        lStatus = process.wait()

        if lStatus == 0:
            lIndexFile = open(self._indexFile,"w")
            lIndexFile.write(str(self._nextIndex))
            lIndexFile.close()
            self.update()
            print(self._layout)
        else:
            print("Could not set the keybord layout: ",  self._nextLayout, "\nError:"+lOutput)


        





        
        
