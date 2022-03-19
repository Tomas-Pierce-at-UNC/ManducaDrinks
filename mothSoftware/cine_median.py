
import ctypes
import struct
import numpy
import os

from .cine import Cine

if __name__ == '__main__':
    _libpath = "./median.so"
else:  
    _libpath = os.path.dirname(__file__) + "/median.so"

_medianlib = ctypes.cdll.LoadLibrary(_libpath)
_medianlib.get_time_median.restype = ctypes.c_char_p


def take_chrono_median(video :Cine) -> numpy.ndarray:
    video.close()
    filename = video.filename.encode()
    median = _medianlib.get_time_median(filename)
    video.reopen()
    data = struct.unpack("B"*video.image_size(), median)
    bits = numpy.array(data, dtype=numpy.uint8)
    shaped = numpy.reshape(bits, (video.image_height(),video.image_width()))
    flipped = numpy.flip(shaped, 0)
    return flipped

def video_median(video :Cine) -> numpy.ndarray:
    filename = video.filename.encode()
    buffer = ctypes.create_string_buffer(video.image_size())
    video.close()
    _medianlib.video_median(filename, buffer)
    video.reopen()
    bits = buffer.raw
    data = struct.unpack("B"*video.image_size(), bits)
    arr = numpy.array(data, dtype=numpy.uint8)
    shaped = numpy.reshape(arr, (video.image_height(),video.image_width()))
    flipped = numpy.flip(shaped,0)
    return flipped
