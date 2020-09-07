#include "rubberband.h"

RubberBandState lyrebird_rubberband_setup(int samplerate, int channels) {
    RubberBandOptions options = RubberBandOptionPitchHighQuality | RubberBandOptionFormantShifted | RubberBandOptionProcessRealTime;
    double initial_timeratio = 1.0;
    double initial_pitchscale = 1.0;

    /* Initialize rubberband */
    RubberBandState state = rubberband_new(samplerate, channels, options, initial_timeratio, initial_pitchscale);
    return state;
}

void lyrebird_rubberband_stop(RubberBandState state) {
    rubberband_delete(state);
}