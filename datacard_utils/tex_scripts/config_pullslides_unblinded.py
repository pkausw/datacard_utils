slide_template = """\\subsection*{%(CLEARNAME)s}
\\begin{frame}{%(CLEARNAME)s}
\label{%(LABEL)s}
	\\begin{center}
		\includegraphics[width=\\textwidth]{\pathToPulls/%(PLOTNAME)s}
	\end{center}
\end{frame}
	"""
label_template = "unblinded_pulls::%s"