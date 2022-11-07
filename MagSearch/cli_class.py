# Library for Command Line Interpreter

# USE
# ===
# Define all functions for the commands. The function has a single entry 'pars' which contains the parameters
#     after the command as a single list. Functions can receive global variables but when these have to be
#     changed, they need to be defined as 'global'
# Make an instance of the CLI: p = cli(app, sort), use 'app' to specify a short description of the application,
#     use 'sort' to specify whether the commands in help should be sorted
# Define the syntax of the commands:
#    p.command('command1', ['par1', '[par2]'], helpstring, function)
#    The parameters are specified in a list. An optional parameter is enclosed with [ and ] within the string
# The method 'timed(func)' attaches a timed function which is continuously executed. The frequency of the loop can
#    be set with the method 'wait(sec)'. The method 'no_timed' disables the timed loop.
# Define the body of the program
# Start the CLI with the 'main' method

# Example
# =======

# TODO

# Colors, see https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
# retain quoted substrings

import os
import re
import sys
import termios
import tty
import fcntl
import time
import shlex

class cli:
    def __init__(self, app='', sort=False):
        self.sort = sort
        self.commands, self.lmax = [], 0
        self.command('help', ['[command]'], 'Prints help', None)
        self.command('quit', [], 'Exits the command line interpreter', None)
        self.timed_active = False
        self.waittime = 1.0
        self.cmds_per_line = 8   # number of displayed commands per line in 'help'
        self.print(app)

    class raw(object):
        def __init__(self, stream):
            self.stream = stream
            self.fd = self.stream.fileno()
        def __enter__(self):
            self.original_stty = termios.tcgetattr(self.stream)
            tty.setcbreak(self.stream)
        def __exit__(self, type, value, traceback):
            termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)

    class nonblocking(object):
        def __init__(self, stream):
            self.stream = stream
            self.fd = self.stream.fileno()
        def __enter__(self):
            self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
            fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
        def __exit__(self, *args):
            fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)

    def command(self, cmd, pars, help, func):
        # cmd  : main command
        # pars : list of additional parameters to the command
        # help : help string
        # func : a function which accepts 'pars' as input, e.g. fdel(pars)
        
        for e in self.commands:
            if e[0] == cmd:
                print('Method "cli.command": command "{}" already exists'.format(cmd))
                return()
        
        if len(cmd) > self.lmax:
            self.lmax = len(cmd)      
        self.commands.append((cmd, pars, help, func))
        if self.sort:
            self.commands = sorted(self.commands, key=lambda x:x[0])

    def __execute__(self, cmdv):
        # cmdv : list of command + options list

        if len(cmdv) > 0:
            cmd, pars = cmdv[0], cmdv[1:]
            found = False
            
            for e in self.commands:

                if cmd[-1] == '.':   # abbreviation
                    L = re.search('^'+cmd[:-1], e[0])
                else:
                    L = (cmd == e[0])

                if L:
                    cmd = e[0]
                    found = True
                    
                    # Check number of required parameters
                    n_req, n_opt = 0, len(e[1])
                    for g in e[1]:
                        if g[0] != '[':
                            n_req += 1
                    
                    if cmd == 'help':
                        self.help(pars)
                    elif cmd == 'quit':
                        sys.exit()
                    else:
                        if len(pars) >= n_req:
                            e[3](pars)   # execute function
                        else:
                            print('{0}Insufficient number of parameters for command "{2}". Type "help {2}".{1}'.format('\u001b[31;1m', '\033[0m', cmd))   # bright red
                    break

            if not found:
                    print('{0}Unknown command "{2}". Type "help" for available commands.{1}'.format('\u001b[31;1m', '\033[0m', cmd))   # bright red

    def help(self, cmd):
        if cmd == []:
            print('{}Commands{}'.format('\u001b[32;1m', '\033[0m'), end='')   # bright green
            for i in range(len(self.commands)):
                if i % self.cmds_per_line == 0:
                    print('\n  ', end='')                
                print('{:{x}s}'.format(self.commands[i][0], x=self.lmax+2), end='')
        else:
            for e in self.commands:
                found = False
                if cmd[0] == e[0]:
                    print('{}Usage :{} {} '.format('\u001b[32;1m', '\033[0m', e[0]), end='')   # bright green
                    for f in e[1]:
                        print('<{}> '.format(f), end='')

                    helpstr = e[2].split('\n')
                    print('\n{}Help  :{} {}'.format('\u001b[32;1m', '\033[0m', helpstr[0]), end='')   # bright green
                    if len(helpstr) > 1:
                        for h in helpstr[1:]:
                            if h != '':
                                print('\n{}{}'.format(8*' ', h), end='')

                    found = True
                    break
            if not found:
                    print('{0}Unknown command "{2}"{1}'.format('\u001b[31;1m', '\033[0m', cmd[0]), end='')   # bright red
        print()
        
    def main(self):
        # Execute the main loop

        cmd, ichar = '', 0
        line_buf, idx = [''], 0
        last_time = time.time()
        print('# ', end='', flush=True)
        with self.raw(sys.stdin):
            with self.nonblocking(sys.stdin):
                while True:
                    time.sleep(0.001)   # reduce processor load
                    c = sys.stdin.read(1)
                    if c:
                        if c not in ['\x1b', '\x09', '\x15', '\x7f', '\x0c', '\n']:
                            high = cmd[ichar:]
                            print(c + high + len(high)*'\x08', end='', flush=True)

                        if ord(c) == 127:   # backspace
                            if len(cmd) > 0:
                                low, high = cmd[0:ichar-1], cmd[ichar:]
                                print('\x08' + high + ' ' + (len(high)+1)*'\x08', end='', flush=True)
                                cmd = low + high
                                ichar -= 1
                                
                        elif ord(c) == 9:   # tab, vul de directory aan
                            pass

                        elif ord(c) == 0x15:   # control-U clear line
                            print(len(cmd)*'\x08 \x08', end='', flush=True)   # delete line
                            cmd, ichar = '', 0

                        elif c == '\x1b':   # process escape sequences
                            esc_seq = c
                            time.sleep(0.01)
                            c = sys.stdin.read(1)
                            if not c:   # single escape code terminates program
                                print()
                                break
                            else:
                                esc_seq += c
                                if c == '\x4f':   # Function keys F1-F4
                                    c = sys.stdin.read(1)
                                    esc_seq += c
                                if c == '\x5b':
                                    c = sys.stdin.read(1)   # E.g. arrows have 1 additional character, but 'insert' has two codes
                                    esc_seq += c
                                    if ord(c) <= 0x40:
                                        while c != '\x7e':
                                            c = sys.stdin.read(1)
                                            esc_seq += c

                            # process escape sequence 'esc_seq', if required
                            if esc_seq == '\x1b[A':   # up-arrow gets previous command
                                for j in range(len(cmd)):
                                    print('\x08 \x08', end='', flush=True)   # delete line
                                if idx > 0:
                                    idx -= 1    
                                cmd = line_buf[idx]
                                ichar = len(cmd)
                                print(cmd, end='', flush=True)
                                
                            if esc_seq == '\x1b[B':   # down-arrow gets next command
                                for j in range(len(cmd)):
                                    print('\x08 \x08', end='', flush=True)   # delete line
                                if idx < len(line_buf)-1:
                                    idx += 1
                                    cmd = line_buf[idx]
                                else:
                                    idx = len(line_buf)
                                    cmd = ''
                                ichar = len(cmd)
                                print(cmd, end='', flush=True)
                                
                            if esc_seq == '\x1b[D':   # left-arrow shifts cursor to the left
                                if ichar > 0:
                                    print('\x08', end='', flush=True)
                                    ichar -= 1

                            if esc_seq == '\x1b[C':   # right-arrow shifts cursor to the right
                                if ichar < len(cmd):
                                    print(cmd[ichar], end='', flush=True)
                                    ichar += 1
                            
                            if esc_seq == '\x1b[3~':   # delete
                                high = cmd[ichar+1:]
                                print(high + ' ' + (len(high)+1)*'\x08', end='', flush=True)
                                cmd = cmd[0:ichar] + high

                        elif c == '\n':   # enter
                            print(flush=True)
                            self.__execute__(shlex.split(cmd))   # keep text between quotes
                            print('# ', end='', flush=True)
                            if cmd != line_buf[-1]:   # only append if it is not the same as the previous one
                                line_buf.append(cmd)
                                idx = len(line_buf)   # move ptr to after the end of the buffer again
                            cmd, ichar = '', 0

                        else:
                            cmd = cmd[0:ichar] + c + cmd[ichar:]
                            ichar += 1

                    # Timed loop
                    if self.timed_active:
                        current_time = time.time()
                        if (current_time - last_time) > self.waittime:
                            last_time = current_time
                            self.func()

    def timed(self, func):
        # func is a function which is regularly executed
        self.timed_active = True
        self.func = func
        
    def no_timed(self):
        # Remove the timed function
        self.time_active = False
        
    def wait(self, waittime):
        # Determine the time interval with which the timed function is executed
        self.waittime = waittime

    def print(self, string):
        # Print string with '# ' in front of it
        print('# {}'.format(string))
        
    def error(self, string):
        # Print the message in bright red
        print('{0}{1}{2}'.format('\u001b[31;1m', string, '\033[0m'))
