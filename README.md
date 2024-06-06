# teXsite
A simple python-based solution for creating websites in LaTeX

TeXsite is a solution for including math on websites, say if you want to post course notes or a blog. (1) Initialize a teXsite directory using texsiteinit.py <new-directory-name>. (2) Write the content in LaTeX-friendly .txt files, following the formatting of the boilerplate files. (3) Compile the site together using compilesite.py <directory-name> -e. (4) Copy the resulting <directory-name>/publichtml folder to your website's root directory, and you are done. TeXsite produces a static HTML site and has support for figures, tables, cross-site references (i.e. referencing equations on a different page), and bibliographies; see the example files for a full list of features.

Python dependencies (required in order to run; make sure you can import them): pybtex, latex2mathml, shutil, json, pathlib, subprocess, sys, os
