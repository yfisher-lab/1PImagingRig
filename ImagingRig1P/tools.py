import PIL
import numpy as np


def open_multipage_tiff(filepath):
    """_summary_

    Args:
        filepath (_type_): _description_

    Returns:
        _type_: _description_
    """

    img = PIL.Image.open(filepath)
    images = []

    try:
        while True:
            images.append(img.copy())
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    return np.array(images)