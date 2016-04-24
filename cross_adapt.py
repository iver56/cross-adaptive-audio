from __future__ import absolute_import
from __future__ import print_function
import template_handler
import csound_handler
import os
import settings
import sound_file
import hashlib
import json
import standardizer
import copy


class CrossAdapter(object):
    @staticmethod
    def cross_adapt(input_sound, parameter_vectors, effect, generation):
        vectors = copy.deepcopy(parameter_vectors)

        # map normalized values to the appropriate ranges of the effect parameters
        for i in range(effect.num_parameters):
            mapping = effect.parameters[i]['mapping']
            min_value = mapping['min_value']
            max_value = mapping['max_value']
            skew_factor = mapping['skew_factor']

            for parameter_vector in vectors:
                parameter_vector[i] = standardizer.Standardizer.get_mapped_value(
                    normalized_value=parameter_vector[i],
                    min_value=min_value,
                    max_value=max_value,
                    skew_factor=skew_factor
                )

        channels = zip(*parameter_vectors)
        data_md5 = hashlib.md5(json.dumps(channels)).hexdigest()

        channels_csv = []
        for channel in channels:
            channel_csv = ','.join(map(str, channel))
            channels_csv.append(channel_csv)

        template = template_handler.TemplateHandler('templates/dist_lpf.csd.jinja2')
        template.compile(
            input_sound_filename=input_sound.filename,
            parameter_channels=channels_csv,
            ksmps=settings.CSOUND_KSMPS,
            duration=input_sound.get_duration()
        )

        csd_path = os.path.join(settings.CSD_DIRECTORY, 'cross_adapt.csd')
        template.write_result(csd_path)
        csound = csound_handler.CsoundHandler(csd_path)
        output_filename = input_sound.filename + '.cross_adapted.gen{0:04d}.{1}.wav'.format(generation, data_md5)
        csound.run(output_filename, async=False)
        output_sound_file = sound_file.SoundFile(
            output_filename,
            is_input=False
        )
        return output_sound_file
