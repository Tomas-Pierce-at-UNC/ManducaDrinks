#ifndef MEDIAN_H_INCLUDED
#define MEDIAN_H_INCLUDED

/* represents a histogram of 8-bit data */
struct Histogram {
    int *data;
};

struct Histogram init_histogram();

void cleanup_histogram(struct Histogram *histogram);

void update_histogram(struct Histogram *histogram, uint8_t value);

uint8_t median_of_histogram(struct Histogram *histogram);

struct Histogram* cine_temporal_histograms(FILE* cine);

uint8_t* get_median_image(struct Histogram *histograms, size_t image_size);

unsigned char* get_cine_median(FILE* cine);

unsigned char* get_time_median(const char* name);

void video_median(const char* name, unsigned char *out);

#endif // MEDIAN_H_INCLUDED
