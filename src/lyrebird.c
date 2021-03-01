#include "lyrebird.h"

void display_help() {
  printf("Lyrebird v2.0 alpha build 1\nCopyright (c) Lyrebird Team\n\nusage: lyrebird <semitones>\n");
}

void sigkill_handler(int sig) {
  printf("[debug] unloading pulse sinks %d\n", sig);
  lyrebird_pulse_unload_sinks();
  exit(0);
}

int main(int argc, char *argv[]) {
  signal(SIGINT, sigkill_handler);

  GMainLoop *loop = NULL;
  loop = g_main_loop_new(NULL, 0);
  lyrebird_internal_t *data = malloc(sizeof(lyrebird_internal_t));

  if (argv[1] == NULL) {
    display_help();

    free(data);
    return 1; 
  }
  float semitones = atof(argv[1]);
  data->semitones = semitones; 

  if (lyrebird_pulse_create_null_sink() != 0) {
    printf("[error] failed to create null sinks\n");
    free(data);
    return 1;
  }

  if (lyrebird_pulse_setup(data) != 0) {
    printf("[error] failed to setup pulseaudio\n");
    free(data);
    return 1;
  }

  g_main_loop_run(loop);

  if (lyrebird_pulse_unload_sinks()) {
    printf("[warning] failed to unload sinks");
  }

  free(data);

  return 0;
}
