#include "lyrebird.h"

int main() {
  GMainLoop *loop = NULL;
  loop = g_main_loop_new(NULL, 0);
  lyrebird_internal_t *data = malloc(sizeof(lyrebird_internal_t));

  /*
  if (lyrebird_pulse_create_null_sink() != 0) {
    printf("ERROR: Failed to create null sinks\n");
    return 1;
  }
  */

  if (lyrebird_pulse_setup(data) != 0) {
    printf("[error] failed to setup pulseaudio\n");
    return 1;
  }

  g_main_loop_run(loop);
  free(data);

  return 0;
}
