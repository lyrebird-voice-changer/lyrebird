#include "pulse.h"

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

