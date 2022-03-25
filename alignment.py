
from skimage.feature import ORB,SIFT,match_descriptors
from skimage.measure import ransac
from skimage.transform import EuclideanTransform, warp
import numpy

def register(reference,image):
    # register the image to the reference

    # based on
    # https://stackoverflow.com/questions/62280342/image-alignment-with-orb-and-ransac-in-scikit-image#62332179
    
    # extracts descriptors and keypoints
    de = SIFT()
    #de = ORB()
    de.detect_and_extract(reference)
    ref_keypoints = de.keypoints
    ref_descriptors = de.descriptors
    de.detect_and_extract(image)
    keypoints = de.keypoints
    descriptors = de.descriptors
    matches = match_descriptors(ref_descriptors, descriptors, cross_check=True)
    ref_matches = ref_keypoints[matches[:,0]]
    matches = keypoints[matches[:,1]]
    transform_robust,inliers = ransac((ref_matches, matches),
                                      EuclideanTransform,
                                      min_samples=5,
                                      residual_threshold=0.5,
                                      max_trials = 1000
                                      )
    robust = EuclideanTransform(rotation = transform_robust.rotation) + EuclideanTransform(translation = -numpy.flip(transform_robust.translation))
    warped = warp(
        image,
        robust.inverse,
        order = 1,
        mode = "constant",
        cval = 0,
        clip = True,
        preserve_range = True
        )
    return warped.astype(image.dtype)

if __name__ == '__main__':
    from cinelib import Cine, video_median
    from skimage.io import imshow
    from matplotlib import pyplot
    fname = "../CineFilesOriginal/moth22_2022_02_09_bad_Cine1.cine"
    vid = Cine(fname)
    z = vid.get_ith_image(0)
    median = video_median(vid)
    vid.close()
    unreged_delta = z.astype(numpy.int16) - median.astype(numpy.int16)
    reged = register(median,z)
    reged_delta = reged.astype(numpy.int16) - median.astype(numpy.int16)
    fig,axes = pyplot.subplots(ncols=2)
    axes[0].imshow(unreged_delta)
    axes[1].imshow(reged_delta)
    pyplot.show()
    
