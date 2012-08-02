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
from __future__ import with_statement

import socket
import threading
import select
import os
import time

from Lima import Core

from ctypes import *
from ADSC_par import *
from ADSC_conf import *

class Communication(threading.Thread):
    Core.DEB_CLASS(Core.DebModCameraCom, 'Communication')
    
    DTC_STATE_IDLE,\
        DTC_STATE_EXPOSING,\
        DTC_STATE_READING,\
        DTC_STATE_ERROR,\
        DTC_STATE_CONFIGDET,\
        DTC_STATE_RETRY,\
        DTC_STATE_TEMPCONTROL\
        =range(7)
    DTC_STATE = {DTC_STATE_IDLE:"IDLE",
                 DTC_STATE_EXPOSING:"EXPOSING",
                 DTC_STATE_READING:"READING",
                 DTC_STATE_ERROR:"ERROR",
                 DTC_STATE_CONFIGDET:"CONFIGDET",
                 DTC_STATE_RETRY:"RETRY",
                 DTC_STATE_TEMPCONTROL:"TEMPCONTROL"}	

    COM_NONE,COM_START,COM_STOP,COM_GETIMAGE,COM_SRESET,COM_HRESET=range(6)

    def __init__(self):
        threading.Thread.__init__(self)

        self.__cond = threading.Condition()
        self.__Command = self.COM_NONE
        self.__Run = True
        self.__DarksReady = False
        self.__Kind = 5
        self.__NbFrames = 0
        self.__FrameId = -1 
        self.__LastFrameId = -1
        self.__ExposureTime = 0
        self.__LatencyTime = 0
        self.__WaitTime = 0.05

#        self._FileName = './DefaultImage'
        self._file_path = '/ramdisk/adscbuffer/'
        self._file_base = 'adsc_img_'
        self._file_ext = '.img'
        self._dll = cdll.LoadLibrary("libadsc.so")
        self._Status = self._dll.CCDStatus
        self._Status.restype = c_char_p

        if not os.environ.has_key(   "CCD_DTHOSTNAME"):
            self._dll.CCDSetProperty("CCD_DTHOSTNAME",   ENV_DTHOSTNAME,1)
        if not os.environ.has_key(   "CCD_DTPORT"):
            self._dll.CCDSetProperty("CCD_DTPORT",       ENV_DTPORT,1)
        if not os.environ.has_key(   "CCD_DTSECPORT"):
            self._dll.CCDSetProperty("CCD_DTSECPORT",    ENV_DTSECPORT,1)
        if not os.environ.has_key(   "CCD_XFHOSTNAME"):
            self._dll.CCDSetProperty("CCD_XFHOSTNAME",   ENV_XFHOSTNAME,1)
        if not os.environ.has_key(   "CCD_XFPORT"):
            self._dll.CCDSetProperty("CCD_XFPORT",       ENV_XFPORT,1)
        if not os.environ.has_key(   "CCD_DC_LOCAL_LOG"):
            self._dll.CCDSetProperty("CCD_DC_LOCAL_LOG", ENV_DC_LOCAL_LOG,1)
        if not os.environ.has_key(   "CCD_DC_CONFIG"):
            self._dll.CCDSetProperty("CCD_DC_CONFIG",    ENV_DC_CONFIG,1)
        if not os.environ.has_key(   "CCD_N_CTRL"):
            self._dll.CCDSetProperty("CCD_N_CTRL",       ENV_N_CTRL,1)
        
        self._dll.CCDInitialize()
        
    def quit(self) :
        self.softReset()
        with self.__cond:
            print "###Communication: Send quit command"
            self.__Run = False
            self.__cond.notify()
        time.sleep(0.01)
        self.join()

    @Core.DEB_MEMBER_FUNCT
    def Configure(self) :
        self.__FrameId = -1 
        self.__LastFrameId = -1

        with self.__cond:
            self._dll.CCDSetHwPar(HWP_BIN,cast(        \
                    pointer(c_int(CONF_BIN)),POINTER(c_char)))
            self._dll.CCDSetHwPar(HWP_ADC,cast(        \
                    pointer(c_int(CONF_ADC)),POINTER(c_char)))
            self._dll.CCDSetHwPar(HWP_SAVE_RAW,cast(   \
                    pointer(c_int(CONF_SAVE_RAW)),POINTER(c_char)))
            self._dll.CCDSetHwPar(HWP_NO_XFORM,cast(   \
                    pointer(c_int(CONF_NO_XFORM)),POINTER(c_char)))
            self._dll.CCDSetHwPar(HWP_STORED_DARK,cast(\
                    pointer(c_int(CONF_STORED_DARK)),POINTER(c_char)))

#             self._dll.CCDSetHwPar(HWP_MULT_TRIGTYPE,cast(\
#                     pointer(c_int(CONF_STORED_DARK)),POINTER(c_char)))
#             self._dll.CCDSetHwPar(HWP_STORED_DARK,cast(\
#                     pointer(c_int(CONF_STORED_DARK)),POINTER(c_char)))
#             self._dll.CCDSetHwPar(HWP_STORED_DARK,cast(\
#                     pointer(c_int(CONF_STORED_DARK)),POINTER(c_char)))
#             self._dll.CCDSetHwPar(HWP_STORED_DARK,cast(\
#                     pointer(c_int(CONF_STORED_DARK)),POINTER(c_char)))

            self._dll.CCDSetFilePar(FLP_COMMENT,       \
                                        c_char_p(CONF_COMMENT))
            self._dll.CCDSetFilePar(FLP_BEAM_X,cast(     \
                    pointer(c_float(CONF_BEAM_X)),POINTER(c_char)))
            self._dll.CCDSetFilePar(FLP_BEAM_Y,cast(     \
                    pointer(c_float(CONF_BEAM_Y)),POINTER(c_char)))
            self._dll.CCDSetFilePar(FLP_WAVELENGTH,cast( \
                    pointer(c_float(CONF_WAVELENGTH)),POINTER(c_char)))
            self._dll.CCDSetFilePar(FLP_DISTANCE,cast(   \
                    pointer(c_float(CONF_DISTANCE)),POINTER(c_char)))
            self._dll.CCDSetFilePar(FLP_AXIS,cast(       \
                    pointer(c_int(  CONF_AXIS)),POINTER(c_char)))
            self._dll.CCDSetFilePar(FLP_PHI,cast(        \
                    pointer(c_float(CONF_PHI)),POINTER(c_char)))
            self._dll.CCDSetFilePar(FLP_TWOTHETA,cast(   \
                    pointer(c_float(CONF_TWOTHETA)),POINTER(c_char)))
            self._dll.CCDSetFilePar(FLP_COMPRESS,cast(   \
                    pointer(c_int(  CONF_COMPRESS)),POINTER(c_char)))
            self._dll.CCDSetFilePar(FLP_OSC_RANGE,cast(  \
                    pointer(c_float(CONF_OSC_RANGE)),POINTER(c_char)))

    @Core.DEB_MEMBER_FUNCT
    def getState(self) :
        with self.__cond:
            return self._dll.CCDState()

    @Core.DEB_MEMBER_FUNCT
    def getStatus(self) :
        with self.__cond:
            return self._Status()

    def getCurrentCommand(self) :
        with self.__cond:
            return self.__Command

    @Core.DEB_MEMBER_FUNCT
    def getExposureTime(self) :
        with self.__cond:
            ftmp = c_float()
            self._dll.CCDGetFilePar(FLP_TIME,pointer(ftmp))
            self.__ExposureTime = ftmp.value
            return self.__ExposureTime

    @Core.DEB_MEMBER_FUNCT
    def setExposureTime(self,Time) :
        with self.__cond:
            if Time == self.__ExposureTime :
                return
            self.__ExposureTime = Time
            self._dll.CCDSetFilePar(FLP_TIME,cast(\
                    pointer(c_float(self.__ExposureTime)),POINTER(c_char)))
            
    @Core.DEB_MEMBER_FUNCT
    def getNbFrames(self) :
        with self.__cond:
            return self.__NbFrames

    @Core.DEB_MEMBER_FUNCT
    def setNbFrames(self,NF) :
        with self.__cond:
            self.__NbFrames = NF

    def getFilePath(self) :
        return self._file_path
    
    def getFileBase(self) :
        return self._file_base
    
    def getFileExtension(self) :
        return self._file_ext
    
    def setFilePath(self,path) :
        print "###Communication: New file path=" + path 
        self._file_path = path
        
    def setFileBase(self,base) :
        print "###Communication: New file base=" + base 
        self._file_base = base
                
    def setFileExtension(self,ext) :
        print "###Communication: New file extension=" + ext 
        self._file_ext  = ext

    @Core.DEB_MEMBER_FUNCT
    def takeDarks(self,Texp) :
        with self.__cond:
            print "###Communication: Send takeDarks command"
            self.__Kind = 0
            self.__LastFrameId = -1
            self.__FrameId = -1
            self.setExposureTime(Texp)
            self.__Command = self.COM_START    
            self.__cond.notify()
        time.sleep(0.01)

    @Core.DEB_MEMBER_FUNCT
    def darksReady(self) :
        return self.__DarksReady

    @Core.DEB_MEMBER_FUNCT
    def startAcquisition(self) :
        with self.__cond:
            print "###Communication: Send startAcquisition command"
            self.__Kind = 5
            self.__Command = self.COM_START
            self.__cond.notify()
        time.sleep(0.01)

    @Core.DEB_MEMBER_FUNCT
    def stopAcquisition(self) :
        with self.__cond:
            print "###Communication: Send stopAcquisition command"
            self.__Command = self.COM_STOP
            self.__cond.notify()
        time.sleep(0.01)

    @Core.DEB_MEMBER_FUNCT
    def getImage(self) :
        with self.__cond:
            print "###Communication: Send getImage command"
            self.__Command = self.COM_GETIMAGE
            self.__cond.notify()
        time.sleep(0.01)

    @Core.DEB_MEMBER_FUNCT
    def softReset(self) :
        with self.__cond:
            print "###Communication: Send softReset command"
            self.__Command = self.COM_SRESET
            self.__cond.notify()
        time.sleep(0.01)

    @Core.DEB_MEMBER_FUNCT
    def hardReset(self) :
        with self.__cond:
            print "###Communication: Send hardReset command"
            self.__Command = self.COM_HRESET
            self.__cond.notify()
        time.sleep(0.01)

    def run(self) :
        with self.__cond:
            while self.__Run :

                # Test if any error
                if  self._dll.CCDState() == self.DTC_STATE_ERROR:
                    raise Exception,'Communication: Unknown Error'

                

                # Start Command
                if self.__Command == self.COM_START : 
                    print "###Communication: Start Command"                    
                    ## Setup acquisition
                    while self.__FrameId - self.__LastFrameId < self.__NbFrames or self.__Kind<5:
                        nextFullPath = os.path.join(self._file_path,
                                                    '%s%.5d%s' % (self._file_base,self.__FrameId+1,
                                                                  self._file_ext))
                        self.__cond.release()
                        self._dll.CCDSetFilePar(FLP_FILENAME,c_char_p(nextFullPath))
                        self._dll.CCDSetFilePar(FLP_KIND ,cast(\
                                pointer(c_int(self.__Kind)),POINTER(c_char)))      
                        if  self._dll.CCDState() == self.DTC_STATE_ERROR:
                            self.__cond.acquire()
                            raise Exception,'Communication: Error returned at pre-acquisition'

                        ## Start acquisition
                        while self._dll.CCDState() != self.DTC_STATE_IDLE:
                            time.sleep(self.__WaitTime)
                            #self.__cond.wait( self.__WaitTime)
                        print "###Communication: Start Img",nextFullPath,self.__Kind
                        self._dll.CCDStartExposure()
                        if  self._dll.CCDState() == self.DTC_STATE_ERROR:
                            self.__cond.acquire()
                            raise Exception,'Communication: Error returned from CCDStartExposure()'

                        ## Exposure time
                        time.sleep(self.__ExposureTime)

                        ## Stop acquisition
                        while self._dll.CCDState() != self.DTC_STATE_EXPOSING:
                            time.sleep(self.__WaitTime)
                            #self.__cond.wait(self.__WaitTime)
                        print "###Communication: Stop Img",nextFullPath,self.__Kind
                        self._dll.CCDStopExposure()
                        if  self._dll.CCDState() == self.DTC_STATE_ERROR:
                            self.__cond.acquire()
                            raise Exception,'Communication: Error returned from CCDStopExposure()'
                        
                        if self.__Kind==0:
                            self.__Kind = 1
                            self.__cond.acquire()
                            continue
                        elif self.__Kind==1:
                            self.__DarksReady = True
                            self.__Kind = 5     
                            self.__cond.acquire()
                            break

                        ## Get Image
                        self._dll.CCDSetFilePar(FLP_LASTIMAGE,cast(\
                                pointer(c_int(1)),POINTER(c_char)))
                        if  self._dll.CCDState() == self.DTC_STATE_ERROR:
                            self.__cond.acquire()
                            raise Exception,'Communication: Error returned at pot-acquisition'

                        while  self._dll.CCDState() != self.DTC_STATE_IDLE:
                            time.sleep(self.__WaitTime)
                            #self.__cond.wait(self.__WaitTime)                    
                        print "###Communication: Get Img",nextFullPath,self.__Kind
                        self._dll.CCDGetImage()
                        if  self._dll.CCDState() == self.DTC_STATE_ERROR:
                            self.__cond.acquire()
                            raise Exception,'Communication: Error returned from CCDGetImage()'

                        ## Latency time
                        time.sleep(self.__LatencyTime)

                        self.__FrameId += 1
                        self.__cond.acquire()

                    self.__LastFrameId = self.__FrameId
                    if self.__Command == self.COM_START :
                        self.__Command = self.COM_NONE

                # Stop Command
                elif self.__Command == self.COM_STOP :
                    print "###Communication: Stop Command"
                    self._dll.CCDAbort() 
                    if  self._dll.CCDState() == self.DTC_STATE_ERROR:
                        raise Exception,'Communication: Error returned from CCDReset()'
                    if self.__Command == self.COM_STOP :
                        self.__Command = self.COM_NONE

                # Soft Reset Command
                elif self.__Command == self.COM_SRESET :
                    print "###Communication: SReset Command"
                    self._dll.CCDReset()
                    if  self._dll.CCDState() == self.DTC_STATE_ERROR:
                        raise Exception,'Communication: Error returned from CCDReset()'
                    if self.__Command == self.COM_SRESET :
                        self.__Command = self.COM_NONE

                # Hardware Reset Command
                elif self.__Command == self.COM_HRESET :
                    print "###Communication: HReset Command"
                    self._dll.CCD_HWReset()
                    if  self._dll.CCDState() == self.DTC_STATE_ERROR:
                        raise Exception,'Communication: Error returned from CCD_HWReset()'
                    if self.__Command == self.COM_HRESET :
                        self.__Command = self.COM_NONE

                # By default wait for a command
                else :
                    print "###Communication: No Command"
                    while self.__Command == self.COM_NONE and \
                            self.__Run == True:
                        self.__cond.wait()

