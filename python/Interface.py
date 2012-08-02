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
import time
from Lima import Core

from DetInfoCtrlObj import DetInfoCtrlObj
from SyncCtrlObj import SyncCtrlObj
from BufferCtrlObj import BufferCtrlObj
from Communication import Communication

class Interface(Core.HwInterface) :
    Core.DEB_CLASS(Core.DebModCamera, "Interface")

    def __init__(self) :
	Core.HwInterface.__init__(self)

        self.__comm = Communication()
        self.__comm.start()
        self.__detInfo = DetInfoCtrlObj()
        self.__detInfo.init()
        self.__buffer = BufferCtrlObj(self.__comm,self.__detInfo)
        self.__syncObj = SyncCtrlObj(self.__comm,self.__detInfo)
	self.__acquisition_start_flag = False
        self.__kind = 5

    def __del__(self) :
        self.__comm.quit()
        self.__buffer.quit()

    def quit(self) :
        self.__comm.quit()
        self.__buffer.quit()
        
    @Core.DEB_MEMBER_FUNCT
    def getCapList(self) :
        return [Core.HwCap(x) for x in [self.__detInfo,self.__syncObj,
                                        self.__buffer]]

    @Core.DEB_MEMBER_FUNCT
    def reset(self,reset_level):
        if reset_level == self.HardReset:
            self.__comm.hardReset()

        self.__buffer.reset()
        self.__comm.softReset()

    @Core.DEB_MEMBER_FUNCT
    def takeDarks(self,Texp):
        self.__comm.takeDarks(Texp)

    @Core.DEB_MEMBER_FUNCT
    def prepareAcq(self):
        self.__buffer.reset()
        self.__syncObj.prepareAcq()
        self.__comm.Configure()
        self.__acquisition_start_flag = False

    @Core.DEB_MEMBER_FUNCT
    def startAcq(self) :
        self.__acquisition_start_flag = True
        self.__buffer.start()
        self.__comm.startAcquisition()

    @Core.DEB_MEMBER_FUNCT
    def stopAcq(self) :
        self.__comm.stopAcquisition()
        self.__buffer.stop()
        self.__acquisition_start_flag = False
        
    @Core.DEB_MEMBER_FUNCT
    def getStatus(self) :
        ComState = self.__comm.getState()
        status = Core.HwInterface.StatusType()

        if self.__buffer.is_error() :
            status.det = Core.DetFault
            status.acq = Core.AcqFault
            deb.Error("Buffer is in Fault state")
        elif ComState == Communication.DTC_STATE_ERROR:
            status.det = Core.DetFault
            status.acq = Core.AcqFault
            deb.Error("Detector is in Fault state")
        elif ComState == Communication.DTC_STATE_CONFIGDET or not self.__comm.darksReady()  :
            status.det = Core.DetFault
            status.acq = Core.AcqConfig
            deb.Warning("Waiting for configuration")
        else:
            if ComState != Communication.DTC_STATE_IDLE:
                status.det = Core.DetFault
                status.acq = Core.AcqRunning
            else:
                status.det = Core.DetIdle
                lastAcquiredFrame = self.__buffer.getLastAcquiredFrame()
                requestNbFrame = self.__syncObj.getNbFrames()
                print "Frames set-rdy:",requestNbFrame,lastAcquiredFrame+1
                if (not self.__acquisition_start_flag) or \
                        (lastAcquiredFrame >= 0 and \
                             lastAcquiredFrame == (requestNbFrame - 1)):
                    status.acq = Core.AcqReady
                else:
                    status.acq = Core.AcqRunning
            
        status.det_mask = (Core.DetExposure|Core.DetFault)
        return status
    
    @Core.DEB_MEMBER_FUNCT
    def getNbAcquiredFrames(self) :
        return self.__buffer.getLastAcquiredFrame() + 1
    
    @Core.DEB_MEMBER_FUNCT
    def getNbHwAcquiredFrames(self):
        return self.getNbAcquiredFrames()

    #get lower communication
    def communication(self) :
        return self.__comm

    #get lower buffer
    def buffer(self) :
        return self.__buffer

    def setFilePath(self,path) :
        self.__comm.setFilePath(path)

    def setFileBase(self,base) :
        self.__comm.setFileBase(base)

    def setFileExtension(self,ext) :
        self.__comm.setFileExtension(ext)

