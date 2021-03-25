
from PIL import Image
from PIL import ImageGrab
from audio import CLIENT_SOCKET, sendColorCode, exit


def getDominantColor(image, palette_size=4):
    # *  Resize image to speed up processing
    image.thumbnail((256, 256))

    # * Reduce colors (uses k-means internally)
    paletted = image.convert('P', palette=Image.ADAPTIVE, colors=palette_size)

    # * Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    palette_index = color_counts[0][1]
    dominant_color = palette[palette_index*3:palette_index*3+3]

    return dominant_color


if __name__ == "__main__":
    print("Starting to record screen...")
    try:
        while True:
            screen = ImageGrab.grab()
            r, g, b = getDominantColor(screen)
            sendColorCode(r, g, b, 0)
    except KeyboardInterrupt:
        CLIENT_SOCKET.close()
        print()
        exit()
