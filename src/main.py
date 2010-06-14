################################################################################
#   (c) 2010, The Honeynet Project
#   Author: Patrik Lantz  patrik@pjlantz.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################

import cmd, sys, os, signal
import threading, time
from conf import configHandler
from modules import moduleManager

if os.name == "nt":
    try:
        import pyreadline
    except ImportError:
        print "Error: Windows PyReadline support missing"
        sys.exit(1)

class CLI(cmd.Cmd):
    """
    Handles command line input with support for 
    command line completion and command history. 
    Additionally the cmd module provides a nice help feature,
    the comments for the do_command functions are shown 
    when issuing help <command>
    """
	
    def __init__(self):
        """
        Constructor, sets up cmd variables and other
        data structures holding modules, configs etc.
        Starts a thread that looks for new modules
        """
        
        cmd.Cmd.__init__(self)
        self.prompt = ">> "
        self.intro = "\nType help or '?' for a list of commands\n"
        moduleManager.handle_modules_onstart()
        self.moduleThread = LoadModules()
        self.moduleThread.start()
        self.config = configHandler.ConfigHandler()
        self.modlist = []
        
    def do_exec(self, arg):
        """
        Execute a module with the current config. 
        Usage: exec modulename
        """
        
        moduleManager.execute(arg)
    
    def do_lsmod(self, arg):
        """
        List all modules currently installed
        """
        
        lsStr = "\nInstalled modules\n=================\n"
        self.modlist = moduleManager.get_modules()
        for mod in self.modlist:
            lsStr += mod + "\n"
        print lsStr
            
    def do_lsexec(self, arg):
        """
        List all modules being executed at the moment
        """
        
        execMods = moduleManager.get_running()
        if len(execMods) == 0:
            print "No modules executing"
            return
        for mod in execMods:
            print mod
            
    def do_lsconf(self, arg):
        """
        List all configurations
        """
        
        self.config.listConf()
        
    def do_useconf(self, arg):
        """
        Sets the current config to use, if argument
        is empty, current config used is printed out
        """
        
        self.config.useConf(arg)
        
    
    def default(self, line):
        """
        Called when command input is not recognized
        and outputs an error message
        """
        
        print "Unkown command: " + line
        
    def emptyline(self):
        """
        Called when empty line was entered at the prompt
        """
        
        pass
        
    def do_quit(self, arg):
        """
        Exit the program gracefully
        """
        
        self.do_exit(arg)
        
    def do_exit(self, arg):
        """
        Exit the program gracefully
        """
        
        self.moduleThread.stop()
        self.moduleThread.join()
        sys.exit(0)
        
class LoadModules(threading.Thread):
    """
    This thread call the function 'load_modules'
    in moduleManager periodically to check for 
    newly registered modules and modules recently
    removed
    """

    def __init__(self):
        """
        Constructor, sets continue flag
        """
        
        self.continueThis = True
        threading.Thread.__init__ (self)

    def run(self):
        """
        Handles the call to 'load_modules'
        """
        
        while self.continueThis:
            moduleManager.load_modules()
            time.sleep(1)
            
    def stop(self):
        """
        Mark the continue flag to stop thread
        """
        
        self.continueThis = False

def set_ctrlc_handler(func):
    """
    Catch CTRL+C and let the function
    on_ctrlc take care of it
    """
    
    signal.signal(signal.SIGINT, func)

if __name__ == "__main__":
    """
    Main program starts
    """
    
    def on_ctrlc(sig, func=None):
        """
        Ignore pressed CTRL+C
        """
        pass

    set_ctrlc_handler(on_ctrlc)
    CLI().cmdloop()
            
