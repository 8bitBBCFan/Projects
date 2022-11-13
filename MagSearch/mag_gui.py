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

# subprocess required for execution under windows
import subprocess

# Example messagebox
# result = messagebox.askokcancel('Title', 'Message')

# Program name and version
PROGNAM = "MagSearch (search through a magazine)"
VERSION = 'v0.8'

# Platform
PLATFORM = None
if os.name == 'nt': PLATFORM = 'Windows'
if os.name == 'posix': PLATFORM = 'Linux'

if PLATFORM == 'Windows':
    nasPath =  'D:/HOBBY'
    buttonWidth = 6
    winWidth    = 750
    winHeight   = 400
    guiFont     = ("Segoe UI", 9)
    txtFont     = ("Courier New", 10)
    statusFont  = ("Segoe UI", 9)
    
elif PLATFORM == 'Linux':
    nasPath = r'/home/pi/nas/HOBBY'
    buttonWidth = 6
    guiFont     = ("PibotoLt", 12)
    txtFont     = ("Courier", 9)
    winWidth    = 850
    winHeight   = 320
    statusFont  = ("PibotoLt", 10)

se = ScanMag(PLATFORM)

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
                db_changed = False
                for nr in range(start, end+1):
                    self.SetStatus('Adding #{} ...'.format(nr))
                    if se.add_magazine(nr):
                        db_changed = True
                    if self.abort:
                        break
                if db_changed:
                    print('Saving to {}'.format(se.database))
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
        prognam, version = PROGNAM, VERSION
        
        # Set up title and size, position
        # root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        root.geometry('%dx%d+%d+%d' % (winWidth, winHeight, x, y))
        root.title(prognam+" "+version)
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
        menubar.add_cascade(label="Help", menu=helpmenu)
                
        # Show menubar
        root.config(menu=menubar)
        
        # Set up 'baseframe' and status bar
        self.root = root
        self.baseframe = tk.Frame(root, bg=bg)
        self.baseframe.pack(fill=tk.BOTH, expand=tk.TRUE)
        
        # Statusbar: set text with self.statusbar["text"]
        self.statusbar = ttk.Label(root, text="Ready", anchor=tk.W, font=statusFont)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Widget definitions
        textbgcolor = se.config['textbackgroundcolor']
        xscrollbar = tk.Scrollbar(self.baseframe, orient=tk.HORIZONTAL, bg=bg)        
        self.txt = tk.Text(self.baseframe, bg=textbgcolor, height=15, width=100, wrap='none', font=txtFont, xscrollcommand=xscrollbar.set)   # PibotoLt
        xscrollbar.config(command=self.txt.xview)
        self.txt.pack(padx=5, pady=5, side=tk.TOP)
        xscrollbar.pack(side=tk.TOP, fill='x', padx=5)
        self.src = tk.Frame(self.baseframe, bg=bg)
        self.src.pack(side=tk.TOP, pady=5)
        lb1 = tk.Label(self.src, text='Search', bg=bg)
        self.keys = tk.Entry(self.src, width=45, justify=tk.CENTER)
        lb1.grid(row=0, column=0, padx=(0, 10), pady=(5,0))
        self.keys.grid(row=0, column=1, pady=(5,0))
        
        # radiobuttons for match
        self.match_nr = tk.IntVar()
        rb1 = tk.Radiobutton(self.src, text='Any', variable=self.match_nr, value=0, bg=bg, highlightthickness=0, command=self.match)
        rb2 = tk.Radiobutton(self.src, text='Start', variable=self.match_nr, bg=bg, value=1, highlightthickness=0, command=self.match)
        rb3 = tk.Radiobutton(self.src, text='Exact', variable=self.match_nr, bg=bg, value=2, highlightthickness=0, command=self.match)
        rb1.grid(row=0, column=2, pady=(5,0), padx=(15,0))
        rb2.grid(row=0, column=3, pady=(5,0))
        rb3.grid(row=0, column=4, pady=(5,0))
        self.match()
        
        # color definitions for text window
        self.txt.tag_config('blue', foreground='blue', font=('Courier', 10))
        self.txt.tag_config('black', foreground='black', font=('Courier', 10))
        self.txt.tag_config('red', foreground='red', font=('Courier', 10))
        self.txt.tag_config('redbold', foreground='red', font=('Courier', 10, 'bold'))
        
        # set output of ScanMag to the GUI
        se.print_gui = (root, self.txt)
        se.print_enable = True

        # Set up bindings
        root.bind_all("<Control-q>", self.QuitEvent)
        self.keys.bind('<Return>', self.search)
        self.txt.bind("<Button-1>", self.left_mouseclick)
        self.txt.bind("<Button-3>", self.right_mouseclick)
        
        self.db_main = None
        self.new_mag()
        self.key_window_open = False

    def key_window(self):
        if not self.key_window_open:
            self.kw = tk.Toplevel(root)
            self.kw.title('Frequently observed words')
            self.kw.geometry('+%d+%d' % (myapp.root.winfo_x()+350, myapp.root.winfo_y()+60))
            self.kw.protocol("WM_DELETE_WINDOW", self.key_window_quit)
            self.kw.resizable(1,1)

            bg = '#ededed'            
            baseframe = tk.Frame(self.kw, bg=bg)
            baseframe.pack(fill=tk.BOTH, expand=tk.TRUE)
            
            textbgcolor = se.config['textbackgroundcolor']
            self.kw.txt = tk.Text(baseframe, bg=textbgcolor, height=8, width=60, wrap=tk.WORD, font=txtFont)
            self.kw.txt.pack(padx=5, pady=5, side=tk.TOP)
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
        se.init(magazine)
        se.save_db_enable = True
        se.print(clear=True)
        descr = se.config['magazines'][magazine]['descr']
        self.SetStatus(descr)
        if se.load_db(se.database):
            se.print(clear=True)
            se.print('The {} has been loaded ({} magazines).'.format(descr, len(se.mag_db)), 'blue')
            se.print('Enter space-separated keywords in the Search field\n')

    def get_page(self, xpos, s):
        def __scan(dr):
            i = 0
            while s[xpos+i].isdigit(): i += dr
            return (xpos+i+1 if i!=0 and s[xpos+i]==' ' else -1)

        if xpos<len(s) and s!='':
            i_left, i_right = __scan(-1), __scan(+1)
            if i_left!=-1 and i_right!=-1:
                return int(s[i_left:i_right])
        return(-1)

    def left_mouseclick(self, event):        
        p = self.txt.index('current').split('.')
        line, xpos = int(p[0]), int(p[1])
        
        # get complete line of text
        s = self.txt.get(str(line)+'.0', str(line+1)+'.0')[:-1]
        colon = s.find(':')
        if s != '':
            magazine = s.split(':')[0].strip()
            fl = se.mag_folder + magazine + '.pdf'
            page = self.get_page(xpos, s) if xpos > colon else 1
            if page != -1:
                if PLATFORM == 'Linux':
                    s = 'evince -i ' + str(page) + ' "'+ fl +'" 2>/dev/null &'
                    os.system(s)
                else:
                    s = 'C:/Program Files (x86)/Adobe/Acrobat Reader DC/Reader/AcroRd32 '
                    s += '/A "page=' + str(page) + '"' + ' "' + fl + '"'
                    subprocess.Popen(s, creationflags=0x00000008)
    
    def right_mouseclick(self, event):
        self.key_window()
        p = self.txt.index('current').split('.')
        line, xpos = int(p[0]), int(p[1])
        
        # get complete line of text
        s = self.txt.get(str(line)+'.0', str(line+1)+'.0')[:-1]
        colon = s.find(':')
        if s != '':
            magazine = s.split(':')[0].strip()
            page = self.get_page(xpos, s) if xpos > colon else 1
            if page != -1:
                self.kw.txt.delete('1.0', tk.END)
                self.kw.txt.insert(tk.END, '{} - page {}\n\n'.format(magazine, page), 'blue')
                dct = se.mag_db[magazine][int(page)]
                results = sorted(dct.items(), key=lambda item: item[1], reverse=True)
                s = ''                
                for r in results:
                    if r[1] > 0: s += '{}  '.format(r[0])
                self.kw.txt.insert(tk.END, s + '\n')

    def search(self, event):
        entry = self.keys.get().lower().strip()
        if entry[0] == '#':
            # open an specific magazine on a specific page
            numbers = entry[1:].split()
            mag_nr, page = int(numbers[0]), int(numbers[1])
            fn = se.nr_to_fn(mag_nr)
            if fn != '':
                s = 'evince -i ' + str(page) + ' "'+ se.mag_folder + fn +'" 2>/dev/null &'
                os.system(s)

        else:
            keys = entry.split()
            se.search(keys)
            
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
            
            res = sorted(m.items(), key=lambda item: len(item[1]), reverse=True)
            imax = 100 if len(res) > 100 else len(res)
            for i in range(imax):
                mag_s = '  {:10s} : '.format(res[i][0])
                self.txt.insert(tk.END, mag_s, 'blue')
                pages = res[i][1]
                s = ''
                for p in pages:
                    self.txt.insert(tk.END, '{:>3d}'.format(p), 'redbold')
                    id = res[i][0]+'_'+str(p)
                    nhits = d[id][0]
                    self.txt.insert(tk.END, ' [{:2d}] '.format(nhits), 'black')
                self.txt.insert(tk.END, '\n', 'black')

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
