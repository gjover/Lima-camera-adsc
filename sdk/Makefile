
BASE   = adsc_sources
DIR    = $(BASE)/src_std
OSTYPE = linux
EXE    = ccd_image_gather  det_api_workstation
LIBS   = libadsc.so  libauxlib.a  libauxlib.so  libdetcon_th.a  libdetcon_th.so  libwincompat.a

all: $(EXE) $(LIBS)


libauxlib.a  libauxlib.so :
	cd $(DIR)/auxlib; $(MAKE) -f Makefile.$(OSTYPE)  $(MFLAGS)

libdetcon_th.a  libdetcon_th.so : 
	cd $(DIR)/detcon_lib_th; $(MAKE) -f Makefile.$(OSTYPE)  $(MFLAGS)

libwincompat.a : 
	cd $(DIR)/libwincompat; $(MAKE) -f Makefile.$(OSTYPE)  $(MFLAGS)

ccd_image_gather : libauxlib.a libwincompat.a
	cd $(DIR)/ccd_image_gather; $(MAKE) -f Makefile.$(OSTYPE)  $(MFLAGS)

det_api_workstation : libauxlib.a  libwincompat.a
	cd $(DIR)/det_api_workstation; $(MAKE) -f Makefile.$(OSTYPE)  $(MFLAGS)

libadsc.so : libauxlib.a libdetcon_th.a
	cd $(DIR)/libadsc; $(MAKE)  $(MFLAGS)

clean :
	cd $(DIR)/auxlib; $(MAKE) -f Makefile.$(OSTYPE) clean
	cd $(DIR)/detcon_lib_th; $(MAKE) -f Makefile.$(OSTYPE) clean
	cd $(DIR)/libwincompat; $(MAKE) -f Makefile.$(OSTYPE) clean
	cd $(DIR)/det_api_workstation; $(MAKE) -f Makefile.$(OSTYPE) clean
	cd $(DIR)/ccd_image_gather; $(MAKE) -f Makefile.$(OSTYPE) clean

veryclean : clean
	rm -f $(BASE)/lib/$(OSTYPE)/*.a $(BASE)/lib/$(OSTYPE)/*.so $(BASE)/bin/$(OSTYPE)/*