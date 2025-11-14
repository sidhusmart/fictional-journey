#!/usr/bin/env python3
"""
Icon generator for Blast from the Past Chrome Extension
Generates icon16.png, icon48.png, and icon128.png

Requirements: pip install Pillow
"""

try:
    from PIL import Image, ImageDraw
    import os
except ImportError:
    print("Error: Pillow is required. Install it with: pip install Pillow")
    exit(1)


def create_gradient(size):
    """Create a purple gradient background"""
    image = Image.new('RGB', (size, size), '#667eea')
    draw = ImageDraw.Draw(image)

    for y in range(size):
        # Gradient from #667eea to #764ba2
        r = int(102 + (118 - 102) * y / size)
        g = int(126 + (75 - 126) * y / size)
        b = int(234 + (162 - 234) * y / size)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    return image


def draw_clock(draw, size, center):
    """Draw a clock on the image"""
    # Clock face (white circle)
    clock_radius = int(size * 0.375)
    clock_bbox = [
        center - clock_radius,
        center - clock_radius,
        center + clock_radius,
        center + clock_radius
    ]
    draw.ellipse(clock_bbox, fill='rgba(255, 255, 255, 240)')

    # Clock markers
    marker_radius = max(2, int(size * 0.023))
    marker_positions = [
        (center, int(size * 0.19)),  # 12
        (center, int(size * 0.81)),  # 6
        (int(size * 0.19), center),  # 9
        (int(size * 0.81), center),  # 3
    ]

    for x, y in marker_positions:
        marker_bbox = [x - marker_radius, y - marker_radius,
                      x + marker_radius, y + marker_radius]
        draw.ellipse(marker_bbox, fill='#667eea')

    # Clock hands
    hand_width = max(2, int(size * 0.031))

    # Hour hand (pointing up)
    draw.line([center, center, center, int(size * 0.28)],
             fill='#667eea', width=hand_width)

    # Minute hand (pointing right)
    draw.line([center, center, int(size * 0.66), center],
             fill='#764ba2', width=hand_width)

    # Center dot
    center_radius = max(2, int(size * 0.039))
    center_bbox = [
        center - center_radius,
        center - center_radius,
        center + center_radius,
        center + center_radius
    ]
    draw.ellipse(center_bbox, fill='#764ba2')


def generate_icon(size):
    """Generate an icon of the specified size"""
    # Create gradient background
    img = create_gradient(size)

    # Convert to RGBA for transparency support
    img = img.convert('RGBA')

    # Add clock
    draw = ImageDraw.Draw(img)
    center = size // 2

    # Draw outer circle
    outer_radius = int(size * 0.47)
    outer_bbox = [
        center - outer_radius,
        center - outer_radius,
        center + outer_radius,
        center + outer_radius
    ]
    draw.ellipse(outer_bbox, fill=None)

    # Draw clock
    draw_clock(draw, size, center)

    # Draw back arrow (only for larger icons)
    if size >= 48:
        arrow_points = [
            (int(size * 0.25), int(size * 0.19)),
            (int(size * 0.16), int(size * 0.25)),
            (int(size * 0.19), int(size * 0.25)),
            (int(size * 0.19), int(size * 0.31)),
            (int(size * 0.13), int(size * 0.31)),
            (int(size * 0.125), int(size * 0.16)),
            (int(size * 0.22), int(size * 0.156)),
        ]
        draw.polygon(arrow_points, fill=(118, 75, 162, 200))

    return img


def main():
    """Generate all icon sizes"""
    sizes = [16, 48, 128]
    icons_dir = 'icons'

    # Create icons directory if it doesn't exist
    os.makedirs(icons_dir, exist_ok=True)

    print("Generating icons...")

    for size in sizes:
        filename = f'{icons_dir}/icon{size}.png'
        print(f"  Creating {filename}...")

        icon = generate_icon(size)
        icon.save(filename, 'PNG')

        print(f"  ✓ {filename} created ({size}x{size})")

    print("\n✨ All icons generated successfully!")
    print("\nNext steps:")
    print("1. Load the extension in Chrome (chrome://extensions)")
    print("2. Enable Developer Mode")
    print("3. Click 'Load unpacked' and select this folder")


if __name__ == '__main__':
    main()
