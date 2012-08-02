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
import weakref

from Lima import Core

class SyncCtrlObj(Core.HwSyncCtrlObj) :
    #Core.Debug.DEB_CLASS(Core.DebModCamera, "SyncCtrlObj")
    def __init__(self,comm_object,det_info) :
        Core.HwSyncCtrlObj.__init__(self)
        self.__comm = weakref.ref(comm_object)
        self.__det_info = weakref.ref(det_info)
        
        #Variables
        self.__latency = det_info.get_min_latency()
        #self.__exposure = comm_object.getExposureTime()
        self.__exposure = 1             # default value 1s
        self.__nb_frames = 1            # default value 1frame

    #@Core.Debug.DEB_MEMBER_FUNCT
    def checkTrigMode(self,trig_mode) :
        return trig_mode == Core.IntTrig
        
    #@Core.Debug.DEB_MEMBER_FUNCT
    def setTrigMode(self,trig_mode):
        if trig_mode != Core.IntTrig :
            raise Core.Exceptions(Core.Hardware,Core.NotSupported)


    #@Core.Debug.DEB_MEMBER_FUNCT
    def getTrigMode(self) :
        return Core.IntTrig
    
    #@Core.Debug.DEB_MEMBER_FUNCT
    def setExpTime(self,exp_time):
        self.__exposure = exp_time
        com = self.__comm()
        com.setExposureTime(exp_time)
        
    #@Core.Debug.DEB_MEMBER_FUNCT
    def getExpTime(self) :
#        if self.__exposure is None:
        com = self.__comm()
        self.__exposure = com.getExposureTime()
        return self.__exposure

    #@Core.Debug.DEB_MEMBER_FUNCT
    def setLatTime(self,lat_time):
        self.__latency = lat_time
        com = self.__comm()
        com.setLatencyTime(lat_time)

    #@Core.Debug.DEB_MEMBER_FUNCT
    def getLatTime(self) :
#        if self.__latency is None:
        com = self.__comm()
        self.__latency = com.getLatencyTime()
        return self.__latency

    #@Core.Debug.DEB_MEMBER_FUNCT
    def setNbFrames(self,nb_frames) :
        self.__nb_frames = nb_frames

    #@Core.Debug.DEB_MEMBER_FUNCT
    def getNbFrames(self) :
        return self.__nb_frames

    #@Core.Debug.DEB_MEMBER_FUNCT
    def setNbHwFrames(self,nb_frames) :
        self.setNbFrames(nb_frames)

    #@Core.Debug.DEB_MEMBER_FUNCT
    def getNbHwFrames(self) :
        return self.getNbFrames()

    #@Core.Debug.DEB_MEMBER_FUNCT
    def getValidRanges(self) :
        det_info = self.__det_info()
        return Core.HwSyncCtrlObj.ValidRangesType(det_info.get_min_exposition_time(),
                                                  det_info.get_max_exposition_time(),
                                                  det_info.get_min_latency(),
                                                  det_info.get_max_latency())

    def prepareAcq(self) :
        com = self.__comm()
        com.setExposureTime( self.__exposure)
        com.setNbFrames(self.__nb_frames)
