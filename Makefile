common.so: common.c
	gcc common.c -I/usr/include/python3.9 -L/usr/lib/x86_64-linux-gnu/ -lpython3.9 -shared -fPIC -o common.so

common.c: common.py
	cython -3 common.py
# an example of what to do above
