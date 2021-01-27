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

texfile = "%s_impacts.tex"
