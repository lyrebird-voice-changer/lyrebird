#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <errno.h>
#include <string.h>
#include <stddef.h>
#include <unistd.h>
#include <pulse/pulseaudio.h>
#include <pulse/glib-mainloop.h>
#include <pulse/error.h>

#include "pulse.h"
#include "rubberband.h"

struct lyrebird_internal_t {
  pa_context *pa_context;
} typedef lyrebird_internal_t;

void pulseaudio_read_callback(pa_stream *stream, size_t nbytes, void *userdata) {
  printf("read data\n");
  pa_stream_drop(stream);
}

static void pulseaudio_stream_state_cb(pa_stream *stream, void *userdata) {
  switch(pa_stream_get_state(stream)) {
    case PA_STREAM_UNCONNECTED:
      printf("unconnected\n");
      break;
    case PA_STREAM_CREATING:
      printf("creating\n");
      break;
    case PA_STREAM_READY:
      printf("ready\n");
      break;
    case PA_STREAM_FAILED:
      printf("failed\n");
      const char *strerr;

      int err;
      pa_context *context = pa_stream_get_context(stream);
      if ((err = pa_context_errno(context)) != 0) {
        if ((strerr = pa_strerror(err)) == NULL)
          printf("Unknown error\n");

        printf("Error: %s\n", strerr);
      }
      break;
    case PA_STREAM_TERMINATED:
      printf("terminated\n");
      break;
    default:
      printf("unknown error\n");
  }
}

int pulseaudio_record_stream_setup(lyrebird_internal_t *data) {
  const pa_sample_spec spec = {
    .format = PA_SAMPLE_S16LE,
    .rate = 44100,
    .channels = 1
  };

  pa_stream *stream;
  stream = pa_stream_new(data->pa_context, "Lyrebird Stream", &spec, NULL);

  if (stream == NULL) {
    printf("stream is null, exiting\n");
    exit(1);
  }

  pa_stream_set_state_callback(stream, pulseaudio_stream_state_cb, data);
  pa_stream_set_read_callback(stream, pulseaudio_read_callback, NULL);

  pa_buffer_attr buffer_attr;

  memset(&buffer_attr, 0, sizeof(buffer_attr));
  buffer_attr.maxlength = (uint32_t) -1;
  buffer_attr.prebuf = (uint32_t) -1;
  buffer_attr.fragsize = buffer_attr.tlength = (uint32_t) -1;
  buffer_attr.minreq = (uint32_t) -1;

  int cb_result = pa_stream_connect_record(stream, NULL, &buffer_attr, 0);
  if (cb_result != 0) {
    printf("failed to connect stream to callback, status: %d\n", cb_result);
  }

  return 0;
}

static void pulseaudio_state_cb(pa_context *context, void *userdata) {

  if (userdata == NULL) {
    printf("fatal error: pulseaudio state cb missing data\n");
    exit(1);
  }

  lyrebird_internal_t *data = (lyrebird_internal_t *)userdata;

  int err = 0;
  const char *strerr;

  switch (pa_context_get_state(context)) {
    case PA_CONTEXT_CONNECTING:
      printf("connecting...\n");
      break;
    case PA_CONTEXT_AUTHORIZING:
      printf("authing...\n");
      break;
    case PA_CONTEXT_SETTING_NAME:
      printf("setting names... \n");
      break;
    case PA_CONTEXT_READY:
      printf("ready... \n");
      pulseaudio_record_stream_setup(data);
      //g_thread_new("Lyrebird Pulseaudio setup", pulseaudio_record_stream_setup, data);
      break;
    case PA_CONTEXT_TERMINATED:
      printf("terminated... \n");
      break;
    case PA_CONTEXT_FAILED:
    default:
      printf("failed / didn't catch the state code\n");
      if ((err = pa_context_errno(context)) != 0) {
        if ((strerr = pa_strerror(err)) == NULL)
          printf("Unknown error\n");

        printf("Error: %s\n", strerr);
      }
  }
}

int main() {

  // glib main loop

  GMainLoop *loop = NULL;
  loop = g_main_loop_new(NULL, 0);

  // pulse setup

  /*
  if (lyrebird_pulse_create_null_sink() != 0) {
    printf("ERROR: Failed to create null sinks\n");
    return 1;
  }
  */

  pa_glib_mainloop *mainloop = NULL;
  pa_mainloop_api *mainloop_api;

  if ((mainloop = pa_glib_mainloop_new(NULL)) == NULL) {
    printf("ERROR: couldn't create glib mainloop\n");
    return 1;
  }

  mainloop_api = pa_glib_mainloop_get_api(mainloop);

  if (pa_signal_init(mainloop_api) < 0) {
    printf("ERROR: failed to init pa signal\n");
    return 1;
  }

  lyrebird_internal_t *data = malloc(sizeof(lyrebird_internal_t));
  data->pa_context = pa_context_new(mainloop_api, "Lyrebird");

  pa_context_set_state_callback(data->pa_context, pulseaudio_state_cb, data);

  int context_status;
  if ((context_status = pa_context_connect(data->pa_context, NULL, 0, NULL)) != 0) {
    printf("context connection failure: %d\n", context_status);
  }

  g_main_loop_run(loop);

  free(data);

  return 0;
}
