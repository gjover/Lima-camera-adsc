############################################################################
# This file is part of LImA, a Library for Image Acquisition
#
# Copyright (C) : 2009-2011
# European Synchrotron Radiation Facility
# BP 220, Grenoble 38043
# FRANCE
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
############################################################################
import os

from Lima import Core


class DetInfoCtrlObj(Core.HwDetInfoCtrlObj) :
    """Handles static information about the detector and the current image dimension."""

    #Core.DEB_CLASS(Core.DebModCamera, "DetInfoCtrlObj")
    def __init__(self) :
        Core.HwDetInfoCtrlObj.__init__(self)

        ## Detector type and model separated by ,
        self.__name = 'ADSC,Quantum 210'
        ## Max image width
        ##@todo Set the actual max width (4096) and implement the binning capability
        self.__width  = 2048
        ## Max image height
        ##@todo Set the actual max height (4096) and implement the binning capability
        self.__height = 2048
#         self.__width  = 4096
#         self.__height = 4096
        ## Image depth in bits per pixel
        self.__bpp = 16

    def init(self) :
        pass
        
    #@Core.DEB_MEMBER_FUNCT
    ##@todo Set the actual size and implement the binning capability
    def getMaxImageSize(self) :
        """Maximum size of the image
        @return """        
        return Core.Size(self.__width,self.__height)

    #@Core.DEB_MEMBER_FUNCT
    ##@todo Set the actual size and implement the binning capability
    def getDetectorImageSize(self) :
        """Size of the image in pixel
        @return Size of the image in pixels"""
        return self.getMaxImageSize()
    
    #@Core.DEB_MEMBER_FUNCT
    def getDefImageType(self) :
        """Default data type of image"""
        if self.__bpp == 16:
            return Core.Bpp16
        else:
            raise Core.Exception(Core.Hardware,Core.NotSupported)

    #@Core.DEB_MEMBER_FUNCT
    def getCurrImageType(self) :
        """Current data type of image"""
        return self.getDefImageType()

    #@Core.DEB_MEMBER_FUNCT
    def setCurrImageType(self) :
        raise Core.Exceptions(Core.Hardware,Core.NotSupported)

    
    #@Core.DEB_MEMBER_FUNCT
    def getPixelSize(self) :
        """Physical size of pixels in um"""
        return 81.7e-6

    #@Core.DEB_MEMBER_FUNCT
    def getDetectorType(self) :
        """Type of detector"""
        return 'ADSC'

    #@Core.DEB_MEMBER_FUNCT
    def getDetectorModel(self):
        """Model of the detector"""
	if self.__name :
           return self.__name.split(',')[0].split()[-1]
	else:
	   return "ADSC unknown"


    #@Core.DEB_MEMBER_FUNCT
    ##@todo Implement when binning capability implementation
    def registerMaxImageSizeCallback(self,cb) :
        pass

    #@Core.DEB_MEMBER_FUNCT
    ##@todo Implement when binning capability implementation
    def unregisterMaxImageSizeCallback(self,cb) :
        pass

    #@Core.DEB_MEMBER_FUNCT
    ##@todo Set the actual value
    def get_min_exposition_time(self):
        """Minimum exposition time allowed in seconds"""
        return 10e-6

    #@Core.DEB_MEMBER_FUNCT
    ##@todo don't know realy what is the maximum exposure time
    #for now set to a high value 1 hour
    def get_max_exposition_time(self) :
        """Maximum exposition time allowed in seconds"""
        return 3600

    #@Core.DEB_MEMBER_FUNCT

    def get_min_latency(self) :
        """Minimum latency time after exposition in seconds"""
	#return 0.140
        return 1.0

    #@Core.DEB_MEMBER_FUNCT
    ##@todo don't know
    #@see get_max_exposition_time
    def get_max_latency(self):
        """Maximum latency time after exposition in seconds"""
        return 2**31
