#ifndef LYREBIRD_RECORDING
#define LYREBIRD_RECORDING

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <errno.h>
#include <string.h>
#include <pulse/pulseaudio.h>
#include <pulse/glib-mainloop.h>
#include <pulse/error.h>
#include <rubberband/rubberband-c.h>

#include "lyrebird.h"
#include "pulse.h"
#include "rubberband.h"

int lyrebird_pulse_record_stream_setup(lyrebird_internal_t *data);

#endif
