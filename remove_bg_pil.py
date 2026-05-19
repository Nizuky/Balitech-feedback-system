from PIL import Image

def make_white_transparent(image_path, output_path, tolerance=30):
    img = Image.open(image_path)
    img = img.convert("RGBA")
    datas = img.getdata()
    
    newData = []
    for item in datas:
        # Check if pixel is close to white
        if item[0] > 255 - tolerance and item[1] > 255 - tolerance and item[2] > 255 - tolerance:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
            
    img.putdata(newData)
    img.save(output_path, "PNG")

if __name__ == "__main__":
    make_white_transparent('assets/balitech logo.png', 'static/img/logo.png', tolerance=15)
    print("PIL white background removal done")
