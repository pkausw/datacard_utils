slide_template = """\\subsection*{{{clearname}}}
\\begin{{frame}}
\label{{{label}}}
	\\begin{{center}}
		\\begin{{Huge}}
			{clearname}
		\end{{Huge}}
		
		\\ Missing inputs: \\texttt{{
			{missing_vars}
		}}
	\end{{center}}
\end{{frame}}
\input{{\pathToImpactTex/{filename}}}
	"""

prefix_label = "unblinded_impacts"
prefix_clearname = "all_years"

logfile = "json_creation.log"

texfile = "impacts*.tex"

parameters = """
PTH_0_60
PTH_60_120
PTH_120_200
PTH_200_300
PTH_GT300
""".split()
