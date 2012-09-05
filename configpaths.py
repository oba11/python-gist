import sys
import os

def get_config_path(appname,config_filename=''):
    #modified from http://stackoverflow.com/questions/1084697/how-do-i-store-desktop-application-data-in-a-cross-platform-way-for-python
    if sys.platform == 'darwin':
        from AppKit import NSSearchPathForDirectoriesInDomains
        # http://developer.apple.com/DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous/Foundation_Functions/Reference/reference.html#//apple_ref/c/func/NSSearchPathForDirectoriesInDomains
        # NSApplicationSupportDirectory = 14
        # NSUserDomainMask = 1
        # True for expanding the tilde into a fully qualified path
        appdata = path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], appname, config_filename)
    
    elif sys.platform == 'win32':
        appdata = os.path.join(os.environ['APPDATA'], appname, config_filename)

    elif os.environ['XDG_CONFIG_HOME']:
        appdata = os.path.join(os.environ['XDG_CONFIG_HOME'], appname, config_filename)
    else:
        appdata = os.path.expanduser(path.join('~', '.' + appname, config_filename))

    configpath = os.path.dirname(appdata)
    if not os.path.exists(configpath):
        os.makedirs(configpath)

    return appdata
if __name__=='__main__':
    print get_config_path("test","test.cfg")