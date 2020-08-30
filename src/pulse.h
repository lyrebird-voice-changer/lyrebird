#ifndef LYREBIRD_PULSE
#define LYREBIRD_PULSE

#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <stddef.h>
#include <unistd.h>
#include <pulse/simple.h>
#include <pulse/error.h>

#define PULSE_BUFFERSIZE 32

int lyrebird_pulse_start();
int lyrebird_pulse_stop();
int lyrebird_pulse_read(int16_t *buf, int sample_num);

#endif