#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <errno.h>
#include <string.h>
#include <stddef.h>
#include <unistd.h>
#include <pulse/pulseaudio.h>
#include <pulse/glib-mainloop.h>
#include <pulse/simple.h>
#include <pulse/error.h>

#include "pulse.h"
#include "rubberband.h"

// initial boilerplate to connect to pulse audio,
// currently the connection is refused, most
// likely the code can't find the server
// - harry

static void pulseaudio_state_cb(pa_context *context, void *userdata) {
  int err = 0;
  const char *strerr;

  // boilerplate
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

static pa_context *context;
int main() {

  // glib main loop

  GMainLoop *loop = NULL;
  loop = g_main_loop_new(NULL, 0);

  // pulse setup

  if (lyrebird_pulse_create_null_sink() != 0) {
    printf("ERROR: Failed to create null sinks\n");
    return 1;
  }

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

  context = pa_context_new(mainloop_api, "lyrebird-context");
  pa_context_set_state_callback(context, pulseaudio_state_cb, NULL);

  int context_status;
  if ((context_status = pa_context_connect(context, "default Pulse Audio", 0, NULL)) != 0) {
    printf("context connection failure: %d\n", context_status);
  }

  g_main_loop_run(loop);

  return 0;
}
