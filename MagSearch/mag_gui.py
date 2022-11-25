#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# chmod 755 prog.py to set execution

# Baseframe for Tkinter GUI

# new modules: keyboard
# sudo pip3 install PyPDF2
# sudo pip3 install pyyaml
# sudo pip3 install keyboard. keyboard module must be run under root

import sys, os, os.path
sys.path.append('/home/pi/Python/lib')
from mag_class import ScanMag

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkFileDialog
from tkinter import messagebox
from tkinter import font
import pickle
import keyboard

# Example messagebox
# result = messagebox.askokcancel('Title', 'Message')

# Program name and version
PROGNAM = "MagSearch"
VERSION = 'v0.9.4'

# Platform
PLATFORM = None
if os.name == 'nt': PLATFORM = 'Windows'
if os.name == 'posix': PLATFORM = 'Linux'

if PLATFORM == 'Windows':
    import subprocess
    
    nasPath =  'D:\\HOBBY'
    buttonWidth = 6
    winWidth    = 850
    winHeight   = 415
    guiFont     = ("Segoe UI", 9)
    txtFont     = ("Courier New", 10)
    txt2Font    = ("Segoe UI", 10)
    statusFont  = ("Segoe UI", 9)
    config_file = 'config_windows.yml'
    
elif PLATFORM == 'Linux':
    nasPath = r'/home/pi/nas/HOBBY'
    buttonWidth = 6
    guiFont     = ("PibotoLt", 12)
    txtFont     = ("Courier", 9)
    txt2Font    = ("PibotoLt", 11)
    winWidth    = 750
    winHeight   = 330
    statusFont  = ("PibotoLt", 10)
    config_file = 'config.yml'

se = ScanMag(config_file)

def pdf_reader(file, page):
    if PLATFORM == 'Linux':
        s = 'evince -i ' + str(page) + ' "'+ file +'" 2>/dev/null &'
        os.system(s)
    else:
        s = 'C:/Program Files (x86)/Adobe/Acrobat Reader DC/Reader/AcroRd32 '
        s += '/A "page=' + str(page) + '"' + ' "' + file + '"'
        subprocess.Popen(s, creationflags=0x00000008)

def best_article(lst, max_spacing=2):
    # best article is the article with the largest series of sequential pages
    finished, best, len_best, i = False, [], -1, 0
    while not finished:
        istart = i
        while True:
            last = lst[i]
            i += 1
            if i >= len(lst):
                finished = True
                break
            if lst[i]-last > max_spacing: break
        len_series = i-istart
        if len_series > len_best:
            len_best = len_series
            best = (len_series, istart, i, lst[istart:i])
    return(best)

class DatabaseMaintenance:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent, bg='#ededed')
        self.top.title('Database')
        self.top.geometry('%dx%d+%d+%d' % (230, 140 , myapp.root.winfo_x()+350, myapp.root.winfo_y()+60))

        # GUI style
        bg = '#ededed'
        
        root = self.top
        self.baseframe = tk.Frame(root, bg=bg)
        self.baseframe.pack(fill=tk.BOTH, expand=tk.TRUE)
        
        # Statusbar: set text with self.statusbar["text"]
        self.statusbar = ttk.Label(root, text='Ready', anchor=tk.W, font=statusFont)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        offx, offy = 25, 15
        lb1 = ttk.Label(self.baseframe, text='Start')
        lb2 = ttk.Label(self.baseframe, text='End')
        self.en1 = ttk.Entry(self.baseframe, width=5, justify=tk.CENTER)
        self.en2 = ttk.Entry(self.baseframe, width=5, justify=tk.CENTER)
        bt1 = ttk.Button(self.baseframe, text='Add', state='normal', width=6, command=self.add)
        bt2 = ttk.Button(self.baseframe, text='New', state='normal', width=6, command=self.new)
        lb1.grid(row=0, column=0, sticky='e', padx=(offx,0), pady=(offy,0))
        self.en1.grid(row=0, column=1, sticky='e', padx=(10,0), pady=(offy,0))
        bt1.grid(row=0, column=2, sticky='e', padx=(10,10), pady=(offy,5))
        lb2.grid(row=1, column=0, sticky='e', padx=(offx,0), pady=(0,0))
        self.en2.grid(row=1, column=1, sticky='e', padx=(10,0), pady=(0,0))
        bt2.grid(row=1, column=2, sticky='e', padx=(10,10), pady=(0,0))
        
        self.cb_overwrite = tk.BooleanVar(value=False)
        cb1 = ttk.Checkbutton(self.baseframe, text='Overwrite', variable=self.cb_overwrite)
        cb1.grid(row=2, column=1, sticky='w', columnspan=2, padx=(7,0), pady=(2,5))

        se.mag_nrs()
        if se.folder_lastmag == -1000:
            self.SetStatus('Database is up to date')
            self.en1.delete(0, tk.END)
            self.en2.delete(0, tk.END)
        else:
            self.SetStatus('Database not up-to-date')
            self.en1.insert(tk.END, str(se.folder_firstmag))
            self.en2.insert(tk.END, str(se.folder_lastmag))
            
        se.print_enable = True

        try:
            keyboard.on_press(self.on_key)
        except:
            pass
        
    def on_key(self, event):
        if event.name == 'esc':
            self.abort = True

    def SetStatus(self, msg):
        self.statusbar["text"] = msg
        self.top.update_idletasks()

    def add(self):
        se.overwrite = self.cb_overwrite.get()
        self.abort = False
        start_s, end_s = self.en1.get(), self.en2.get()
        if start_s != '':
            if end_s == '': end_s = start_s
            start, end = int(start_s), int(end_s)
            if start <= end:
                for nr in range(start, end+1):
                    self.SetStatus('Adding #{} ...'.format(nr))
                    se.add_magazine(nr)
                    if self.abort:
                        break
                se.save_db(se.database)
                self.SetStatus('Ready')
                se.print('Ready')
            else:
                self.SetStatus('Error: Start is larger than End')

    def new(self):
        se.mag_db = {}
        se.mag_nrs()
        self.en1.delete(0, tk.END)
        self.en2.delete(0, tk.END)
        self.en1.insert(tk.END, str(se.folder_firstmag))
        self.en2.insert(tk.END, str(se.folder_lastmag))
        se.print(clear=True)
        se.print('A new database will be created.', 'blue')
        if se.db_file_present:
            se.print('The old database (\'{}\') will be lost. Make a backup if you want to keep it!\n'.format(se.database), 'red')
        se.print('Press \'Add\' to start a new database. This will take some time.\n')

class MyApp:
    def __init__(self, root, width=winWidth, height=winHeight, x=200, y=200):

        # Program name
        self.prognam, self.version = PROGNAM, VERSION
        
        # Set up title and size, position
        root.geometry('%dx%d+%d+%d' % (winWidth, winHeight, x, y))
        root.title(self.prognam + " " + self.version)
        root.resizable(0,0)         # Switch off resizing
        root.protocol("WM_DELETE_WINDOW", self.QuitWindow)
        
        # GUI style
        fg   = "#101010"
        bg   = "#ededed"   # background menu and status bar #ededed
        bg2  = "#fcfcfc"   # background pulldown menu
        bg3  = '#87919b'   # color of highlighted window title or menu item
        gui_fnt = guiFont
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure('.', font=gui_fnt, background=bg)   # change root style
        style.map('TButton', background=[('!active',bg),('active','#dedede')])
        style.configure('TButton', padding=2)
        style.configure('TEntry', padding=1)
        style.configure('TMenubutton', padding=2)

        # Change font in messagebox
        font_mb = font.Font(name='TkCaptionFont', exists=True)
        font_mb.config(family='PibotoLt', size=12, weight='normal')
        
        # Top level menu definition
        menubar = tk.Menu(root, relief=tk.FLAT, font=gui_fnt, fg=fg, bg=bg, activeborderwidth=0, activebackground='white')

        # Set up File menu
        filemenu = tk.Menu(menubar, tearoff=0, font=gui_fnt, fg=fg, bg=bg2, activeborderwidth=0, activebackground=bg3, activeforeground='white')
        filemenu.add_command(label="Database ...", command=self.database_maintenance)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=self.Quit, accelerator="Ctrl+Q", underline=0)   # underlines the 2nd character
        menubar.add_cascade(label="File", menu=filemenu)
        
        # Set up Magazine selection
        self.mag = tk.IntVar()
        magmenu = tk.Menu(menubar, tearoff=0, font=gui_fnt, fg=fg, bg=bg2, activeborderwidth=0, activebackground=bg3, activeforeground='white')
        value = 0
        for m in se.config['magazines'].keys():
            magmenu.add_radiobutton(label=se.config['magazines'][m]['filename'], var=self.mag, value=value, command=self.new_mag)
            value += 1
        menubar.add_cascade(label="Magazines", menu=magmenu)
        self.mag.set(0) # default MagPi

        # Set up Help menu
        helpmenu = tk.Menu(menubar, tearoff=0, font=gui_fnt, fg=fg, bg=bg2, activeborderwidth=0, activebackground=bg3, activeforeground='white')
        helpmenu.add_command(label="Manual", command=self.help_manual)
        helpmenu.add_command(label="About", command=self.help_about)
        menubar.add_cascade(label="Help", menu=helpmenu)
                
        # Show menubar
        root.config(menu=menubar)
        
        # Set up 'baseframe' and status bar
        self.root = root
        self.baseframe = tk.Frame(root, bg=bg)
        self.baseframe.pack(fill=tk.BOTH, expand=tk.TRUE)
        
        # Statusbar: set text with self.statusbar["text"]
        self.statusbar = ttk.Label(root, text="Ready", anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Widget definitions
        textbgcolor = se.config['textbackgroundcolor']
        topframe = tk.Frame(self.baseframe, bg=bg) # for text and scrollbars
        topframe.pack(side=tk.TOP, pady=5)
        xscrollbar = tk.Scrollbar(topframe, orient=tk.HORIZONTAL, bg=bg)
        yscrollbar = tk.Scrollbar(topframe, orient=tk.VERTICAL, bg=bg)
        yscrollbar.pack(side=tk.RIGHT, fill='y', padx=(0,5), pady=(5,18))
        self.txt = tk.Text(topframe, bg=textbgcolor, height=15, width=100, wrap='none', font=txtFont, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)   # PibotoLt
        self.txt.pack(padx=5, pady=5, side=tk.TOP)
        xscrollbar.pack(side=tk.TOP, fill='x', padx=5)
        xscrollbar.config(command=self.txt.xview)
        yscrollbar.config(command=self.txt.yview)
        self.src = tk.Frame(self.baseframe, bg=bg)
        self.src.pack(side=tk.TOP, pady=5)
        lb1 = tk.Label(self.src, text='Search', bg=bg, font=txt2Font)
        self.keys = tk.Entry(self.src, width=45, justify=tk.CENTER)
        lb1.grid(row=0, column=0, padx=(0, 7), pady=(5,0))
        self.keys.grid(row=0, column=1, pady=(5,0))
        
        # radiobuttons for match
        self.match_nr = tk.IntVar()
        self.match_nr.set(['--any', '--start', '--exact'].index(se.config['match_mode']))
        rb1 = tk.Radiobutton(self.src, text='Any', font=txt2Font, variable=self.match_nr, value=0, bg=bg, highlightthickness=0, command=self.match)
        rb2 = tk.Radiobutton(self.src, text='Start', font=txt2Font, variable=self.match_nr, bg=bg, value=1, highlightthickness=0, command=self.match)
        rb3 = tk.Radiobutton(self.src, text='Exact', font=txt2Font, variable=self.match_nr, bg=bg, value=2, highlightthickness=0, command=self.match)
        rb1.grid(row=0, column=2, pady=(5,0), padx=(10,0))
        rb2.grid(row=0, column=3, pady=(5,0))
        rb3.grid(row=0, column=4, pady=(5,0))
        self.match()
        
        # color definitions for text window
        fntnam = 'DejaVu Sans Mono'
        self.txt.tag_config('blue', foreground='blue', font=(fntnam, 10))
        self.txt.tag_config('black', foreground='black', font=(fntnam, 10))
        self.txt.tag_config('red', foreground='red', font=(fntnam, 10))
        self.txt.tag_config('redbold', foreground='black', font=(fntnam, 10, 'bold'))
        
        # set output of ScanMag to the GUI
        se.print_gui = (root, self.txt)
        se.print_enable = True

        # Set up bindings
        root.bind_all("<Control-q>", self.QuitEvent)
        root.bind_all("<Control-b>", self.display_best_articles)
        self.keys.bind('<Return>', self.search)
        self.keys.bind('<Button-2>', self.display_best_articles)
        self.keys.bind('<Button-3>', self.search)
        self.txt.bind("<Button-1>", self.mouseclick)
        self.txt.bind("<Button-3>", self.mouseclick)
        
        self.db_main = None
        self.new_mag()
        self.key_window_open = False
        
    def help_manual(self):
        # os.system('evince -i 1 manual.pdf 2>/dev/null &')
        pdf_reader('manual.pdf', 1)

    def help_about(self):
        ha = tk.Toplevel(root)
        bg = '#ededed'
        
        ha.title('About ' + PROGNAM)
        ha.geometry('%dx%d+%d+%d' % (400, 340, myapp.root.winfo_x()+250, myapp.root.winfo_y()+60))
        ha.protocol("WM_DELETE_WINDOW", self.help_about_quit)
        ha.resizable(0,0)
        self.ha = ha

        fr = tk.Frame(self.ha, bg=bg)
        fr.pack(fill=tk.BOTH, expand=tk.TRUE)
        fr.picture = tk.PhotoImage(file='about_image.png')
        lb1 = tk.Label(fr, image=fr.picture, bg=bg)
        lb2 = tk.Label(fr, text=PROGNAM, font=guiFont + ('bold',), bg=bg)
        lb3 = tk.Label(fr, text=VERSION[1:], font=guiFont, bg=bg)
        lb4 = tk.Label(fr, text='Search for keywords in a magazine', font=guiFont, bg=bg)
        lb5 = tk.Label(fr, text='Hans van Zon, 2022', font=guiFont, bg=bg)
        
        lb1.place(relx=0.5, rely=0.25, anchor=tk.CENTER)
        lb2.place(relx=0.5, rely=0.58, anchor=tk.CENTER)
        lb3.place(relx=0.5, rely=0.68, anchor=tk.CENTER)
        lb4.place(relx=0.5, rely=0.78, anchor=tk.CENTER)
        lb5.place(relx=0.5, rely=0.88, anchor=tk.CENTER)
        
    def help_about_quit(self):
        self.ha.destroy()

    def key_window(self):
        if not self.key_window_open:
            self.kw = tk.Toplevel(root)
            self.kw.title('Frequently observed (n>1) words')
            self.kw.geometry('+%d+%d' % (myapp.root.winfo_x()+350, myapp.root.winfo_y()+60))
            self.kw.protocol("WM_DELETE_WINDOW", self.key_window_quit)
            self.kw.resizable(1,1)

            bg = '#ededed'
            textbgcolor = se.config['textbackgroundcolor']
            baseframe = tk.Frame(self.kw, bg=textbgcolor)
            baseframe.pack(fill=tk.BOTH, expand=tk.TRUE)
            
            self.kw.txt = tk.Text(baseframe, bg=textbgcolor, highlightthickness=0, bd=0, height=9, width=60, wrap=tk.WORD, font=txtFont)
            self.kw.txt.pack(padx=15, pady=15, side=tk.TOP)
            self.kw.txt.tag_config('blue', foreground='blue', font=('Courier', 10, 'bold'))
            self.key_window_open = True

    def key_window_quit(self):
        # Used by exiting the window via 'X' top right
        self.key_window_open = False
        self.kw.destroy()

    def database_maintenance(self):
        self.db_main = DatabaseMaintenance(self.root)
        self.root.wait_window(self.db_main.top)

    def match(self):
        nr = self.match_nr.get()
        se.match_mode = ['--any', '--start', '--exact'][nr]

    def new_mag(self):
        # select a new magazine from the drop down menu
        if self.db_main is not None:
            self.db_main.top.destroy()
            self.db_main = None

        magazine = se.magazines[self.mag.get()]
        se.print(clear=True)
        err = se.init(magazine)
        if err == '':
            se.save_db_enable = True
            descr = se.config['magazines'][magazine]['descr']
            self.SetStatus('Ready')
            if se.load_db(se.database):
                se.print(clear=True)
                se.print('The {} has been loaded ({} magazines).'.format(descr, len(se.mag_db)), 'blue')
                se.print('Enter space-separated keywords in the Search field or \'#magnr page\'')
                se.print('Keywords can be preceded with \'!\' (exact match) or \'$\' (start match)\n')
            root.title(self.prognam + " " + self.version + " - " +descr)
        else:
            se.print(err, 'red')

    def get_page(self, xpos, s):
        def __scan(dr):
            i = 0 if dr==1 else -1
            while s[xpos+i].isdigit(): i += dr
            return(-1 if s[xpos+i] != ' ' else xpos+i)

        if xpos<len(s) and s!='':
            i_left, i_right = __scan(-1), __scan(+1)
            if i_left!=-1 and i_right!=-1 and i_left!=i_right:
                return int(s[i_left+1:i_right])
        return(-1)
    
    def mouseclick(self, event):
        p = self.txt.index('current').split('.')
        line, xpos = int(p[0]), int(p[1])
        s = self.txt.get(str(line)+'.0', str(line+1)+'.0')[:-1]
        colon = s.find(':')
        if s != '':
            magazine = s.split(':')[0].strip()
            page = self.get_page(xpos, s) if xpos > colon else 1
            if page != -1:
                if event.num==1: # left mouseclick, open PDF
                    fl = se.mag_folder + magazine + '.pdf'
#                     s = 'evince -i ' + str(page) + ' "'+ fl +'" 2>/dev/null &'
#                     os.system(s)
                    pdf_reader(fl, page)

                if event.num==3: # right mouseclick, display keywords
                    self.key_window()
                    self.kw.txt.delete('1.0', tk.END)
                    self.kw.txt.insert(tk.END, '{} - page {}\n\n'.format(magazine, page), 'blue')
                    dct = se.mag_db[magazine][int(page)]
                    results = sorted(dct.items(), key=lambda item: item[1], reverse=True)
                    s = ''                
                    for r in results:
                        if r[1] > 1: s += '{}  '.format(r[0])
                    self.kw.txt.insert(tk.END, s + '\n')

    def display_best_articles(self, event):
        self.txt.delete('1.0', tk.END)
        self.txt.insert(tk.END, '\n')
        results = sorted(self.best_options, key=lambda item: se.fn_to_nr(item[0])[1]) # sort on mag nr
        results = sorted(results, key=lambda item: len(item[4]), reverse=True) # sort on #pages
        for r in results:
            self.txt.insert(tk.END, '  {:10s} : '.format(r[0]), 'blue')
            for p in r[4]:
                self.txt.insert(tk.END, '{:>3d} '.format(p), 'redbold')
            self.txt.insert(tk.END, '\n')

    def search(self, event):
        global best_options

        entry = self.keys.get().lower().strip()
        if entry[0] == '#':
            # open an specific magazine on a specific page
            numbers = entry[1:].split()
            if numbers != [] and numbers[0].isnumeric():
                mag_nr = int(numbers[0])
            else:
                self.SetStatus('A magazine number is expected after #')
                return()
            page = 1
            if len(numbers) > 1:
                if numbers[1].isnumeric():
                    page = int(numbers[1])
                else:
                    self.SetStatus('A valid page number is expected as second parameter')
                    return()
            fn = se.nr_to_fn(mag_nr)
            if fn != '':
                s = 'evince -i ' + str(page) + ' "'+ se.mag_folder + fn +'" 2>/dev/null &'
                os.system(s)

        else:   
            # split string in keywords and replace c++ by cpp
            keys = [s.replace('c++', 'cpp') for s in entry.split()]
            
            if keys[0][0] == '@':
                mag = se.nr_to_fn(int(keys[0][1:])).split('.')[0]
                keys = keys[1:]
            else:
                mag = ''

            se.search(keys, mag)
            
            d = {}
            for e in se.results:
                d[e[0]] = e[1]
            
            m = {}
            for e in se.results:
                us = e[0].rindex('_')
                magazine, page = e[0][:us], int(e[0][us+1:])
                if magazine in m.keys():
                    m[magazine].append(page)
                    m[magazine].sort()
                else:
                    m[magazine] = [page]
            
            self.txt.delete('1.0', tk.END)
            self.txt.insert(tk.END, '\n')
            
            res = sorted(m.items(), key=lambda item: se.fn_to_nr(item[0])[1]) # sort on mag number
            res = sorted(res, key=lambda item: len(item[1]), reverse=True) # sort on #pages
            imax = 100 if len(res) > 100 else len(res)
            self.best_options = []
            for i in range(imax):
                mag_s = '  {:10s} : '.format(res[i][0])
                self.txt.insert(tk.END, mag_s, 'blue')
                pages = res[i][1]
                self.best_options.append((res[i][0],) + best_article(pages, max_spacing=se.max_spacing))
                s = ''
                for p in pages:
                    self.txt.insert(tk.END, '{:>3d}'.format(p), 'redbold')
                    id = res[i][0]+'_'+str(p)
                    nhits = d[id][0]
                    self.txt.insert(tk.END, ' [{:2d}] '.format(nhits), 'black')
                self.txt.insert(tk.END, '\n', 'black')
            self.SetStatus('Found in {} magazines'.format(len(res)))

    def Quit(self):
        # Used by menu - Quit command
        self.root.destroy()
        
    def QuitEvent(self, event):
        # Used by binding event
        self.root.destroy()
        
    def QuitWindow(self):
        # Used by exiting the window via 'X' top right
        self.root.destroy()

    def SetStatus(self, msg1='Ready', msg2=''):
        self.statusbar["text"] = msg1 + msg2
        self.root.update_idletasks()

    def File_Open(self):
        filnam = tkFileDialog.askopenfilename(title="Open file", filetypes=[('Text','.txt')], initialdir='')
        self.statusbar["text"] = filnam

    def File_save(self):
        filnam = tkFileDialog.asksaveasfilename(title="Save file", filetypes=[('Text','.txt')])

    def Save_Settings(self):
        #~ fh = open("data.pkl", 'wb')
        #~ pickle.dump(self.datalist, fh, 2)
        #~ fh.close()
        pass
        
    def Load_Settings(self):
        #~ fh = open("data.pkl", 'rb')
        #~ self.datalist = pickle.load(fh)
        #~ fh.close()
        pass
        
    def TimedLoop(self):
        # Place here functions which need to be repeated
        self.root.after(msec, self.TimedLoop)
        
    # User functions within class


# Main application start
if __name__ == "__main__":
    root = tk.Tk()
    myapp = MyApp(root)
    root.mainloop()
