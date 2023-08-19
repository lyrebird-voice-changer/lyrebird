import subprocess

class Audio:
    def __init__(self):
        self.sox_process = None

    def kill_sox(self, timeout=1):
        if self.sox_process is not None:
            self.sox_process.terminate()
            try:
                self.sox_process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.sox_process.kill()
                self.sox_process.wait(timeout=timeout)
            self.sox_process = None

    # trying a lower buffer size
    def run_sox(self, scale, preset, buffer=20):
        '''
        Builds and returns a sox command from a preset object
        '''
        buffer = 17
        multiplier = 100
        command_effects = []

        command_effects += ["pitch", str(scale * multiplier)]

        # Volume boosting
        if preset.volume_boost != None:
            command_effects += ["vol", str(preset.volume_boost) + "dB"]
        else:
            # Fix a bug where SoX uses last given volumne
            command_effects += ["vol", "0"]

        # Downsampling
        if preset.downsample_amount != None:
            command_effects += ["downsample", str(preset.downsample_amount)]
        else:
            # Append downsample of 1 to fix a bug where the downsample isn't being reverted
            # when we disable the effect with it on.
            command_effects += ["downsample", "1"]

        command = ["sox", "--buffer", str(buffer), "-q", "-t", "pulseaudio", "default", "-t", "pulseaudio", "Lyrebird-Output"] + command_effects
        self.sox_process = subprocess.Popen(command)

    def get_sink_name(self, tuple):
        if tuple[0] == "sink_name":
            return tuple[1]
        elif tuple[0] == "source_name":
            return tuple[1]
        else:
            return None

    def load_pa_modules(self):
        self.null_sink = subprocess.check_call(
            'pactl load-module module-null-sink sink_name=Lyrebird-Output node.description="Lyrebird Output"'.split(' ')
        )
        self.remap_sink = subprocess.check_call(
            'pactl load-module module-remap-source source_name=Lyrebird-Input master=Lyrebird-Output.monitor node.description="Lyrebird Virtual Input"'\
                .split(' ')
        )

    def get_pactl_modules(self):
        '''
        Parses `pactl info short` into tuples containing the module ID,
        the module type and the attributes of the module. It is designed
        only for named modules and as such junk data may be included in
        the returned list.
        
        Returns an array of tuples that take the form:
            (module_id (str), module_type (str), attributes (attribute tuples))
        
        The attribute tuples:
            (key (str), value (str))
            
        An example output might look like:
            [
                ( '30', 'module-null-sink', [('sink_name', 'Lyrebird-Output')] ),
                ( '31', 'module-remap-source', [('source_name', 'Lyrebird-Input'), ('master', 'Lyrebird-Output.monitor')] )
            ]
        '''
        pactl_list = subprocess.run(["pactl", "list", "short"], capture_output=True, encoding="utf8")
        lines = pactl_list.stdout
        data = []
        split_lines = lines.split("\n")
        for line in split_lines:
            info = line.split("\t")
            if len(info) <= 2:
                continue
            
            if info[2] and len(info[2]) > 0:
                key_values = list(map(lambda key_value: tuple(key_value.split("=")), info[2].split(" ")))
                data.append((info[0], info[1], key_values))
            else:
                data.append((info[0], info[1], []))
        return data

    def unload_pa_modules(self):
        '''
        Unloads all Lyrebird null sinks.
        '''
        modules = self.get_pactl_modules()
        lyrebird_module_ids = []
        for module in modules:
            if len(module) < 3:
                continue;
            if len(module[2]) < 1:
                continue;

            if module[1] == "module-null-sink":
                sink_name = self.get_sink_name(module[2][0])
                if sink_name == "Lyrebird-Output":
                    lyrebird_module_ids.append(module[0])
            elif module[1] == "module-remap-source":
                sink_name = self.get_sink_name(module[2][0])
                if sink_name == "Lyrebird-Input":
                    lyrebird_module_ids.append(module[0])

        for id in lyrebird_module_ids:
                subprocess.run(["pactl", "unload-module", str(id)])
