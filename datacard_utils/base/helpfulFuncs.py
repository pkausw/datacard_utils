import ROOT
import os
import shutil

class helpfulFuncs(object):

    def __init__(self):
        pass

    def getLatex(self, x,y,text):
        tests = ROOT.TLatex(x, y,text)
        tests.SetTextFont(42)
        tests.SetTextSize(0.04)
        tests.SetNDC()
        return tests


    def getCanvas(self, name='c',ratiopad=False):
        c=ROOT.TCanvas(name,name,1024,1024)
        c.SetRightMargin(0.14)
        c.SetTopMargin(0.12)
        c.SetLeftMargin(0.12)
        c.SetBottomMargin(0.12)
        c.SetTicks(1,1)

        return c
    def getLegend(self):
        legend=ROOT.TLegend()
        legend.SetX1NDC(0.15)
        legend.SetX2NDC(0.45)
        legend.SetY1NDC(0.68)
        legend.SetY2NDC(0.86)
        legend.SetBorderSize(0);
        legend.SetLineStyle(0);
        legend.SetTextFont(42);
        legend.SetTextSize(0.04);
        legend.SetFillStyle(1001); #1001 -> solid, 0 -> hollow
        return legend


    def setupPad(self, p):
        p.SetRightMargin(0.14)
        p.SetTopMargin(0.12)
        p.SetLeftMargin(0.12)
        p.SetBottomMargin(0.12)
        p.SetTicks(1,1)


    def lnn(self, beta,err):
        return pow(1.+err,beta)
        
    def check_wildcard(self, key, paramlist):
        # print "input list:\n", nuisancelist
        for p in paramlist:
            if "*" in p:
                # print "checking", p
                parts = p.split("*")
                start = parts[0]
                body = parts[1:len(parts)-1]
                end = parts[-1]
                # print "start =", start
                # print "body = ", body
                # print "end = ", end
                if  key.startswith(start) and all( x in key for x in body) and key.endswith(end):
                    return True
            else:
                if p == key:
                    return True
        return False

    def insert_values(self, cmds, keyword, toinsert, joinwith=","):
        if keyword in cmds:
            i = cmds.index(keyword)
            if joinwith == "replace":
                cmds[i+1] = toinsert
            elif joinwith == "insert":
                pass
            else:
                cmds[i+1] = joinwith.join([cmds[i+1],toinsert])
        else:
            cmds += [keyword, toinsert]

    def check_workspace(self, pathToDatacard):
        workspacePath = ""
        parts = pathToDatacard.split(".")
        outputPath = ".".join(parts[:len(parts)-1]) + ".root"
        if not os.path.exists(outputPath):
            print "generating workspace for", pathToDatacard
            
            bashCmd = ["source {0} ;".format(pathToCMSSWsetup)]
            bashCmd.append("text2workspace.py -m 125 " + pathToDatacard)
            bashCmd.append("-o " + outputPath)
            print bashCmd
            subprocess.call([" ".join(bashCmd)], shell = True)
    
        workspacePath = outputPath
    
        if os.path.exists(workspacePath):
            f = ROOT.TFile(workspacePath)
            if not (f.IsOpen() and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered)):
                workspacePath = ""
            else:
                test = f.Get("w")
                if not isinstance(test, ROOT.RooWorkspace):
                    print "could not find workspace in", workspacePath
                    workspacePath = ""
        else:
            print "could not find", workspacePath
            workspacePath = ""
        return workspacePath
        
    def check_for_reset(self, folder):
        
        if os.path.exists(folder):
            print "resetting folder", folder
            shutil.rmtree(folder)
        os.makedirs(folder)

    def treat_special_chars(self, string):
        string = string.replace("#", "")
        string = string.replace(" ", "_")
        string = string.replace("{", "")
        string = string.replace("}", "")
        string = string.replace("?", "X")
        string = string.replace("*", "X")
        return string