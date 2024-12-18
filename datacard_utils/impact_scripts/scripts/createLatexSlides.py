import os
import sys
import glob

# from PyPDF2 import PdfFileReader
# def get_n_pages(pdfpath):
#     pdf = PdfFileReader(open(pdfpath,'rb'))
#     return pdf.getNumPages()

paramsperpage = int(sys.argv[1])
wildcards = sys.argv[2:]


base = os.getcwd()
for wildcard in wildcards:
    for impactplot in glob.glob(wildcard):
        impactplot = os.path.abspath(impactplot)
        dirname = os.path.dirname(impactplot)
        print "cd into", dirname
        os.chdir(dirname)
        rootfiles = glob.glob("higgsCombine_paramFit*.root")
        npages = int(len(rootfiles)/paramsperpage)
        if len(rootfiles) % paramsperpage is not 0:
            npages += 1
        parts = dirname.split("_")
        texcode = ""
        for i in range(0, npages):
            texcode += "\\begin{frame}{"+ parts[-2] + " " + parts[-1] + " - " + str(i+1) +"}\n"
            texcode += "\\begin{center}\n"
            
            texcode += "\includegraphics[page = " + str(i+1) + ", height=0.8\\textheight]"
            texcode += "{\pathToImpactPlots/" + os.path.basename(impactplot) + "}\n"
            
            texcode += "\end{center}\n"
            texcode += "\end{frame}\n"
        
        outfile = open(impactplot.replace(".pdf", ".tex"), "w")
        outfile.write(texcode)
        outfile.close()
        os.chdir(base)
    
