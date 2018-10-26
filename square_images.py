from PIL import Image, ImageDraw
import os, errno

src_dir = "./source_images"
dst_dir = "./square_images"
try:
	os.makedirs(dst_dir)
except OSError as exc:
	if exc.errno == errno.EEXIST and os.path.isdir(dst_dir):
		pass
	else:
		raise

for filename in os.listdir(src_dir):
    if filename.endswith(".jpg"):
        full_src_path = os.path.join(src_dir, filename)
        img = Image.open(full_src_path)
        min_dim = min(img.size)
        cropped_img = img.crop((0, 0, min_dim, min_dim))

        full_dst_path = os.path.join(dst_dir, filename)
        cropped_img.save(full_dst_path)
        print "Squared " + filename
