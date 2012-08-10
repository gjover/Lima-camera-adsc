//###########################################################################
// This file is part of LImA, a Library for Image Acquisition
//
// Copyright (C) : 2009-2011
// European Synchrotron Radiation Facility
// BP 220, Grenoble 38043
// FRANCE
//
// This is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// (at your option) any later version.
//
// This software is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>.
//###########################################################################
#include "AdscInterface.h"

/*******************************************************************
 * \brief DetInfoCtrlObj constructor
 *******************************************************************/
DetInfoCtrlObj::DetInfoCtrlObj(Camera& adsc) :
		m_adsc(adsc)
{
	DEB_CONSTRUCTOR();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
DetInfoCtrlObj::~DetInfoCtrlObj()
{
	DEB_DESTRUCTOR();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void DetInfoCtrlObj::getMaxImageSize(Size& max_image_size)
{
	DEB_MEMBER_FUNCT();
	FrameDim fdim;
	m_adsc.getFrameDim(fdim);
	max_image_size = fdim.getSize();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void DetInfoCtrlObj::getDetectorImageSize(Size& det_image_size)
{
	DEB_MEMBER_FUNCT();
	m_adsc.getMaxImageSize(det_image_size);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void DetInfoCtrlObj::getDefImageType(ImageType& def_image_type)
{
	DEB_MEMBER_FUNCT();
	FrameDim fdim;
	m_adsc.getFrameDim(fdim);
	def_image_type = fdim.getImageType();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void DetInfoCtrlObj::setCurrImageType(ImageType curr_image_type)
{
	DEB_MEMBER_FUNCT();
	FrameDim fdim;
	m_adsc.getFrameDim(fdim);
	fdim.setImageType(curr_image_type);
	m_adsc.setFrameDim(fdim);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void DetInfoCtrlObj::getCurrImageType(ImageType& curr_image_type)
{
	DEB_MEMBER_FUNCT();
	FrameDim fdim;
	m_adsc.getFrameDim(fdim);
	curr_image_type = fdim.getImageType();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void DetInfoCtrlObj::getPixelSize(double& x_size,double &y_size)
{
	DEB_MEMBER_FUNCT();
	x_size = 0.1025880;
	y_size = 0.1025880;
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void DetInfoCtrlObj::getDetectorType(string& det_type)
{
	DEB_MEMBER_FUNCT();
	det_type = "Adsc";
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void DetInfoCtrlObj::getDetectorModel(string& det_model)
{
	DEB_MEMBER_FUNCT();
	det_model = "Q315r";
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void DetInfoCtrlObj::registerMaxImageSizeCallback(HwMaxImageSizeCallback& cb)
{
	DEB_MEMBER_FUNCT();
	m_mis_cb_gen.registerMaxImageSizeCallback(cb);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void DetInfoCtrlObj::unregisterMaxImageSizeCallback(HwMaxImageSizeCallback& cb)
{
	DEB_MEMBER_FUNCT();
	m_mis_cb_gen.unregisterMaxImageSizeCallback(cb);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void DetInfoCtrlObj::MaxImageSizeCallbackGen::setMaxImageSizeCallbackActive(bool cb_active)
{
}

/*******************************************************************
 * \brief BufferCtrlObj constructor
 *******************************************************************/

BufferCtrlObj::BufferCtrlObj(Camera& cam) :
		m_buffer_cb_mgr(m_buffer_alloc_mgr),
		m_buffer_ctrl_mgr(m_buffer_cb_mgr),
		m_cam(cam)
{
	DEB_CONSTRUCTOR();
	m_reader = new Reader(cam, *this);
	m_reader->go(2000);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
BufferCtrlObj::~BufferCtrlObj()
{
	DEB_DESTRUCTOR();
	m_reader->reset();
	m_reader->exit();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::setFrameDim(const FrameDim& frame_dim)
{
	DEB_MEMBER_FUNCT();
	m_buffer_ctrl_mgr.setFrameDim(frame_dim);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::getFrameDim(FrameDim& frame_dim)
{
	DEB_MEMBER_FUNCT();
	m_buffer_ctrl_mgr.getFrameDim(frame_dim);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::setNbBuffers(int nb_buffers)
{
	DEB_MEMBER_FUNCT();
	m_buffer_ctrl_mgr.setNbBuffers(nb_buffers);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::getNbBuffers(int& nb_buffers)
{
	DEB_MEMBER_FUNCT();
	m_buffer_ctrl_mgr.getNbBuffers(nb_buffers);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::setNbConcatFrames(int nb_concat_frames)
{
	DEB_MEMBER_FUNCT();
	m_buffer_ctrl_mgr.setNbConcatFrames(nb_concat_frames);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::getNbConcatFrames(int& nb_concat_frames)
{
	DEB_MEMBER_FUNCT();
	m_buffer_ctrl_mgr.getNbConcatFrames(nb_concat_frames);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::getMaxNbBuffers(int& max_nb_buffers)
{
	DEB_MEMBER_FUNCT();
	m_buffer_ctrl_mgr.getMaxNbBuffers(max_nb_buffers);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void *BufferCtrlObj::getBufferPtr(int buffer_nb, int concat_frame_nb)
{
	DEB_MEMBER_FUNCT();
	return m_buffer_ctrl_mgr.getBufferPtr(buffer_nb, concat_frame_nb);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void *BufferCtrlObj::getFramePtr(int acq_frame_nb)
{
	DEB_MEMBER_FUNCT();
	return m_buffer_ctrl_mgr.getFramePtr(acq_frame_nb);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::getStartTimestamp(Timestamp& start_ts)
{
	DEB_MEMBER_FUNCT();
	m_buffer_ctrl_mgr.getStartTimestamp(start_ts);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::getFrameInfo(int acq_frame_nb, HwFrameInfoType& info)
{
	DEB_MEMBER_FUNCT();
	m_buffer_ctrl_mgr.getFrameInfo(acq_frame_nb, info);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::registerFrameCallback(HwFrameCallback& frame_cb)
{
	DEB_MEMBER_FUNCT();
	m_buffer_ctrl_mgr.registerFrameCallback(frame_cb);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::unregisterFrameCallback(HwFrameCallback& frame_cb)
{
	DEB_MEMBER_FUNCT();
	m_buffer_ctrl_mgr.unregisterFrameCallback(frame_cb);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::start()
{
	DEB_MEMBER_FUNCT();

}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::stop()
{
	DEB_MEMBER_FUNCT();
	m_reader->start();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::reset()
{
	DEB_MEMBER_FUNCT();
	m_reader->reset();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
int BufferCtrlObj::getLastAcquiredFrame()
{
    return m_reader->getLastAcquiredFrame();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
bool BufferCtrlObj::isTimeoutSignaled()
{
    return m_reader->isTimeoutSignaled();
}


//-----------------------------------------------------
//
//-----------------------------------------------------
bool BufferCtrlObj::isRunning()
{
    return m_reader->isRunning();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::setTimeout(int TO)
{
    DEB_MEMBER_FUNCT();
    m_reader->setTimeout(TO);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::enableReader(void)
{
    DEB_MEMBER_FUNCT();
	m_reader->enableReader();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BufferCtrlObj::disableReader(void)
{
    DEB_MEMBER_FUNCT();
	m_reader->disableReader();
}

/*******************************************************************
 * \brief SyncCtrlObj constructor
 *******************************************************************/
SyncCtrlObj::SyncCtrlObj(Camera& adsc) :
		HwSyncCtrlObj(),
		m_adsc(adsc)
{
	DEB_CONSTRUCTOR();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
SyncCtrlObj::~SyncCtrlObj()
{
	DEB_DESTRUCTOR();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
bool SyncCtrlObj::checkTrigMode(TrigMode trig_mode)
{
	DEB_MEMBER_FUNCT();
	bool valid_mode = false;
	switch(trig_mode)
	{
		case IntTrig :
			valid_mode = true;
		break;
		default :
			valid_mode = false;
		break;
	}
	return valid_mode;
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void SyncCtrlObj::setTrigMode(TrigMode trig_mode)
{
	DEB_MEMBER_FUNCT();
	if(!checkTrigMode(trig_mode))
		THROW_HW_ERROR(InvalidValue) << "Invalid " << DEB_VAR1(trig_mode);
	//m_adsc.setTrigMode(trig_mode);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void SyncCtrlObj::getTrigMode(TrigMode& trig_mode)
{
	DEB_MEMBER_FUNCT();
	trig_mode = IntTrig;
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void SyncCtrlObj::setExpTime(double exp_time)
{
	DEB_MEMBER_FUNCT();
	m_adsc.setExpTime(exp_time);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void SyncCtrlObj::getExpTime(double& exp_time)
{
	DEB_MEMBER_FUNCT();
	m_adsc.getExpTime(exp_time);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void SyncCtrlObj::setLatTime(double lat_time)
{
	DEB_MEMBER_FUNCT();
	m_adsc.setLatTime(lat_time);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void SyncCtrlObj::getLatTime(double& lat_time)
{
	DEB_MEMBER_FUNCT();
	m_adsc.getLatTime(lat_time);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void SyncCtrlObj::setNbHwFrames(int nb_frames)
{
	DEB_MEMBER_FUNCT();
	m_adsc.setNbFrames(nb_frames);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void SyncCtrlObj::getNbHwFrames(int& nb_frames)
{
	DEB_MEMBER_FUNCT();
	m_adsc.getNbFrames(nb_frames);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void SyncCtrlObj::getValidRanges(ValidRangesType& valid_ranges)
{
	DEB_MEMBER_FUNCT();
	double min_time = 10e-9;
	double max_time = 1e6;
	valid_ranges.min_exp_time = min_time;
	valid_ranges.max_exp_time = max_time;
	valid_ranges.min_lat_time = min_time;
	valid_ranges.max_lat_time = max_time;
}

/*******************************************************************
 * \brief BinCtrlObj constructor
 *******************************************************************/
BinCtrlObj::BinCtrlObj(Camera& adsc) :
		m_adsc(adsc)
{
	DEB_CONSTRUCTOR();
}

//-----------------------------------------------------
BinCtrlObj::~BinCtrlObj()
{
	DEB_DESTRUCTOR();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BinCtrlObj::setBin(const Bin& bin)
{
	DEB_MEMBER_FUNCT();
	m_adsc.setBin(bin);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BinCtrlObj::getBin(Bin& bin)
{
	DEB_MEMBER_FUNCT();
	m_adsc.getBin(bin);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void BinCtrlObj::checkBin(Bin& bin)
{
	DEB_MEMBER_FUNCT();
	m_adsc.checkBin(bin);
}

/*******************************************************************
 * \brief Interface constructor
 *******************************************************************/
Interface::Interface(Camera& adsc) :
		m_adsc(adsc),
		m_det_info(adsc),
		m_buffer(adsc),
		m_sync(adsc),
		m_bin(adsc)
{
	DEB_CONSTRUCTOR();
	HwDetInfoCtrlObj *det_info = &m_det_info;
	m_cap_list.push_back(HwCap(det_info));
	
	HwSyncCtrlObj *sync = &m_sync;
	m_cap_list.push_back(HwCap(sync));
	
	HwBufferCtrlObj *buffer = &m_buffer;
	m_cap_list.push_back(HwCap(buffer));
	
	HwBinCtrlObj *bin = &m_bin;
	m_cap_list.push_back(HwCap(bin));
}

//-----------------------------------------------------
//
//-----------------------------------------------------
Interface::~Interface()
{
	DEB_DESTRUCTOR();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::getCapList(HwInterface::CapList &aReturnCapList) const
{
	DEB_MEMBER_FUNCT();
	aReturnCapList = m_cap_list;
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::reset(ResetLevel reset_level)
{
	DEB_MEMBER_FUNCT();
	m_adsc.reset();
	m_buffer.stop();
	Size image_size;
	m_det_info.getMaxImageSize(image_size);
	ImageType image_type;
	m_det_info.getDefImageType(image_type);
	FrameDim frame_dim(image_size, image_type);
	m_buffer.setFrameDim(frame_dim);
	
	m_buffer.setNbConcatFrames(1);
	m_buffer.setNbBuffers(1);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::prepareAcq()
{
	DEB_MEMBER_FUNCT();
	m_buffer.reset();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::startAcq()
{
	DEB_MEMBER_FUNCT();
	m_adsc.startAcq();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::stopAcq()
{
	DEB_MEMBER_FUNCT();
	m_adsc.stopAcq();
	m_buffer.stop();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::getStatus(StatusType& status)
{
	DEB_MEMBER_FUNCT();
	Camera::Status adsc_status = m_adsc.getStatus();
	switch(adsc_status)
	{
		case Camera::Ready :
		{
			status.det = DetIdle;
	        int nbHwFrames = 0;
	        m_sync.getNbHwFrames(nbHwFrames);
	        if( m_buffer.getLastAcquiredFrame() >= nbHwFrames)
	            status.acq = AcqReady;
	        else if(m_buffer.isTimeoutSignaled())
	        	status.acq = AcqFault;
	        else if (m_buffer.isRunning())
	            status.acq = AcqRunning;
	        else
	        	status.acq = AcqReady;
		}
		break;
		case Camera::Exposure :
			status.det = DetExposure;
			status.acq = AcqRunning;
		break;
		case Camera::Readout :
			status.det = DetReadout;
			status.acq = AcqRunning;
		break;
		case Camera::Latency :
			status.det = DetLatency;
			status.acq = AcqRunning;
		break;
	}
	status.det_mask = DetExposure | DetReadout | DetLatency;
}

//-----------------------------------------------------
//
//-----------------------------------------------------
int Interface::getNbHwAcquiredFrames()
{
	DEB_MEMBER_FUNCT();
    int acq_frames = m_buffer.getLastAcquiredFrame();
    return acq_frames;
}


//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::setStoredImageDark(bool value)
{
	DEB_MEMBER_FUNCT();
	m_adsc.setStoredImageDark(value);
		
}

//-----------------------------------------------------
//
//-----------------------------------------------------
bool Interface::getStoredImageDark(void)
{
	return m_adsc.getStoredImageDark();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::setImageKind(int image_kind)
{
	DEB_MEMBER_FUNCT();
	m_adsc.setImageKind(image_kind);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
int Interface::getImageKind(void)
{
	DEB_MEMBER_FUNCT();
	return 	m_adsc.getImageKind();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::setLastImage(int last_image)
{
	DEB_MEMBER_FUNCT();
	m_adsc.setImageKind(last_image);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
int Interface::getLastImage(void)
{
	DEB_MEMBER_FUNCT();
	return 	m_adsc.getImageKind();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::setFileName(const std::string& name)
{
	DEB_MEMBER_FUNCT();
	m_adsc.setFileName(name);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
const std::string& Interface::getFileName(void)
{
	DEB_MEMBER_FUNCT();
	return m_adsc.getFileName();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::setImagePath(const std::string& path)
{
	DEB_MEMBER_FUNCT();
	m_adsc.setImagePath(path);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
const std::string& Interface::getImagePath(void)
{
	DEB_MEMBER_FUNCT();
	return m_adsc.getImagePath();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::setHeaderParameters(const std::string& header)
{
	DEB_MEMBER_FUNCT();
	m_adsc.setHeaderParameters(header);
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::setTimeout(int TO)
{
    DEB_MEMBER_FUNCT();
    m_buffer.setTimeout(TO);
}
//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::enableReader(void)
{
	m_buffer.enableReader();
}

//-----------------------------------------------------
//
//-----------------------------------------------------
void Interface::disableReader(void)
{
	m_buffer.disableReader();
}
//-----------------------------------------------------
//
//-----------------------------------------------------
