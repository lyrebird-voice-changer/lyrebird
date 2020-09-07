#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <errno.h>
#include <string.h>
#include <stddef.h>
#include <unistd.h>
#include <pulse/simple.h>
#include <pulse/error.h>

#include "pulse.h"
#include "rubberband.h"

int16_t buffer[PULSE_BUFFERSIZE];
RubberBandState testing_rb_state;

int real_time_loop_active = 1;

void sigint_handler(int signum) {
  real_time_loop_active = 0;
  lyrebird_pulse_stop();
  lyrebird_rubberband_stop(testing_rb_state);
}

/**

  NOTES:

    - You should only pull 32 samples at a time from Pulse, anything more makes results
      in a semi-inaudible track

    - Raw data can be converted to a file using SoX, pipe the raw data to stdout and run
      `sox -t raw -b 16 -e signed-integer -r 44100 test.raw test.wav`

      IMPORTANT! Before you listen to any data PLEASE take off your headphones or lower the
      volume of your speakers, it most likely is VERY BAD AUDIO!

  STATUS:

    The code takes mic data and sends it through RubberBand where it outputs raw VERY BAD
    AUDIO THAT HURTS YOUR EARS to the stdout. However within the bad audio your voice can
    be heard pitch shifted which means its working. The very bad audio most likely comes
    from a) asking for more than 32 samples from Pulse and b) not being sure if RubberBand
    outputs floats or (un)signed ints and then pushing the data to SoX as a signed int.

    Please once again, if you want to try it out and listen PLEASE PLEASE PLEASE take OFF
    YOUR HEADPHONES or LOWER THE VOLUME OF YOUR SPEAKERS. IT'S VERY BAD AUDIO!

*/

int main() {

  signal(SIGINT, sigint_handler);

  // Temporary RubberBand state struct for testing
  testing_rb_state = lyrebird_rubberband_setup(44100, 1);
  rubberband_set_pitch_scale(testing_rb_state, 1);

  // Start Pulse
  lyrebird_pulse_start();

  // Run forever
  while (real_time_loop_active) {

    // Find out how many samples RubberBand wants and pull that many from Pulse, in
    // reality this won't work in reality since pulling any samples over 32 makes
    // inaudible sounds
    unsigned int samples_required = rubberband_get_samples_required(testing_rb_state);
    /*int pulse_samples_recv = */lyrebird_pulse_read(buffer, samples_required);

    // DEBUG: Write raw Pulse data to stdout, will sounds bad unless 32 samples
    // fwrite(buffer, sizeof(int16_t), samples_required, stdout);

    // Creating the first (and only) channel for RubberBand
    float in_samples_chan1[samples_required];
    memset(in_samples_chan1, 0, samples_required);
    for (unsigned int i = 0; i < samples_required; i++) {
      // Making sure value doesn't equal 0 or exceed/be less than -1.0f/1.0f bounds
      float value;
      if (buffer[i] == 0) {
        value = 0;
      } else {
        // Find float value by dividing by sample rate
        float calculated = (float)buffer[i] / 44100.0;
        if (calculated > 1) {
          value = 1;
        } else if (calculated < -1) {
          value = -1;
        } else {
          value = calculated;
        }
      }
      // Write calculated value to buffer
      in_samples_chan1[i] = value;
    }
    // Create final buffer for RubberBand
    float *in_samples[1] = { in_samples_chan1 };

    // Process data in RubberBand
    rubberband_process(testing_rb_state, (const float* const*)in_samples, samples_required, 0);

    // How many frames available to receive from RubberBand
    int available_frames = rubberband_available(testing_rb_state);
    if (available_frames > 0) {
      // More than 0, read from RubberBand
      float out_chan1[available_frames];
      memset(out_chan1, 0, available_frames);
      float *out[1] = { out_chan1 };

      // Pull samples from RubberBand
      /*size_t out_samples_size = */rubberband_retrieve(testing_rb_state, out, available_frames);

      // DEBUG: Write raw RubberBand data to stdout
      fwrite(out[0], sizeof(float), available_frames, stdout);
    }
  }



  return 0;
}