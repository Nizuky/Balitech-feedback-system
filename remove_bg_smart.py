from PIL import Image

def remove_bg(image_path, output_path, tolerance=30):
    img = Image.open(image_path).convert("RGBA")
    
    # Get the top-left pixel as the background color
    bg_color = img.getpixel((0, 0))
    print(f"Detected background color: {bg_color}")
    
    width, height = img.size
    
    # Make a copy to edit
    newData = []
    
    for y in range(height):
        for x in range(width):
            pixel = img.getpixel((x, y))
            # Check if pixel is close to bg_color
            if abs(pixel[0] - bg_color[0]) <= tolerance and \
               abs(pixel[1] - bg_color[1]) <= tolerance and \
               abs(pixel[2] - bg_color[2]) <= tolerance:
                newData.append((255, 255, 255, 0)) # transparent
            else:
                newData.append(pixel)
                
    # Update image
    img2 = Image.new("RGBA", (width, height))
    img2.putdata(newData)
    img2.save(output_path, "PNG")

if __name__ == "__main__":
    remove_bg('assets/balitech logo.png', 'static/img/logo.png', tolerance=25)
    print("Background removal done based on top-left pixel.")
