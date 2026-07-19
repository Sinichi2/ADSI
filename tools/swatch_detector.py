"""Dominant-color detection for PDF palette swatches (no text). Uses Pillow only."""


def dominant_colors(image_path, max_colors=8):
    """Return list of hex colors, most frequent first, from a swatch image/crop."""
    from PIL import Image  # pillow is a base dep
    img = Image.open(image_path).convert("RGB")
    # ponytail: quantize is a cheap dominant-color proxy; swap for k-means if palettes get noisy.
    quant = img.quantize(colors=max_colors)
    palette = quant.getpalette()
    counts = sorted(quant.getcolors(), reverse=True)  # [(count, index), ...]
    out = []
    for _, idx in counts:
        r, g, b = palette[idx * 3: idx * 3 + 3]
        out.append(f"#{r:02x}{g:02x}{b:02x}")
    return out
