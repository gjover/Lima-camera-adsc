
CONF_STORED_DARK=1                   # 1 to use stored darks, 0 to take darks    
CONF_COMMENT=" "                     # Comment to add to header
CONF_BEAM_X=0.0                      # Beam center, x 
CONF_BEAM_Y=0.0                      # Beam center, y 
CONF_WAVELENGTH=1.0                  # Wavelength
CONF_DISTANCE=4000.0                 # Distance
CONF_AXIS=1                          #  1 for phi, 0 for omega 
CONF_PHI=0.0                         # Phi or Omega angle
CONF_TWOTHETA=0.0                    # Two theta angle
CONF_BIN=2                           # Binning 1 or 2 (0 means Default = 2)
CONF_ADC=1                           # 0 for slow, 1 for fast adc
CONF_SAVE_RAW=0                      # 1 to save the raw file
CONF_NO_XFORM=0                      # 0 to transform image (in order to generate the .img file)
CONF_COMPRESS=0                      # 1 to compress output images 
CONF_OSC_RANGE=1.0                   #

ENV_DTHOSTNAME="bl11adsc"            # hostname for the data server (data)
ENV_DTPORT="8141"                    # tcp/ip data port numbe
ENV_DTSECPORT="8149"                 # tcp/ip data secure port number ?
ENV_XFHOSTNAME="bl11adsc"            # hostname for the xform server (control)
ENV_XFPORT="8146"                    # tcp/ip xform port number
ENV_DC_LOCAL_LOG="/homelocal/opbl11/tmp/adsc/LogADSC.log"     # Local log file
ENV_DC_CONFIG   ="/homelocal/opbl11/tmp/adsc/config_ccd"         # CCD configuraion file
ENV_N_CTRL="4"                       # Number of controllers/modules in the detector.
