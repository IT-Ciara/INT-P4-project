from PIL import Image, ImageDraw, ImageFont
# Port positions on the switch image
PORT_POSITIONS = {
    0: (80, 84), 1: (190, 84), 2: (304, 84), 3: (415, 84), 
    4: (528, 84), 5: (639, 84), 6: (749, 84), 7: (861, 84), 
    8: (971, 84), 9: (76, 610), 10: (188, 610), 11: (299, 610), 
    12: (414, 610), 13: (527, 610), 14: (637, 610), 15: (750, 610), 
    16: (864, 610)
}

# Paths to images
image_path = "./diagram/switch.png"
output_path = "./diagram/modified_image.png"

# Step 4: Image Label Drawing
def draw_labels_on_image(port_labels):
    """Draws port labels on the specified image of the switch."""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    for port, position in PORT_POSITIONS.items():
        port_name = port_labels.get(port)
        if port_name:
            font = ImageFont.truetype("arial.ttf", 12) if ImageFont.truetype else ImageFont.load_default()
            draw.text(position, str(port_name), fill="black", font=font)

    img.save(output_path)
    print("Modified image saved to:", output_path)