"""
Created on Wed Mar  9 10:39:22 2022

@author: tomas
"""

import struct
import numpy

class Cine:
    
    END = "little"
    
    def __init__(self, filename):
        "Representation of a CINE file format video file"
        
        self.filename = filename
        
        self.handle = open(filename, "rb")
        
        self.offsets = self.__image_offsets()
        
    
    def close(self):
        "Closes the underlying file handle."
        
        self.handle.close()
    
    def reopen(self):
        "Reopens file handle. Only safe after a close call."
        self.handle = open(self.filename, "rb")
        
    
    def image_count(self):
        self.handle.seek(0x14)
        mybytes = self.handle.read(4)
        return int.from_bytes(mybytes, self.END, signed=False)
    
    def __to_images_offset(self):
        self.handle.seek(0x20)
        mybytes = self.handle.read(4)
        return int.from_bytes(mybytes, self.END, signed=False)
    
    def __image_offsets(self):
        to = self.__to_images_offset()
        count = self.image_count()
        self.handle.seek(to)
        mybytes = self.handle.read(count * 8)
        offsets = struct.unpack("q"*count, mybytes)
        return offsets
    
    def image_width(self):
        self.handle.seek(0x30)
        mybytes = self.handle.read(4)
        return int.from_bytes(mybytes, self.END, signed=True)
    
    def image_height(self):
        self.handle.seek(0x34)
        mybytes = self.handle.read(4)
        return int.from_bytes(mybytes, self.END, signed=True)
    
    def image_size(self):
        self.handle.seek(0x40)
        mybytes = self.handle.read(4)
        return int.from_bytes(mybytes, self.END, signed=False)
    
    def __get_ith_bytes(self, i :int):
        offset = self.offsets[i]
        self.handle.seek(offset)
        a_size_bytes = self.handle.read(4)
        annote_size = int.from_bytes(a_size_bytes, self.END, signed=False)
        size = self.image_size()
        self.handle.seek(offset + annote_size)
        mybytes = self.handle.read(size)
        return mybytes
    
    def get_ith_image(self, i:int):
        mybytes = self.__get_ith_bytes(i)
        as_numbers = struct.unpack("B" * self.image_size(), mybytes)
        arr = numpy.array(as_numbers, numpy.uint8)
        width = self.image_width()
        height = self.image_height()
        shaped = numpy.reshape(arr, (height,width))
        flipped = numpy.flip(shaped,0)
        return flipped
    
    def gen_frames(self):
        for i in range(0,self.image_count()):
            yield self.get_ith_image(i)
    
    def load_all(self):
        frames = []
        scenes = self.gen_frames()
        for scene in scenes:
            frames.append(scene)
        return numpy.array(frames)
    
    def load_slice(self, begin :int, end :int):
        if begin < 0 or end > self.image_count():
            raise IndexError()
        frames = []
        for i in range(begin,end):
            frame = self.get_ith_image(i)
            frames.append(frame)
        
        return numpy.array(frames)
    
    
