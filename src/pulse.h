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

int lyrebird_pulse_create_null_sink();
int lyrebird_pulse_unload_sinks();

#endif
