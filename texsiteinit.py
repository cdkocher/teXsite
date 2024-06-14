#!/usr/bin/env python3

# texsiteinit.py - this is a python script to initialize a new texsite by making the boilerplate files 

# import statements
import sys
import os
import json
from pathlib import Path
import shutil

# Print usage
if len(sys.argv) == 1 or '-h' in sys.argv:
    print("Usage: texsiteinit.py <directory> [options]")
    print()
    print("Initializes a new teXsite directory. Options must be after the directory.")
    print()
    print("Options:")
    print("-h: Show this (h)elp menu.")
    print("-v: Print the (v)ersion number.")
    exit()

versionnumber = '0.0.3'

if '-v' in sys.argv:
    print("teXsite initialization script, version {}".format(versionnumber))
    exit()
    
# if here, then we should test that the given argument is not an existing directory.

rootdir = sys.argv[1]

if os.path.isdir(rootdir):
    # not a directory
    print("ERROR: {} already exists! Try another name.".format(rootdir))
    exit()

# if here, then it is not a directory. Make it and images subdirectory

imagesdir = os.path.join(os.getcwd(),rootdir,"images")
Path(imagesdir).mkdir(parents=True, exist_ok=True)

# cp example image to that subdirectory
shutil.copy('example.png', imagesdir)

# make index.txt with some boilerplate

tocFname = os.path.join(os.getcwd(), rootdir, 'index.txt')
toctxt = '\\title{teXsite}\n'
toctxt += '\\author{Charles D. Kocher}\n'
toctxt += '\\backto{Previous Page}{https://github.com/cdkocher/teXsite}\n\n'
toctxt += 'Insert a description of your site here! This is a good place to say what your project is about, since it is the landing page for the whole thing.\n\n'
toctxt += '\\include{firstpage.txt}{1}{Your First Page}\n'
toctxt += '\\include{secondpage.txt}{2}{Your Second Page}\n'
with open(tocFname, 'w') as file:
    file.write(toctxt)

# write the example page to firstpage.txt
firstpageFname = os.path.join(os.getcwd(), rootdir, 'firstpage.txt')
firstpagetxt = '\\section{How do you make a teXsite?}{sec:howtomake}\n\n'
firstpagetxt += 'This is the first page of your teXsite. Here, we will give demonstrations of how everything works, including math, tables, images, and cross-site references.\n\n'
firstpagetxt += '\\subsection{Math}{subsec:math}\n\n'
firstpagetxt += 'TeXsite supports math. Here is an example of an inline formula: $$a^2 + b^2 = c^2$$. To include math like this, you enclose the math on each end by two dollar signs. It is like LaTeX, but with extra dollar signs. ## You can make comments like this, with two number signs!\n\n'
firstpagetxt += '\\subsection{Equations}{subsec:equations}\n\n'
firstpagetxt += 'Here is an example of an equation on a teXsite:\n\n'
firstpagetxt += '\\begin{equation}{eq:sample-eq}\n  \int \; dx \; x^2 = \\frac{x^3}{3} \; . \n\end{equation}\n\n'
firstpagetxt += 'You use begin and end equation commands like LaTeX, but you must include the label as another argument of begin. The equations are formatted using mathML. TeXsite will automatically number the equations in the order derived from your index.txt file. If you do not want an equation to be numbered, then you use equation* with no label argument:\n\n'
firstpagetxt += '\\begin{equation*}\n  \\frac{d}{dx} \\frac{x^3}{3} = x^2 \; . \n\end{equation*}\n\n'
firstpagetxt += 'There is no support for aligning multi-line equations currently.\n\n'
firstpagetxt += '\\subsection{Tables}{subsec:tables}\n\n'
firstpagetxt += 'Here is an example table. The syntax is like LaTeX, but again the label and caption are necessary in the positions shown in the firstpage.txt file. There is only support for multicolumn, not multirow. Math and references work in the table and caption.\n\n'
firstpagetxt += '\\begin{table}{tab:resource-shift-vals}\n & $$k_n$$ & $$B_n$$ & $$c_n$$ & $$q_n$$ & $$D_n$$\n$$A_1$$ & \\multicolumn{2}{1 & 1 & 1 & 2\n$$A_2$$ & 2 & 1 & 1 & 1 & 2\n$$A_3$$ & 3 & 1 & 1 & 1 & 1\n\\caption{This is an example table with a multicolumn. We have math in the table, and it also works in the caption, for example $$k_n^2$$.}\n\\end{table}\n\n'
firstpagetxt += '\\subsection{Figures}{subsec:figures}\n\n'
firstpagetxt += 'You can also include figures. Just like before, the syntax is TeX-like, but with the label and caption required. Changing the fraction in the new argument for \\includegraphics allows you to scale the figure by a certain percent. Image files must be in the images folder of your teXsite project.\n\n'
firstpagetxt += '\\begin{figure}{fig:example-fig}\n  \\includegraphics{example.png}{0.5}\n  \\caption{This is an example of a figure. Here, we have plotted $$x^2$$ over a certain domain near the origin.}\n\end{figure}\n\n'
firstpagetxt += '\\subsection{References}{subsec:references}\n\n'
firstpagetxt += 'Your teXsite can automatically compile a bibliography for you from a bib file, including in-line citations. Simply give the bibliography command a bib file and your preferred style, then cite within your txt file as normally for LaTeX, and it should compile correctly. For example, I can cite an article \\cite{kocher2023darwinian}, and I can cite a range of articles \\cite{kocher2023origins, kocher2021nanoscale, kocher2023darwinian}. Only the cited articles from your bib file will appear, so you only need to use one bib file for the whole site. You can check the second page, starting with Section \\ref{sec:pagetwo}, for demonstration. \n\n'
firstpagetxt += '\\subsection{Cross-Site References}{subsec:references}\n\n'
firstpagetxt += 'One great feature of teXsite is that you can make references across pages. For example, not only can you reference things on this page like Equation \\ref{eq:sample-eq} or Section \\ref{sec:howtomake}, but you can also reference things on another page, like Equation \\ref{eq:einstein}. References work in figure and table captions and in tables themselves. This is the advantage of compiling the whole project together versus, say, using javascript to compile the page client-side.\n\n'
firstpagetxt += '\\subsection{Other Features and Peculiarities}{subsec:peculiarities}\n\n'
firstpagetxt += 'You can also make comments in your txt files that will not compile with the project using two number signs. The rest of that line will be ignored. The compiler is a bit finnicky (the tradeoff is that it is fairly simple and easily extended to whatever your needs are). Stick closely to the formatting of these example pages, and make sure you use newlines appropriately. Try to avoid curly braces in your text if at all possible. Do not use extra dots in txt filenames. Keep everything in the same directory, your project cannot have subfolders. Do not use math in section names. Keep your TOC description to plain text.\n\n'
firstpagetxt += "HTML tags will work. Instead of adding them to the compiler with separate commands, we just pass them through. They are simple enough to learn, and we did not want to reinvent them. You can try <b>bold</b>, <u>underline</u>, <i>italics</i>, and even <a href='https://google.com' target='_blank'>links</a>, although make sure you use target='_blank' in your tag so the link opens in a new tab (it's nicer that way).\n\n"
firstpagetxt += '\\section{Final Words}{sec:finalwords}\n\n'
firstpagetxt += 'So, what else do you need to know? All you have to do is type up your .txt files in your project folder and \\include them in the index.txt file, including the chapter numbering you would like (you do not even need to use numbers). Then, you should run compilesite.py <project directory> to make the site. It will spit out .html files. Thus, you get a static html website that is easy to host. You can even do it for free on <a href="https://pages.github.com/" target="_blank">Github</a>. Why use teXsite? You easily get math, and it is in mathML, which is <a href="https://w3c.github.io/mathml-docs/gap-analysis/" target="_blank">accessible to screen readers</a>. The site is static html (no slow javascript). And, you can basically code the site like LaTeX (although with a few minor changes to how labeling works, and the use of a few simple HTML tags). Now go and make great teXsites!\n'
firstpagetxt += '\\bibliography{refs.bib}{unsrt}'

with open(firstpageFname, 'w') as file:
    file.write(firstpagetxt)

# write the example page to secondpage.txt
secondpageFname = os.path.join(os.getcwd(), rootdir, 'secondpage.txt')
secondpagetxt = '\\section{Another Page}{sec:pagetwo}\n\n'
secondpagetxt += 'This is the another page of your teXsite. Here, we will give an equation that is referenced on your first page, from Subsection \\ref{subsec:references}. Also, we can use different references on this page that will not show up there, like \cite{kocher2023prebiotic}.\n\n'
secondpagetxt += '\\begin{equation}{eq:einstein}\n  E = m c^2 \; . \n\end{equation}\n\n'
secondpagetxt += '\\bibliography{refs.bib}{unsrt}'

with open(secondpageFname, 'w') as file:
    file.write(secondpagetxt)

# write the bib file for the example
bibFname = os.path.join(os.getcwd(), rootdir, 'refs.bib')
bibtxt = '@article{kocher2023darwinian,\n'
bibtxt += '  title={Darwinian evolution as a dynamical principle},\n'
bibtxt += '  author={Kocher, Charles D and Dill, Ken A},\n'
bibtxt += '  journal={Proceedings of the National Academy of Sciences},\n'
bibtxt += '  volume={120},\n'
bibtxt += '  number={11},\n'
bibtxt += '  pages={e2218390120},\n'
bibtxt += '  year={2023},\n'
bibtxt += '  publisher={National Acad Sciences}\n'
bibtxt += '}\n\n'
bibtxt += '@article{kocher2023origins,\n'
bibtxt += '  title={Origins of life: first came evolutionary dynamics},\n'
bibtxt += '  author={Kocher, Charles and Dill, Ken A},\n'
bibtxt += '  journal={QRB discovery},\n'
bibtxt += '  volume={4},\n'
bibtxt += '  pages={e4},\n'
bibtxt += '  year={2023},\n'
bibtxt += '  publisher={Cambridge University Press}\n'
bibtxt += '}\n\n'
bibtxt += '@article{kocher2021nanoscale,\n'
bibtxt += '  title={Nanoscale catalyst chemotaxis can drive the assembly of functional pathways},\n'
bibtxt += '  author={Kocher, Charles and Agozzino, Luca and Dill, Ken},\n'
bibtxt += '  journal={The Journal of Physical Chemistry B},\n'
bibtxt += '  volume={125},\n'
bibtxt += '  number={31},\n'
bibtxt += '  pages={8781--8786},\n'
bibtxt += '  year={2021},\n'
bibtxt += '  publisher={ACS Publications}\n'
bibtxt += '}\n\n'
bibtxt += '@article{kocher2023prebiotic,\n'
bibtxt += '  title={The prebiotic emergence of biological evolution},\n'
bibtxt += '  author={Kocher, Charles D and Dill, Ken A},\n'
bibtxt += '  journal={arXiv preprint arXiv:2311.13650},\n'
bibtxt += '  year={2023}\n'
bibtxt += '}\n\n'

with open(bibFname, 'w') as file:
    file.write(bibtxt)
