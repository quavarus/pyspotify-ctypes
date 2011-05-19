'''
Created on 29/04/2011

@author: mikel
'''
import ctypes

from _spotify import link as _link

from spotify import track, playlist, user

from spotify.utils.decorators import synchronized



@synchronized
def create_from_string(string):
    return Link(_link.create_from_string(string))


@synchronized
def create_from_track(track, offset = 0):
    return Link(_link.create_from_track(track.get_struct(), offset))


@synchronized
def create_from_artist(artist):
    return Link(_link.create_from_artist(artist.get_struct()))


@synchronized
def create_from_album(album):
    return Link(_link.create_from_album(album.get_struct()))


@synchronized
def create_from_search(search):
    return Link(_link.create_from_search(search.get_struct()))


@synchronized
def create_from_playlist(playlist):
    return Link(_link.create_from_playlist(playlist.get_struct()))


@synchronized
def create_from_user(user):
    return Link(_link.create_from_user(user.get_struct()))



class LinkType:
    Invalid = 0
    Track = 1
    Album = 2
    Artist = 3
    Search = 4
    Playlist = 5
    Profile = 6
    Starred = 7
    Localtrack = 8



class Link:
    __link_struct = None
    
    
    def __init__(self, link_struct):
        self.__link_struct = link_struct
    
    
    @synchronized
    def as_string(self):
        buf = (ctypes.c_char * 255)()
        
        #Should check return value?
        _link.as_string(self.__link_struct, ctypes.byref(buf), 255)
        
        return buf.value
    
    
    @synchronized
    def type(self):
        return _link.type(self.__link_struct)
    
    
    @synchronized
    def as_track(self):
        return track.Track(_link.as_track(self.__link_struct)) 
    
    
    @synchronized
    def as_track_and_offset(self):
        offset = ctypes.c_int
        track = track.Track(_link.as_track_and_offset)
        return track, offset.value
    
    @synchronized
    def as_album(self):
        pass
    
    
    @synchronized
    def as_artist(self):
        pass
    
    
    @synchronized
    def as_user(self):
        return user.User(_link.as_user(self.__link_struct))
    
    
    @synchronized
    def add_ref(self):
        _link.add_ref(self.__link_struct)
    
    
    @synchronized
    def release(self):
        _link.release(self.__link_struct)
    
    
    def get_struct(self):
        return self.__link_struct
    
    
    def __str__(self):
        return self.as_string()
    
    
    def __del__(self):
        self.release()