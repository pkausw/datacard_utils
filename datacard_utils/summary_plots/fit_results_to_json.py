import os
import sys
import json

unblinded = True

fit_version_philip = "v8108" # messy version naming; it is HIG18030_v01
fit_version_marino = "HIG18030_v01"

path_fitDiagnostics = "/nfs/dust/cms/user/missirol/ttHbb_2017/combination_outputs/"+fit_version_marino+"/outputs/"
path_systSplittings = "/nfs/dust/cms/user/pkeicher/ttH_2018/datacards/HIG-18-030/results_HIG18030_v02/groupsplittings/" # messy version naming; it is HIG18030_v01


channels = [
        "2016",
        "2016_dl",
        "2016_fh",
        "2016p2017",
        "2016p2017_dl",
        "2016p2017_fh",
        "2016p2017_sl",
        "2016p2017_sldl",
        "2016_sl",
        "2016_sldl",
        "2017",
        "2017_dl",
        "2017_dl_3j",
        "2017_dl_4j",
        "2017_fh",
        "2017_fh_3b",
        "2017_fh_4b",
        "2017_sl",
        "2017_sl_4j",
        "2017_sl_5j",
        "2017_sl_6j",
        "2017_sldl",
]


def get_r(file_name):
        """
        Return [r,dn,up] from fitDiagnostic out.txt log file (Marino's format)
        """
        with open( file_name, "r" ) as in_file:
            for line in in_file:
                    if line.startswith("Best fit r:"):
                            r_nom = float( line.split()[3] )
                            r_dn  = abs( float( line.split()[4].split("/")[0] ) )
                            r_up  = abs( float( line.split()[4].split("/")[1] ) )

                            return r_nom, r_dn, r_up


def get_r_uncertainty_groups(file_name):
        """
        Return { source : [dn,up] } of uncertainty groups from uncertainty breakdown json file (Philip's format)
        """
        uncertainties = {}
        with open( file_name, "r" ) as in_file:
                dic = json.load(in_file)
                if not "xvals" in dic["r"]:
                        for name,source in dic["r"].items():
                                val_dn = abs( source["valdown"][0] )
                                val_up = abs( source["valup"][0] )
                                uncertainties[name] = [ val_dn, val_up ]

        return uncertainties



def get_significance(file_name):
        """
        Return significance from Signifiance out.txt file (Marino's format)
        """
        with open( file_name, "r" ) as in_file:
            for line in in_file:
                    if line.startswith("Significance:"):
                            return float(line.split()[1])

       
                
def main():

        results_per_channel = {}
        
        for channel in channels:

                # get significances (observed, expected)
                sig_obs = 0
                if unblinded:
                        sig_obs = get_significance(path_fitDiagnostics+"Significance_Obs/higgsCombine_"+channel+".Significance.mH125.out.txt")
                sig_exp = get_significance(path_fitDiagnostics+"Significance_Exp/higgsCombine_"+channel+".Significance.mH125.out.txt")
                

                # get best-fit mu from fitDiagnostic fit
                mlfit_file = path_fitDiagnostics+"FitDiagnostics_Asimov1p0_PullsAndShapesWithUncs/higgsCombine_"+channel+".FitDiagnostics.mH125.out.txt"
                if unblinded:
                    mlfit_file = path_fitDiagnostics+"FitDiagnostics_Data_PullsAndShapesWithUncs/higgsCombine_"+channel+".FitDiagnostics.mH125.out.txt"    
                r_nom = get_r( mlfit_file )[0]
                r_dn  = get_r( mlfit_file )[1]
                r_up  = get_r( mlfit_file )[2]
                

                # get uncertainties on mu from splittings
                systSplittings_json_file = path_systSplittings+"blinded/substracted_breakdowns_"+fit_version_philip+"_blinded_ttH_hbb_13TeV_"+channel+".json"
                if unblinded:
                        systSplittings_json_file = path_systSplittings+"unblinded/substracted_breakdowns_"+fit_version_philip+"_unblinded_ttH_hbb_13TeV_"+channel+".json"
                dic = get_r_uncertainty_groups(systSplittings_json_file)
                r_tot_dn = dic["Total"][0]
                r_tot_up = dic["Total"][1]                
                r_stat_dn = dic["Stat"][0]
                r_stat_up = dic["Stat"][1]                
                r_syst_dn = dic["Total-Stat"][0]
                r_syst_up = dic["Total-Stat"][1]                
        
                results_per_channel[channel] = {
                        "r_nom"     : r_nom,
                        "r_up"      : r_up,
                        "r_dn"      : r_dn,
                        "r_tot_dn"  : r_tot_dn,
                        "r_tot_up"  : r_tot_up,
                        "r_stat_dn" : r_stat_dn,
                        "r_stat_up" : r_stat_up,
                        "r_syst_dn" : r_syst_dn,
                        "r_syst_up" : r_syst_up,
                        "sig_obs"   : sig_obs,
                        "sig_exp"   : sig_exp,
                }
        
        #print results_per_channel
        out_name = "HIG-18-030_"+fit_version_marino+"_results_blinded.json"
        if unblinded:
                out_name = out_name.replace("blinded","unblinded")
        
        with open( out_name, "w" ) as write_file:
                json.dump( results_per_channel, write_file, indent=4 )

                
                                
if __name__ == '__main__':
	main()
