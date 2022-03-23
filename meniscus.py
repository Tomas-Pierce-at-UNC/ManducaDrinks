#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 13:40:03 2022

@author: tomas
"""

# This sort of works. A little.
# Outcomes are best with videos tagged 'hover' and 'freeflight'

from mothSoftware.cine import Cine
from mothSoftware.cine_median import video_median
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


# # IMAGE RESTRICTION TO TUBE SECTION
# # KNOWN FAILURE MODE: TILTED TUBE
# # KNOWN SUCCESS MODE: FREE FLYING MOTH

def tallness_histogram(image) -> numpy.ndarray:
    verticals = filters.sobel_v(image)
    magnitudes = numpy.abs(verticals)
    threshold = filters.threshold_isodata(magnitudes)
    mask = magnitudes > threshold
    mask = morphology.skeletonize(mask)
    
    tallnesses = []
    
    for i in range(mask.shape[1]):
        col = mask[:,i]
        total = col.sum()
        tallnesses.append((i,total))
    
    tallnesses.sort(key=lambda x : x[1], reverse=True)
    
    return numpy.array(tallnesses)

def magnitude_percent_difference(baseline, comparison):
    """What is the difference between baseline and comparison
    as a percentage of baseline?"""
    delta = abs(baseline - comparison)
    ratio = float(delta) / float(baseline)
    percent = ratio * 100
    return percent
    

def get_column_bounds(tallness_histogram :numpy.ndarray):
    # one side boundary
    side_a = tallness_histogram[0][0]
    # side boundary tallness
    side_a_tallness = tallness_histogram[0][1]
    
    side_b = None
    
    for i in range(1,tallness_histogram.shape[0]):
        local_tallness = tallness_histogram[i][1]
        side_b = tallness_histogram[i][0]
        mpd = magnitude_percent_difference(side_a_tallness,local_tallness)
        if mpd > 50:
            break
    
    left = min(side_a,side_b)
    right = max(side_a,side_b)
    
    return (left - 10, right + 10)


def openVideo(filename :str) -> Cine:
    return Cine(filename)

def apply(function, image_seq):
    for image in image_seq:
        yield function(image)

def subtract(leftImage, rightImage) -> numpy.ndarray:
    left = leftImage.astype(numpy.int16)
    right = rightImage.astype(numpy.int16)
    return left - right

def read_data(video :Cine, left, right):
    images = []
    frames = video.gen_frames()
    for frame in frames:
        restricted = frame[:,left:right]
        images.append(restricted)
    return numpy.array(images)

def inverse(data :numpy.ndarray):
    return -data + 255

def threshold(deltas):
    iso = filters.threshold_isodata(deltas)
    low = deltas < iso
    return low

def isolate_meniscus(filename, display = False):
    vid = Cine(filename)
    median = video_median(vid)
    histogram = tallness_histogram(median)
    left,right = get_column_bounds(histogram)
    median = median[:,left:right]
    data = read_data(vid, left, right)
    deltas = subtract(data,median)
    isolated = threshold(deltas)
    vid.close()
    if display:
        for i in range(len(data)):
            fig,axes = pyplot.subplots(ncols=3)
            axes[0].imshow(data[i])
            axes[1].imshow(deltas[i])
            axes[2].imshow(isolated[i])
            pyplot.show(block=False)
            pyplot.pause(0.25)
            pyplot.close("all")
    return isolated
