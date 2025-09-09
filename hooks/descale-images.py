import logging
import os
from io import BytesIO

import cv2
import filetype
import numpy as np

from mkdocs.structure.files import Files
from PIL import Image

log = logging.getLogger(f"mkdocs.plugins.{__name__}")


def descale_image(input_path) -> BytesIO | None:
    # Open the image with Pillow
    with Image.open(input_path) as img:
        # # image is already small, no need to resize
        if img.width < 1500:
            return None

        # Calculate new dimensions (25% of original)
        new_width = img.width // 2
        new_height = img.height // 2

        # Convert to RGB if image is in RGBA mode
        if img.mode == "RGBA":
            img = img.convert("RGB")

        # Resize the image using LANCZOS resampling
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)

        content = BytesIO()
        # Save as PNG with optimal compression
        resized_img.save(content, "PNG", optimize=True)
        print(
            f"size before {os.path.getsize(input_path)}; after: {len(content.getvalue())}"
        )
        return content


def compress_image(input_path, quality=80) -> BytesIO | None:
    # Open the image with Pillow
    with Image.open(input_path) as image:
        # Downscale if larger than 16MP
        max_pixels = 16_000_000  # 16 Megapixels
        width, height = image.size
        if width * height > max_pixels:
            scale_factor = (max_pixels / (width * height)) ** 0.5
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.LANCZOS)

        # Convert to OpenCV format (BGR for better compression control)
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Apply WebP compression
        success, encoded = cv2.imencode(
            ".jpeg", image_cv, [cv2.IMWRITE_JPEG_QUALITY, quality]
        )
        if not success:
            raise ValueError("Encoding failed")

        content = BytesIO(encoded.tobytes())
        print(
            f"size before {os.path.getsize(input_path)}; after: {len(content.getvalue())}"
        )
        return content


def on_files(files: Files, config):
    do_descale = int(os.environ.get("DESCALE", "1"))
    if do_descale == 0:
        return

    for mf in files.media_files():
        if not filetype.is_image(mf.abs_src_path) or ".gif" in mf.abs_src_path:
            continue
        filetype.filetype
        maybe_descaled_content = compress_image(mf.abs_src_path)
        if maybe_descaled_content:
            print(f"resized {mf.name}")
            mf.content_bytes = maybe_descaled_content.getvalue()

    # from ipdb import set_trace; set_trace()
    return files
