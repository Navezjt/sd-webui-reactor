from collections import Counter
from PIL import Image
from math import isqrt, ceil
from typing import List

def make_grid(image_list: List):
    
    # Count the occurrences of each image size in the image_list
    size_counter = Counter(image.size for image in image_list)
    
    # Get the most common image size (size with the highest count)
    common_size = size_counter.most_common(1)[0][0]
    
    # Filter the image_list to include only images with the common size
    image_list = [image for image in image_list if image.size == common_size]
    
    # Get the dimensions (width and height) of the common size
    size = common_size
    
    # If there are more than one image in the image_list
    if len(image_list) > 1:
        num_images = len(image_list)
        
        # Calculate the number of rows and columns for the grid
        rows = isqrt(num_images)
        cols = ceil(num_images / rows)

        # Calculate the size of the square image
        square_size = (cols * size[0], rows * size[1])

        # Create a new RGB image with the square size
        square_image = Image.new("RGB", square_size)

        # Paste each image onto the square image at the appropriate position
        for i, image in enumerate(image_list):
            row = i // cols
            col = i % cols

            square_image.paste(image, (col * size[0], row * size[1]))

        # Return the resulting square image
        return square_image
    
    # Return None if there are no images or only one image in the image_list
    return None
