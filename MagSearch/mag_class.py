# Class for scanning the magazines Elektor, MagPi and HackSpace
#    installed software PyYAML, PyPDF2
#    pdftotext, based on Poppler

import os, re, pickle, time
import PyPDF2
from os import listdir
from os.path import isfile, join
import yaml

class ScanMag:
    def __init__(self):
        with open('config.yml') as f:
            self.config = yaml.load(f, yaml.SafeLoader)
        with open('parser.yml') as f:
            self.parser = yaml.load(f, yaml.SafeLoader)
        self.magazines = list(self.config['magazines'].keys())
        self.print_enable = False
        self.print_gui = None # tuple (root, text widget)
        self.new_line = True

    def init(self, mag_id):
        self.mag_db = {}   # database
        self.mag_id = self.config['magazines'][mag_id]['filename']
        self.language = self.config['magazines'][mag_id]['language']
        self.mag_folder = self.config['magazines'][mag_id]['directory']
        self.database = self.config['magazines'][mag_id]['database']
        self.files = [f for f in listdir(self.mag_folder) if isfile(join(self.mag_folder, f)) and f.startswith(self.mag_id)]
        self.stopwords = [w.strip() for w in self.parser['stopwords'][self.language].split(',')]
        self.except_words = [w.strip() for w in self.parser['except_1_2char'].split(',')]
        self.except_words += [w.strip() for w in self.parser['except_3char'].split(',')]
        self.results = []
        self.match_mode = self.config['match_mode']
        self.save_db_enable = False
        self.db_file_present = False
        self.overwrite = False
        self.max_spacing = self.config['max_spacing']
        
        # sort file list according to numbers
        nrs = [self.fn_to_nr(f)[1] for f in self.files]
        self.files = [x for _,x in sorted(zip(nrs, self.files), key=lambda pair: pair[0])]

    def fn_to_nr(self, fn):
        # retrieve integer number and descriptor from filename
        s = fn.split('.')[0]   # remove extension if present
        us = s.find('_')       # check for underscore
        descr = ''
        if us >= 0:
            descr = s[us+1:]
            s = s[:us]
        nr = int(s[len(self.mag_id):])
        return((self.mag_id, nr, descr))

    def nr_to_fn(self, nr):
        # select a filename based on the issue number
        for fn in self.files:
            if nr == self.fn_to_nr(fn)[1]: return(fn)
        return('')
    
    def mag_nrs(self):
        # determine which files are not in the database
        self.folder_firstmag, self.folder_lastmag = 1000, -1000
        files_db = self.mag_db.keys()
        for fn in self.files:
            if fn.split('.')[0] not in files_db:
                if fn.startswith(self.mag_id):
                    nr = self.fn_to_nr(fn)[1]
                    if nr > self.folder_lastmag: self.folder_lastmag = nr
                    if nr < self.folder_firstmag: self.folder_firstmag = nr

    def pdf2text(self, file_input, page):
        # Converts the MagPi PDF file to a list of words
        # Some codes are removed and C++ is replaced by cpp
        # file_input is the full filepath

        file_output = './tmp.txt'

        s = 'pdftotext -enc "UTF-8" -q -f '+str(page)+' -l '+str(page)+' "'+file_input+'" "'+file_output+'"'
        os.system(s)
        with open(file_output, 'rb') as f:
            self.doc = f.read()

        self.doc = re.sub(b'(c|C)\+\+', b'cpp', self.doc)
        self.doc = re.sub(b'[\x00-\x2f,\x3a-\x3f,\x5b-\x60,\x7b-\xff]', b' ', self.doc)
        self.wordlst = self.doc.decode().split()
        
    def remove_small_words(self, nchar=2):
        tmp = []
        for i in range(len(self.wordlst)):
            word = self.wordlst[i].lower()
            if (len(word) > nchar) or (word in self.except_words):
                tmp.append(word)
        self.wordlst = tmp

    def remove_stopwords(self):
        self.wordlst = [w for w in self.wordlst if w not in self.stopwords]
        
    def freqdict(self):
        wordfreq = [self.wordlst.count(p) for p in self.wordlst]
        self.freqtable = dict(list(zip(self.wordlst,wordfreq)))

    def print(self, msg='', color='white', end='\n', clear=False):
        if self.print_enable is not None:
            if self.print_enable:
                if self.print_gui is None:
                    # text goes to the CLI (command line interpreter)
                    prefix = '  ' if self.new_line else ''
                    # ANSI escape sequences
                    col = {'white':'\033[0m', 'red':'\u001b[31;1m', 'green':'\u001b[32;1m',\
                           'yellow':'\u001b[33;1m', 'blue':'\u001b[34;1m'}
                    print('{3}{1}{0}{2}'.format(msg, col[color], col['white'], prefix), end=end)
                    self.new_line = False if end == '' else True
                else:
                    # text goes to the GUI
                    if not clear:
                        postfix = 'black' if color=='white' else color
                        self.print_gui[1].insert('end', ' '+msg+end, postfix)
                        self.print_gui[1].see('end')
                    else:
                        self.print_gui[1].delete('1.0', 'end')
                        self.print_gui[1].insert('end', '\n')
                    self.print_gui[0].update_idletasks()
            else:
                print(msg, end=end)   # for testing purposes

    def add_magazine(self, mag_nr):
        mag = self.mag_id + str(mag_nr).zfill(2)
        
        filnam = ''
        for fn in self.files:
            if mag in fn:
                filnam = fn.split('.')[0]   # short filename without extension
                break
        if filnam == '':
            self.print('Magazine {} (does not exist - skipped)'.format(mag), 'red')
            return(False)
        if (filnam in self.mag_db.keys()) and not self.overwrite: return(False)
        else:
            # determine maximum number of pages
            t0 = time.time()
            self.print('Processing magazine {} ...'.format(filnam))
            file = open(self.mag_folder + filnam + '.pdf', 'rb')
            readpdf = PyPDF2.PdfFileReader(file)
            maxpage = readpdf.numPages
            self.print('Number of pages : {}, indexing ...'.format(maxpage), end='')

            # scan all pages
            pages = [None]*(maxpage+1)
            self.mag_db[filnam] = pages
            for page in range(1, maxpage+1):
                self.pdf2text(self.mag_folder + filnam + '.pdf', page)
                self.remove_small_words(nchar=int(self.config['remove_size']))
                self.remove_stopwords()
                self.freqdict()
                pages[page] = self.freqtable
            self.print(' ({:4.1f} secs)'.format(time.time() - t0))
            return(True)

    def load_db(self, db_file):
        if os.path.exists(db_file):
            with open(db_file, 'rb') as f:
                self.mag_db = pickle.load(f)
            self.db_file_present = True
            return True
        else:
            self.mag_db = {}
            self.db_file_present = False
            self.print('A database file is not yet present.', 'red')
            return False

    def save_db(self, db_file):
        if self.save_db_enable:
            with open(db_file, 'wb') as f:
                pickle.dump(self.mag_db, f)

    def search(self, keys):
        # keys is a list of key words
        result = {}   # dict van alle gevonden resultaten, index is mag_pagina
        for nummer in self.mag_db.keys():
            c = self.mag_db[nummer]
            maxpage = len(c)-1
            for page in range(1, maxpage+1):
                dct2 = c[page]
                tot_freq = 0
                rk = {}
                for key in keys:
                    
                    # detect key-specific matching
                    start, exact = False, False
                    if key[0] == '!': key, exact = key[1:], True
                    if key[0] == '$': key, start = key[1:], True

                    if self.match_mode == '--start' or start:
                        s = [e for e in dct2.keys() if e.startswith(key)]
                    elif self.match_mode == '--exact' or exact:
                        s = [e for e in dct2.keys() if key == e]
                    else:
                        s = [e for e in dct2.keys() if key in e]
                    freq = 0   # frequentie van 1 woord
                    for e in s:
                        freq += dct2[e]
                    if freq != 0:
                        tot_freq += freq
                    else:
                        tot_freq = 0
                        break   # 1 woord bestaat niet, dan wordt het zoekresultaat nul
                    rk[key] = freq
                if tot_freq != 0:
                    result['{}_{}'.format(nummer, page)] = tot_freq, rk

        # list of sorted results
        self.results = sorted(result.items(), key=lambda item: item[1][0], reverse=True)
