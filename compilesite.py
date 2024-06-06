#!/usr/bin/env python3

# compilesite.py - this is a python script to compile the given directory into a teXsite using the rules we have defined. 

# import statements
import sys
import os
import json
from pathlib import Path
import subprocess
import latex2mathml.converter
import shutil
from pybtex.database import parse_file
from pybtex.database import BibliographyData
from pybtex import format_from_string

# Print usage. TODO: -e flag to export to <directory>/publichtml, copying the html files and the image folder, so we can easily just grab everything and throw it on our production server
if len(sys.argv) == 1 or '-h' in sys.argv:
    print("Usage: compilesite.py <directory> [options]")
    print()
    print("Compiles the given directory into a teXsite. Options must be after the directory. Try using texsiteinit.py for creating your first directory to see the required files.")
    print()
    print("Options:")
    print("-h: Show this (h)elp menu.")
    print("-e: Put compile files in publichtml directory for easy (e)xporting.")
    exit()
    
# if here, then we should test that the given argument is a directory.

rootdir = sys.argv[1]

if not os.path.isdir(rootdir):
    # not a directory
    print("ERROR: {} is not a directory! Try compilesite.py -h for help.".format(rootdir))
    exit()

# if here, then it is a directory. check for index.txt.

tocFname = os.path.join(os.getcwd(), rootdir, 'index.txt')

if not os.path.exists(tocFname):
    # not a texsite directory
    print("ERROR: {} is not a teXsite directory! Missing required files! Try compilesite.py -h for help.".format(rootdir))
    exit()
    
# make images if it doesn't exist. 
mathdir = os.path.join(os.getcwd(),rootdir,"images")
Path(mathdir).mkdir(parents=True, exist_ok=True)

# load in index.txt toc into the compilerules dict, and pull the titles

# save filenames for the export
usedFnames = [os.path.join(os.getcwd(),rootdir,'index.html'),os.path.join(os.getcwd(),rootdir,'style.css')]

titlerules = dict()
compilerules = dict()
with open(tocFname) as f:
    for line in f:
        # if \include is here, assign \include{key}{valcompilerules}{title}
        # title rules maps fname (key) : valcompilerules title
        if '\\include' in line:
            compilerules[line.split('}{')[0].split('{')[1]] = line.split('}{')[1]
            titlerules[line.split('}{')[0].split('{')[1]] = line.split('}{')[1] + ' ' + line.split('}{')[2].split('}')[0]
            usedFnames.append(os.path.join(os.getcwd(), rootdir, line.split('}{')[0].split('{')[1].split('.')[0] + '.html'))
            
    
# first, run through each file and pull all the labels to make the map. Don't want more than one file open at a time. Probably not a big deal, but do it this way anyway

mapping = dict()
linkmapping = dict() # for storing the hyperlink
tocompileFnames = list(compilerules.keys())
substructuremap = dict() # for storing sections and subsections
for fname in tocompileFnames:
    # first, initialize all counting indices
    sections = 0
    subsections = 0
    #subsubsections = 0 # don't want this one, too small
    figures = 0
    equations = 0
    tables = 0
    bibflag = 0
    substructuremap[fname] = list() # to add the substructure lines to
    with open(os.path.join(os.getcwd(), rootdir, fname)) as file:
        for line in file:
            # check for each thing. then pull label, determine number, add to mapping
            if '\\bibliography' in line:
                # treat it as a section
                sectionname = 'References'
                label = fname + '-references'
                sections += 1
                mapping[label] = compilerules[fname] + '.' + str(sections)
                #linkmapping[label] = '/' + fname + '#' + label
                linkmapping[label] = fname.split('.')[0] + '.html' + '#' + label
                # start over on subsections and subsubsections
                subsections = 0
                subsubsections = 0
                # add substructure line for printing on TOC
                substructuremap[fname].append('<h3><pre>   <a href="' + linkmapping[label] + '">' + mapping[label] + ' ' + sectionname + '</a></pre></h3>')
                
            if '\\section' in line:
                # add a section
                sectionname = line.split('}{')[0].split('{')[1]
                label = line.split('}{')[1].split('}')[0] # cut out that last }
                # increment sections
                sections += 1
                mapping[label] = compilerules[fname] + '.' + str(sections)
                #linkmapping[label] = '/' + fname + '#' + label
                linkmapping[label] = fname.split('.')[0] + '.html' + '#' + label
                # start over on subsections and subsubsections
                subsections = 0
                subsubsections = 0
                # add substructure line for printing on TOC
                substructuremap[fname].append('<h3><pre>   <a href="' + linkmapping[label] + '">' + mapping[label] + ' ' + sectionname + '</a></pre></h3>')
                
            if '\\subsection' in line:
                # add a subsection
                sectionname = line.split('}{')[0].split('{')[1]
                label = line.split('}{')[1].split('}')[0] # cut out that last }
                # increment subsections
                subsections += 1
                mapping[label] = compilerules[fname] + '.' + str(sections) + '.' + str(subsections)
                #linkmapping[label] = '/' + fname + '#' + label
                linkmapping[label] = fname.split('.')[0] + '.html' + '#' + label
                # add substructure line for printing on TOC
                substructuremap[fname].append('<h4><pre>            <a href="' + linkmapping[label] + '">' + mapping[label] + ' ' + sectionname + '</a></pre></h4>')
                
            if '\\begin{figure}' in line:
                # add a figure
                label = line.split('}{')[1].split('}')[0] # cut out that last }
                # increment figures
                figures += 1
                mapping[label] = compilerules[fname] + '.' + str(figures)
                #linkmapping[label] = '/' + fname + '#' + label
                linkmapping[label] = fname.split('.')[0] + '.html' + '#' + label
                
            if '\\begin{table}' in line:
                # add a table
                label = line.split('}{')[1].split('}')[0] # cut out that last }
                # increment figures
                tables += 1
                mapping[label] = compilerules[fname] + '.' + str(tables)
                #linkmapping[label] = '/' + fname + '#' + label
                linkmapping[label] = fname.split('.')[0] + '.html' + '#' + label
                
            if '\\begin{equation}' in line: # here we only give a single equation number to an align..... is that ok?
                # add an equation
                label = line.split('}{')[1].split('}')[0] # cut out that last }
                # increment equations
                equations += 1
                mapping[label] = compilerules[fname] + '.' + str(equations)
                #linkmapping[label] = '/' + fname.split('.')[0] + '.html' + '#' + label
                linkmapping[label] = fname.split('.')[0] + '.html' + '#' + label
                
# and that should conclude the map. No need to store it to a file

# may want to add compilerules so we can reference pages themselves, not just sections.

for page in compilerules.keys():
    mapping[page] = compilerules[page]
    #linkmapping[page] = '/' + page.split('.')[0] + '.html'
    linkmapping[page] = page.split('.')[0] + '.html'

#print(mapping)

# next, we go through each file and make our replacements, then write it to an html file

usedfigureFnames = [] # keep these for copying later with -e flag if necessary

for fname in tocompileFnames:
    # open the file and get the lines
    with open(os.path.join(os.getcwd(), rootdir, fname)) as file:
        lines = list(file)

    # check for a bibliography to make
    filestring = ''.join(lines)
    bib_data = dict() # empty dict so that cite just gives ?? if something is wrong with bib file
    citedarticles = dict() # this keeps the map of key:ref number for us. Later, use citedarticles.values() to actually make the bibliography
    if '\\bibliography' in filestring:
        # grab the bib file we are making the bibliography from and the style
        bibfname = filestring.split('\\bibliography{')[1].split('}{')[0] # \\bibliography{file.bib}{style}
        bibstyle = filestring.split('\\bibliography{')[1].split('}{')[1].split('}')[0] # \\bibliography{file.bib}{style}
        # get full bibfname
        bibfname = os.path.join(os.getcwd(), rootdir, bibfname)
        # check that it exists, then do it
        if os.path.exists(bibfname):
            # it does exist, so do it
            # process the file, getting all possible bib keywords that could appear in cite
            bib_data = parse_file(bibfname) # bib_data.entries holds key:data information
        
    # now that we have the lines, loop through and do our replacements
    newlines = ['<html><head><link rel="stylesheet" href="style.css"></head><body><div><p><a href=index.html>Table of Contents</a></p>','<h1>' + titlerules[fname] + '</h1>']
    kk = 0
    while kk < (len(lines)):
        currentline = lines[kk].split('##')[0] # split off any comments
        newline = '<p>' + str(currentline) + '</p>' # str to stop copy issues, wrap in <p> for default behavior.
        # deal with sections
        if '\\section' in currentline:
            heading = currentline.split('}{')[0].split('{')[1] # cut out the beginning
            label = currentline.split('}{')[1].split('}')[0] # cut out that last }
            newline = "<h2 id='" + label + "'>" + mapping[label] + ' ' + heading + '</h2>\n'
            
        # deal with subsections
        if '\\subsection' in currentline:
            heading = currentline.split('}{')[0].split('{')[1] # cut out the beginning
            label = currentline.split('}{')[1].split('}')[0] # cut out that last }
            newline = "<h3 id='" + label + "'>" + mapping[label] + ' ' + heading + '</h3>\n'
            
        # deal with ref
        if '\\ref' in currentline:
            # split along the refs
            splitcurrentline = currentline.split('\\ref{')
            newline = splitcurrentline[0]
            for jj in range(1,len(splitcurrentline)):
                label = splitcurrentline[jj].split('}')[0]
                mappingoflabel = '??'
                linkmappingoflabel = fname.split('.')[0] + '.html'
                if label in mapping.keys():
                    # it is a valid label, so we should grab the actual mapping and linkmapping
                    mappingoflabel = mapping[label]
                    linkmappingoflabel = linkmapping[label]
                    
                newline += "<a href='" + linkmappingoflabel + "'>" + mappingoflabel + "</a>" + '}'.join(splitcurrentline[jj].split('}')[1:])
                
            newline = '<p>' + newline + '</p>'
                
        # deal with equations
        if '\\begin{equation}' in currentline:
            # find all lines we need to take
            jj = 0
            while '\\end{equation}' not in lines[kk+jj]:
                jj += 1
                
            # once we get here, lines[kk+jj] is the corresponding end. So, now use \tag{mapping[label]} instead of {label} and we're set
            label = currentline.split('}{')[1].split('}')[0] # cut out that last }
            #newline = currentline.split('}')[0] + '} \\tag{' + mapping[label] + '}\n'
            #newline = currentline.split('}')[0] + '}\n \\text{(' + mapping[label] + ')}\;\;\;\;\;\;\;\;\;\;\;'
            newline = currentline.split('}')[0] + '}\n' 
            latexbody = ''
            latexbody += newline
            for nn in range(1,jj+1):
                # insert the equation number
                if nn==jj-1:
                    # line before end, remove any new line characters, then add the number and \n
                    lines[kk+nn] = lines[kk+nn].strip() + '\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\; \\text{(' + mapping[label] + ')}\n'
                    
                latexbody += lines[kk+nn]
            
            # make the mathml and put it at the right spot
            newline = latex2mathml.converter.convert(latexbody,display="block")
            newline = newline[:5] + " id='" + label + "'" + newline[5:]
            #print(latexbody)
            kk += jj # skip to the appropriate place after all the equation body   
            
        # deal with equation*
        if '\\begin{equation*}' in currentline:
            # find all lines we need to take
            jj = 0
            while '\\end{equation*}' not in lines[kk+jj]:
                jj += 1
                
            # once we get here, lines[kk+jj] is the corresponding end. No label to grab
            #label = currentline.split('}{')[1].split('}')[0] # cut out that last }
            #newline = currentline.split('}')[0] + '} \\tag{' + mapping[label] + '}\n'
            #newline = currentline.split('}')[0] + '}\n \\text{(' + mapping[label] + ')}\;\;\;\;\;\;\;\;\;\;\;'
            #newline = currentline
            latexbody = ''
            latexbody += currentline
            for nn in range(1,jj+1):
                # No need to insert the equation number, but still insert the padding
                if nn==jj-1:
                    # line before end, remove any new line characters, then add the number and \n
                    lines[kk+nn] = lines[kk+nn].strip() + '\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;'
                    
                latexbody += lines[kk+nn]
            
            # make the mathml and put it at the right spot
            newline = latex2mathml.converter.convert(latexbody,display="block")
            #newline = newline[:5] + " id='" + label + "'" + newline[5:]
            #print(latexbody)
            kk += jj # skip to the appropriate place after all the equation body 
            
        # deal with figures 
        if '\\begin{figure}' in currentline:
            # take this line, next line (which is include graphics), next line (which is caption), and next line (which is \\end{figure})
            label = currentline.split('}{')[1].split('}')[0] # cut out that last }
            figureFname = lines[kk+1].split('}')[0].split('{')[1]
            usedfigureFnames.append(os.path.join(os.getcwd(), rootdir, 'images', figureFname))
            multiple = 1
            if '}{' in lines[kk+1]:
                # we have some scaling to deal with
                multiple = lines[kk+1].split('}{')[1].split('}')[0]
                
            caption = '}'.join(('{'.join(lines[kk+2].split('{')[1:])).split('}')[:-1]) # do it this way just in case {} are in the caption itself                   
            # now we add <figure><img src="images/figureFname" alt="caption" style="width:100*multiple%"><figcaption>Fig label caption</figcaption></figure>
            newline = '<figure id="' + label + '"><img src="images/' + figureFname + '" alt="' + caption + '" style="width:' + str(int(100*float(multiple))) + '%">'
            # now within caption, we need to do any inline math. This is only for the display, not for the alt
            if '$$' in caption:
                splitcaption = caption.split('$$')
                if len(splitcaption) > 2:
                    # we have format text $$ math $$ text $$ math $$ text ...
                    newcaption = splitcaption[0]
                    for jj in range(1,len(splitcaption)):
                        if jj%2 == 1:
                            # odds are math
                            newcaption += latex2mathml.converter.convert(splitcaption[jj])
                        else:
                            # evens are text
                            newcaption += splitcaption[jj]
                            
                    caption = str(newcaption)
                    
            # also do any refs
            if '\\ref' in caption:
                # split along the refs
                splitcaption = caption.split('\\ref{')
                newcaption = splitcaption[0]
                for mm in range(1,len(splitcaption)):
                    reflabel = splitcaption[mm].split('}')[0]
                    mappingoflabel = '??'
                    linkmappingoflabel = fname.split('.')[0] + '.html'
                    if reflabel in mapping.keys():
                        # it is a valid label, so we should grab the actual mapping and linkmapping
                        mappingoflabel = mapping[reflabel]
                        linkmappingoflabel = linkmapping[reflabel]
                        
                    newcaption += "<a href='" + linkmappingoflabel + "'>" + mappingoflabel + "</a>" + '}'.join(splitcaption[mm].split('}')[1:])
                    
                caption = newcaption
            
            newline += '<figcaption><b>Fig ' + mapping[label] + '</b> ' + caption + '</figcaption></figure>'
            kk += 3 # we just finished the end figure line
        
        # deal with tables, make every line but make the lines light gray for readability 
        if '\\begin{table}' in currentline:
            label = currentline.split('}{')[1].split('}')[0] # cut out that last }
            # find all lines we need to take. should be begin table, table body, caption, end table
            jj = 0
            while '\\end{table}' not in lines[kk+jj]:
                jj += 1
                
            # now we need to assemble the table 
            newline = '<figure id="' + label + '"><table>'
            for nn in range(1,jj-1):
                # split along &
                newline += '<tr>'
                splittabrow = lines[kk+nn].split('&')
                for tabentry in splittabrow:
                    # figure out if we take up more than one column
                    data = str(tabentry) # avoid copying issues
                    colspantext = ''
                    if '\\multicolumn' in tabentry:
                        colspan = tabentry.split('}{')[0].split('{')[1]
                        colspantext = ' colspan="' + colspan + '"'
                        data = tabentry.split('}{')[1].split('}')[0]
                        
                    tagtype = 'td'
                    # if first row, use th
                    if nn == 1:
                        tagtype = 'th'
                        
                    # deal with math
                    if '$$' in data:
                        newdata = ''
                        # we have math, make sure we have two otherwise skip
                        splitdata = data.split('$$')
                        if len(splitdata) > 2:
                            # text $$ math $$ text $$ math $$ text ...
                            newdata = splitdata[0]
                            for mm in range(1,len(splitdata)):
                                if mm %2 == 1:
                                    # odds are math
                                    newdata += latex2mathml.converter.convert(splitdata[mm])
                                else:
                                    # evens are text
                                    newdata += splitdata[mm]
                                    
                            data = newdata
                            
                    # deal with refs in data TODO
                    
                    newline += '<' + tagtype + colspantext + '>' + data + '</' + tagtype + '>'
                    
                newline += '</tr>'
            
            newline += '</table>'
            # now do caption. First, pull it
            caption = '}'.join(('{'.join(lines[kk+jj-1].split('{')[1:])).split('}')[:-1]) # do this in case {} in line
            # compile math in caption
            if '$$' in caption:
                newcaption = ''
                # we have math, make sure we have two otherwise skip
                splitcaption = caption.split('$$')
                if len(splitcaption) > 2:
                    # text $$ math $$ text $$ math $$ text ...
                    newcaption = splitcaption[0]
                    for mm in range(1,len(splitcaption)):
                        if mm%2 == 1:
                            # odds are math
                            newcaption += latex2mathml.converter.convert(splitcaption[mm])
                        else:
                            # evens are text
                            newcaption += splitcaption[mm]
                            
                    caption = newcaption
                    
            # also do any refs
            if '\\ref' in caption:
                # split along the refs
                splitcaption = caption.split('\\ref{')
                newcaption = splitcaption[0]
                for mm in range(1,len(splitcaption)):
                    reflabel = splitcaption[mm].split('}')[0]
                    mappingoflabel = '??'
                    linkmappingoflabel = fname.split('.')[0] + '.html'
                    if reflabel in mapping.keys():
                        # it is a valid label, so we should grab the actual mapping and linkmapping
                        mappingoflabel = mapping[reflabel]
                        linkmappingoflabel = linkmapping[reflabel]
                        
                    newcaption += "<a href='" + linkmappingoflabel + "'>" + mappingoflabel + "</a>" + '}'.join(splitcaption[mm].split('}')[1:])
                    
                caption = newcaption
            
            newline += '<figcaption><b>Tab ' + mapping[label] + '</b> ' + caption + '</figcaption></figure>'
            kk += jj # set to the right line, the end table line
        
        # deal with inline math, $$ $$
        if '$$' in currentline:
            # make sure we have two of them, otherwise just skip it
            splitcurrentline = currentline.split('$$')
            if len(splitcurrentline) > 2:
                # we have format text $$ math $$ text $$ math $$ text ...
                newline = splitcurrentline[0]
                for jj in range(1,len(splitcurrentline)):
                    if jj%2 == 1:
                        # odds are math
                        newline += latex2mathml.converter.convert(splitcurrentline[jj])
                    else:
                        # evens are text
                        newline += splitcurrentline[jj]
                        
                newline = '<p>' + newline + '</p>'
        
        # everything else is wrapped in <p>
            
        newlines.append(newline)
        kk += 1

    # now that we have all the lines, let's find and replace all cites and replace the bibliography command with the actual bibliography
    biblioindex = ''
    for kk in range(len(newlines)):
        nwln = newlines[kk]
        if '\\cite' in nwln:
            # words \\cite{key,key,key,...} words \cite{key,key,key,...} words etc...
            brokenline = nwln.split('\\cite{')
            for jj in range(1,len(brokenline)):
                # all start with keylists
                keystr = brokenline[jj].split('}')[0]
                keylist = keystr.split(',')
                keylist = [ky.strip() for ky in keylist] # get rid of spaces etc
                vallist = [citedarticles[kv] if kv in citedarticles.keys() else '??' for kv in keylist] # default is ??
                # test keys for in bibliography
                for hh in range(len(keylist)):
                    if vallist[hh] == '??' and keylist[hh] in bib_data.entries.keys():
                        # it is here, add it
                        citedarticles[keylist[hh]] = len(citedarticles.values()) + 1
                        vallist[hh] = citedarticles[keylist[hh]]

                # now do the replacement
                vallist = sorted(vallist)
                kkind = 0
                while kkind+2 < len(vallist):
                    if vallist[kkind+2] - vallist[kkind] == 2:
                        # we have consecutives
                        runind = kkind+2
                        while runind < len(vallist) and vallist[runind] - vallist[kkind] == runind-kkind:
                            runind += 1

                        vallist[kkind:runind] = [str(vallist[kkind]) + '-' + str(vallist[runind-1])]
                        
                    kkind += 1
                # replace consecutives with a-b
                brokenline[jj] = '[' + ', '.join([str(vv) for vv in vallist]) + ']' + ''.join(brokenline[jj].split('}')[1:])

            # now rejoin up brokenline
            newlines[kk] = ''.join(brokenline)
            
        if '\\bibliography' in nwln:
            biblioindex = kk # this is where to put it

    # now create and insert the bibliography
    if biblioindex != '':
        invertedcitedarticles = {vv:ke for ke,vv in zip(citedarticles.keys(),citedarticles.values())}
        orderedcitedarticles = [invertedcitedarticles[vv+1] for vv in range(len(citedarticles))]
        actuallycitedbibdata = [format_from_string(BibliographyData({ke:bib_data.entries[ke]}).to_string('bibtex'),bibstyle,output_backend='html') for ke in orderedcitedarticles]
        # now pull just the entries from each and put the correct numbering in
        #actuallycitedbibdata = ['<dt>' + str(indx+1) + '</dt>\n<dd>' + actuallycitedbibdata[indx].split('<dd>')[1].split('</dd>')[0] + '</li>\n' for indx in range(len(actuallycitedbibdata))]
        actuallycitedbibdata = ['<p><li>' + actuallycitedbibdata[indx].split('<dd>')[1].split('</dd>')[0] + '</li></p>\n' for indx in range(len(actuallycitedbibdata))]
        bibhtml = "<h2 id='" + fname + '-references' + "'>" + mapping[fname + '-references'] + ' References' + '</h2>\n'
        bibhtml += '<ol>\n' + ''.join(actuallycitedbibdata) + '</ol>\n'
        newlines[biblioindex:biblioindex+1] = bibhtml
    
    # write the whole thing to html
    # first append toc link and div part again, and add watermark
    newlines.append('<p><a href=index.html>Table of Contents</a></p>')
    newlines.append('<p class=texsite>This is a <a href="https://github.com/cdkocher/teXsite" target="_blank">teXsite</a>.</p></body></html>')
    newlines.append('</div>')
    towrite = ''.join(newlines)
    with open(os.path.join(os.getcwd(), rootdir, fname.split('.')[0] + '.html'), 'w') as file:
        file.write(towrite) 
        
    #print(''.join(newlines))
    
# make stylesheet: 
csstowrite = "div{max-width: 1000px; position: absolute; left: 50%; transform: translate(-50%,0); text-align: justify;}\n"
csstowrite += "math{font-size: 20px}\n"
csstowrite += "figcaption math{font-size: 16px}\n"
csstowrite += 'p{text-align: justify; font-size: 20px;}\n'
csstowrite += '.texsite{text-align: justify; font-size: 13px; color: gray;}\n'
csstowrite += 'h1{font-size: 38px}\n'
csstowrite += 'h2{font-size: 30px}\n'
csstowrite += 'h3{font-size: 25px}\n'
csstowrite += 'figcaption{text-align: justify; padding-top: 5px;}\n'
csstowrite += 'figure{text-align: center;}\n'
csstowrite += 'table{text-align: center; border: 1px solid #ddd; font-size: 18px;  margin-left: auto; margin-right: auto;}\n'
csstowrite += 'td{text-align: center; border: 1px solid #ddd;}\n'
csstowrite += 'th{text-align: center; border: 1px solid #ddd;}\n'
with open(os.path.join(os.getcwd(), rootdir,'style.css'), 'w') as file:
    file.write(csstowrite)

# make TOC page with substructure
tochtml = '<html><head><link rel="stylesheet" href="style.css"></head><body><div><h1>Table of Contents</h1>'
with open(tocFname) as f:
    for line in f:
        newline = str(line)
        # if \include is here, make a link
        if '\\include' in line:
            currentfname = line.split('}{')[0].split('{')[1]
            newline = "<h2><a href='" + line.split('}{')[0].split('{')[1].split('.')[0] + '.html' + "'>" + line.split('}{')[1] + ' ' + line.split('}{')[2].split('}')[0] + "</a></h2>"
            # now add substructure
            for substructurestring in substructuremap[currentfname]:
                newline += substructurestring
            
        tochtml += newline
        
tochtml += '<p class=texsite>This is a <a href="https://github.com/cdkocher/teXsite" target="_blank">teXsite</a>.</p></div></body></html>'
toctowrite = ''.join(tochtml)
with open(os.path.join(os.getcwd(), rootdir,'index.html'), 'w') as file:
    file.write(toctowrite)

# if -e, copy stuff to publichtml
if '-e' in sys.argv:
    # if publichtml exists, delete it
    publichtmldir = os.path.join(os.getcwd(), rootdir, 'publichtml')
    if os.path.exists(publichtmldir):
        # delete it
        shutil.rmtree(publichtmldir)
    
    # add publichtml and images dir
    publichtmlimagesdir = os.path.join(os.getcwd(), rootdir, 'publichtml', 'images')
    Path(publichtmlimagesdir).mkdir(parents=True, exist_ok=True)
    # copy files
    for htmlfile in usedFnames:
        shutil.copy(htmlfile,publichtmldir)
        
    for figfile in usedfigureFnames:
        shutil.copy(figfile,publichtmlimagesdir)
        

# TODO: could further make a script that converts a latex project into a texsite one. That seems like it would be nice. Just put the labels in the right place, change the figures to the right format, do inline math to $$ not $, change aligns to separate equations, tables as well.

# TODO: should make support for references from .bib file...

# Also should switch toc to index, and include support for \underline, \bold, \link


