slide_template = """\\subsection*{{{clearname}}}
\\begin{{frame}}
\\label{{ {label} }}
	\\begin{{scriptsize}}
	\\begin{{center}}
		\\begin{{Huge}}
			{clearname}
		\\end{{Huge}}

	\\end{{center}}
	\\end{{scriptsize}}
\\end{{frame}}
\\begin{{frame}}{{ {clearname} }}
	\\begin{{scriptsize}}
		\\input{{\\pathToResultTex/{filename} }}
	\\end{{scriptsize}}
\\end{{frame}}
	"""

prefix_label = "blinded_results"
prefix_clearname = "2017"
