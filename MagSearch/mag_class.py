# Class for scanning the magazines Elektor, MagPi and HackSpace
#    installed software PyYAML, PyPDF2
#    pdftotext, based on Poppler
#    subprocess module for Windows command 'pdftotext' from https://www.xpdfreader.com
#    text processing based on 'https://programminghistorian.org/en/lessons/counting-frequencies'

import os, re, pickle, time
import PyPDF2
from os import listdir
from os.path import isfile, join
import yaml, subprocess

class ScanMag:
    def __init__(self, os):
        # os: Linux, Windows
        with open('config.yml') as f:
            self.config = yaml.load(f, yaml.SafeLoader)
        self.magazines = list(self.config['magazines'].keys())
        self.print_enable = False
        self.print_gui = None # tuple (root, text widget)
        self.new_line = True
        self.os = os.lower()

    def init(self, mag_id):
        self.mag_db = {}   # database
        self.mag_id = self.config['magazines'][mag_id]['filename']
        self.language = self.config['magazines'][mag_id]['language']
        self.mag_folder = self.config['magazines'][mag_id]['directory']
        self.database = self.config['magazines'][mag_id]['database']
        self.files = [f for f in listdir(self.mag_folder) if isfile(join(self.mag_folder, f)) and f.startswith(self.mag_id)]
        self.define_stopwords()
        self.results = []
        self.match_mode = self.config['match_mode']
        self.save_db_enable = False
        self.db_file_present = False
        self.overwrite = False
        
        # sort file list according to numbers
        nrs = [self.fn_to_nr(f)[1] for f in self.files]
        self.files = [x for _,x in sorted(zip(nrs, self.files), key=lambda pair: pair[0])]

    def define_stopwords(self):
        if self.language == 'EN':
            self.stopwords = ['a', 'about', 'above', 'across', 'after', 'afterwards']
            self.stopwords += ['again', 'against', 'all', 'almost', 'alone', 'along']
            self.stopwords += ['already', 'also', 'although', 'always', 'am', 'among']
            self.stopwords += ['amongst', 'amoungst', 'amount', 'an', 'and', 'another']
            self.stopwords += ['any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere']
            self.stopwords += ['are', 'around', 'as', 'at', 'back', 'be', 'became']
            self.stopwords += ['because', 'become', 'becomes', 'becoming', 'been']
            self.stopwords += ['before', 'beforehand', 'behind', 'being', 'below']
            self.stopwords += ['beside', 'besides', 'between', 'beyond', 'bill', 'both']
            self.stopwords += ['bottom', 'but', 'by', 'call', 'called', 'can', 'cannot', 'cant']
            self.stopwords += ['co', 'come', 'comes', 'con', 'could', 'couldnt', 'cry', 'de']
            self.stopwords += ['describe', 'detail', 'did', 'do', 'does', 'done', 'down', 'due']
            self.stopwords += ['during', 'each', 'eg', 'eight', 'either', 'eleven', 'else']
            self.stopwords += ['elsewhere', 'empty', 'enough', 'etc', 'even', 'ever']
            self.stopwords += ['every', 'everyone', 'everything', 'everywhere', 'except']
            self.stopwords += ['few', 'fifteen', 'fifty', 'fill', 'find', 'fire', 'first']
            self.stopwords += ['five', 'fix', 'for', 'former', 'formerly', 'forty', 'found']
            self.stopwords += ['four', 'from', 'front', 'full', 'further', 'get', 'give']
            self.stopwords += ['go', 'going', 'got', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her']
            self.stopwords += ['here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers']
            self.stopwords += ['herself', 'him', 'himself', 'his', 'how', 'however']
            self.stopwords += ['hundred', 'i', 'ie', 'if', 'in', 'inc', 'indeed']
            self.stopwords += ['interest', 'into', 'is', 'it', 'its', 'itself', 'keep']
            self.stopwords += ['last', 'latter', 'latterly', 'least', 'less', 'let', 'lets', 'likes', 'ltd', 'made', 'magpi']
            self.stopwords += ['make', 'makes', 'making', 'many', 'may', 'me', 'means', 'meanwhile', 'might', 'mill', 'mine']
            self.stopwords += ['more', 'moreover', 'most', 'mostly', 'move', 'much']
            self.stopwords += ['must', 'my', 'myself', 'name', 'namely', 'neither', 'never']
            self.stopwords += ['nevertheless', 'next', 'nine', 'no', 'nobody', 'none']
            self.stopwords += ['noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of']
            self.stopwords += ['off', 'often', 'on','once', 'one', 'only', 'onto', 'or']
            self.stopwords += ['other', 'others', 'otherwise', 'our', 'ours', 'ourselves']
            self.stopwords += ['out', 'over', 'own', 'part', 'per', 'perhaps', 'please']
            self.stopwords += ['put', 'rather', 're', 's', 'same', 'see', 'seem', 'seemed']
            self.stopwords += ['seeming', 'seems', 'serious', 'several', 'she', 'should']
            self.stopwords += ['show', 'side', 'since', 'sincere', 'six', 'sixty', 'so']
            self.stopwords += ['some', 'somehow', 'someone', 'something', 'sometime']
            self.stopwords += ['sometimes', 'somewhere', 'still', 'such', 'system', 'take']
            self.stopwords += ['ten', 'than', 'that', 'the', 'their', 'them', 'themselves']
            self.stopwords += ['then', 'thence', 'there', 'thereafter', 'thereby']
            self.stopwords += ['therefore', 'therein', 'thereupon', 'these', 'they']
            self.stopwords += ['thick', 'thin', 'third', 'this', 'those', 'though', 'three']
            self.stopwords += ['three', 'through', 'throughout', 'thru', 'thus', 'to']
            self.stopwords += ['together', 'too', 'top', 'toward', 'towards', 'twelve']
            self.stopwords += ['twenty', 'two', 'un', 'under', 'until', 'up', 'upon']
            self.stopwords += ['us', 'very', 'via', 'want', 'was', 'we', 'well', 'were', 'what']
            self.stopwords += ['whatever', 'when', 'whence', 'whenever', 'where']
            self.stopwords += ['whereafter', 'whereas', 'whereby', 'wherein', 'whereupon']
            self.stopwords += ['wherever', 'whether', 'which', 'while', 'whither', 'who']
            self.stopwords += ['whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with']
            self.stopwords += ['within', 'without', 'would', 'yet', 'you', 'your']
            self.stopwords += ['yours', 'yourself', 'yourselves']
            self.stopwords += ['possible', 'http', 'uk', 'it’s', 'goes', 'like', 'don’t', 'just', 'that’s', 'he’s', 'let’s']
            self.stopwords += ['need', 'using', 'i’m', 'she’s', 'we’ll', 'there’s', 'you’ll', 'use', 'uses', 'used', 'we’ve', 'we’re', 'says']

        if self.language == 'NL':
            self.stopwords = ['aan', 'acht', 'achter', 'achteren', 'afhankelijk', 'alle', 'alleen', 'allemaal', \
                 'alles', 'als', 'alsnog', 'altijd', 'andere', 'anders', 'beetje', 'behalve', 'behoorlijk', \
                 'behulp', 'beide', 'believen', 'best', 'bestaan', 'bestaat', 'betekent', 'beter', 'betreft', \
                 'bevat', 'bevinden', 'bieden', 'biedt', 'bij', 'bijna', 'bijvoorbeeld', 'binnen', 'blijft', \
                 'blijkbaar', 'blijven', 'bouwt', 'boven', 'bovenaan', 'buiten', 'circa', 'daar', 'daarbij', 'daarentegen', \
                 'daarmee', 'daarna', 'daarom', 'daarop', 'daartoe', 'daarvan', 'daarvoor', 'dan', 'dankzij', \
                 'danwel', 'dat', 'de', 'denkt', 'derde', 'dergelijk', 'dergelijke', 'desondanks', 'deze', 'dezelfde', \
                 'die', 'dik', 'dikkere', 'direct', 'direkt', 'dit', 'doen', 'doet', 'door', 'doorgaans', \
                 'draaien', 'draait', 'drie', 'dringend', 'dus', 'echt', 'echter', 'een', 'eens', 'eenvoudig', \
                 'eerder', 'eerst', 'eerste', 'eigen', 'eigenlijk', 'elk', 'elkaar', 'elke', 'enige', 'enkele', 'eraan', \
                 'erg', 'erin', 'ermee', 'eruit', 'ervoor', 'evenals', 'extra', 'figuur', 'gaan', 'gaat', \
                 'gaf', 'gebeurd', 'gebeurde', 'gebeuren', 'gebeurt', 'gebruik', 'gebruiken', 'gebruikt', \
                 'gedraaid', 'geeft', 'geen', 'gegeven', 'gehad', 'geheel', 'geholpen', 'gehouden', 'gelegen', \
                 'gemaakt', 'gemeten', 'genoeg', 'genomen', 'geschikt', 'geschreven', 'geval', 'geven', 'gewoon', \
                 'goed', 'goede', 'gratis', 'groot', 'grote', 'grotere', 'haalt', 'had', 'heb', 'hebben', \
                 'hebt', 'heeft', 'heel', 'helaas', 'hele', 'helpen', 'helpt', 'hen', 'het', 'hetzelfde', \
                 'hier', 'hierin', 'hiermee', 'hiervan', 'hiervoor', 'hij', 'hoe', 'hoewel', 'hoge', 'hoog', \
                 'hou', 'houd', 'houden', 'houdt', 'hun', 'ieder', 'iedere', 'iets', 'indien', 'is', 'juist', \
                 'juiste', 'kan', 'kant', 'kijken', 'kijker', 'klaar', 'klein', 'kleine', 'komen', 'komt', \
                 'kort', 'korte', 'krijgen', 'kun', 'kunnen', 'kunt', 'laag', 'laat', 'lang', 'langer', 'laten', \
                 'later', 'liefst', 'liggen', 'ligt', 'lijken', 'lijkt', 'links', 'maak', 'maakt', 'maar', \
                 'mag', 'maken', 'makkelijk', 'manier', 'mee', 'meer', 'meest', 'meestal', 'meeste', 'meet', \
                 'men', 'met', 'meteen', 'meten', 'midden', 'mij', 'mijn', 'min', 'minder', 'minst', 'minstens', \
                 'misschien', 'moest', 'moet', 'moeten', 'mogelijk', 'mogen', 'na', 'naar', 'naarmate', 'naast', \
                 'nadat', 'nagenoeg', 'natuurlijk', 'nauwelijks', 'nee', 'neemt', 'negen', 'nemen', 'nergens', \
                 'niet', 'nodig', 'nog', 'nogmaals', 'nooit', 'nou', 'nu', 'ofwel', 'omdat', 'omvat', 'onder', \
                 'onderaan', 'ongeveer', 'ons', 'onze', 'ooit', 'ook', 'opeenvolgende', 'opnieuw', 'over', 'overigens', \
                 'paar', 'pas', 'per', 'plus', 'prettig', 'qua', 'recent', 'recente', 'rechts', 'rond', 'schikt', \
                 'schreef', 'schrijven', 'sla', 'slaan', 'slaat', 'slecht', 'slechts', 'snelle', 'soepel', 'sommige', \
                 'soms', 'soort', 'staan', 'start', 'steeds', 'stevig', 'stop', 'stuk', 'tegen', 'telkens', \
                 'ten', 'tenslotte', 'ter', 'terug', 'terwijl', 'tevens', 'tien', 'toch', 'toe', 'toen', \
                 'tonen', 'toonde', 'toont', 'tot', 'tussen', 'twee', 'tweede', 'uit', 'uiteraard', 'uitgebreid', \
                 'uitvoeren', 'vaak', 'van', 'vanaf', 'vanuit', 'vast', 'vasthouden', 'vastzetten', 'veel', 'verder', \
                 'verdere', 'verscheidene', 'vervolgens', 'via', 'vier', 'vijf', 'vind', 'vinden', 'vindt', \
                 'vlot', 'vlotte', 'voeren', 'volgende', 'volgens', 'volledig', 'voor', 'vooraf', 'vooral', \
                 'voordat', 'vrij', 'vrijwel', 'vroeger', 'waar', 'waarbij', 'waardoor', 'waarmee', 'waarna', \
                 'waarom', 'waaronder', 'waarop', 'waarschijnlijk', 'waaruit', 'waarvan', 'wanneer', 'want', \
                 'was', 'wat', 'weer', 'weg', 'wegens', 'weinig', 'wel', 'weliswaar', 'welk', 'welke', 'wellicht', \
                 'werd', 'werkelijk', 'werken', 'werkt', 'wie', 'wil', 'willen', 'wilt', 'worden', 'wordt', \
                 'www', 'zal', 'zeer', 'zeker', 'zelden', 'zelf', 'zelfs', 'zes', 'zeven', 'zich', 'zie', \
                 'zien', 'ziet', 'zijn', 'zit', 'zitten', 'zoals', 'zodat', 'zodoende', 'zodra', 'zogenaamd', \
                 'zogenaamde', 'zolang', 'zonder', 'zou', 'zouden', 'zoveel', 'zowel', 'zozeer', 'zulke', 'zullen']

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

        file_output = os.getcwd() + '/tmp.txt'
        if self.os == 'linux':
            s = 'pdftotext -enc "UTF-8" -q -f '+str(page)+' -l '+str(page)+' "'+file_input+'" "'+file_output+'"'
            os.system(s)
        else:
            s = 'pdftotext.exe -enc "UTF-8" -q -f '+str(page)+' -l '+str(page)+' "'+file_input+'" "'+file_output+'"'
            subprocess.call(s, creationflags=0x00000008) # .call waits until command is finished, .Popen continues immediately
        
        with open(file_output, 'rb') as f:
            self.doc = f.read()

        self.doc = re.sub(b'c\+\+', b'cpp', self.doc)
        self.doc = re.sub(b'[\x00-\x2f,\x3a-\x3f,\x5b-\x60,\x7b-\xff]', b' ', self.doc)
        self.wordlst = self.doc.decode().split()
        
    def remove_small_words(self, nchar=2):
        except_words = ['3d', 'a6', 'a8', 'ai', 'ir', 'os', 'pi', 'sd', 'tk', 'qt', 'hz']
        except_words += ['arm', 'bbc', 'cpp', 'cpu', 'gps', 'gtk', 'gui', 'i2c', 'led', 'ssh']
        tmp = []
        for i in range(len(self.wordlst)):
            word = self.wordlst[i].lower()
            if (len(word) > nchar) or (word in except_words):
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
        
        if (filnam in self.mag_db.keys()) and not self.overwrite:
            return(False)
        
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
                self.remove_small_words()
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
                    if self.match_mode == '--start':
                        s = [e for e in dct2.keys() if e.startswith(key)]
                    elif self.match_mode == '--exact':
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
