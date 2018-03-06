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
total_bkg = "TotalBkg"
total_sig = "TotalSig"
data      = "data_obs"

njet_categories = [ "SL 4j", "SL 5j", "SL 6j", "DL 4j" ]
sub_categories_sl = [ "ttH", "ttbb", "tt2b", "ttb", "ttcc", "ttlf" ]
sub_categories_dl = [ "3t", "4tl", "4th" ]

category_channel_map = {
    "SL 5j ttH"  : "ch1",
    "SL 6j ttbb" : "ch2",
    "SL 6j ttlf" : "ch3",
    "SL 4j ttbb" : "ch4",
    "SL 5j ttbb" : "ch5",
    "SL 6j tt2b" : "ch6",
    "SL 4j ttcc" : "ch7",
    "SL 4j ttlf" : "ch8",
    "SL 4j ttH"  : "ch9",
    "SL 5j ttlf" : "ch10",
    "DL 4j 4th"  : "ch11",
    "SL 6j ttb"  : "ch12",
    "SL 5j ttb"  : "ch13",
    "SL 5j tt2b" : "ch14",
    "SL 5j ttcc" : "ch15",
    "DL 4j 4tl"  : "ch16",
    "SL 4j ttb"  : "ch17",
    "SL 4j tt2b" : "ch18",
    "SL 6j ttH"  : "ch19",
    "SL 6j ttcc" : "ch20",
    "DL 4j 3t"   : "ch21",
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
    "TotalBkg"       : "Total\\;bkg.",
    "TotalSig"       : "\\ttH",
    "data_obs"       : "Data",
}

sub_category_commands = {
    "ttH"  : "\\ttH",
    "ttlf" : "\\ttlf",
    "ttcc" : "\\ttcc",
    "ttb"  : "\\ttb",
    "tt2b" : "\\tttwob",
    "ttbb" : "\\ttbb",
    "3t"   : "\\dlFourThree",
    "4tl"  : "\\dlFourFour BDT-low",
    "4th"  : "\\dlFourFour BDT-high",
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
    if process == "ttbarV":
        return get_sum_of_hists(in_file,dir_name,"ttbarW","ttbarZ","ttbarV")
    elif process == "vjets":
        return get_sum_of_hists(in_file,dir_name,"wjets","zjets","vjets")
    else:
        return in_file.Get(dir_name+"/"+process)


def get_yields(in_file, categories, prepostfit):
    category_yield_map = {}

    processes = []
    for process in bkg_processes:
        processes.append(process)
    processes.append(total_bkg)
    processes.append(total_sig)
    processes.append(data)
    
    for category in categories:
        dir_name = category_channel_map[category]+"_"+prepostfit
        process_hist_map = {}
        for process in processes:
            process_hist_map[process] = get_hist(in_file,dir_name,process)

        category_yield_map[category] = process_hist_map

    return category_yield_map


def get_yield_string(category_yield_map,category,process,sig_scale=1):
    y  = category_yield_map[category][process].GetBinContent(1)
    ye = category_yield_map[category][process].GetBinError(1)

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

    
def print_table(category_yield_map_prefit,category_yield_map_postfit,njet_category):
    print "print_table: ", njet_category

    sub_categories = []
    if "SL" in njet_category:
        for sub_category in sub_categories_sl:
            sub_categories.append( sub_category )
    elif "DL" in njet_category:
        for sub_category in sub_categories_dl:
            sub_categories.append( sub_category )

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

if __name__ == "__main__":

    in_file = ROOT.TFile("yields.root","READ")
    
    categories = []
    for njet_category in njet_categories:
        if "SL" in njet_category:
            for sub_category in sub_categories_sl:
                categories.append( category( njet_category, sub_category ) )
        elif "DL" in njet_category:
            for sub_category in sub_categories_dl:
                categories.append( category( njet_category, sub_category ) )
                
    
    category_yield_map_prefit  = get_yields(in_file, categories, "prefit" )
    category_yield_map_postfit = get_yields(in_file, categories, "postfit" )

    #print category_yield_map_prefit

    for njet_category in njet_categories:
        print
        print
        print_table(category_yield_map_prefit,category_yield_map_postfit,njet_category)

    

    
    in_file.Close()
