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

import weakref
import threading
import numpy
import os
import time

from Lima import Core
#import EdfFile
#from PilatusError import PilatusError

def _invert_sort_file(a,b) :
    b1,ext = os.path.splitext(a)
    b2,ext = os.path.splitext(b)
    n1 = int(b1.split('_')[-1])
    n2 = int(b2.split('_')[-1])
    return n2 - n1

class _ImageReader(threading.Thread) :
    Core.DEB_CLASS(Core.DebModCamera,"_ImageReader")
    """Read images from the ADSC Buffer directory and loads the frame info"""

    def __init__(self,buffer_ctrl,comm_object) :
        threading.Thread.__init__(self)

        self.__cond = threading.Condition()
        self.__continue = True
        self.__buffer_ctrl = weakref.ref(buffer_ctrl)
        self.__com = weakref.ref(comm_object)

        self.__waitFlag = True
        #self.__numberOfNewFile = 0
        self.__lastImageRead = -1
        self.__readError = False
        
    @Core.DEB_MEMBER_FUNCT
    def is_read_error(self) :
        with self.__cond:
            return self.__readError
        
    @Core.DEB_MEMBER_FUNCT
    def reset(self) :
        with self.__cond:
            self.__waitFlag = True
            #self.__numberOfNewFile = 0
            self.__lastImageRead = -1
            self.__readError = False
            
            buffer_ctrl = self.__buffer_ctrl()
            #Remove all images in the tmp buffer
            for filename in os.listdir( self.__com().getFilePath()) :
                base,ext = os.path.splitext(filename)
                if ext.lower() == self.__com().getFileExtension() :
                    try:
                        os.unlink(os.path.join(self.__com().getFilePath(),filename))
                    except OSError:
                        import traceback
                        traceback.print_exc()
                        break

    @Core.DEB_MEMBER_FUNCT
    def start_read(self) :
        with self.__cond:
            print "###ImgReader: Send start command"
            self.__waitFlag = False
            self.__cond.notify()

    @Core.DEB_MEMBER_FUNCT
    def stop_read(self) :
        with self.__cond:
            print "###ImgReader: Send stop command"
            self.__waitFlag = True
            
    @Core.DEB_MEMBER_FUNCT
    def quit(self) :
        with self.__cond:
            print "###ImgReader: Send quit command"
            self.__waitFlag = False
            self.__continue = False
            self.__cond.notify()
        self.join()

    @Core.DEB_MEMBER_FUNCT
    def getLastAcquiredFrame(self) :
        with self.__cond:
            return self.__lastImageRead
        
    @Core.DEB_MEMBER_FUNCT
    def run(self) :
        lastDirectoryTime = None

	#if not self.__dirFd: return #@todo should throw an execption

        with self.__cond:
            #print " #1 "*100
            while(self.__continue) :
                #newDirectoryTime = os.fstat(self.__dirFd).st_mtime
                newDirectoryTime = os.stat(self.__com().getFilePath()).st_mtime
                
                #print " #2 "*100
                print "###ImgReader: waiting",self.__waitFlag
                #print "Last directory time:",lastDirectoryTime
                while(self.__waitFlag or
                      (self.__continue and lastDirectoryTime == newDirectoryTime)):
                    self.__cond.wait(1)
#                     print "New directory time:",newDirectoryTime
#                     print "Wait?",self.__waitFlag
                    #newDirectoryTime = os.fstat(self.__dirFd).st_mtime
                    newDirectoryTime = os.stat(self.__com().getFilePath()).st_mtime
                #print " #3 "*100
                print "###ImgReader: working"
                while(self.__continue and not self.__waitFlag) :
                    nextFrameId = self.__lastImageRead + 1
                    self.__cond.release()
                    #print " #4 "*100
                    try:
                        nextFullPath = os.path.join(self.__com().getFilePath(),
                                                    '%s%.5d%s' % (self.__com().getFileBase(),nextFrameId,
                                                                  self.__com().getFileExtension()))
                    except:
                        #print " #5 "*100
                        self.__cond.acquire()
                        raise

                    if os.access(nextFullPath,os.R_OK) :
                        #print " #6 "*100
                        try:
                            # f = EdfFile.EdfFile(nextFullPath)
                            # data = f.GetData(0)

                            # Whait for the file to be written
                            while os.stat(nextFullPath).st_size != 512 + 2048*2048*2 :
                                print "###ImgReader: Waiting for file %s to be ready" % nextFullPath
                                time.sleep(0.1);
                            
                            f = open(nextFullPath,'rb')
                            f.seek(0x200)
                            s = f.read(2048*2048*2)
                            d = numpy.fromstring(s, numpy.uint16)
                            data = d.reshape(2048, 2048)
                        except Exception, e:
                            print "###ImgReader: Exception %s" % e
                            self.__cond.acquire()
                            raise Exception, e
                            break
                        else:
                            print "###ImgReader: Reading file",nextFullPath
                            #print " #8 "*100
                            try:
                                buffer_ctrl = self.__buffer_ctrl()                              
                                continueFlag = True
                                if buffer_ctrl._cbk:
                                    hw_frame_info = Core.HwFrameInfoType(nextFrameId,data,Core.Timestamp(),
                                                                         0,Core.HwFrameInfoType.Transfer)
                                    #print hw_frame_info
                                    continueFlag = buffer_ctrl._cbk.newFrameReady(hw_frame_info)
                                    
                                del data
                                del f
                                #remove old image from buffer (tmp_fs)
                                idImage2remove = nextFrameId - buffer_ctrl.getNbBuffers()
                                if idImage2remove >= 0 :
                                    fullImagePath2remove = os.path.join(self.__com().getFilePath(),
                                                    '%s%.5d%s' % (self.__com().getFileBase(),idImage2remove,
                                                                  self.__com().getFileExtension()))
                                    os.unlink(fullImagePath2remove)                                    
                            except Exception, e:
                                print "###ImgReader: Exception %s ." % e
                                #print " #9 "*100
                                self.__cond.acquire()
                                raise Exception, e

                            self.__cond.acquire()
                            self.__lastImageRead = nextFrameId
                            self.__waitFlag = not continueFlag
                    else:               # We didn't managed to access the file
                        #print " #10 "*100
                        print "###ImgReader: File",nextFullPath,"not found"
                        try:
                        
                            ErrorFlag = False
                            lastDirectoryTime = newDirectoryTime
                            #Get all images from directory
                            files = [x for x in os.listdir(self.__com().getFilePath() ) if os.path.splitext(x)[-1] == '.edf']
                            if files:
                                files.sort(_invert_sort_file)
                                lastImageName,_ = os.path.splitext(files[0])
                                lastImageId = int(lastImageName.split('_')[-1])
                                #We're probably losing some frames
                                if lastImageId - nextFrameId > 10 :
                                    ErrorFlag = True
                                    deb.Error('Missing frame %d, Acquisition is in Fault stat' % nextFrameId) 
                                #buffer_ctrl = self.__buffer_ctrl()
			    	com = self.__com()
			    	if com:
                                        com.stop_acquisition()	
                        except Exception, e:
                            print "###ImgReader: Exception %s .." % e
                            #print " #11 "*100
                            self.__cond.acquire()
                            raise Exception, e

                        self.__cond.acquire()
                        if ErrorFlag:
                            #print " #12 "*100
                            self.__waitFlag = True
                            self.__readError = True
                        break
                        

                
                
            
class BufferCtrlObj(Core.HwBufferCtrlObj):
	Core.DEB_CLASS(Core.DebModCamera,"BufferCtrlObj")

        def __init__(self,comm_object,det_info) :
            Core.HwBufferCtrlObj.__init__(self)
            self.__com = weakref.ref(comm_object)
            self.__det_info = weakref.ref(det_info)
            self._cbk = None
            self.__nb_buffer = 1
#             MaxImgSize = self.__det_info().getDetectorImageSize()
#             Height = MaxImgSize.getHeight()
#             Width  = MaxImgSize.getWidth()
#             self.__tmpfs_size = 2 * Height * Width * 2
            statvfs = os.statvfs(self.__com().getFilePath())
            self.__tmpfs_size = statvfs.f_bfree * statvfs.f_bsize

            # All definitions must be done before the ImageReader starts
            self.__imageReader = _ImageReader(self,comm_object)
            self.__imageReader.start()


        def __del__(self) :
            self.__imageReader.quit()

        @Core.DEB_MEMBER_FUNCT
        def quit(self) :
            self.__imageReader.quit()

        @Core.DEB_MEMBER_FUNCT
        def start(self) :
            print "###BufferCtrlObj: MaxNbBuffers =",self.getMaxNbBuffers()
            self.__imageReader.start_read()

        @Core.DEB_MEMBER_FUNCT
        def stop(self) :
            self.__imageReader.stop_read()

        def is_error(self) :
            return self.__imageReader.is_read_error()
        
        @Core.DEB_MEMBER_FUNCT
	def setFrameDim(self,frame_dim) :
            pass
            
        @Core.DEB_MEMBER_FUNCT
        def getFrameDim(self) :
            det_info = self.__det_info()
            return Core.FrameDim(det_info.getDetectorImageSize(),
                                 det_info.getDefImageType())
        
        @Core.DEB_MEMBER_FUNCT
        def setNbBuffers(self,nb_buffers) :
            self.__nb_buffer = nb_buffers
            
        @Core.DEB_MEMBER_FUNCT
        def getNbBuffers(self) :
            return self.__nb_buffer

        @Core.DEB_MEMBER_FUNCT
        def setNbConcatFrames(self,nb_concat_frames) :
            if nb_concat_frames != 1:
                raise Core.Exception(Core.Hardware,Core.NotSupported)

        @Core.DEB_MEMBER_FUNCT
        def getNbConcatFrames(self) :
            return 1

#         @Core.DEB_MEMBER_FUNCT
#         def setNbAccFrames(self,nb_acc_frames) :
#             com = self.__com()
#             com.set_nb_exposure_per_frame(nb_acc_frames)
            
#         @Core.DEB_MEMBER_FUNCT
# 	def getNbAccFrames(self) :
#             com = self.__com()
#             return com.nb_exposure_per_frame()

        @Core.DEB_MEMBER_FUNCT
        def setTmpfsSize(self, new_size):
            det_info = self.__det_info()
            imageFormat = det_info.getMaxImageSize()
            imageSize = imageFormat.getWidth() * imageFormat.getHeight() * 2 # 2 == image 16bits
            if new_size * 0.8 < imageSize:  # 80% occupancy
                raise Core.Exception(Core.Hardware,Core.InvalidValue)
            self.__tmpfs_size = new_size
            
        @Core.DEB_MEMBER_FUNCT
        def getMaxNbBuffers(self) :
#            com = self.__com()
            det_info = self.__det_info()
            imageFormat = det_info.getMaxImageSize()
            imageSize = imageFormat.getWidth() * imageFormat.getHeight() * 2 # 2 == image 16bits
            return self.__tmpfs_size / imageSize * 0.8 # 80% occupancy

        @Core.DEB_MEMBER_FUNCT
        def getBufferPtr(self,buffer_nb,concat_frame_nb = 0) :
            pass
        
        @Core.DEB_MEMBER_FUNCT
        def getFramePtr(self,acq_frame_nb) :
            pass

        @Core.DEB_MEMBER_FUNCT
        def getStartTimestamp(self,start_ts) :
            pass
        
        @Core.DEB_MEMBER_FUNCT
        def getFrameInfo(self,acq_frame_nb) :
            deb.Param('acq_frame_nb: %d' % acq_frame_nb)
            com = self.__com()
            fullPath = os.path.join(com.getFilePath(),
                                    '%s%.5d%s' % (com.getFileBase(),acq_frame_nb,
                                                  com.getFileExtension()))
            deb.Trace('Try to read : %s' % fullPath)
            if os.access(fullPath,os.R_OK) :
                try:
                    # f = EdfFile.EdfFile(fullPath)
                    # data = f.GetData(0)
                    f = open(nextFullPath,'rb')
                    f.seek(0x200)
                    s = f.read(2048*2048*2)
                    d = numpy.fromstring(s, numpy.uint16)
                    data = d.reshape(2048, 2048)
                except:
                    pass
                else:
                    frInfo = Core.HwFrameInfoType(acq_frame_nb,data,Core.Timestamp(),
                                                0,Core.HwFrameInfoType.Transfer)
                    return frInfo

        @Core.DEB_MEMBER_FUNCT
        def registerFrameCallback(self,frame_cb) :
            self._cbk = frame_cb
            
        @Core.DEB_MEMBER_FUNCT
	def unregisterFrameCallback(self,frame_cb) :
            self._cbk = None


        @Core.DEB_MEMBER_FUNCT
        def getLastAcquiredFrame(self) :
            return self.__imageReader.getLastAcquiredFrame()
        
        def reset(self) :
            self.__imageReader.reset()
        
