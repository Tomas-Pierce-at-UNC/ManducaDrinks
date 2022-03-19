

#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <stdbool.h>

#define BINS 256

#include "cine.h"

#include "median.h"

struct Histogram init_histogram() {
    struct Histogram histogram;
    histogram.data = malloc(sizeof(int) * BINS);
    for(int i = 0; i < BINS; i++) {
        histogram.data[i] = 0;
    }
    return histogram;
}

void cleanup_histogram(struct Histogram *histogram) {
    free(histogram->data);
    histogram->data = NULL;
}

void update_histogram(struct Histogram *histogram, uint8_t value) {
    histogram->data[value] += 1;
}

uint8_t median_of_histogram(struct Histogram *histogram) {
    long int tally_count = 0;
    for(int i = 0; i < BINS; i++) {
        tally_count += histogram->data[i];
    }
    /* zero indexing problems are why the -1 is there */
    long int location = (tally_count / 2) - 1;
    //bool even = tally_count % 2 == 0;
    long int here_index = 0;
    bool breakout = false;
    uint8_t here = 0;
    //uint8_t next = 0;

    for(int bin = 0; bin < BINS; bin++) {
        int count = histogram->data[bin];
        here = bin;
        for(int i = 0; i < count; i++) {
            here_index += 1;
            if(here_index == location) {
                if(i+1 == count) {
                    //next = bin + 1;
                } else {
                    //next = bin;
                }
                breakout = true;
                break;
            }
        }
        if(breakout) {
            break;
        }
    }

    /*
    if(even) {
        return ((uint16_t)here + (uint16_t)next) / 2);
    } else {
        return here;
    }
    */
    // inaccuracies should not exceed 1
    return here;
}


struct Histogram* cine_temporal_histograms(FILE* cine) {
    CINEFILEHEADER cfh = Get_Cine_Header(cine);
    BITMAPINFOHEADER bih = Get_Bitmap_Header(cine);
    long image_size = bih.biSizeImage;
    struct Histogram *histograms = calloc((size_t)bih.biSizeImage, sizeof(struct Histogram));
    if(histograms == NULL) return NULL;
    for(unsigned int k = 0; k < image_size; k++) {
        histograms[k] = init_histogram();
    }
    for(unsigned int i = 0; i < cfh.ImageCount; i++) {
        uint8_t *image = Get_Ith_Image(cine, i);
        for(unsigned int j = 0; j < image_size; j++) {
            update_histogram(histograms + j, image[j]);
        }
        free(image);
        image = NULL;
    }
    return histograms;
}

uint8_t* get_median_image(struct Histogram *histograms, size_t image_size) {

    uint8_t *buffer = malloc(image_size * sizeof(uint8_t) + 1);

    for(size_t i = 0; i < image_size; i++) {
        uint8_t mid = median_of_histogram(histograms + i);
        buffer[i] = mid;
    }

    buffer[image_size] = '\0';

    return buffer;
}

unsigned char* get_cine_median(FILE* cine) {
    BITMAPINFOHEADER bih = Get_Bitmap_Header(cine);
    size_t image_size = (size_t)bih.biSizeImage;
    struct Histogram *histograms = cine_temporal_histograms(cine);
    uint8_t *median_img = get_median_image(histograms, image_size);
    for(size_t i = 0; i < image_size; i++) {
        cleanup_histogram(histograms + i);
    }
    free(histograms);
    histograms = NULL;
    return (unsigned char*)median_img;
}

unsigned char* get_time_median(const char* name) {
    FILE* handle = fopen(name, "r");
    unsigned char *median = get_cine_median(handle);
    fclose(handle);
    return median;
}

void video_median(const char* name, unsigned char *out) {
    FILE* handle = fopen(name, "r");
    BITMAPINFOHEADER bih = Get_Bitmap_Header(handle);
    size_t im_size = (size_t)bih.biSizeImage;
    unsigned char *median = get_cine_median(handle);
    fclose(handle);
    for(size_t i = 0; i < im_size; i++) {
        out[i] = median[i];
    }
}
