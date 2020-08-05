

def resize_keep_ratio(pil_image, new_height):
    w, h = pil_image.size
    new_width = round(w * new_height / h)
    return pil_image.resize((new_width, new_height))