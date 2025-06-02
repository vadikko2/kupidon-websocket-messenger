import array
import math
import pathlib
import typing

import pydub

MAX_COLUMNS = 100
MAX_LEVELS = 32


class DecodeVoiceError(Exception):
    pass


class HistogramExtractionError(Exception):
    pass


class AudioToHistogram:
    def __init__(self, decoder: typing.Callable[[pathlib.Path], array.array[int]]):
        self._decoder = decoder

    @staticmethod
    def aggregate(
        amplitudes: array.array[int],
        max_columns: int,
    ) -> list[tuple[float, float]]:
        """
        Агрегация амплитуд до нужного кол-ва столбцов
        :param amplitudes: значения амплитуд
        :param max_columns: макс кол-во столбцов
        :return: list[tuple[float, float]] со значением амплитуд, агрегированных до max_columns
        """
        aggregated_by_columns_data = []
        batch_size = math.ceil(len(amplitudes) // max_columns)

        for idx in range(0, len(amplitudes), batch_size):
            temp_data = amplitudes[idx : idx + batch_size]
            temp_data_neg = list(filter(lambda x: x < 0, temp_data))
            temp_data_not_neg = list(filter(lambda x: x >= 0, temp_data))
            aggregated_by_columns_data.append(
                (
                    sum(temp_data_not_neg) // (len(temp_data_not_neg) + 1),
                    sum(temp_data_neg) // (len(temp_data_neg) + 1),
                ),
            )

        return aggregated_by_columns_data

    @staticmethod
    def quantize(
        amplitudes: list[tuple[float, float]],
        max_levels: int,
    ) -> list[tuple[int, int]]:
        """
        Квантование амплитуд до нужного уровня детализации
        :param amplitudes: значения амплитуд
        :param max_levels: максимальное значение детализации
        :return: значения амплитуд, квантованных до max_levels
        """
        max_amplitude_value = max(amplitudes, key=lambda x: x[0])[0]
        min_amplitude_value = min(amplitudes, key=lambda x: x[1])[1]
        value_for_quant_max = abs(max_amplitude_value // (max_levels // 2))
        value_for_quant_min = abs(min_amplitude_value // (max_levels // 2))

        return list(map(lambda x: (int(x[0] // value_for_quant_max), int(x[1] // value_for_quant_min)), amplitudes))

    def __call__(
        self,
        audio_filename: pathlib.Path,
        max_columns: int = MAX_COLUMNS,
        max_levels: int = MAX_LEVELS,
    ) -> list[tuple[int, int]]:
        amplitudes = self._decoder(audio_filename)
        try:
            aggregated_by_columns_data = self.aggregate(amplitudes, max_columns)
            return self.quantize(aggregated_by_columns_data, max_levels)
        except Exception as e:
            raise HistogramExtractionError(e)


def mp3_decoder(filename: pathlib.Path) -> array.array[int]:
    try:
        return pydub.AudioSegment.from_file(str(filename.absolute())).get_array_of_samples()
    except Exception as e:
        raise DecodeVoiceError(f"MP3 decoding failed: {str(e)}")
