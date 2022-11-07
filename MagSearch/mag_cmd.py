#!/usr/bin/env python3
# Command line search for magazines

import sys, os, os.path
sys.path.append('/home/pi/Python/lib')
from cli_class import cli
from mag_class import ScanMag

def search(pars):
    if len(pars) > 0:
        # scan parameters for options (start with --)
        options, keys = [], []
        for p in pars:
            if p.startswith('--'):
                options.append(p)
            else:
                keys.append(p.lower())
        if len(options) == 0: options = ['--any']
        se.match_mode = options[0]

        se.search(keys)
        if len(se.results) > 0:
            se.print('\nNumber of hits : {}'.format(len(se.results)))
            imax = 10 if len(se.results) > 10 else len(se.results)
            for i in range(imax):
                el = se.results[i]
                us = el[0].rindex('_')
                magazine, page = el[0][:us], el[0][us+1:]
                nhits = el[1][0]
                s = '{:02d} {:20s}  page{:>4s} [{:3d}]   '.format(i, magazine+' '+'.'*(20-len(magazine)), page, nhits)
                for e in el[1][1].items():
                    s += '{:2d}%|'.format(round(e[1]/nhits*100))
                se.print(s[:-1])
            
            # print the magazines with the most occurrences and show the page numbers
            m = {}
            for e in se.results:
                us = e[0].rindex('_')
                magazine, page = e[0][:us], e[0][us+1:]
                if magazine in m.keys():
                    m[magazine].append(int(page))
                    m[magazine].sort()
                else:
                    m[magazine] = [int(page)]

            print('')
            res = sorted(m.items(), key=lambda item: len(item[1]), reverse=True)
            imax = 5 if len(res) > 5 else len(res)
            for i in range(imax):
                s = '  {:10s} : '.format(res[i][0])
                pages = res[i][1]
                for p in pages:
                    s += '{:>3d} '.format(p)
                print(s)
                
def pdf(pars):
    def __loadpdf__(magazine):
        fl = se.mag_folder + magazine + '.pdf'
        if os.path.exists(fl):
            print('  PDF : {}  page {}'.format(fl, page))
            s = 'evince -i ' + page + ' "'+ fl +'" 2>/dev/null &'
            os.system(s)
        else:
            se.print('{} does not exist'.format(fl), 'red')

    magazine, page = __pars_to_fn__(pars)
    if magazine != '':
        __loadpdf__(magazine)

def __pars_to_fn__(pars):
    # return input to magazine_id and page
    if len(pars)>=1 and not pars[0].isnumeric():
        page = '1' if len(pars)<2 else pars[1]
        if pars[0][0] != '#':
            if not pars[0]+'.pdf' in se.files:
                se.print('Magazine {} does not exist'.format(pars[0]), 'red')
                return('', 0)
            else:
                return(pars[0], page) # magazine manually entered
        else:
            fn = se.nr_to_fn(int(pars[0][1:])) # inclusive extension
            if fn != '':
                return(fn.split('.')[0], page) # remove extension
            else:
                se.print('Magazine {} does not exist'.format(pars[0]), 'red')
                return('', 0)

    elif len(se.results) > 0:
        if len(pars) == 0: pars = ['0']
        if len(pars) == 1:
            mag_page = se.results[int(pars[0])][0]
            us = mag_page.rindex('_')
            return(mag_page[:us], mag_page[us+1:])
    else:
        se.print('No search results available', 'red')
        return('', 0)

def new(pars):
    if len(pars) == 1:
        if pars[0] in se.magazines:
            se.init(pars[0])
            # se.load_db(pars[0] + '.db')
            se.load_db(se.database)
            se.print('Search for keywords in the magazine ' + se.mag_id)
        else:
            se.print('Magazine should be ' + ', '.join(se.magazines).format(), 'red')
    else:
        se.print('Available : ', end='')
        se.print(', '.join(se.magazines), 'green')

def add(pars):
    if len(pars) == 1:
        if se.add_magazine(pars[0]):
            # db_file = se.mag_id.lower() + '.db'
            db_file = se.database
            se.print('Saved to database \'{}\''.format(db_file))
            se.save_db(db_file)
    else:
        se.mag_nrs()
        se.print('{} folder : first = {}  last = {}'.format(se.mag_id, se.folder_firstmag, se.folder_lastmag))
        se.print('Database : last = {}'.format(se.db_lastmag))
        if se.db_lastmag != se.folder_lastmag:
            se.print('Database is not up to date', 'red')

def keys(pars):
    (magazine, page) = __pars_to_fn__(pars)
    if magazine != '':
        dct = se.mag_db[magazine][int(page)]
        results = sorted(dct.items(), key=lambda item: item[1], reverse=True)
        nitems = 7
        for j in range(2):
            s = '  '
            for i in range(nitems):
                idx = i + nitems*j
                s += '{}  '.format(results[idx][0])
            print(s)

def build(pars):
    if se.save_db_enable:
        if len(pars) >= 2:
            se.mag_db = {}
            
            if len(pars) >= 3:
                path = pars[2]
                if path[-1] != '/': path += '/'
                se.mag_folder = path
                
            db_file = pars[3] if len(pars)==4 else se.database

#             for nr in range(int(pars[0]), int(pars[1])+1):
#                 se.add_magazine(nr)
#             se.save_db(db_file)
        se.save_db_enable = False
    else:
        se.print('Creation of a new database has not been enabled'.format(), 'red')
        
def enable(pars):
    se.save_db_enable = True
    se.print('The creation of a new database has been enabled'.format(), 'green')

se = ScanMag()

# start from the command line
if len(sys.argv) < 2:
    print('magsearch <' + '/'.join(se.magazines) + '>')
    sys.exit()
else:
    magazine = sys.argv[1].lower()
    if magazine not in se.magazines:
        se.print('Magazine should be ' + ', '.join(se.magazines).format(), 'red')
        sys.exit()

# initialize search class and start cli
se.init(magazine)
se.print_enable = True

p = cli('Search for keywords in the magazine ' + se.mag_id)
p.command('add', ['[mag nr]'], 'Add a magazine to the database', add)
p.command('build', ['startnr', 'endnr', '[path to magazines]', '[database]'], 'Build a new database', build)
p.command('keys', ['[item in search table/magazine [page]/#nr [page]]'], 'Show the most occurring keywords on the page', keys)
p.command('new', ['[magazine]'], 'Change to a new magazine', new)
p.command('pdf', ['[item in search table/magazine [page]/#nr [page]]'], 'Open the PDF file of an item in the search table or open a magazine', pdf)
p.command('search', ['keyword', '[, keyword/--option]'], 'Search for a series of keywords. Options: --any, --start, --exact', search)
p.command('enable', [], 'Enable the building of a new database', enable)

# se.load_db(magazine.lower() + '.db')
se.load_db(se.database)

p.main()
