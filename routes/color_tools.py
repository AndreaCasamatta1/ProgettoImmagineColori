from PIL import Image
from collections import Counter
import webcolors

def exact_palette_with_percentages(image_path, max_colors=None):
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())  # lista di tuple (r,g,b)

    counts = Counter(pixels)
    total = sum(counts.values())

    # ordina per conteggio decrescente
    items = counts.most_common(max_colors)

    results = []
    for (r, g, b), count in items:
        percent = (count / total) * 100
        hexv = f"#{r:02x}{g:02x}{b:02x}"
        results.append({
            "rgb": (r, g, b),
            "hex": hexv,
            "percent": round(percent, 2)
        })
    return results


def quantized_palette_with_percentages(image_path, n_colors=15, resize=None):
    img = Image.open(image_path).convert("RGB")

    if resize is not None:
        w, h = img.size
        if max(w, h) > resize:
            scale = resize / max(w, h)
            img = img.resize((int(w*scale), int(h*scale)), resample=Image.NEAREST)

    q = img.quantize(colors=n_colors, method=Image.Quantize.MEDIANCUT)

    hist = q.histogram()
    total = sum(hist)
    palette = q.getpalette()

    results = []
    for idx, count in enumerate(hist):
        if count == 0:
            continue

        r = palette[idx*3 + 0]
        g = palette[idx*3 + 1]
        b = palette[idx*3 + 2]

        percent = (count / total) * 100
        hexv = f"#{r:02x}{g:02x}{b:02x}"

        results.append({
            "rgb": (r, g, b),
            "hex": hexv,
            "percent": round(percent, 2)
        })

    results.sort(key=lambda x: x["percent"], reverse=True)
    return results


def closest_color_name(rgb_tuple):
    r, g, b = rgb_tuple
    min_dist = None
    closest_name = None

    names = webcolors.names("css3")

    for name in names:
        hexv = webcolors.name_to_hex(name, spec="css3")
        cr, cg, cb = webcolors.hex_to_rgb(hexv)

        dist = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if min_dist is None or dist < min_dist:
            min_dist = dist
            closest_name = name

    return closest_name


def analyze_image_colors(image_path, n_colors=15, exact_threshold=256):

    img = Image.open(image_path).convert("RGB")
    unique_colors = len(set(img.getdata()))

    if unique_colors <= exact_threshold:
        palette = exact_palette_with_percentages(image_path, max_colors=n_colors)
    else:
        palette = quantized_palette_with_percentages(image_path, n_colors=n_colors, resize=300)

    for entry in palette:
        entry["name"] = closest_color_name(entry["rgb"])
        entry["rgb_name"] = f"RGB{entry['rgb']}"

    return palette
