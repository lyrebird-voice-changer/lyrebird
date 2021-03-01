#ifndef LYREBIRD_PULSE
#define LYREBIRD_PULSE

#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <stddef.h>
#include <unistd.h>
#include <pulse/simple.h>
#include <pulse/error.h>
#include <stdlib.h>

#define LB_PA_SPEC_FORMAT PA_SAMPLE_FLOAT32LE
#define LB_PA_SPEC_RATE 44100
#define LB_PA_SPEC_CHANNELS 1

#include "lyrebird.h"
#include "recording.h"
#include "playback.h"

int lyrebird_pulse_create_null_sink();
int lyrebird_pulse_unload_sinks();
int lyrebird_pulse_setup(lyrebird_internal_t *data);

#endif
