from rembg import remove
from PIL import Image

input_path = 'assets/balitech logo.png'
output_path = 'static/img/logo.png'

input_image = Image.open(input_path)
output_image = remove(input_image)
output_image.save(output_path)
print("Background removed successfully")
