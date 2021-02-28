#include "playback.h"

static void playback_stream_state_cb(pa_stream *stream, void *userdata) {
  switch(pa_stream_get_state(stream)) {
    case PA_STREAM_READY:
      printf("[debug] playback stream ready\n");
      break;
    case PA_STREAM_FAILED:
      // braces because c
      {
        const char *strerr;
        int err;
        pa_context *context = pa_stream_get_context(stream);
        if ((err = pa_context_errno(context)) != 0) {
          if ((strerr = pa_strerror(err)) != NULL) {
            printf("[error] playback stream failed, exiting: %s\n", strerr);
            exit(1);
          }
          printf("[error] playback stream failed with error code %d, exiting\n", err);
          exit(1);
        }
        printf("[error] playback stream failed for an unknown reason, exiting\n");
        exit(1);
        break;
      }
    case PA_STREAM_UNCONNECTED:
      printf("[debug] playback stream unconnected\n");
      break;
    case PA_STREAM_CREATING:
      printf("[debug] playback stream creating\n");
      break;
    case PA_STREAM_TERMINATED:
      printf("[debug] playback stream terminated\n");
      break;
  }
}


int lyrebird_pulse_playback_stream_setup(lyrebird_internal_t *data) {
  pa_stream *stream;

  static const pa_sample_spec pulse_spec = {
    .format = LB_PA_SPEC_FORMAT,
    .rate = LB_PA_SPEC_RATE,
    .channels = LB_PA_SPEC_CHANNELS
  };

  stream = pa_stream_new(data->pa_context, "Lyrebird Playback", &pulse_spec, NULL);
  data->playback_stream = stream;

  if (stream == NULL) {
    printf("[error] failed to create recording stream\n");
    return 1;
  }

  pa_stream_set_state_callback(stream, playback_stream_state_cb, data);

  int connect_status = pa_stream_connect_playback(stream, NULL, NULL, 0, NULL, NULL);
  if (connect_status != 0) {
    printf("[error] failed to connect stream to playback\n");
    return 1;
  }

  return 0;
}
