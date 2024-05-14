from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

def analyze_colors_from_image(image_path, num_colors=5):
    image = Image.open(image_path)
    image = image.resize((150, 150))  # Resize the image for faster processing
    pixels = np.array(image)
    pixels = pixels.reshape((-1, 3))

    # Perform K-means clustering to find dominant colors
    kmeans = KMeans(n_clusters=num_colors)
    kmeans.fit(pixels)

    # Get the dominant colors
    dominant_colors = kmeans.cluster_centers_.astype(int)

    # Convert RGB to hex
    hex_colors = ['#' + ''.join(f'{c:02x}' for c in color) for color in dominant_colors]

    return hex_colors