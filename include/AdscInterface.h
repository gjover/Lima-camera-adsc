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
#ifndef ADSCINTERFACE_H
#define ADSCINTERFACE_H

#include "AdscCompatibility.h"
#include "HwInterface.h"
#include "AdscCamera.h"
#include "AdscReader.h"

using namespace lima;
using namespace lima::Adsc;
using namespace std;

namespace lima
{
namespace Adsc
{

/*******************************************************************
 * \class DetInfoCtrlObj
 * \brief Control object providing simulator detector info interface
 *******************************************************************/
class DetInfoCtrlObj : public HwDetInfoCtrlObj
{
	DEB_CLASS_NAMESPC(DebModCamera, "DetInfoCtrlObj", "Adsc");
public:
	DetInfoCtrlObj(Camera& adsc);
	virtual ~DetInfoCtrlObj();

	virtual void getMaxImageSize(Size& max_image_size);
	virtual void getDetectorImageSize(Size& det_image_size);

	virtual void getDefImageType(ImageType& def_image_type);
	virtual void getCurrImageType(ImageType& curr_image_type);
	virtual void setCurrImageType(ImageType curr_image_type);

	virtual void getPixelSize(double& x_size,double &y_size);
	virtual void getDetectorType(string& det_type);
	virtual void getDetectorModel(string& det_model);

	virtual void registerMaxImageSizeCallback(HwMaxImageSizeCallback& cb);
	virtual void unregisterMaxImageSizeCallback(HwMaxImageSizeCallback& cb);

private:
	class MaxImageSizeCallbackGen : public HwMaxImageSizeCallbackGen
	{
	protected:
		virtual void setMaxImageSizeCallbackActive(bool cb_active);
	};

	Camera& m_adsc;
	MaxImageSizeCallbackGen m_mis_cb_gen;
};

//*******************************************************************
// \class BufferCtrlObj
// \brief Control object providing Marccd buffering interface
//*******************************************************************
class BufferCtrlObj : public HwBufferCtrlObj
{
	DEB_CLASS_NAMESPC(DebModCamera, "BufferCtrlObj", "Marccd");

public:
	BufferCtrlObj(Camera& simu);
	virtual ~BufferCtrlObj();

	virtual void setFrameDim(const FrameDim& frame_dim);
	virtual void getFrameDim(FrameDim& frame_dim);

	virtual void setNbBuffers(int nb_buffers);
	virtual void getNbBuffers(int& nb_buffers);

	virtual void setNbConcatFrames(int nb_concat_frames);
	virtual void getNbConcatFrames(int& nb_concat_frames);

	virtual void getMaxNbBuffers(int& max_nb_buffers);

	virtual void *getBufferPtr(int buffer_nb, int concat_frame_nb = 0);
	virtual void *getFramePtr(int acq_frame_nb);

	virtual void getStartTimestamp(Timestamp& start_ts);
	virtual void getFrameInfo(int acq_frame_nb, HwFrameInfoType& info);

	// -- Buffer control object
	BufferCtrlMgr& getBufferMgr()
	{
		return m_buffer_ctrl_mgr;
	}
	;
	StdBufferCbMgr& getBufferCbMgr()
	{
		return m_buffer_cb_mgr;
	}
	;

	virtual void registerFrameCallback(HwFrameCallback& frame_cb);
	virtual void unregisterFrameCallback(HwFrameCallback& frame_cb);

	//Reader stuff
	void start();
	void stop();
	void reset();
	int  getLastAcquiredFrame(void);
	bool isTimeoutSignaled(void);
	bool isRunning(void);
	void setTimeout(int TO);
	void enableReader(void);
	void disableReader(void);
private:
	SoftBufferAllocMgr m_buffer_alloc_mgr;
	StdBufferCbMgr m_buffer_cb_mgr;
	BufferCtrlMgr m_buffer_ctrl_mgr;
	Camera& m_cam;
	Reader* m_reader;
};

/*******************************************************************
 * \class SyncCtrlObj
 * \brief Control object providing simulator synchronization interface
 *******************************************************************/
class SyncCtrlObj : public HwSyncCtrlObj
{
	DEB_CLASS_NAMESPC(DebModCamera, "SyncCtrlObj", "Adsc");
public:
	SyncCtrlObj(Camera& adsc);
	virtual ~SyncCtrlObj();

	virtual bool checkTrigMode(TrigMode trig_mode);
	virtual void setTrigMode(TrigMode trig_mode);
	virtual void getTrigMode(TrigMode& trig_mode);

	virtual void setExpTime(double exp_time);
	virtual void getExpTime(double& exp_time);

	virtual void setLatTime(double lat_time);
	virtual void getLatTime(double& lat_time);

	virtual void setNbHwFrames(int nb_frames);
	virtual void getNbHwFrames(int& nb_frames);

	virtual void getValidRanges(ValidRangesType& valid_ranges);

private:
	Camera& m_adsc;
};

/*******************************************************************
 * \class adscBinCtrlObj
 * \brief Control object providing simulator binning interface
 *******************************************************************/
class BinCtrlObj : public HwBinCtrlObj
{
	DEB_CLASS_NAMESPC(DebModCamera, "BinCtrlObj", "Adsc");
public:
	BinCtrlObj(Camera& adsc);
	virtual ~BinCtrlObj();

	virtual void setBin(const Bin& bin);
	virtual void getBin(Bin& bin);
	virtual void checkBin(Bin& bin);

private:
	Camera& m_adsc;
};

/*******************************************************************
 * \class Interface
 * \brief Adsc interface
 *******************************************************************/
class Interface : public HwInterface
{
	DEB_CLASS_NAMESPC(DebModCamera, "Interface", "Adsc");
public:
	Interface(Camera& adsc);
	virtual ~Interface();

	virtual void 	getCapList(CapList&) const;

	virtual void 	reset(ResetLevel reset_level);
	virtual void 	prepareAcq();
	virtual void 	startAcq();
	virtual void 	stopAcq();
	virtual void 	getStatus(StatusType& status);
	virtual int 	getNbHwAcquiredFrames();
    //! Set the header parameters
	void 			setHeaderParameters(const string& header);
    //! Say to ADSC to store or not an image dark
	void			setStoredImageDark(bool value);
    //! Get the StoredImageDark flag
	bool			getStoredImageDark(void);
    //! Set the kind of image to be acquired (1-> ??; 2-> ?? ... 5-> ??)
	void    		setImageKind(int image_kind);
    //! Getter of the ImageKind
	int	    		getImageKind(void);	
    //! Set the Last image (0-> ??; 1-> ??)
	void    		setLastImage(int last_image);
    //! Getter of the last image
	int	    		getLastImage(void);		
    //! Set the file name to be saved
	void 			setFileName(const string& name);
    //! Get the file name
	const string& 	getFileName(void);
    //! Set the image path
	void 			setImagePath(const string& path);
    //! Get the image path
	const string& 	getImagePath(void);
    //! set the timeout
	void 			setTimeout(int TO);
    //! enable the image file reading (the image will be in lima)
	void 			enableReader(void);
    //! disable the image file reading (the image will NOT be in lima)
	void 			disableReader(void);

private:
	Camera& 		m_adsc;
	CapList 		m_cap_list;
	DetInfoCtrlObj 	m_det_info;
	BufferCtrlObj 	m_buffer;
	SyncCtrlObj 	m_sync;
	BinCtrlObj 		m_bin;
};

} // namespace Adsc
} // namespace lima

#endif // ADSCINTERFACE_H
