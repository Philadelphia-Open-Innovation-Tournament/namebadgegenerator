import csv
import os
import random
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from reportlab.graphics.shapes import Group, Drawing
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

def is_mostly_white(drawing):
    total_luminance = 0
    pixel_count = 0

    def calculate_luminance(shape):
        nonlocal total_luminance, pixel_count
        if hasattr(shape, 'fillColor') and shape.fillColor:
            luminance = (0.299 * shape.fillColor.red + 
                         0.587 * shape.fillColor.green + 
                         0.114 * shape.fillColor.blue)
            total_luminance += luminance
            pixel_count += 1
        if isinstance(shape, Group):
            for elem in shape.contents:
                calculate_luminance(elem)

    calculate_luminance(drawing)

    return pixel_count > 0 and (total_luminance / pixel_count) > 0.7

def invert_svg(drawing):
    def invert_shape(shape):
        if hasattr(shape, 'fillColor'):
            if shape.fillColor:
                r, g, b = shape.fillColor.rgb()
                shape.fillColor = colors.Color(1-r, 1-g, 1-b)
        if hasattr(shape, 'strokeColor'):
            if shape.strokeColor:
                r, g, b = shape.strokeColor.rgb()
                shape.strokeColor = colors.Color(1-r, 1-g, 1-b)
        if isinstance(shape, Group):
            for elem in shape.contents:
                invert_shape(elem)

    invert_shape(drawing)
    return drawing

def process_logo(logo_path, target_width, target_height):
    if logo_path.lower().endswith('.svg'):
        drawing = svg2rlg(logo_path)

        # Convert SVG to greyscale
        def convert_to_greyscale(shape):
            if hasattr(shape, 'fillColor') and shape.fillColor:
                grey = (shape.fillColor.red + shape.fillColor.green + shape.fillColor.blue) / 3
                shape.fillColor = colors.Color(grey, grey, grey)
            if hasattr(shape, 'strokeColor') and shape.strokeColor:
                grey = (shape.strokeColor.red + shape.strokeColor.green + shape.strokeColor.blue) / 3
                shape.strokeColor = colors.Color(grey, grey, grey)
            if isinstance(shape, Group):
                for elem in shape.contents:
                    convert_to_greyscale(elem)

        convert_to_greyscale(drawing)

        if is_mostly_white(drawing):
            drawing = invert_svg(drawing)

        scale_x = target_width / drawing.width
        scale_y = target_height / drawing.height
        scale = min(scale_x, scale_y)
        drawing.width, drawing.height = drawing.minWidth() * scale, drawing.height * scale
        drawing.scale(scale, scale)
        return drawing
    else:
        # Handle PNG with potential transparency
        img = Image.open(logo_path)
        if img.mode == 'RGBA':
            # Create a white background
            bg = Image.new('RGBA', img.size, (255, 255, 255))
            # Paste the image on the background
            bg.paste(img, (0, 0), img)
            img = bg.convert('RGB')

        # Convert to RGB if it's not already
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Save to a BytesIO object
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        return ImageReader(img_io)

def create_badge(c, name, x, y, width, height, logo):
    # Badge background
    c.setFillColor(colors.white)
    c.rect(x, y, width, height, fill=1)

    # Event name
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 16)
    c.drawCentredString(x + width/2, y + height - 0.5*inch, "Philadelphia Open")
    c.setFont("Helvetica", 16)
    c.drawCentredString(x + width/2, y + height - 0.8*inch, "Innovation Tournament")

    # Person's name
    name_font_size = 28
    c.setFont("Helvetica-Bold", name_font_size)
    name_width = stringWidth(name, "Helvetica-Bold", name_font_size)
    while name_width > width * 0.9:
        name_font_size -= 1
        c.setFont("Helvetica-Bold", name_font_size)
        name_width = stringWidth(name, "Helvetica-Bold", name_font_size)
    name_y = y + height/2 + 0.75*inch
    c.drawCentredString(x + width/2, name_y, name)

    # Logo
    logo_width = width * 0.7
    logo_height = height * 0.3
    logo_y = y + 1*inch

    if isinstance(logo, ImageReader):  # It's a PNG file
        c.drawImage(logo, x + width/2 - logo_width/2, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, anchor='c')
    else:  # It's an SVG
        renderPDF.draw(logo, c, x + width/2 - logo_width/2, logo_y)


def create_badges(csv_file, output_pdf, logos_folder):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter

    badge_width = 4.25 * inch
    badge_height = 6 * inch

    logos = [os.path.join(logos_folder, f) for f in os.listdir(logos_folder) 
             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header row if present

        for i, row in enumerate(reader):
            if row:
                name = row[0]

                page_num = i // 2
                badge_num = i % 2

                if badge_num == 0:
                    c.showPage()
                    c.setFillColor(colors.white)
                    c.rect(0, 0, width, height, fill=1)

                    # Add cutting guides
                    c.setStrokeColor(colors.lightgrey)
                    c.line(badge_width, 0, badge_width, height)
                    c.line(0, height - badge_height, width, height - badge_height)

                x = 0 if badge_num == 0 else badge_width
                y = height - badge_height if badge_num == 0 else 0

                logo_width = badge_width * 0.7
                logo_height = badge_height * 0.3
                logo = process_logo(random.choice(logos), logo_width, logo_height)

                create_badge(c, name, x, y, badge_width, badge_height, logo)

    c.save()

# Usage
create_badges('names.csv', 'badges.pdf', 'logos')

