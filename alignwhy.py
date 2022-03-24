
from cinelib import Cine, video_median
from matplotlib import pyplot
import numpy
from skimage.io import imshow

def subtract(left_image, right_image):
    return left_image.astype(numpy.int16) - right_image.astype(numpy.int16)

vid = Cine("../CineFilesOriginal/moth22_2022_02_09_bad_Cine1.cine")
z = vid.get_ith_image(0)
median = video_median(vid)
vid.close()
#res = z[:,380:420]
#res_median = median[:,380:420]
dif = subtract(median, z)
imshow(dif)
pyplot.show()
