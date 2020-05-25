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

prefix_label = "blinded_impacts"
prefix_clearname = "2017"

logfile = "json_creation.log"

texfile = "%s_impacts.tex"
