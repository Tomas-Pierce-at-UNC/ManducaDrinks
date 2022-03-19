
#include "cine.h"

#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

CINEFILEHEADER Get_Cine_Header(FILE* file) {
    fseek(file, 0, SEEK_SET);
    CINEFILEHEADER cfh;
    fread(&cfh, sizeof(CINEFILEHEADER), 1, file);
    return cfh;
}

BITMAPINFOHEADER Get_Bitmap_Header(FILE* file) {
    CINEFILEHEADER cfh = Get_Cine_Header(file);
    long int offset = (long int)cfh.OffImageHeader;
    fseek(file, offset, SEEK_SET);
    BITMAPINFOHEADER bih;
    fread(&bih, sizeof(BITMAPINFOHEADER), 1, file);
    return bih;
}

SETUP Get_Setup_Header(FILE* file) {
    CINEFILEHEADER cfh = Get_Cine_Header(file);
    long int offset = (long int)cfh.OffSetup;
    fseek(file,offset,SEEK_SET);
    SETUP setup;
    fread(&setup, sizeof(SETUP), 1, file);
    return setup;
}

uint8_t* Get_Ith_Image(FILE* cine, uint32_t image) {
    CINEFILEHEADER cfh = Get_Cine_Header(cine);
    BITMAPINFOHEADER bih = Get_Bitmap_Header(cine);
    if(image >= cfh.ImageCount) {
        return NULL;
    }
    long int offset = (long int)cfh.OffImageOffsets + ((long int)image * (long int)sizeof(int64_t));
    fseek(cine, offset, SEEK_SET);
    int64_t imagePos = 0;
    fread(&imagePos, sizeof(int64_t), 1, cine);
    fseek(cine, imagePos, SEEK_SET);
    uint32_t annoteSize = 0;
    fread(&annoteSize, sizeof(uint32_t), 1, cine);
    int64_t dataPos = imagePos + (int64_t)annoteSize;
    fseek(cine, dataPos, SEEK_SET);
    uint8_t *data = malloc(sizeof(uint8_t) * (size_t)bih.biSizeImage);
    fread(data, sizeof(uint8_t), (size_t)bih.biSizeImage, cine);
    return data;
}
