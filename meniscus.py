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


# def apply(func, im_seq) -> numpy.ndarray:
    
#     images = []
    
#     for image in im_seq:
#         #bytesImage = util.img_as_ubyte(func(image))
#         result = func(image)
#         images.append(result)
    
#     return numpy.array(images)

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


# def to_tube_restrict(image_seq :numpy.ndarray):
#     left =   100000000000000 
#     right = -100000000000000
#     for image in image_seq:
#         histogram = tallness_histogram(image)
#         myleft,myright = get_column_bounds(histogram)
#         if myleft < left:
#             left = myleft
#         if myright > right:
#             right = myright
#     return image_seq[:,:,left:right]

# def show_random_image(seq):
#     count = seq.shape[0]
#     place = random.randint(0,count-1)
#     image = seq[place]
#     imshow(image)
#     return place
    
# def open_unrestricted_cine_data(filename):
#     cine = Cine(filename)
#     data = cine.load_all()
#     return data
    
# def open_restricted_cine_data(filename):
#     cine = Cine(filename)
#     data = cine.load_all()
#     restricted = to_tube_restrict(data)
#     cine.close()
#     return restricted

# def temporal_mode(image_seq):
#     moderesult = stats.mode(image_seq)
#     mode = moderesult.mode
#     return mode[0] # fix shape issue

# def make_background(image_seq):
#     return numpy.quantile(image_seq, 0.25, 0)


# def process(image_seq):
#     edges = apply(filters.sobel, image_seq)
#     background = make_background(edges)
#     deltas = edges - background
#     return deltas

# def otsu_mask(image):
#     otsu = filters.threshold_otsu(image)
#     return image > otsu

# def find_meniscus(image_seq):
#     h_edges = apply(filters.sobel_h, image_seq)
#     back = make_background(h_edges).astype(numpy.uint8)
#     dif = h_edges - back
#     #dif = apply(
#         #lambda image : image / image.max(),
#        # dif
#        # )
#     dilates = apply(
#         morphology.dilation,
#         dif
#         )
#     didilates = apply(
#         morphology.dilation,
#         dilates
#         )
#     masks = apply(otsu_mask, didilates)
#     return masks

# def task(images):
#     mid = numpy.median(images, 0)
#     mid = mid.astype(numpy.uint8)
#     delta = images.astype(numpy.int16) - mid.astype(numpy.int16)
#     delta[delta > 0] = 0
#     return delta

def openVideo(filename :str) -> Cine:
    return Cine(filename)

def apply(function, image_seq):
    for image in image_seq:
        yield function(image)

def subtract(leftImage, rightImage) -> numpy.ndarray:
    left = leftImage.astype(numpy.int16)
    right = rightImage.astype(numpy.int16)
    return left - right

def get_differences(video :Cine):
    
    median = video_median(video)
    
    images = video.gen_frames()
    
    def minus_bg(image):
        return subtract(image, median)
    
    differences = apply(minus_bg, images)
    
    for delta in differences:
        
        yield delta

def get_restrictions(video :Cine):

    images = video.gen_frames()

    left = 1000000000000000
    right = -100000000000000
    
    for image in images:
        histogram = tallness_histogram(image)
        myleft,myright = get_column_bounds(histogram)
        if myleft < left:
            left = myleft
        if myright > right:
            right = myright

    return left,right

def prep(video :Cine):
    left,right = get_restrictions(video)
    deltas = get_differences(video)
    for delta in deltas:
        yield delta[:,left:right]

def make_mask(image):
    image[image > 0] = 0
    threshold = filters.threshold_isodata(image)
    high = image > threshold
    return ~high

def get_masks(image_seq):

    for image in image_seq:

        yield make_mask(image)

def isolate_meniscus(masks_seq):

    for mask in masks_seq:

        yield morphology.erosion(mask)

def find_meniscus_canidates(processed_image):
    blobs = feature.blob_log(processed_image)
    #filter by sigma for plausible sizes
    canidates = blobs[blobs[:,2] > 1.0]
    canidates = canidates[canidates[:,2] < 10.0]
    return canidates
##
##def get_positions(processed_seq):
##
##    for image in processed_seq:
##
##        yield find_meniscus(image)
##

def accumulate_meniscus_canidates(processed_sequence):

    for i,image in enumerate(processed_sequence):

        yield (i,find_meniscus_canidates(image))


def shared_x_meniscus(pairs):
    frequencies = {}
    values = []

    for i, canidate_list in pairs:
        for canidate in canidate_list:
            y,x,sigma = canidate
            if x in frequencies:
                frequencies[x] += 1
            else:
                frequencies[x] = 1

            potential = (i,y,x,sigma)
            values.append(potential)

    data = numpy.array(values)
    
    x_coord_maxed = None
    x_coord_maxed_count = 0
    
    for x,count in frequencies.items():
        if count > x_coord_maxed_count:
            x_coord_maxed = x
            x_coord_maxed_count = count

    return data[data[:,2] == x_coord_maxed]
