#ifndef LYREBIRD_RUBBERBAND
#define LYREBIRD_RUBBERBAND

#include <stdio.h>
#include <rubberband/rubberband-c.h>

float lyrebird_semitones_pitch(float semitones);
RubberBandState lyrebird_rubberband_setup(int samplerate, int channels);

#endif
