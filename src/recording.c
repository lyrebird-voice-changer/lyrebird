#include "recording.h"

void record_stream_read_cb(pa_stream *stream, size_t nbytes, void *userdata) {
  printf("[super debug] read data from recording stream\n");

  if (nbytes <= 0) {
    printf("[super debug] data from recording stream is empty\n");
    return;
  }

  while (pa_stream_readable_size(stream) > 0) {
    void *data;
    size_t length;
    if (pa_stream_peek(stream, (const void**)&data, &length) < 0) {
      int err;
      if ((err = pa_context_errno(pa_stream_get_context(stream))) != 0) {
        const char *strerr;
        if ((strerr = pa_strerror(err)) != NULL) {
          printf("[error] failed to read record stream: %s, exiting\n", strerr);
        } else {
          printf("[error] failed to read record stream, error code %d, exiting\n", err);
        }
      } else {
        printf("[error] failed to read record stream for an unknown reason, exiting\n");
      }
      exit(1);
    }

    if (data == NULL) {
      printf("[super debug] recording data is null");
    }

    size_t max_writable_size = pa_stream_writable_size(stream);
    size_t data_len = fmin(max_writable_size, length);
    if (data_len != length) {
      printf("[warning] mismatch between data buffer and max write len: (max) %ld vs (buffer) %ld\n", max_writable_size, data_len);
    }

    lyrebird_internal_t *lyrebird_data;
    if ((lyrebird_data = (lyrebird_internal_t *)userdata) == NULL) {
      printf("[error] lyrebird user data not available to recording callback, exiting\n");
      exit(1);
    }

    pa_stream *playback_stream = lyrebird_data->playback_stream;
  
    if (pa_stream_write(playback_stream, data, data_len, NULL, 0, PA_SEEK_RELATIVE) != 0) {
      printf("[error] failed to write to playback stream, exiting\n");
      exit(1);
    }

    pa_stream_drop(stream);
  }
}

static void record_stream_state_cb(pa_stream *stream, void *userdata) {
  switch(pa_stream_get_state(stream)) {
    case PA_STREAM_READY:
      printf("[debug] recording stream ready\n");
      break;
    case PA_STREAM_FAILED:
      // braces because c
      {
        const char *strerr;
        int err;
        pa_context *context = pa_stream_get_context(stream);
        if ((err = pa_context_errno(context)) != 0) {
          if ((strerr = pa_strerror(err)) != NULL) {
            printf("[error] recording stream failed, exiting: %s\n", strerr);
            exit(1);
          }
          printf("[error] recording stream failed with error code %d, exiting\n", err);
          exit(1);
        }
        printf("[error] recording stream failed for an unknown reason, exiting\n");
        exit(1);
        break;
      }
    case PA_STREAM_UNCONNECTED:
      printf("[debug] recording stream unconnected\n");
      break;
    case PA_STREAM_CREATING:
      printf("[debug] recording stream creating\n");
      break;
    case PA_STREAM_TERMINATED:
      printf("[debug] recording stream terminated\n");
      break;
  }
}

int lyrebird_pulse_record_stream_setup(lyrebird_internal_t *data) {
  pa_stream *stream;

  static const pa_sample_spec pulse_spec = {
    .format = LB_PA_SPEC_FORMAT,
    .rate = LB_PA_SPEC_RATE,
    .channels = LB_PA_SPEC_CHANNELS
  };

  stream = pa_stream_new(data->pa_context, "Lyrebird Recording", &pulse_spec, NULL);
  data->record_stream = stream;

  if (stream == NULL) {
    printf("[error] failed to create recording stream\n");
    return 1;
  }

  pa_stream_set_state_callback(stream, record_stream_state_cb, data);
  pa_stream_set_read_callback(stream, record_stream_read_cb, data);

  pa_buffer_attr buffer_attr;
  memset(&buffer_attr, 0, sizeof(buffer_attr));
  buffer_attr.maxlength = (uint32_t) -1;
  buffer_attr.prebuf = (uint32_t) -1;
  buffer_attr.fragsize = buffer_attr.tlength = (uint32_t) -1;
  buffer_attr.minreq = (uint32_t) -1;

  int cb_result = pa_stream_connect_record(stream, NULL, &buffer_attr, 0);
  if (cb_result != 0) {
    printf("[error] failed to activate recording for stream\n");
    return 1;
  }

  return 0;
}

