import ROOT
import os
import sys
import importlib
from optparse import OptionParser

mu_s = 1

def category(njet_category,sub_category):
    return njet_category+" "+sub_category


def get_sum_of_hists(in_file,dir_name,name1,name2,new_name):
    hist1 = get_hist(in_file,dir_name,name1)
    hist2 = get_hist(in_file,dir_name,name2)
    if not isinstance(hist1, ROOT.TH1):
        if isinstance(hist2, ROOT.TH1):
            print("Will return {} for {}".format(name2, new_name))
            return hist2
        else:
            print("Cannot add {} and {}! Skipping {}".format(name1, name2, new_name))
            return None
    if not isinstance(hist2, ROOT.TH1):
        if isinstance(hist1, ROOT.TH1):
            print("Will return {} for {}".format(name1, new_name))
            return hist1
        else:
            print("Cannot add {} and {}! Skipping {}".format(name1, name2, new_name))
            return None
    hist = hist1.Clone(new_name)
    hist.Add(hist2)
    return hist

def get_hist(in_file,dir_name,process):
    histpath = os.path.join(dir_name, process)
    print("searching for '{}'".format(histpath))
    outhist=None
    if process == "ttbarV":
        outhist= get_sum_of_hists(in_file,dir_name,"ttbarW","ttbarZ","ttbarV")
    elif process == "vjets":
        outhist= get_sum_of_hists(in_file,dir_name,"wjets","zjets","vjets")
    else:
        outhist= in_file.Get(histpath)
    if outhist!=None:
        print("found '{}'".format(outhist.GetName()))
    else:
        print("did not find '{}'".format(histpath))
    return outhist    

def get_yields(in_file, categories, prepostfit, cfg_module):
    category_yield_map = {}

    processes = []
    for process in cfg_module.bkg_processes:
        processes.append(process)
    processes.append(cfg_module.total_bkg)
    processes.append(cfg_module.total_sig)
    processes.append(cfg_module.data)
    
    for category in categories:
        dir_name = "shapes_"+prepostfit
        dir_name = os.path.join(dir_name, cfg_module.category_channel_map[category])
        #dir_name = "shapes_"+prepostfit+"/"+category_channel_map[category]+"_"+prepostfit

        process_hist_map = {}
        for process in processes:
            process_hist_map[process] = get_hist(in_file,dir_name,process)

        category_yield_map[category] = process_hist_map

    return category_yield_map

def get_yield_string(category_yield_map,category,process,sig_scale=1, total_sig = "total_sig"):
    y=0
    ye=0
    if not category_yield_map:
        return "{:5.1f}".format(y), "{:3.1f}".format(ye)
    obj = category_yield_map[category][process]
    if isinstance(obj, ROOT.TH1):
        y  = obj.Integral()
        ye = obj.GetBinError(1)
    elif isinstance(obj,ROOT.TGraphAsymmErrors):
        for i in range(obj.GetN()):
            y  += obj.GetY()[i]
        ye = obj.GetErrorYhigh(0)
        ye += obj.GetErrorYlow(0)
        ye /= 2.
    else:
        print("WARNING: could not read object at [{}][{}]".format(category,process))
    ye = 0
    # because signal is not scaled by fitted mu, but mu = 1
    if process == total_sig:
        y  = sig_scale * y
        ye = sig_scale * ye

    if y < 1:
        return "{:10.1f}".format(y), "{:5.1f}".format(ye)
    else:
        return "{:10.0f}".format(y), "{:5.0f}".format(ye)

def fill_template_line( template, sub_categories, njet_category, 
                        process, yield_map_prefit, yield_map_postfit):
    entries = []
    for sub_category in sub_categories:
        cat_string = category(njet_category,sub_category)
        val_prefit, err_prefit = get_yield_string(yield_map_prefit, cat_string, process)
        val_postfit, err_postfit = get_yield_string(yield_map_postfit, 
                                                    cat_string, process, mu_s)

        entries.append(template.format( prefit_val = val_prefit, 
                                        postfit_val = val_postfit,
                                        prefit_err = err_prefit,
                                        postfit_err = err_postfit
                                    )
                        )
    return entries

def print_table_line(yield_map_prefit, yield_map_postfit, njet_category, 
                        sub_categories, process, cfg_module, print_error):
    proc_cmd = "{:10}".format(cfg_module.process_commands.get(process, process))
    postfit = bool(yield_map_postfit)
    
    line_template = "{process} & {values}\\\\ \n"
    val_template = "${prefit_val}$"
    if process != cfg_module.data:
        if postfit:
            val_template += " & (${postfit_val}$)"
    else:
        if postfit:
            val_template = "\\multicolumn{{2}}{{c}}{{${prefit_val}$}}"
    
    entries = fill_template_line(   template = val_template, 
                                    sub_categories = sub_categories,
                                    njet_category = njet_category,
                                    yield_map_prefit = yield_map_prefit,
                                    yield_map_postfit = yield_map_postfit,
                                    process = process
                                )
    print("entries for process '{}'".format(process))
    print(entries)
    l = line_template.format(process = proc_cmd, values = " & ".join(entries))
    print(l)
    if print_error and process != cfg_module.data:
        val_template = "$\\pm {prefit_err}$"
        if postfit:
            val_template += " & ($\\pm {postfit_err}$)"
        entries = fill_template_line(   template = val_template, 
                                    sub_categories = sub_categories,
                                    njet_category = njet_category,
                                    yield_map_prefit = yield_map_prefit,
                                    yield_map_postfit = yield_map_postfit,
                                    process = process
                                ) 
        l += line_template.format(  process = "{:10}".format("$\\pm$ tot unc."),
                                   values = " & ".join(entries))
    return l

def create_header(sub_categories, sub_category_cmds, postfit = False):
    ncols = len(sub_categories) if not postfit else 2*len(sub_categories)
    s = """
    \\renewcommand{\\arraystretch}{1.5}
    \\begin{tabular}{l"""
    s += "r"*ncols + "}"
    if not postfit:
        header_text = "pre-fit yields $\\pm$ tot unc."
        categories = [sub_category_cmds.get(x,x) for x in sub_categories]
    else:
        header_text = "pre-fit (post-fit) yields"
        categories = ["\\multicolumn{{2}}{{c}}{{ {} }}".format(sub_category_cmds.get(x,x)) 
                                                            for x in sub_categories]
    sub = """
    \\hline\\hline
    & \\multicolumn{{ {length} }}{{c}}{{ {header_text} }} \\\\
    Process & {categories} \\\\
    \\hline\n""".format(  length = ncols,
                    header_text = header_text,
                    categories = " & ".join(categories)
                    )
    return "\n".join([s, sub])

def create_footer():
    s = """
    \\hline\\hline
    \\end{tabular}
    \\renewcommand{\\arraystretch}{1}
    """
    return s

def print_table(yield_map_prefit, njet_category, cfg_module, yield_map_postfit = None):
    print "print_table: ", njet_category

    sub_categories = []
    # if "SL" in njet_category:
    #     for sub_category in cfg_module.sub_categories_sl:
    #         sub_categories.append( sub_category )
    # elif "DL" in njet_category:
    #     for sub_category in cfg_module.sub_categories_dl:
    #         sub_categories.append( sub_category )

    for sub_category in cfg_module.sub_categories:
        sub_categories.append( sub_category )

    header = create_header( sub_categories = sub_categories, 
                            sub_category_cmds = cfg_module.sub_category_commands,
                            postfit = bool(yield_map_postfit)
                            )
    
    bodylines = []
    opts = {
        "yield_map_prefit"  : yield_map_prefit,
        "njet_category"     : njet_category,
        "sub_categories"    : sub_categories,
        "yield_map_postfit" : yield_map_postfit,
        "cfg_module"        : cfg_module
    }

    for process in cfg_module.bkg_processes:
        bodylines.append(print_table_line(  process = process, 
                                            print_error = False, **opts)
                        )
    bodylines.append(print_table_line(process = cfg_module.total_bkg, 
                                        print_error = True, **opts)
                    )
    bodylines.append(print_table_line(process = cfg_module.total_sig, 
                                        print_error = True, **opts)
                    )
    bodylines.append(print_table_line(process = cfg_module.data, 
                                        print_error = False, **opts)
                    )
    body = "\\hline\n".join(bodylines)

    footer = create_footer()
    return "\n".join([header, body, footer])


def init_module(config_path):
    dirname = os.path.dirname(config_path)
    if not dirname in sys.path:
        sys.path.append(dirname)
    module_name = os.path.basename(config_path)
    if module_name.endswith(".py"): 
        module_name = ".".join(module_name.split(".")[:-1])
    return importlib.import_module(module_name)

def load_keyword(dict, keyword):
    item = dict.get(keyword, None) 
    if not item:
        raise ValueError("Could not load keyword '{}'".format(keyword))
    return item

def main(**kwargs):
    #in_file = ROOT.TFile("yields.root","READ")
    inpath = load_keyword(kwargs, "infile")
    in_file = ROOT.TFile(inpath,"READ")

    cfg_path = load_keyword(kwargs, "config")
    cfg_module = init_module(cfg_path)
    categories = []
    for njet_category in cfg_module.njet_categories:
        # if "SL" in njet_category:
        #     for sub_category in cfg_module.sub_categories_sl:
        #         categories.append( category( njet_category, sub_category ) )
        # elif "DL" in njet_category:
        #     for sub_category in cfg_module.sub_categories_dl:
        #         categories.append( category( njet_category, sub_category ) )
        for sub_category in cfg_module.sub_categories:
            categories.append( category( njet_category, sub_category ) )
                
    
    yield_map_prefit = get_yields(in_file, categories, "prefit" , cfg_module)
    mode = load_keyword(kwargs, "mode")
    yield_map_postfit = None
    if not mode == "prefit":
        yield_map_postfit = get_yields(in_file, categories, mode , cfg_module)

    #print category_yield_map_prefit
    outname = kwargs.get("outfile")
    if outname is None:
        outname = ".".join(inpath.split(".")[:-1])

    for njet_category in cfg_module.njet_categories:
        print
        print
        s = print_table(    yield_map_prefit = yield_map_prefit,
                        njet_category = njet_category,
                        cfg_module = cfg_module,
                        yield_map_postfit = yield_map_postfit)
        print(s)

        pathname = njet_category.replace("\\", "")
        pathname = pathname.replace(" ", "_")
        outpath = "{}_{}.tex".format(outname, pathname)
        print("Will save table in '{}'".format(outpath))
        with open(outpath, "w") as f:
            f.write(s)
        
   
    in_file.Close()

def parse_arguments():
    parser = OptionParser()

    parser.add_option(  "-c", "--config",
                        help = " ".join("""
                        Path to config specifying processes, latex code for
                        processes, categories
                        """.split()),
                        dest = "config",
                        type = "str"
                    )
    parser.add_option(  "-s", "--signalstrength",
                        help = " ".join("""
                        scale total signal histogram with this parameter
                        """.split()),
                        dest = "mu",
                        type = "float",
                        default = 1.
                    )
    parser.add_option(  "-i", "--inputfile",
                        help = " ".join("""
                        path to input file
                        """.split()),
                        dest = "infile",
                        metavar = "path/to/input.root",
                        type = "str"
                    )
    parser.add_option(  "-m", "--mode",
                        help = " ".join("""
                        switch that decides whether to create prefit
                        or postfit table. Choices: 'prefit' (prefit tables),
                        'fit_s' (s+b tables), 'fit_b' (b-only tables)
                        """.split()),
                        dest = "mode",
                        choices = ["prefit", "fit_s", "fit_b"]
                    )

    parser.add_option(  "-o", "--outputfile",
                        help = " ".join("""
                        save table string in this file
                        """.split()),
                        dest = "outfile",
                        metavar = "path/to/output.tex",
                        type = "str"
                    )

    options, args = parser.parse_args()

    if not (options.config and os.path.exists(options.config)):
        parser.error("Could not find config in path '{}'".format(options.config))

    if not (options.infile and os.path.exists(options.infile)):
        parser.error("Could not find input file in path '{}'".format(options.infile))
    
    global mu_s
    mu_s = options.mu

    return options, args

if __name__ == "__main__":
    
    options, args = parse_arguments()
    main(**vars(options))
