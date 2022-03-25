
"""
Created on Wed Mar  9 13:40:03 2022

@author: tomas
"""

# This sort of works. A little.
# Outcomes are best with videos tagged 'hover' and 'freeflight'

from cinelib import Cine
from cinelib import video_median
from skimage.io import imshow
from skimage import filters
from skimage import morphology
#from skimage import exposure
from skimage import feature
#from skimage import util
import numpy
import random
import math
from scipy import stats
from matplotlib import pyplot
from common import tallness_histogram, magnitude_percent_difference, get_column_bounds
from point import Point
from alignment import register


def get_col_bounds(image):
    histogram = tallness_histogram(image)
    left,right = get_column_bounds(histogram)
    return left,right

def openVideo(filename :str) -> Cine:
    return Cine(filename)

def apply(function, image_seq):
    for image in image_seq:
        yield function(image)

def subtract(leftImage, rightImage) -> numpy.ndarray:
    left = leftImage.astype(numpy.int16)
    right = rightImage.astype(numpy.int16)
    return left - right

def read_data(video :Cine, left, right, median):
    images = []
    frames = video.gen_frames()
    for frame in frames:
        aligned = register(median, frame)
        restricted = aligned[:,left:right]
        images.append(restricted)
    return numpy.array(images)

def inverse(data :numpy.ndarray):
    return -data + 255

def threshold(deltas):
    iso = filters.threshold_isodata(deltas)
    low = deltas < iso
    return low

##def isolate_meniscus(filename, debug = False):
##    vid = Cine(filename)
##    median = video_median(vid)
##    left,right = get_col_bounds(median)
##    scene = median[:,left:right]
##    data = read_data(vid,left,right)
##    deltas = subtract(data,scene)
##    deltas[deltas > 0] = 0
##    masks = numpy.ndarray(deltas.shape, dtype=bool)
##    
##    if debug:
##        edges = []
##        mag_edges = []
##        debug_masks = []
##        
##    for i,frame in enumerate(deltas):
##        h_edges = filters.sobel_h(frame)
##        edge_mag = numpy.abs(h_edges)
##        li = filters.threshold_li(edge_mag)
##        mask = edge_mag > li
##        #opened = morphology.opening(mask)
##        eroded = morphology.erosion(mask)
##        masks[i] = eroded
##        
##        if debug:
##            edges.append(h_edges)
##            mag_edges.append(mag_edges)
##            debug_masks.append(mask)
##
##    if debug:
##        return scene,deltas,edges,mag_edges,masks, debug_masks
##
##    return masks
##
##

if __name__ == '__main__':

    fname = "/home/tomas/Projects/BIOL395/CineFilesOriginal/moth22_2022-02-01b_Cine1.cine"
    vid = Cine(fname)
    median = video_median(vid)
    count = vid.image_count()
    left,right = get_col_bounds(median)
    res_median = median[:,left:right]
    images = []
    for i in range(0,count):
        frame = vid.get_ith_image(i)
        restricted = frame[:,left:right]
        aligned = register(res_median,restricted)
        sub = subtract(aligned,res_median)
        images.append(sub)
        print('.',end='')
        if i % 50 == 0:
            print('')
    deltas = numpy.array(images)
    vid.close()
    rows = []
    for i,delta in enumerate(deltas):
        li2 = filters.threshold_li(delta) * 2
        low = delta < li2
        blobs = feature.blob_log(low)
        multi_pix = blobs[blobs[:,2] > 1]
        row = multi_pix[:,0].mean()
        rows.append(row)
        print(',',end='')
        if i % 50 == 0:
            print('')
    rows = numpy.array(rows)
    pyplot.plot(rows)
    #median = video_median(vid)
    #left,right = get_col_bounds(median)
    #data = read_data(vid,left,right,median)
    #vid.close()
    #res_median = median[:,left:right]
    #deltas = subtract(data,res_median)
    
