#include "pulse.h"

static pa_simple *s = NULL;
static char name_buf[] = "PulseAudio default device";

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