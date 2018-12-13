import ROOT

mu_s = 0.72

bkg_processes = [
    "ttbarOther",
    "ttbarPlusCCbar",
    "ttbarPlusB",
    "ttbarPlus2B",
    "ttbarPlusBBbar",
    "singlet",
    "vjets",
    "ttbarV",
    "diboson",
]
total_bkg = "total_background"
total_sig = "total_signal"
data      = "data"

njet_categories = [ "SL 4j", "SL 5j", "SL 6j"]
sub_categories_sl = [ "ttH", "ttbb", "tt2b", "ttb", "ttcc", "ttlf" ]
sub_categories_dl = [ "3t", "4tl", "4th" ]

category_channel_map = {
    "SL 5j ttH"  : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttH",
    "SL 6j ttbb" : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttbb",
    "SL 6j ttlf" : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttlf",
    "SL 4j ttbb" : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttbb",
    "SL 5j ttbb" : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttbb",
    "SL 6j tt2b" : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_tt2b",
    "SL 4j ttcc" : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttcc",
    "SL 4j ttlf" : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttlf",
    "SL 4j ttH"  : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttH",
    "SL 5j ttlf" : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttlf",
    #"DL 4j 4th"  : "ch11",
    "SL 6j ttb"  : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttb",
    "SL 5j ttb"  : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttb",
    "SL 5j tt2b" : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_tt2b",
    "SL 5j ttcc" : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttcc",
    #"DL 4j 4tl"  : "ch16",
    "SL 4j ttb"  : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttb",
    "SL 4j tt2b" : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_tt2b",
    "SL 6j ttH"  : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttH",
    "SL 6j ttcc" : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttcc",
    #"DL 4j 3t"   : "ch21",
}

process_commands = {
    "ttbarOther"     : "\\ttlf",
    "ttbarPlusCCbar" : "\\ttcc",
    "ttbarPlusB"     : "\\ttb",
    "ttbarPlus2B"    : "\\tttwob",
    "ttbarPlusBBbar" : "\\ttbb",
    "singlet"        : "\\singlet",
    "vjets"          : "\\Vjets",
    "ttbarV"         : "\\ttV",
    "diboson"        : "\\diboson",
    "total_background"       : "Total\\;bkg.",
    "total_signal"       : "\\ttH",
    "data"       : "Data",
}

sub_category_commands = {
    "ttH"  : "\\ttH",
    "ttlf" : "\\ttlf",
    "ttcc" : "\\ttcc",
    "ttb"  : "\\ttb",
    "tt2b" : "\\tttwob",
    "ttbb" : "\\ttbb",
    #"3t"   : "\\dlFourThree",
    #"4tl"  : "\\dlFourFour BDT-low",
    #"4th"  : "\\dlFourFour BDT-high",
}


def category(njet_category,sub_category):
    return njet_category+" "+sub_category


def get_sum_of_hists(in_file,dir_name,name1,name2,new_name):
    hist1 = get_hist(in_file,dir_name,name1)
    hist2 = get_hist(in_file,dir_name,name2)
    hist = hist1.Clone(new_name)
    hist.Add(hist2)
    return hist


def get_hist(in_file,dir_name,process):
    print "searching for", dir_name,process
    outhist=None
    if process == "ttbarV":
        outhist= get_sum_of_hists(in_file,dir_name,"ttbarW","ttbarZ","ttbarV")
    elif process == "vjets":
        outhist= get_sum_of_hists(in_file,dir_name,"wjets","zjets","vjets")
    else:
        outhist= in_file.Get(dir_name+"/"+process)
    if outhist!=None:
        print "found", outhist.GetName()
    else:
        print "did not find ", dir_name,process
    return outhist    

def get_yields(in_file, categories, prepostfit):
    category_yield_map = {}

    processes = []
    for process in bkg_processes:
        processes.append(process)
    processes.append(total_bkg)
    processes.append(total_sig)
    processes.append(data)
    
    for category in categories:
        dir_name = "shapes_"+prepostfit+"/"+category_channel_map[category] #+"_"+prepostfit
        #dir_name = "shapes_"+prepostfit+"/"+category_channel_map[category]+"_"+prepostfit

        process_hist_map = {}
        for process in processes:
            process_hist_map[process] = get_hist(in_file,dir_name,process)

        category_yield_map[category] = process_hist_map

    return category_yield_map


def get_yield_string(category_yield_map,category,process,sig_scale=1):
    y=0
    ye=0
    if isinstance(category_yield_map[category][process],ROOT.TH1):
        y  = category_yield_map[category][process].GetBinContent(1)
        ye = category_yield_map[category][process].GetBinError(1)
    elif isinstance(category_yield_map[category][process],ROOT.TGraphAsymmErrors):
        y  = category_yield_map[category][process].GetY()[0]
        ye = (category_yield_map[category][process].GetEYlow()[0]+category_yield_map[category][process].GetEYlow()[0])/2.0
    # because signal is not scaled by fitted mu, but mu = 1
    if process == total_sig:
        y  = sig_scale * y
        ye = sig_scale * ye

    if y < 1:
        return "{:5.1f}".format(y), "{:3.1f}".format(ye)
    else:
        return "{:5.0f}".format(y), "{:3.0f}".format(ye)


def print_table_line(category_yield_map_prefit,category_yield_map_postfit,njet_category,sub_categories,process,print_error):
    print "{:10}".format(process_commands[process]),
    for sub_category in sub_categories:
        yield_val_prefit, yield_err_prefit = get_yield_string(category_yield_map_prefit,category(njet_category,sub_category),process)
        yield_val_postfit, yield_err_postfit = get_yield_string(category_yield_map_postfit,category(njet_category,sub_category),process,mu_s)
        if process == data:
            print "& \\multicolumn{2}{c}{$",yield_val_prefit,"$}",
        else:
            print "& $",yield_val_prefit,"$ & ($",yield_val_postfit,"$)",
    print " \\\\"
    if print_error and process != data:
        print "{:10}".format("$\\pm$ tot unc."),
        for sub_category in sub_categories:
            yield_val_prefit, yield_err_prefit = get_yield_string(category_yield_map_prefit,category(njet_category,sub_category),process)
            yield_val_postfit, yield_err_postfit = get_yield_string(category_yield_map_postfit,category(njet_category,sub_category),process)
            print "& $\\pm",yield_err_prefit,"$ & ($\\pm",yield_err_postfit,"$)",
        print " \\\\"


def print_table_line_prefit(category_yield_map_prefit,njet_category,sub_categories,process,print_error):
    print "{:10}".format(process_commands[process]),
        #yield_val_postfit, yield_err_postfit = get_yield_string(category_yield_map_postfit,category(njet_category,sub_category),process,mu_s)
    if process == data:
        for sub_category in sub_categories:
            yield_val_prefit, yield_err_prefit = get_yield_string(category_yield_map_prefit,category(njet_category,sub_category),process)
            print "& $",yield_val_prefit,"$",
        print " \\\\"    
    else:
            if print_error and process != data:
                #print "{:10}".format("$\\pm$ tot unc."),
                for sub_category in sub_categories:
                    yield_val_prefit, yield_err_prefit = get_yield_string(category_yield_map_prefit,category(njet_category,sub_category),process)
                    #yield_val_postfit, yield_err_postfit = get_yield_string(category_yield_map_postfit,category(njet_category,sub_category),process)
                    print "& $",yield_val_prefit," \\pm",yield_err_prefit,"$ ",
                print " \\\\"
            else:
                #print "{:10}".format("$\\pm$ tot unc."),
                for sub_category in sub_categories:
                    yield_val_prefit, yield_err_prefit = get_yield_string(category_yield_map_prefit,category(njet_category,sub_category),process)
                    #yield_val_postfit, yield_err_postfit = get_yield_string(category_yield_map_postfit,category(njet_category,sub_category),process)
                    print "& $",yield_val_prefit,"$ ",
                print " \\\\"
                 

    
def print_table(category_yield_map_prefit,category_yield_map_postfit,njet_category):
    print "print_table: ", njet_category

    sub_categories = []
    if "SL" in njet_category:
        for sub_category in sub_categories_sl:
            sub_categories.append( sub_category )
    elif "DL" in njet_category:
        for sub_category in sub_categories_dl:
            sub_categories.append( sub_category )
    print "\\renewcommand{\\arraystretch}{1.5}"
    print "\\begin{tabular}{l",
    for i in range(0,len(sub_categories)):
        print "r@{\;}r",
    print "}"
    print "\\hline\\hline"
    print "& \\multicolumn{",2*len(sub_categories),"}{c}{pre-fit (post-fit) yields}"
    print " \\\\"
    print "Process",
    for sub_category in sub_categories:
        print " & \\multicolumn{2}{c}{",sub_category_commands[sub_category]," node}",
    print " \\\\"
    print "\\hline"
    
    for process in bkg_processes:
        print_table_line(category_yield_map_prefit,category_yield_map_postfit,njet_category,sub_categories,process,False)
    print "\\hline"
    print_table_line(category_yield_map_prefit,category_yield_map_postfit,njet_category,sub_categories,total_bkg,True)
    print "\\hline"
    print_table_line(category_yield_map_prefit,category_yield_map_postfit,njet_category,sub_categories,total_sig,True)
    print "\\hline"
    print_table_line(category_yield_map_prefit,category_yield_map_postfit,njet_category,sub_categories,data,False)
    print "\\hline\\hline"
        
    print "\\end{tabular}"
    print "\\renewcommand{\\arraystretch}{1}"

def print_table_prefit(category_yield_map_prefit,njet_category):
    print "print_table: ", njet_category

    sub_categories = []
    if "SL" in njet_category:
        for sub_category in sub_categories_sl:
            sub_categories.append( sub_category )
    elif "DL" in njet_category:
        for sub_category in sub_categories_dl:
            sub_categories.append( sub_category )

    print "\\renewcommand{\\arraystretch}{1.5}"
    print "\\begin{tabular}{l",
    for i in range(0,len(sub_categories)):
        #print "r@{\;}r",
        print "r",
    print "}"
    print "\\hline\\hline"
    print "& \\multicolumn{",1*len(sub_categories),"}{c}{pre-fit yields $\\pm$ tot unc.}"
    print " \\\\"
    print "Process",
    for sub_category in sub_categories:
        print " & ",sub_category_commands[sub_category]," node",
    print " \\\\"
    print "\\hline"
    
    for process in bkg_processes:
        print_table_line_prefit(category_yield_map_prefit,njet_category,sub_categories,process,True)
    print "\\hline"
    print_table_line_prefit(category_yield_map_prefit,njet_category,sub_categories,total_bkg,True)
    print "\\hline"
    print_table_line_prefit(category_yield_map_prefit,njet_category,sub_categories,total_sig,True)
    print "\\hline"
    print_table_line_prefit(category_yield_map_prefit,njet_category,sub_categories,data,False)
    print "\\hline\\hline"
        
    print "\\end{tabular}"
    print "\\renewcommand{\\arraystretch}{1}"

if __name__ == "__main__":

    #in_file = ROOT.TFile("yields.root","READ")
    in_file = ROOT.TFile("fitDiagnostics.root","READ")
    
    categories = []
    for njet_category in njet_categories:
        if "SL" in njet_category:
            for sub_category in sub_categories_sl:
                categories.append( category( njet_category, sub_category ) )
        elif "DL" in njet_category:
            for sub_category in sub_categories_dl:
                categories.append( category( njet_category, sub_category ) )
                
    
    category_yield_map_prefit  = get_yields(in_file, categories, "prefit" )
    #category_yield_map_postfit = get_yields(in_file, categories, "postfit_s" )

    #print category_yield_map_prefit

    for njet_category in njet_categories:
        print
        print
        #print_table(category_yield_map_prefit,category_yield_map_postfit,njet_category)
        print_table_prefit(category_yield_map_prefit,njet_category)
    
    

    
    in_file.Close()
