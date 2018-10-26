from PIL import Image, ImageDraw
import os
import json

def get_pixel_matrix(img):
    """Converts a PIL image into a 2-D pixel matrix.

    Args:
    img -- PIL image object

    Returns:
    A 2-D pixel matrix
    """
    pixels = list(img.getdata())
    return [pixels[i:i+img.width] for i in range(0, len(pixels), img.width)]

def mean_rgb(pixels):
    """Calculates the mean RGB value of the given pixel
    matrix.

    Args:
    pixels -- a 2-D pixel matrix

    Returns:
    A 3-tuple of the average RGB value of the matrix
    """
    r_total = 0
    g_total = 0
    b_total = 0
    n_pixels = 0
    for row in pixels:
        for p in row:
            r_total += p[0]
            g_total += p[1]
            b_total += p[2]

            n_pixels += 1

    return (r_total / n_pixels, g_total / n_pixels, b_total / n_pixels)

def pythagoras_nearest_rgb(target_rgb, source_images_mean_rgbs):
    """Finds the source image with the closest rgb value to
    the target section.

    Args:
    target_rgb -- the average RGB value of the target section
    source_images_mean_rgbs -- a dictionary of source filenames =>
      the mean RGB value of that file

    Returns:
    The filename of the closest matching source image
    """
    best_match_name = None
    best_match_color_difference = None
    for path, source_rgb in source_images_mean_rgbs.iteritems():
        color_difference = pythagoras_color_difference(target_rgb, source_rgb)
        if best_match_color_difference is None or color_difference < best_match_color_difference:
            best_match_name = path
            best_match_color_difference = color_difference

    return best_match_name

def pythagoras_color_difference(p1, p2):
    """Calculates the color difference between 2 points using Pythagoras

    Args:
    p1 -- the RGB value of point 1
    p2 -- the RGB value of point 2

    Returns:
    The color difference between p1 and p2
    """
    tot = 0
    for c1, c2 in zip(p1, p2):
        tot += (c1 - c2)**2

    return tot**0.5

def get_image_square(pixels, corner, size):
    """Returns a square sub-section of the `pixels` matrix,
    with top-left corner at `corner`, and each side of the
    square `size` pixels in length.

    Args:
    pixels -- the pixels matrix of the entire image
    corner -- the top-left corner of the sub-section
    size -- the size of each side of the sub-section

    Returns:
    A pixel matrix of a sub-section of the original matrix
    """
    opposite_corner = (corner[0]+size, corner[1]+size)

    square_rows = pixels[corner[0]:opposite_corner[0]]
    square = []
    for row in square_rows:
        square.append(row[corner[1]:opposite_corner[1]])

    return square

def load_and_scale_source_imgs(dir_path, dim):
    """Loads all JPG images from `dir_path` and scale them to
    `dim` pixels in size (assumes all images are already
    sqaures`
    """
    imgs = {}
    for filename in os.listdir(dir_path):
        if filename.endswith(".jpg"):
            full_path = os.path.join(dir_path, filename)
            img = Image.open(full_path)
            img.thumbnail((dim, dim))
            imgs[filename] = img
    return imgs

def get_mean_rgbs(imgs):
    """Calculates the mean RGB value for every image
    in `imgs`.

    Args:
    imgs -- a dict of filenames => PIL image objects
        (NOT pixel matrices)

    Returns:
    A dict of filenames => mean RGB values
    """
    rgbs = {}
    for path, img in imgs.iteritems():
        print "Processed %s" % path
        pixels = get_pixel_matrix(img)
        rgbs[path] = mean_rgb(pixels)
    return rgbs

class JSONCache:
    """A small class that manages a cache backed
    by a JSON file on disk.
    """

    def __init__(self, cache_path):
        self.cache_path = cache_path

    def has_data(self):
        return os.path.isfile(self.cache_path)

    def write_all(self, data):
        with open(self.cache_path, 'w') as f:
            json.dump(data, f)

    def read_all(self):
		with open(self.cache_path) as f:
			return json.load(f)

# Make sure you have a dir called "./square_images
source_img_dir = "./example_square_images"
# Change this to the location of your input image
input_path = "./example_input.jpg"

square_size = 20

source_imgs = load_and_scale_source_imgs(source_img_dir, square_size)

# Optional - using a cache (see extensions)
cache = JSONCache("./mean_rgb_cache.json")
if not cache.has_data():
    mean_rgbs = get_mean_rgbs(source_imgs)
    cache.write_all(mean_rgbs)

mean_rgbs = cache.read_all()

target_img = Image.open(input_path)
target_pixels = get_pixel_matrix(target_img)
target_image_width, target_image_height = target_img.size

output_img = Image.new('RGB', (target_image_width, target_image_height), (255,255,255,0))
for x in range(0, target_image_width-1, square_size):
    for y in range(0, target_image_height-1, square_size):
        square = get_image_square(target_pixels, (y, x), square_size)
        target_rgb = mean_rgb(square)
        source_img_name = pythagoras_nearest_rgb(target_rgb, mean_rgbs)

        source_img = source_imgs[source_img_name]

        output_img.paste(source_img, (x, y))

output_img.show()
