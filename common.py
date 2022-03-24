
from skimage import filters, morphology
import numpy

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
