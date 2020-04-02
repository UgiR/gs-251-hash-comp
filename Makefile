hash-so:
	g++ -c -fPIC hash.cpp -o hash.o
	g++ -shared -Wl,-soname,hash.so -o hash.so hash.o