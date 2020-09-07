#ifndef LYREBIRD_RUBBERBAND
#define LYREBIRD_RUBBERBAND

#include <stdio.h>
#include <rubberband/rubberband-c.h>

RubberBandState lyrebird_rubberband_setup();
void lyrebird_rubberband_stop(RubberBandState state);
float lyrebird_semitones_pitch(float semitones);

#endif