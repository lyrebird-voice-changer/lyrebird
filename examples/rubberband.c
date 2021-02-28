// non-functional example code from the prototype phase of
// the project. the code uses the single-threaded pulse "simple"
// api to get audio from the default device, run it thru
// rubberband to pitch shift it and then pipe it to STDOUT.
//
// the main value to this code is the rubberband processing,
// not the old pulse code that can't be multi-threaded

#define PULSE_BUFFERSIZE 2046

static pa_simple *s = NULL;
static char name_buf[] = "PulseAudio default device";

int lyrebird_pulse_start() {
    int error;

    static const pa_sample_spec ispec = {
        .format = PA_SAMPLE_S16LE,  /* 16 bit low endian */
        .rate = 44100,              /* 44 khz sampling rate */
        .channels = 1
    };

    if (!(s = pa_simple_new(NULL, "Lyrebird C Test", PA_STREAM_RECORD, NULL, "Lyrebird Recording", &ispec, NULL, NULL, &error))) {
        printf("Error: pa_simple_new() failed: %s\n", pa_strerror(error));
        return 1;
    }
    return 0;
}

int lyrebird_pulse_stop() {
    if (s != NULL) {
        pa_simple_free(s);
        s = NULL;
    }
    return 0;
}

int lyrebird_pulse_read(int16_t *buf, int sample_num) {
    int error;
    int cnt, bufsize;

    bufsize = sample_num * sizeof(int16_t);
    if (bufsize > PULSE_BUFFERSIZE) bufsize = PULSE_BUFFERSIZE;

    if (pa_simple_read(s, buf, bufsize, &error) < 0) {
        printf("Error: pa_sample_read() failed: %s\n", pa_strerror(error));
    }
    cnt = bufsize / sizeof(int16_t);
    return (cnt);
}

int16_t buffer[PULSE_BUFFERSIZE];
RubberBandState testing_rb_state;

int real_time_loop_active = 1;

void sigint_handler(int signum) {
    real_time_loop_active = 0;
    lyrebird_pulse_stop();
    lyrebird_rubberband_stop(testing_rb_state);
    
    if (lyrebird_pulse_unload_sinks() != 0) {
        printf("WARNING: May have failed to unload PulseAudio modules\n");
    }
}

/**

NOTES:

- Raw data can be converted to a file using SoX, pipe the raw data to stdout and run
`sox -t raw -b 16 -e signed-integer -r 44100 test.raw test.wav`

IMPORTANT! Before you listen to any data PLEASE take off your headphones or lower the
volume of your speakers, it is sometimes VERY BAD AUDIO!

*/

int main() {
  // Temporary RubberBand state struct for testing
  testing_rb_state = lyrebird_rubberband_setup(44100, 1);
  rubberband_set_pitch_scale(testing_rb_state, lyrebird_semitones_pitch(1));

  // Start Pulse
  lyrebird_pulse_start();

  signal(SIGINT, sigint_handler);

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

      int16_t *out_buffer = malloc(available_frames * sizeof(uint16_t));
      for (int i = 0; i < available_frames; i++) {
        out_buffer[i] = (uint16_t)(out[0][i] * 44100);
      }
      fwrite(out_buffer, sizeof(uint16_t), available_frames, stdout);
    }
  }


  return 0;
}
