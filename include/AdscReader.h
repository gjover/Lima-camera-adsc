#ifndef READER_H
#define READER_H


///////////////////////////////////////////////////////////
// YAT::TASK 
///////////////////////////////////////////////////////////
#include <yat/threading/Task.h>
#include <DiffractionImage.h>			//- to read back img data


const size_t  TASK_PERIODIC_MS = 100;
const size_t  POST_MSG_TMO     = 2;

const double  DEFAULT_READER_TIMEOUT_MSEC = 1000.;

const size_t  READER_START_MSG     =   (yat::FIRST_USER_MSG + 300);
const size_t  READER_STOP_MSG      =   (yat::FIRST_USER_MSG + 301);
const size_t  READER_RESET_MSG     =   (yat::FIRST_USER_MSG + 302);

///////////////////////////////////////////////////////////


#include <stdlib.h>
#include <limits>

#include "Debug.h"
#include "Data.h"

#include "HwMaxImageSizeCallback.h"
#include "AdscCamera.h"
#include "HwBufferCtrlObj.h"


using namespace lima;
using namespace lima::Adsc;
using namespace std;


namespace lima
{
namespace Adsc
{

/*******************************************************************
 * \class Reader
 * \brief object involved Check/Reading Image file generated by the camera
 *******************************************************************/

class Reader : public yat::Task
{
  DEB_CLASS_NAMESPC(DebModCamera, "Reader", "Adsc");

public:

  ///ctor
  Reader(Camera& cam, HwBufferCtrlObj& buffer_ctrl);
  ///dtor
  virtual ~Reader();

  ///Start check/reading image file
  void start();
  ///NOP
  void stop();
  ///Abort check/reading image file
  void reset();
  ///Return acquired image index, index starting at 0
  int  getLastAcquiredFrame(void);
  ///Signal if a timeout is occured during the reader process
  bool isTimeoutSignaled(void);
  ///Signal if reader process is in progress
  bool isRunning(void);
  ///Define max authorized Time before reading image file is done
  void setTimeout(int timeout);
  ///Enable reading an real image file on disk
  void enableReader(void);
  ///Use simulated image (all pixels sets to 0)
  void disableReader(void);

  //- [yat::Task implementation]
protected: 
  virtual void 	handle_message( yat::Message& msg )    throw (yat::Exception);

private:
  ///Fill image memory using DI library or use simulated image (all pixels sets to 0)
  void 			addNewFrame(std::string filename = "");
  ///Check if file is found on disk
  bool 			isFileExist(const std::string& filename);

  //- Data members
  yat::Mutex                  m_lock;
  Camera&                     m_cam;
  HwBufferCtrlObj&            m_buffer;
  Size                        m_image_size;
  int						  m_periodic_time;
  int                         m_image_number;
	bool 		m_is_timeout_signaled;
  bool						  m_is_running;
  bool 						  m_is_reader_open_image_file;
  bool 						  m_is_reset;
  std::string 				  m_full_file_name;
  yat::Timeout				  m_timeout;

  //simulated image memory zone!
  uint16_t*                   m_image;

};
} // namespace Reader
} // namespace lima


#endif // READER_H
