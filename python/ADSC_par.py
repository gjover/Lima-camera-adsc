# /*
#  *-----------------------------------------------------------
#  *
#  *	Parameter lists for detcon_entry.c
#  *
#  *-----------------------------------------------------------
#  *
#  */

# enum {
# 	HWP_BIN = 0,		/* INT    1 for no binning, 2 for 2x2 binning */
# 	HWP_ADC,		/* INT    0 for slow, 1 for fast adc */
# 	HWP_SAVE_RAW,		/* INT    1 to save raw images */
# 	HWP_DARK,		/* INT    1 if this is a dark */
# 	HWP_STORED_DARK,	/* INT    1 for stored dark, else normal darks */
# 	HWP_NO_XFORM,		/* INT    1 fo no transform */
# 	HWP_LOADFILE,		/* INT    1 to read the image from disk instead of collecting it */
# 	HWP_TEMP_COLD,		/* INT    1 to make the detector COLD (set), or return 1 if the detector is cold (get) */
# 	HWP_TEMP_WARM,		/* INT    1 to make the detector WARM (set), or return 1 if the detector is warm (get) */
# 	HWP_TEMP_MODE,		/* INT    1 if detector temperature changes are done with SETS, 0 for RAMP (default) */
# 	HWP_TEMP_STATUS,	/* STRING returns the detector temperature status string */
# 	HWP_TEMP_VALUE		/* FLOAT  set or get the current "detector temperature" */
#      };

# enum {
# 	FLP_PHI = 0,		/* FLOAT  phi value */
# 	FLP_OMEGA,		/* FLOAT  omega */
# 	FLP_KAPPA,		/* FLOAT  kappa */
# 	FLP_TWOTHETA,		/* FLOAT  two theta */
# 	FLP_DISTANCE,		/* FLOAT  distance */
# 	FLP_WAVELENGTH,		/* FLOAT  wavelength */
# 	FLP_AXIS,		/* INT    1 for phi, 0 for omega */
# 	FLP_OSC_RANGE,		/* FLOAT  frame size */
# 	FLP_TIME,		/* FLOAT  time, if used */
# 	FLP_DOSE,		/* FLOAT  dose, if used */
# 	FLP_BEAM_X,		/* FLOAT  beam center, x */
# 	FLP_BEAM_Y,		/* FLOAT  beam center, y */
# 	FLP_COMPRESS,		/* INT    1 to compress output images */
# 	FLP_KIND,		/* INT    "kind" sequence number */
# 	FLP_FILENAME,		/* STRING filename */
# 	FLP_COMMENT,		/* STRING comment to add to header */
# 	FLP_LASTIMAGE,		/* INT    1 for last image, 0 otherwise, -1 for flush */
# 	FLP_SUFFIX,		/* STRING returns or sets the image suffix */
# 	FLP_IMBYTES,		/* INT    image number of bytes */
# 	FLP_READ_FILENAME,	/* STRING filename to read from for HWP_LOADFILE=1 */
# 	FLP_USERDEF_STR,	/* STRING user defined command */
# 	FLP_USERRET,		/* STRING user defined command return */
# 	FLP_HEADER,		/* STRING for SMV, a header to be merged with input header on image output */
# 				/*        for CBF, a header template to be used on image output */
# 	FLP_JPEG1_NAME,		/* STRING file name for first jpeg file (if specified) */
# 	FLP_JPEG1_SIZE,		/* STRING size of first jpeg file, as a string such as "colsxrow" (e,g. "128x128") */
# 	FLP_JPEG2_NAME,		/* STRING file name for second jpeg file (if specified) */
# 	FLP_JPEG2_SIZE,		/* STRING size of second jpeg file, as a string such as "colsxrow" (e,g. "128x128") */
# 	FLP_OUTFILE_TYPE,	/* INT    output file type: 0 for .img, 1 for just .cbf, and 2 for both .img and .cbf */
#      };

HWP_BIN,\
HWP_ADC,\
HWP_SAVE_RAW,\
HWP_DARK,\
HWP_STORED_DARK,\
HWP_NO_XFORM,\
HWP_LOADFILE,\
HWP_TEMP_COLD,\
HWP_TEMP_WARM,\
HWP_TEMP_MODE,\
HWP_TEMP_STATUS,\
HWP_TEMP_VALUE\
= range(12)

FLP_PHI,\
FLP_OMEGA,\
FLP_KAPPA,\
FLP_TWOTHETA,\
FLP_DISTANCE,\
FLP_WAVELENGTH,\
FLP_AXIS,\
FLP_OSC_RANGE,\
FLP_TIME,\
FLP_DOSE,\
FLP_BEAM_X,\
FLP_BEAM_Y,\
FLP_COMPRESS,\
FLP_KIND,\
FLP_FILENAME,\
FLP_COMMENT,\
FLP_LASTIMAGE,\
FLP_SUFFIX,\
FLP_IMBYTES,\
FLP_READ_FILENAME,\
FLP_USERDEF_STR,\
FLP_USERRET,\
FLP_HEADER,\
FLP_JPEG1_NAME,\
FLP_JPEG1_SIZE,\
FLP_JPEG2_NAME,\
FLP_JPEG2_SIZE,\
FLP_OUTFILE_TYPE\
= range(28)

