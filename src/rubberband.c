#include "rubberband.h"

float lyrebird_semitones_pitch(float semitones) {
  return 1 + (semitones / 12);
}

RubberBandState lyrebird_rubberband_setup(int samplerate, int channels) {
  RubberBandOptions options = RubberBandOptionPitchHighQuality | RubberBandOptionFormantPreserved | RubberBandOptionSmoothingOn | RubberBandOptionProcessRealTime;
  double initial_timeratio = 1.0;
  double initial_pitchscale = 1.0;

  /* Initialize RubberBand */
  RubberBandState state = rubberband_new(samplerate, channels, options, initial_timeratio, initial_pitchscale);
  return state;
}

void lyrebird_rubberband_stop(RubberBandState state) {
  rubberband_delete(state);
}
