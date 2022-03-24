
#include "cine.h"
#include "median.h"

#include <stdio.h>

size_t get_image_size(FILE* cine) {
    BITMAPINFOHEADER bih = Get_Bitmap_Header(cine);
    return (size_t) bih.biSizeImage;
}

int main() {
    const char* filename = "/home/tomas/Projects/BIOL395/CineFilesOriginal/moth22_2022-01-26.cine";
    FILE* handle = fopen(filename, "r");
    size_t im_size = get_image_size(handle);
    unsigned char* median_image = get_cine_median(handle);
    for(size_t i = 0; i < im_size; i++) {
        printf("%d ", median_image[i]);
    }
    fclose(handle);
    free(median_image);
    return 0;
}
