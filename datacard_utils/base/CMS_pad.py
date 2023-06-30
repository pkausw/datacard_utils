import ROOT as rt
from copy import deepcopy
from helperClass import helperClass

helper = helperClass()

# CMS_lumi
#   Initiated by: Gautier Hamel de Monchenault (Saclay)
#   Translated in Python by: Joshua Hardenbrook (Princeton)
#   Updated by:   Dinko Ferencek (Rutgers)
#

class CMS_pad(object):

    _cmsText=None
    _cmsTextFont=None
    _extraText=None
    _extraTextFont = None
    _lumiTextOffset = None
    _lumiTextSize = None
    _cmsTextSize = None
    _cmsTextOffset = None
    _hOffset = None
    _relPosX = None
    _relPosY = None
    _relExtraDY = None
    _extraOverCmsTextSize = None
    _writeExtraText = True
    _drawLogo =False
    _canvas = None
    _lumi_7TeV=None
    _lumi_8TeV=None
    _lumi_13TeV = None
    _lumi_sqrtS = None
    _hOffset = None
    _iPosX = 0
    _iPeriod = 4


    def __init__(
        self, extraText = "Preliminary", cmsText="CMS", cmsTextFont=61,
        lumitext="138 fb^{-1}", extraTextFont=52, lumiTextSize=0.6,
        lumiTextOffset=0.2, cmsTextSize=0.75, cmsTextOffset=0.1, hOffset=0,
        relPosX=0.045, relPosY=0.035, relExtraDY=1.2, extraOverCmsTextSize=0.76,
        iPosX = 0, iPeriod = 4, left_margin=0.15, right_margin=0.05,
        bottom_margin=0.15 , top_margin=0.05, width=700, height=500,
    ):

        self.setCMStext(cmsText)
        self.setCMStextfont(cmsTextFont)
        # _writeExtraText = True
        self.setExtraText(extraText)
        self.setExtraTextFont(extraTextFont)
        self.setLumiTextSize(lumiTextSize)
        self.__lumitext = ""
        self._lumiTextOffset   = 0.2

        self._cmsTextSize      = 0.75
        self._cmsTextOffset    = 0.1

        self._hOffset = 0

        self._relPosX    = 0.045
        self._relPosY    = 0.035
        self._relExtraDY = 1.2

        self._extraOverCmsTextSize  = 0.76

        if not lumitext:
            self._lumi_13TeV = "35.9 fb^{-1}"
            self._lumi_8TeV  = "19.7 fb^{-1}" 
            self._lumi_7TeV  = "5.1 fb^{-1}"
        else:
            self.__lumitext = lumitext
        
        self._lumi_sqrtS = ""
        self._iPosX = iPosX
        self._iPeriod = iPeriod

        # _drawLogo      = False

        # print "initializing canvas"
        self._canvas = rt.TCanvas("canvas", "canvas", width, height)
        self._canvas.SetRightMargin(right_margin)
        self._canvas.SetLeftMargin(left_margin)
        self._canvas.SetBottomMargin(bottom_margin)
        self._canvas.SetTopMargin(top_margin)
        # print "done:", self._canvas

    # def __init__(self):
    #     __init__(extraText = "Preliminary")

    @property
    def lumi_text(self):
        return self.__lumitext
    
    @lumi_text.setter
    def lumi_text(self, text):
        self.__lumitext = str(text)

    def setCMStext(self, cmsText):
        self._cmsText = cmsText

    def getCMStext(self):
        return deepcopy(self._cmsText)

    def setCMStextfont(self, cmsTextFont):
        self._cmsTextFont = cmsTextFont

    def getCMStextfont(self):
        return deepcopy(self._cmsTextFont)

    def setExtraText(self, extraText):
        self._extraText = extraText

    def getExtraText(self):
        return deepcopy(self._extraText)

    def setExtraTextFont(self, extraTextFont):
        self._extraTextFont = extraTextFont

    def getExtraTextFont(self):
        return deepcopy(self._extraTextFont)

    def setLumiTextSize(self, lumiTextSize):
        self._lumiTextSize = lumiTextSize

    def getLumiTextSize(self):
        return deepcopy(self._lumiTextSize)

    def Draw(self, opt):
        self._canvas.Draw(opt)

    def getCanvas(self):
        return self._canvas

    def saveCanvas(self, outname, prefix = ""):
        c = self.getCanvas()
        self.CMS_lumi(prefix = prefix)
        helper.save_canvas(c = c, outname = outname)

    def getLumiText(self, prefix = "", iPeriod = 4, outOfFrame = False):
        lumiText = prefix
        if( iPeriod==1 ):
            lumiText += self._lumi_7TeV
            lumiText += " (7 TeV)"
        elif ( iPeriod==2 ):
            lumiText += self._lumi_8TeV
            lumiText += " (8 TeV)"

        elif( iPeriod==3 ):      
            lumiText = self._lumi_8TeV 
            lumiText += " (8 TeV)"
            lumiText += " + "
            lumiText += self._lumi_7TeV
            lumiText += " (7 TeV)"
        elif ( iPeriod==4 ):
            lumiText += self.lumi_text
            lumiText += ""
            lumiText += " (13 TeV)"
        elif ( iPeriod==7 ):
            if( outOfFrame ):lumiText += "#scale[0.85]{"
            lumiText += self._lumi_13TeV 
            lumiText += " (13 TeV)"
            lumiText += " + "
            lumiText += self._lumi_8TeV 
            lumiText += " (8 TeV)"
            lumiText += " + "
            lumiText += self._lumi_7TeV
            lumiText += " (7 TeV)"
            if( outOfFrame): lumiText += "}"
        elif ( iPeriod==12 ):
            lumiText += "8 TeV"
        elif ( iPeriod==0 ):
            lumiText += self._lumi_sqrtS

        return lumiText

    def CMS_lumi(self, iPosX = 0, iPeriod=4, prefix = ""):
        pad = self._canvas
        outOfFrame    = False
        if(iPosX/10==0 ): outOfFrame = True

        alignY_=3
        alignX_=2
        if( iPosX/10==0 ): alignX_=1
        if( iPosX==0    ): alignY_=1
        if( iPosX/10==1 ): alignX_=1
        if( iPosX/10==2 ): alignX_=2
        if( iPosX/10==3 ): alignX_=3
        align_ = 10*alignX_ + alignY_

        H = pad.GetWh()
        W = pad.GetWw()
        l = pad.GetLeftMargin() + self._hOffset
        t = pad.GetTopMargin()
        r = pad.GetRightMargin() - self._hOffset
        b = pad.GetBottomMargin()
        e = 0.025
        
        pad.cd()

        lumiText = self.getLumiText(prefix = prefix, iPeriod = self._iPeriod, outOfFrame=outOfFrame)
                
        print(lumiText)

        latex = rt.TLatex()
        latex.SetNDC()
        latex.SetTextAngle(0)
        latex.SetTextColor(rt.kBlack)    
        
        extraTextSize = self._extraOverCmsTextSize*self._cmsTextSize
        
        latex.SetTextFont(42)
        latex.SetTextAlign(31) 
        latex.SetTextSize(self._lumiTextSize*t)    

        latex.DrawLatex(1-r,1-t+self._lumiTextOffset*t,lumiText)

        if( outOfFrame ):
            latex.SetTextFont(self._cmsTextFont)
            latex.SetTextAlign(11) 
            latex.SetTextSize(self._cmsTextSize*t)    
            latex.DrawLatex(l,1-t+self._lumiTextOffset*t,self._cmsText)
      
        pad.cd()

        posX_ = 0
        if( iPosX%10<=1 ):
            posX_ =   l + self._relPosX*(1-l-r)
        elif( iPosX%10==2 ):
            posX_ =  l + 0.5*(1-l-r)
        elif( iPosX%10==3 ):
            posX_ =  1-r - self._relPosX*(1-l-r)

        posY_ = 1-t - self._relPosY*(1-t-b)

        if( not outOfFrame ):
            if( self._drawLogo ):
                posX_ =   l + 0.045*(1-l-r)*W/H
                posY_ = 1-t - 0.045*(1-t-b)
                xl_0 = posX_
                yl_0 = posY_ - 0.15
                xl_1 = posX_ + 0.15*H/W
                yl_1 = posY_
                CMS_logo = rt.TASImage("CMS-BW-label.png")
                pad_logo =  rt.TPad("logo","logo", xl_0, yl_0, xl_1, yl_1 )
                pad_logo.Draw()
                pad_logo.cd()
                CMS_logo.Draw("X")
                pad_logo.Modified()
                pad.cd()          
            else:
                latex.SetTextFont(self._cmsTextFont)
                latex.SetTextSize(self._cmsTextSize*t)
                latex.SetTextAlign(align_)
                latex.DrawLatex(posX_, posY_, self._cmsText)
                if( self._writeExtraText ) :
                    latex.SetTextFont(self._extraTextFont)
                    latex.SetTextAlign(align_)
                    latex.SetTextSize(extraTextSize*t)
                    latex.DrawLatex(posX_, posY_- self._relExtraDY*self._cmsTextSize*t, self._extraText)
        elif( self._writeExtraText ):
            if( iPosX==0):
                posX_ =   l +  self._relPosX*(1-l-r)
                posY_ =   1-t+self._lumiTextOffset*t

            latex.SetTextFont(self._extraTextFont)
            latex.SetTextSize(extraTextSize*t)
            latex.SetTextAlign(align_)
            latex.DrawLatex(posX_ + self._relExtraDY*self._cmsTextSize*t, posY_, self._extraText)      

        pad.Update()
