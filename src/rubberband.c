#include "rubberband.h"

RubberBandState state;

void lyrebird_rubberband_setup(int samplerate, int channels) {

    RubberBandOptions options = RubberBandOptionPitchHighQuality | RubberBandOptionFormantShifted;
    double initial_timeratio = 1.0;
    double initial_pitchscale = 1.0;

    /* Initialize rubberband */
    state = rubberband_new(samplerate, channels, options, initial_timeratio, initial_pitchscale);
}