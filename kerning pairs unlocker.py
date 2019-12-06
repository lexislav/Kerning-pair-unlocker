#MenuTitle: Kerning pairs Unlocker
# -*- coding: utf-8 -*-
__doc__="""
Unlock kerning for selected pairs of glyphs
written by Alexandr Hudeček
"""

import GlyphsApp
import vanilla

#globals definitions
VERSION = "1.2"
SCRIPT_NAME = "Kering pairs Unlocker"
run = True

kernDic = None
allMasters =  True

def refreshGlobals():
    #reset values
    global kernDic
    kernDic = thisFont.kerningDict()
    return True
    
def testPrint():
	print kernDic
	return true
    
class AppController:
    
    #WINDOW SETTINGS
    editX = 180
    editY = 180
    textY  = 17
    spaceX = 10
    spaceY = 20
    windowWidth  = spaceX*3+editX*1.5
    windowHeight = 365
    popupAdjust = 3

    #init opens the window
    def __init__(self):
        if not run:
            return
        self.w = self.getWindow()
        self.w.open()
        pass
        
    def __del__(self):
        pass
        
    def process(self, sender):
        #run the process spinner
        self.w.spinner.start()
        #read teh setting from window
        settings = self.getSettings()
        #run the actual process/worker
        worker = AppWorker()
        worker.start(settings)
        #closee the spinner and the window
        self.w.spinner.stop()
        self.w.close()
        
    def pairsCleanup(self,lines):
        pairs = []
        workingArray = []
        wrongLines = False
        #clean white spaces, get the pairs
        for line in lines:
            workingArray.append(line.split())
        #remove not pair lines
        for line in workingArray:
            if len(line) == 2:
                pairs.append(line)
            else:
                wrongLines = True
        if wrongLines:
            #print info that there was some errors on some lines
            print "Script will skipp some lines as there is an input hodgepodge."
        return pairs

    
    def getSettings(self):      
        try:
            c=int(self.w.specifyCorrection.get())
        except ValueError:
            c=0
        out = {
                "lockSide": "left" if self.w.side.get() == 0 else "right",
                "pairs": self.pairsCleanup(self.w.pairsDefinition.get().split("\n")),
                "correction": c,
                "allMasters": self.w.allMasters.get()
        }
        return out
    
    def getWindow(self):
        #open window
        w = vanilla.FloatingWindow(
            ( self.windowWidth, self.windowHeight ), # default window size
            SCRIPT_NAME + " " + VERSION, # window title
            minSize = ( self.windowWidth, self.windowHeight ), # minimum size (for resizing)
            maxSize = ( self.windowWidth + 540, self.windowHeight + 140), # maximum size (for resizing)
            autosaveName = "com.OdOka.kerningPairdUnlocker.mainwindow" # stores last window position and size
            )

        #UI
        height = self.spaceY
        #radio select
        w.text0 = vanilla.TextBox( (self.spaceX, height, 120, self.textY), "Lock position:", sizeStyle='regular' )
        w.side = vanilla.RadioGroup( (self.spaceX+130, height, 120, self.textY), ["Left", "Right"], isVertical = False, sizeStyle='regular' )
        w.side.set(0)
        height += self.textY*2
        w.text2 = vanilla.TextBox( (self.spaceX, height, 120, self.textY), "Specify correction:", sizeStyle='regular' )
        w.specifyCorrection = vanilla.EditText( (self.spaceX + 130, height, -15, 20), "0", sizeStyle = 'regular' )
        height += self.spaceY*2
        #editbox
        w.text1 = vanilla.TextBox( (self.spaceX, height, -self.spaceX, self.textY*2), "Define pairs to unlock\n(use glyph names)", sizeStyle='regular' )
        height += self.spaceY*2
        w.pairsDefinition = vanilla.EditText( (self.spaceX, height, -self.spaceX, -self.spaceY-35), "", continuous=False, placeholder = "Paste pairs here\nOne pair per line", sizeStyle = 'regular' )
        height += self.spaceY*8
        #unheck to process only current master
        w.allMasters = vanilla.CheckBox((self.spaceX, -self.spaceY-20, -self.spaceX - 80, -self.spaceY), "Process all masters", value=True, sizeStyle = 'regular')
        height += self.spaceY*2
        #process button
        w.buttonProcess = vanilla.Button((-15 - 40, -15 - 20, -15, -15), "Go", sizeStyle = 'regular', callback=self.process)
        w.setDefaultButton(w.buttonProcess)
        #spinner
        w.spinner = vanilla.ProgressSpinner((15, -15 - 16, 16, 16), sizeStyle = 'regular')

        return w

class AppWorker:
    
    def __init__(self):
        pass
        
    def start(self,settings):
        pairs = settings['pairs']
        if len(pairs) == 0:
            print "Ups, no pairs to work with."
            return
        self.getToThePoint(pairs,settings['lockSide'],settings['correction'],settings['allMasters'])
        return
        
    def getToThePoint(self,pairs,lockSide,correction,allMasters):
        if allMasters:
            proceedMasters = thisFont.masters
        else:
            proceedMasters = [selectedMaster]
        for master in proceedMasters:
            id = master.id
            for pair in pairs:
                leftGlyphName = pair[0]
                rightGlyphName = pair[1]
                if self.checkPairExistence(leftGlyphName,rightGlyphName,id):
                    self.unlockKerning(lockSide,leftGlyphName,rightGlyphName,correction,id)
        return
                
    def checkPairExistence(self,leftGlyphName,rightGlyphName,mid):
        if thisFont.glyphs[leftGlyphName] and thisFont.glyphs[rightGlyphName]:
            return True
        else:
            return False
            
    def unlockKerning(self,lockSide,leftGlyphName,rightGlyphName,correction,id):
        currentKerningForPair = 0
        currentKerningForPair = thisFont.kerningForPair(id, '@MMK_L_'+leftGlyphName, "@MMK_R_"+rightGlyphName)
        leftName = "@MMK_L_" + leftGlyphName
        rightName = "@MMK_R_" + rightGlyphName
        #has leftGlyph exception?
        if leftGlyphName in kernDic[id]:
            if rightGlyphName in kernDic[id][leftGlyphName]:
                currentKerningForPair = kernDic[id][leftGlyphName][rightGlyphName]
                rightName = rightGlyphName
            elif "@MMK_R_" + rightGlyphName in kernDic[id][leftGlyphName]:
                currentKerningForPair = kernDic[id][leftGlyphName]["@MMK_R_" + rightGlyphName]
            leftName = leftGlyphName
        elif "@MMK_L_"+leftGlyphName in kernDic[id]:
            if rightGlyphName in kernDic[id][leftName]:
                currentKerningForPair = kernDic[id][leftName][rightGlyphName]
                rightName = rightGlyphName
        #if currentKerning is not set, set it for -1
        if currentKerningForPair is None:
            currentKerningForPair = -1
        else: currentKerningForPair += correction
        if lockSide == "left":
            thisFont.setKerningForPair(id, leftName, rightGlyphName, currentKerningForPair)
        else:
            thisFont.setKerningForPair(id, leftGlyphName, rightName, currentKerningForPair)
        return
        
    
# Script start
try:
	thisFont = Glyphs.font
	firstMasterID = Font.masters[0].id
	selectedMaster = thisFont.selectedFontMaster
	masterID = selectedMaster.id
	if thisFont == None:
		run = False
	else:
		refreshGlobals()
		app = AppController()
		del app
except:
    print "No font or another startup error."
    pass