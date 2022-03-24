
from cinelib import Cine
from cinelib import video_median
import numpy
from skimage import filters, morphology, transform, measure, feature
#import math
from matplotlib import pyplot
from skimage.io import imshow
from point import Point
from common import tallness_histogram, magnitude_percent_difference, get_column_bounds

def read_data(video :Cine, left,right) -> numpy.ndarray:
    images = []
    frames = video.gen_frames()
    for frame in frames:
        restricted = frame[:,left:right]
        images.append(restricted)
    return numpy.array(images)

def subtract(left,right):
    return left.astype(numpy.int16) - right.astype(numpy.int16)

def get_on_pixels(mask):
    on = []
    for x in range(mask.shape[1]):
        for y in range(mask.shape[0]):
            if mask[y,x]:
                p = Point(x,y)
                on.append(p)
    on.sort(key=lambda point : point.y)
    return on

def form_islands(pixels):
    mypixels = pixels.copy()
    islands = []
    island = []
    start = mypixels.pop()
    island.append(start)
    while len(mypixels) > 0:
        next_pixel = mypixels.pop()
        found = False
        for place in island:
            if place.four_connected(next_pixel):
                island.append(next_pixel)
                found = True
                break
        if not found:
            island.reverse()
            islands.append(island)
            island = []
            island.append(next_pixel)

    return islands

def only_large_islands(islands):
    return list(filter(lambda isle : len(isle) >= 10, islands))

def get_island_width(island):
    least = min(island, key = lambda point : point.x)
    greatest = max(island, key = lambda point : point.x)
    difference = least.x - greatest.x
    # discrete shenanigans
    width = difference + 1
    return width

def no_one_wide_islands(islands):
    return list(filter(lambda isle : get_island_width(isle) > 1, islands))

def max_y_island_point(island):
    return max(island, key = lambda point : point.y)

def max_y_of_islands_point(islands):
    maxes = map(max_y_island_point, islands)
    max_y_pt = max(maxes, key = lambda point : point.y)
    return max_y_pt

def auto_rotate(image):
    pass
    
def find_tips(filename, display = False):
    vid = Cine(filename)
    median = video_median(vid)
    histogram = tallness_histogram(median)
    left,right = get_column_bounds(histogram)
    data = read_data(vid,left,right)
    median = median[:,left:right]
    deltas = subtract(data,median)
    deltas[deltas > 0] = 0
    masks = numpy.ndarray(deltas.shape,dtype=bool)
    tracking = []
    
    for i,delta in enumerate(deltas):
        iso = filters.threshold_isodata(delta)
        low = delta < (iso * 1.5)
        masks[i] = low
        mask = masks[i]
        pix = get_on_pixels(mask)
        islands = form_islands(pix)
        big_isles = only_large_islands(islands)
        #big_isles = no_one_wide_islands(big_isles)
        max_y_pt = max_y_of_islands_point(big_isles)
        tracking.append((i,max_y_pt.x,max_y_pt.y))
        if display:
            fig,axes = pyplot.subplots(nrows=2,ncols=2)
            axes[1][0].imshow(delta)
            axes[1][1].imshow(mask)
            axes[0][0].imshow(median)
            axes[0][1].imshow(data[i])
            pyplot.show(block=False)
            pyplot.pause(0.25)
            pyplot.close("all")

    vid.close()
    tips = numpy.array(tracking)

    return tips

def align(reference, image_seq):
    # on the to-do list
    pass

def illustrate(filename):
    # demonstrate that the most likely cause is movement of tube.
    # leads to natural solution of image registration via
    # (ORB|SIFT), RANSAC, and warp() function
    c = Cine(filename)
    median = video_median(c)
    f192 = c.get_ith_image(192)
    c.close()
    fig,axes = pyplot.subplots(ncols=2)
    axes[0].imshow(median)
    axes[1].imshow(f192)
    axes[0].axvline(x=460)
    axes[1].axvline(x=460)
    pyplot.show()
    
if __name__ == '__main__':

    f = "/home/tomas/Projects/BIOL395/CineFilesOriginal/moth22_2022-02-07_Cine1.cine"
    tips = find_tips(f)
    pyplot.plot(tips[:,0],tips[:,2])
    pyplot.show()
    #illustrate(f)
