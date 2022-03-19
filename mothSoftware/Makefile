testmedian: testing.o median.o cine.o
	gcc -o testmedian testing.o median.o cine.o

median.so: libmedian.c libcine.c
	gcc -shared -fPIC -o median.so libmedian.c libcine.c

testing.o: testingmain.c
	gcc -c testingmain.c -o testing.o

median.o: libmedian.c cine.o
	gcc -c libmedian.c -o median.o

cine.o: libcine.c
	gcc -c libcine.c -o cine.o

debugmain: testingmain.c libmedian.c libcine.c
	gcc -g -o debugmain testingmain.c libmedian.c libcine.c
