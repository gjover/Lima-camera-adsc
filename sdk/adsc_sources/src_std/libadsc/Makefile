
adsc-objs = $(wildcard ../detcon_lib_th/*.o) $(wildcard ../auxlib/*.o)

libadsc.so : $(adsc-objs)
	gcc $+ -shared -o $@ 
	mv $@ ../../lib/linux

clean :	
	rm libadsc.so
