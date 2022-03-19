
#include <stdint.h>

enum DataType {BYTE=1, SHORT=2, INT=4, LONG=8};
enum Sign {Signed, UnSigned};

union ObjPtr {
    unsigned char *ubytes;
    signed char *ibytes;
    unsigned short *ushorts;
    signed short *ishorts;
    unsigned int *uint;
    signed int *iint;
    unsigned long *ulong;
    signed long *ilong;
};

struct Karray {
    size_t count;
    enum DataType dtype;
    enum Sign sign;
    union ObjPtr obj;
};

struct Karray empty(size_t count, )
