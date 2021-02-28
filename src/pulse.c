#include "pulse.h"

// - PulseAudio Sinks -

// Returns 0 upon success
int lyrebird_pulse_create_null_sink() {
  if (system("pacmd load-module module-null-sink sink_name=Lyrebird-C-Output") != 0)
    return 1;
  if (system("pacmd load-module module-remap-source source_map=Lyrebird-Input master=Lyrebird-Output.monitor") != 0)
    return 1;

  return 0;
}

// Returns 0 upon success
int lyrebird_pulse_unload_sinks() {
  int status = 0;

  // Vital to continue unloading the modules even if the previous command fails
  // in order to clean up as much as possible
  if (system("pacmd unload-module module-null-sink") != 0)
    status = 1;
  if (system("pacmd unload-module module-remap-source") != 0)
    status = 1;

  return status;
}

// - PulseAudio context -

static void pulse_context_state_cb(pa_context *context, void *userdata) {

  if (userdata == NULL) {
    printf("fatal error: pulseaudio state cb missing data\n");
    exit(1);
  }

  lyrebird_internal_t *data = (lyrebird_internal_t *)userdata;

  int err = 0;
  const char *strerr;

  switch (pa_context_get_state(context)) {
    case PA_CONTEXT_CONNECTING:
      printf("[debug] pulseaudio context connecting\n");
      break;
    case PA_CONTEXT_AUTHORIZING:
      printf("[debug] pulseaudio context authorizing\n");
      break;
    case PA_CONTEXT_SETTING_NAME:
      printf("[debug] pulseaudio context setting name\n");
      break;
    case PA_CONTEXT_READY:
      printf("[debug] pulseaudio context ready\n");

      if (lyrebird_pulseaudio_record_stream_setup(data) != 0) {
        printf("[error] could not setup recording stream, exiting\n");
        exit(1);
      }
      break;
    case PA_CONTEXT_TERMINATED:
      printf("[error] pulseaudio context terminated, exiting");
      exit(1);
      break;
    case PA_CONTEXT_FAILED:
    default:
      if ((err = pa_context_errno(context)) != 0) {
        if ((strerr = pa_strerror(err)) != NULL) {
          printf("[error] pulseaudio context init failed, exiting, more info: %s\n", strerr);
          exit(1);
        }
      }
      printf("[error] pulseaudio context init failed with an unknown error, exiting");
      exit(1);
  }
}

int lyrebird_pulse_setup(lyrebird_internal_t *data) {

  // setting up pulseaudio mainloop
  pa_glib_mainloop *mainloop = NULL;
  pa_mainloop_api *mainloop_api;

  if ((mainloop = pa_glib_mainloop_new(NULL)) == NULL) {
    printf("[error] couldn't create pulseaudio glib mainloop\n");
    return 1;
  }


  // init pulse signal
  mainloop_api = pa_glib_mainloop_get_api(mainloop);

  if (pa_signal_init(mainloop_api) < 0) {
    printf("[error] failed to init pulseaudio signal\n");
    return 1;
  }

  // creating pulse context
  data->pa_context = pa_context_new(mainloop_api, "Lyrebird");
  pa_context_set_state_callback(data->pa_context, pulse_context_state_cb, data);

  if (pa_context_connect(data->pa_context, NULL, 0, NULL) != 0) {
    printf("[error] context connection failure\n");
    return 1;
  }

  return 0;
}
