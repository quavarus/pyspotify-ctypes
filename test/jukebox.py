'''
Created on 07/11/2010

@author: mikel
'''
import sys

from appkey import appkey
from spotify import session, MainLoop, playlistcontainer, playlist, handle_sp_error

from spotify import BulkConditionChecker

import cmd
import threading

#Make cherrypy available on path
sys.path.append("../lib/CherryPy-3.2.0-py2.4.egg")


#Proxy http server for resources
from spotify.utils import httpproxy, audio



class JukeboxCallbacks(session.SessionCallbacks):
    _mainloop = None
    __buf = None
    
    def __init__(self, mainloop, buf):
        self._mainloop = mainloop
        self.__buf = buf
    
    def logged_in(self, session, error):
        handle_sp_error(error)
        print "login successful"  
    
    def logged_out(self, session):
        print "logout successful"
            
    
    def connection_error(self, session, error):
        print "conn error"
        
    def log_message(self, session, data):
        print "log: %s" % data
    
    def streaming_error(self, error):
        print "streaming error: %d" % error
    
    def end_of_track(self, session):
        self.__buf.set_track_ended()
        
    def notify_main_thread(self, session):
        self._mainloop.notify()
    
    def metadata_updated(self, session):
        #print "metadata_updated"
        pass
    
    def music_delivery(self, session, data, num_samples, sample_type, sample_rate, num_channels):
        return self.__buf.music_delivery(data, num_samples, sample_type, sample_rate, num_channels)
    
    def get_audio_buffer_stats(self, session):
        return self.__buf.get_stats()



def print_user(user):
    print "user loaded (cb): %d" % user.is_loaded()


def main():
    print "uses SPOTIFY(R) CORE"
    ml = MainLoop()
    buf = audio.MemoryBuffer()
    cb = JukeboxCallbacks(ml, buf)
    s = session.Session(
        cb,
        app_key=appkey,
        user_agent="python ctypes bindings",
        settings_location="C:\\sptest\\settings",
        cache_location="C:\\sptest\\cache",
    )
    
    pr = httpproxy.ProxyRunner(s, buf)
    c = JukeboxCmd(s, ml)
    c.start()
    pr.start()
    ml.loop(s)
    pr.stop()



class JukeboxPlaylistContainerCallbacks(playlistcontainer.PlaylistContainerCallbacks):
    _checker = None
    
    def __init__(self, checker):
        self._checker = checker
    
    def container_loaded(self, container):
        self._checker.check_conditions()



class JukeboxCmd(cmd.Cmd, threading.Thread):
    prompt = "jukebox>"
    
    _session = None
    _mainloop = None
    
    def __init__(self, session, mainloop):
        cmd.Cmd.__init__(self)
        threading.Thread.__init__(self)
        self._session = session
        self._mainloop = mainloop
    
    
    def run(self):
        self.cmdloop()
    
    
    def do_login(self, line):
        args = line.split(' ', 2)
        self._session.login(args[0], args[1])
    
    
    def do_logout(self, line):
        self._session.logout()
    
    
    def do_quit(self, line):
        self._mainloop.quit()
        return True
    
    
    def do_list(self, line):
        container = self._session.playlistcontainer()
        
        if not container.is_loaded():
            checker = BulkConditionChecker()
            #Wait until the container is loaded
            checker.add_condition(container.is_loaded)
            callbacks = JukeboxPlaylistContainerCallbacks(checker)
            container.add_callbacks(callbacks)
            checker.complete_wait()
            
            for item in container:
                item.set_in_ram(self._session, True)
        
        if not line:
            #Print all playlists
            print "%d playlists:" % container.num_playlists()
            
            for k, item in enumerate(container):
                if item.is_loaded():
                    print "playlist #%d: %s" % (k, item.name()) 
                else:
                    print "playlist #%d: loading..." % k
        else:
            pos = int(line)
            pl = container.playlist(pos)
            print "playlist #%d, %d tracks:" % (pos, pl.num_tracks())
            
            for index,item in enumerate(pl):
                if item.is_loaded():
                    print "track #%d: %s" % (index, item.name())
                    #print item.album().cover()
                else:
                    print "track #%d: loading..." % index
    
    
    do_EOF = do_quit


if __name__ == '__main__':
    main()
