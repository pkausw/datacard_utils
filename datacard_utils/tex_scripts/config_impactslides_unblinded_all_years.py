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
prefix_clearname = "Full Run-II"

logfile = "json_creation.log"

texfile = "{}_impacts_r.tex"
