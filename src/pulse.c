#include "pulse.h"

static pa_simple *s = NULL;
static char name_buf[] = "PulseAudio default device";

int lyrebird_pulse_start() {
    int error;

    static const pa_sample_spec ispec = {
        .format = PA_SAMPLE_S16LE,  /* 16 bit low endian */
        .rate = 44100,              /* 44 khz sampling rate */
        .channels = 1
    };

    if (!(s = pa_simple_new(NULL, "Lyrebird C Test", PA_STREAM_RECORD, NULL, "record", &ispec, NULL, NULL, &error))) {
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