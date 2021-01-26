import ROOT
#samples named in the rootfile
samples = {   'diboson': {   'info': {   'color': 862L,
                               'label': 'VV',
                               'typ': 'bkg'},
                   'plot': True},
    'singlet': {   'info': {   'color': 616L,
                               'label': 't',
                               'typ': 'bkg'},
                   'plot': True},
    'tHW_hbb': {   'info': {   'color': 603L,
                               'label': 'tHW (SM)',
                               'typ': 'bkg'},
                   'plot': True},
    'tHq_hbb': {   'info': {   'color': 606L,
                               'label': 'tHq (SM)',
                               'typ': 'bkg'},
                   'plot': True},
    'tHW': {   'info': {   'color': 603L,
                               'label': 'tHW (SM)',
                               'typ': 'bkg'},
                   'plot': True},
    'tHq': {   'info': {   'color': 606L,
                               'label': 'tHq (SM)',
                               'typ': 'bkg'},
                   'plot': True},
    'ttH_hbb': {   'info': {   'color': 601L,
                               'label': 't#bar{t}H (bb)',
                               'typ': 'signal'},
                   'plot': True},
    'ttH_hcc': {   'info': {   'color': 601L,
                               'label': 't#bar{t}H(cc)',
                               'typ': 'signal'},
                   'plot': True},
    'ttH_hgg': {   'info': {   'color': 601L,
                               'label': 't#bar{t}H(#gamma#gamma)',
                               'typ': 'signal'},
                   'plot': True},
    'ttH_hgluglu': {   'info': {   'color': 601L,
                                   'label': 't#bar{t}H(gg)',
                                   'typ': 'signal'},
                       'plot': True},
    'ttH_htt': {   'info': {   'color': 601L,
                               'label': 't#bar{t}H(ll)',
                               'typ': 'signal'},
                   'plot': True},
    'ttH_hww': {   'info': {   'color': 601L,
                               'label': 't#bar{t}H(WW)',
                               'typ': 'signal'},
                   'plot': True},
    'ttH_hzg': {   'info': {   'color': 601L,
                               'label': 't#bar{t}H(Z#gamma)',
                               'typ': 'signal'},
                   'plot': True},
    'ttH_hzz': {   'info': {   'color': 601L,
                               'label': 't#bar{t}H(ZZ)',
                               'typ': 'signal'},
                   'plot': True},
    'ttH_hnonbb': {   'info': {   'color': 601L,
                               'label': 't#bar{t}H(nonbb)',
                               'typ': 'signal'},
                   'plot': True},
    'ttbarW': {   'info': {   'color': 590L,
                              'label': 't#bar{t}+W',
                              'typ': 'bkg'},
                  'plot': True},
    'ttbarZ': {   'info': {   'color': 432L,
                              'label': 't#bar{t}+Z',
                              'typ': 'bkg'},
                  'plot': True},
    'ttbb': {   'info': {   'color': 635L,
                            'label': 't#bar{t}+b#bar{b} (4FS)',
                            'typ': 'bkg'},
                'plot': True},
    'ttbb_5FS': {   'info': {   'color': 635L,
                                'label': 't#bar{t}+b#bar{b} (5FS)',
                                'typ': 'bkg'},
                    'plot': False},
    'ttcc': {   'info': {   'color': 633L,
                            'label': 't#bar{t}+c#bar{c}',
                            'typ': 'bkg'},
                'plot': True},
    'ttlf': {   'info': {   'color': 625L,
                            'label': 't#bar{t}+lf',
                            'typ': 'bkg'},
                'plot': True},
    'wjets': {   'info': {   'color': 409L,
                             'label': 'W+jets',
                             'typ': 'bkg'},
                 'plot': True},
    'zjets': {   'info': {   'color': 413L,
                             'label': 'Z+jets',
                             'typ': 'bkg'},
                 'plot': True},

    'diboson_CR': {   'info': {   'color': 418L,
                               'label': 'VV CR',
                               'typ': 'bkg'},
                   'plot': True},
    'singlet_CR': {   'info': {   'color': 418L,
                               'label': 't CR',
                               'typ': 'bkg'},
                   'plot': True},
    'ttbarW_CR': {   'info': {   'color': 418L,
                              'label': 't#bar{t}+W CR',
                              'typ': 'bkg'},
                  'plot': True},
    'ttbarZ_CR': {   'info': {   'color': 418L,
                              'label': 't#bar{t}+Z CR',
                              'typ': 'bkg'},
                  'plot': True},
    'ttbb_CR': {   'info': {   'color': 418L,
                            'label': 't#bar{t}+b#bar{b} (4FS) CR',
                            'typ': 'bkg'},
                'plot': True},
    'ttbb_5FS_CR': {   'info': {   'color': 418L,
                                'label': 't#bar{t}+b#bar{b} (5FS) CR',
                                'typ': 'bkg'},
                    'plot': False},
    'ttcc_CR': {   'info': {   'color': 418L,
                            'label': 't#bar{t}+c#bar{c} CR',
                            'typ': 'bkg'},
                'plot': True},
    'ttlf_CR': {   'info': {   'color': 418L,
                            'label': 't#bar{t}+lf CR',
                            'typ': 'bkg'},
                'plot': True},
    'wjets_CR': {   'info': {   'color': 418L,
                             'label': 'W+jets CR',
                             'typ': 'bkg'},
                 'plot': True},
    'zjets_CR': {   'info': {   'color': 418L,
                             'label': 'Z+jets CR',
                             'typ': 'bkg'},
                 'plot': True},
    'data_CR': {   'info': {   'color': 418L,
                             'label': 'Multijet CR',
                             'typ': 'bkg'},
                 'plot': True},
    'ttbarGamma': {   'info': {   'color': ROOT.kGreen +1,
                             'label': 't#bar{t}#gamma',
                             'typ': 'bkg'},
                 'plot': True},
    'VH_hbb': {   'info': {   'color': ROOT.kViolet +7,
                             'label': 'VH(bb)',
                             'typ': 'bkg'},
                 'plot': True},                 
    }

tHW_decays = {'tHW_{}'.format(decay): {   'info': {   'color': 603L,
                               'label': 'tHW (SM)',
                               'typ': 'bkg'},
                   'plot': True} for decay in "hbb hcc hww htt hzz hgg hzg hgluglu".split()}
samples.update(tHW_decays)
tHq_decays = {'tHq_{}'.format(decay): {   'info': {   'color': 603L,
                               'label': 'tHq (SM)',
                               'typ': 'bkg'},
                   'plot': True} for decay in "hbb hcc hww htt hzz hgg hzg hgluglu".split()}
samples.update(tHq_decays)
#combined samples
plottingsamples = {   
    't#bar{t}+H': {   'addSamples': [   'ttH_hbb',
                                        'ttH_hcc',
                                        'ttH_htt',
                                        'ttH_hgg',
                                        'ttH_hgluglu',
                                        'ttH_hww',
                                        'ttH_hzz',
                                        'ttH_hzg',
                                        'ttH_hnonbb'],
                      'color': 601L,
                      'label': 't#bar{t}+H',
                      'typ': 'signal'},
    'tHW': {   'addSamples': [ "tHW_{}".format(x) for x in "hbb hcc hww htt hzz hgg hzg hgluglu".split()],
                      'color': 603L,
                      'label': 'tHW (SM)',
                      'typ': 'bkg'},
    'tHq': {   'addSamples': [ "tHq_{}".format(x) for x in "hbb hcc hww htt hzz hgg hzg hgluglu".split()],
                      'color': 606L,
                      'label': 'tHq (SM)',
                      'typ': 'bkg'},
    'ttV': {   'addSamples': [   'ttbarZ',
                                 'ttbarW'],
               'color': 432L,
               'label': 't#bar{t}+V',
               'typ': 'bkg'},
    'vjets': {   'addSamples': [   'wjets',
                                   'zjets'],
                 'color': 18,
                 'label': 'V+jets',
                 'typ': 'bkg'},
    "CRs" : { 'addSamples' : "diboson_CR singlet_CR ttbarW_CR ttbarZ_CR ttbb_CR ttcc_CR ttlf_CR wjets_CR zjets_CR data_CR".split(),
            "color" : 418L,
            "label" : "ddQCD",
            "typ" : "bkg"
        }             
    }

#systematics to be plotted
systematics = [   ]

# order of the stack processes, descending from top to bottom
sortedprocesses = [   
    'signal',
    'total_signal',
    'ttlf',
    'ttcc',
    'ttbb',
    'ttbb_5FS',
    'ttbb_4FS']

#options for the plotting style
plotoptions = {   'cmslabel': 'private Work',
    'data': 'data_obs',
    'datalabel': 'pseudo data',
    'logarithmic': True,
    'lumiLabel': '41.5',
    'nominalKey': '$PROCESS__$CHANNEL',
    'normalize': False,
    'ratio': '#frac{data}{MC Background}',
    'shape': False,
    'signalScaling': -1,
    'splitLegend': True,
    'statErrorband': False,
    'systematicKey': '$PROCESS__$CHANNEL__$SYSTEMATIC',
    # "combineflag" : "shapes_prefit"/"shapes_fit_s",
    # "signallabel" : "Signal"
}
    
