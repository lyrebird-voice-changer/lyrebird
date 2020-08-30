#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <stddef.h>
#include <unistd.h>
#include <pulse/simple.h>
#include <pulse/error.h>

#include "pulse.h"

int16_t buffer[PULSE_BUFFERSIZE];

void sigint_handler(int signum) {
    lyrebird_pulse_stop();
    exit(0);
}

int main() {

    signal(SIGINT, sigint_handler);

    // piping stdout to .raw file and running
    //    sox -t raw -b 16 -e signed-integer -r 44100 test.raw test.wav
    // will convert to a wav file

    lyrebird_pulse_start();
    while (1) {
      int samples = lyrebird_pulse_read(buffer, 32);
      if (write(STDOUT_FILENO, buffer, 32) != 32) {
        printf("Error: write failed: %s\n", strerror(errno));
        lyrebird_pulse_stop();
      }
      usleep(5);
    }

    return 0;
}