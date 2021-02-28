#ifndef LYREBIRD_PLAYBACK
#define LYREBIRD_PLAYBACK

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <pulse/pulseaudio.h>
#include <pulse/glib-mainloop.h>
#include <pulse/error.h>

#include "lyrebird.h"
#include "pulse.h"

int lyrebird_pulse_playback_stream_setup(lyrebird_internal_t *data);

#endif
