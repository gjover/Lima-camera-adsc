#include <yat/threading/Mutex.h>
#include <sstream>
#include <iostream>
#include <string>
#include <math.h>
#include "Debug.h"
#include "Data.h"
#include "AdscReader.h"
#include "AdscInterface.h"

//---------------------------
//- Ctor
//---------------------------
Reader::Reader(Camera& cam, HwBufferCtrlObj& buffer_ctrl)
		: m_cam(cam), m_buffer(buffer_ctrl)
{
	DEB_CONSTRUCTOR();
	try
	{
		m_full_file_name = "";
		m_is_reset = false;
		m_is_reader_open_image_file = true;
		m_is_running = false;
		m_is_timeout_signaled = false;
		m_image_number = 0;
		enable_timeout_msg(false);
		enable_periodic_msg(false);
		set_periodic_msg_period(TASK_PERIODIC_MS);
		m_cam.getMaxImageSize(m_image_size);
	}
	catch (Exception &e)
	{
		// Error handling
		DEB_ERROR() << e.getErrMsg();
		throw LIMA_HW_EXC(Error, e.getErrMsg());
	}
}

//---------------------------
//- Dtor
//---------------------------
Reader::~Reader()
{
	DEB_DESTRUCTOR();
	try
	{
		//nop
	}
	catch (Exception &e)
	{
		// Error handling
		DEB_ERROR() << e.getErrMsg();
		throw LIMA_HW_EXC(Error, e.getErrMsg());
	}
}

//-----------------------------------------------------
// fix timeout value
//-----------------------------------------------------
void Reader::setTimeout(int timeout)
{
    DEB_MEMBER_FUNCT();
    DEB_PARAM() << DEB_VAR1(timeout);
	yat::MutexLock scoped_lock(m_lock);
	m_timeout.set_value(timeout);
}

//-----------------------------------------------------
// enable reading an image file on disk
//-----------------------------------------------------
void Reader::enableReader(void)
{
    DEB_MEMBER_FUNCT();
	m_is_reader_open_image_file = true;
}

//-----------------------------------------------------
// disable reading the image file on disk, only simulated "null" image will be generated
//-----------------------------------------------------
void Reader::disableReader(void)
{
    DEB_MEMBER_FUNCT();
	m_is_reader_open_image_file = false;
}

//---------------------------
//- Start check/reading image
//---------------------------
void Reader::start()
{
	DEB_MEMBER_FUNCT();
	try
	{
		this->post(new yat::Message(READER_START_MSG), POST_MSG_TMO);
	}
	catch (yat::Exception& ex)
	{
		DEB_ERROR() << "Error : " << ex.errors[0].desc;
		throw LIMA_HW_EXC(Error, ex.errors[0].desc);
	}
}

//---------------------------
//- Nothing to do
//---------------------------
void Reader::stop()
{
	DEB_MEMBER_FUNCT();
	try
	{
		this->post(new yat::Message(READER_STOP_MSG), POST_MSG_TMO);
	}
	catch (yat::Exception& ex)
	{
		DEB_ERROR() << "Error : " << ex.errors[0].desc;
		throw LIMA_HW_EXC(Error, ex.errors[0].desc);
	}
}

//---------------------------
//- Abort check/reading image
//---------------------------
void Reader::reset()
{
	DEB_MEMBER_FUNCT();
	try
	{
		this->post(new yat::Message(READER_RESET_MSG), POST_MSG_TMO);
	}
	catch (yat::Exception& ex)
	{
		DEB_ERROR() << "Error : " << ex.errors[0].desc;
		throw LIMA_HW_EXC(Error, ex.errors[0].desc);
	}
}

//---------------------------
//- get the last acquired image number
//---------------------------
int Reader::getLastAcquiredFrame(void)
{
	DEB_MEMBER_FUNCT();
	yat::MutexLock scoped_lock(m_lock);
	return m_image_number;
}

//---------------------------
//- Signal if a timeout is occured during the reader process
//---------------------------
bool Reader::isTimeoutSignaled()
{
	DEB_MEMBER_FUNCT();
	yat::MutexLock scoped_lock(m_lock);
	return 	m_is_timeout_signaled;
}


//---------------------------
//- Signal if reader process is in progress
//---------------------------
bool Reader::isRunning(void)
{
	DEB_MEMBER_FUNCT();
	yat::MutexLock scoped_lock(m_lock);
	return m_is_running;
}

//---------------------------
// yat::task handler
//---------------------------
void Reader::handle_message(yat::Message& msg) throw (yat::Exception)
{
	DEB_MEMBER_FUNCT();
	try
	{
		switch (msg.type())
		{
			//-----------------------------------------------------
			case yat::TASK_INIT:
			{
				DEB_TRACE() << "Reader::->TASK_INIT";

				//- set timeout unit in seconds
				m_timeout.set_unit(yat::Timeout::TMO_UNIT_MSEC);
				//- set default timeout value
				m_timeout.set_value(DEFAULT_READER_TIMEOUT_MSEC);

				//- create empty image initialized to 0 , in order to manage simulated image if necessary
				try
				{
					m_image = new uint16_t[m_image_size.getWidth() * m_image_size.getHeight()];
				}
				catch (const std::bad_alloc&)
				{
					throw LIMA_HW_EXC(Error, "Memory allocation exception !");
				}

				//set simulated image to 0
				memset((uint16_t*) m_image, 0, m_image_size.getWidth() * m_image_size.getHeight() * 2);
			}
			break;
				//-----------------------------------------------------
			case yat::TASK_EXIT:
			{
				DEB_TRACE() << "Reader::->TASK_EXIT";
				delete[] m_image;
			}
			break;
				//-----------------------------------------------------
			case yat::TASK_TIMEOUT:
			{
				DEB_TRACE() << "Reader::->TASK_TIMEOUT";
			}
			break;
				//-----------------------------------------------------
			case yat::TASK_PERIODIC:
			{
				DEB_TRACE() << "Reader::->TASK_PERIODIC";

				//- force exit Task Reader due to a reset command or if timeout expired
				{
					yat::MutexLock scoped_lock(m_lock);
					if ( m_is_reset || m_timeout.expired() )
					{
						DEB_TRACE() << "FATAL::Failed to load image : timeout expired !";
						m_is_timeout_signaled = true;
						//- disable periodic msg
						enable_periodic_msg(false);
						//- disable timeout
						m_timeout.disable();
						//- reset image number
						m_image_number = 0;
						//- reader task is no more running
						m_is_running = false;
						return;
					}
				}

				//- get image file name from camera module and chek if file exist, in case of enabled reader, otherwise simulated image
				if (m_is_reader_open_image_file)
				{
					m_full_file_name = m_cam.getImagePath() + m_cam.getFileName();
					//- looking for file on disk
					if(isFileExist(m_full_file_name))
					{
						enable_periodic_msg(false);	//file found, no need to search it anymore, so stop PERIODIC_MSG and continue forward
					}
					else
					{
						return;						//not found, try PERIODIC_MSG again
					}
				}
				else
				{
					enable_periodic_msg(false);	//no need to read file , so stop
					//- simulated file , continue with addNewFrame()
					m_full_file_name = "SIMULATED_IMAGE_FILE.XXX";
				}

				//- copy image file in a new frame buffer and signal it to the clients
				addNewFrame(m_full_file_name);

				//
				yat::MutexLock scoped_lock(m_lock);
				{
					m_is_running = false;
				}
			}
			break;
				//-----------------------------------------------------
			case READER_START_MSG:
			{
				DEB_TRACE() << "Reader::->START_MSG";
				//start PERIODIC_MSG in order to serach file on disk (if not simulated)
				enable_periodic_msg(true);

				//init. some variables
				yat::MutexLock scoped_lock(m_lock);
				{
					m_image_number = 0;
					m_is_running = true;
					m_is_reset = false;
					m_is_timeout_signaled = false;
					//- re-arm timeout
					m_timeout.restart();
				}
			}
			break;
				//-----------------------------------------------------
			case READER_STOP_MSG:
			{
				DEB_TRACE() << "Reader::->STOP_MSG";
			}
			break;
				//-----------------------------------------------------
			case READER_RESET_MSG:
			{
				DEB_TRACE() << "Reader::->RESET_MSG";
				enable_periodic_msg(false);
				yat::MutexLock scoped_lock(m_lock);
				{
					m_is_timeout_signaled = false;
					m_is_reset = true;
				}
			}
			break;
				//-----------------------------------------------------
		}
	}
	catch (yat::Exception& ex)
	{
		DEB_ERROR() << "Error : " << ex.errors[0].desc;
		throw LIMA_HW_EXC(Error, ex.errors[0].desc);
	}

}

//---------------------------
//- Fill image memory using DI library or use simulated image "null"
//---------------------------
void Reader::addNewFrame(std::string filename)
{
	DEB_MEMBER_FUNCT();
	try
	{
		DEB_TRACE() << "-- file = " << filename;
		StdBufferCbMgr& buffer_mgr = ((reinterpret_cast<BufferCtrlObj&>(m_buffer)).getBufferCbMgr());
		bool continueAcq = false;
		int buffer_nb, concat_frame_nb;

		DEB_TRACE() << "-- image#" << m_image_number << " acquired !";
		buffer_mgr.setStartTimestamp(Timestamp::now());
		buffer_mgr.acqFrameNb2BufferNb(m_image_number, buffer_nb, concat_frame_nb);

		//prepare the buffer !
		DEB_TRACE() << "-- prepare image buffer";
		void *ptr = buffer_mgr.getBufferPtr(buffer_nb, concat_frame_nb);

		//use Diffraction image library or not according to "m_is_reader_open_image_file"
		if (m_is_reader_open_image_file)
		{
			//read image file using diffractionImage library
			DEB_TRACE() << "-- create Diffraction Image object attached to image";
			DI::DiffractionImage di(const_cast<char*>(filename.c_str()));

			if(	m_image_size.getWidth()!=di.getWidth() || m_image_size.getHeight()!=di.getHeight())
				throw LIMA_HW_EXC(Error, "Image size in file is different from the expected image size of this detector !");

			DEB_TRACE() << "-- copy image in buffer";
			for (int j = 0; j < di.getWidth() * di.getHeight(); j++)
			{
				((uint16_t*) ptr)[j] = (uint16_t)(di.getImage()[j]);
			}
		}
		else
		{
			//use simulated image (all pixels are set to 0)
			DEB_TRACE() << "-- copy simulated image in buffer";
			memcpy((uint16_t *) ptr, (uint16_t *) (m_image), m_image_size.getWidth() * m_image_size.getHeight() * 2); //*2 because 16bits
		}

		DEB_TRACE() << "-- newFrameReady";
		HwFrameInfoType frame_info;
		frame_info.acq_frame_nb = m_image_number;
		continueAcq = buffer_mgr.newFrameReady(frame_info);
	}
	catch (yat::Exception& ex)
	{
		// Error handling
		DEB_ERROR() << ex.errors[0].desc;
		throw LIMA_HW_EXC(Error, ex.errors[0].desc);
	}
	return;
}

//---------------------------
// Check if file is found on disk
//---------------------------
bool Reader::isFileExist(const std::string& filename)
{
	//- check if file exist
	std::ifstream file_exist(filename.c_str());
	if ( file_exist )
	{
		//file found
		return true;
	}
	return false;
}

//---------------------------

