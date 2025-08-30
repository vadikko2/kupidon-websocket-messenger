import io
import logging

import blurhash
import numpy as np
import simplejpeg

logger = logging.getLogger(__name__)

COMPONENTS_X = 4
COMPONENTS_Y = 3
RESOLUTION = 100


def generate_blurhash(image_bytes: io.BytesIO) -> str:
    logger.debug("Generating blurhash for image")

    image_bytes.seek(0)
    image_data = image_bytes.getvalue()
    image_bytes.seek(0)

    if not simplejpeg.is_jpeg(image_data):
        raise ValueError("Input image must be JPEG format")

    height, width, _, _ = simplejpeg.decode_jpeg_header(image_data)
    rgb_data: np.ndarray = simplejpeg.decode_jpeg(image_data)

    height_scale = int(height) / RESOLUTION
    width_scale = int(width) / RESOLUTION

    resized_image = np.empty((RESOLUTION, RESOLUTION, 3), dtype=np.uint8)

    for y in range(RESOLUTION):
        for x in range(RESOLUTION):
            original_y = int(y * height_scale)
            original_x = int(x * width_scale)
            resized_image[y, x] = rgb_data[original_y, original_x][:3]

    logger.debug("Blurhash generated")
    return blurhash.encode(resized_image, COMPONENTS_X, COMPONENTS_Y)
