"""
stego_engine.py
───────────────
Core LSB (Least Significant Bit) steganography logic.
Handles encoding and decoding of secret messages inside PNG images.

Works with either file paths OR file-like objects (BytesIO), since
Image.open() / Image.save() from Pillow support both.
"""

from PIL import Image

DELIMITER = "<<END>>"   # Marks the end of a hidden message


# ──────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────

def text_to_binary(text: str) -> str:
    """Convert a string to a binary string (8 bits per character)."""
    return "".join(format(ord(char), "08b") for char in text)


def binary_to_text(binary: str) -> str:
    """Convert a binary string back to readable text."""
    chars = [binary[i:i + 8] for i in range(0, len(binary), 8)]
    return "".join(chr(int(b, 2)) for b in chars if len(b) == 8)


def get_image_capacity(image_source) -> int:
    """Return max number of characters an image can hide."""
    img = Image.open(image_source).convert("RGB")
    w, h = img.size
    return (w * h * 3) // 8 - len(DELIMITER)


# ──────────────────────────────────────────────
#  ENCODE
# ──────────────────────────────────────────────

def encode(image_source, message: str, output_target) -> dict:
    """
    Hide a secret message inside an image.

    Args:
        image_source : Source image path OR file-like object (PNG recommended)
        message      : Secret text to embed
        output_target: Destination path OR file-like object (e.g. BytesIO)

    Returns:
        dict with encoding stats
    """
    img = Image.open(image_source).convert("RGB")
    pixels = list(img.getdata())

    full_message = message + DELIMITER
    binary_msg = text_to_binary(full_message)
    total_bits = len(binary_msg)
    max_capacity = len(pixels) * 3

    if total_bits > max_capacity:
        raise ValueError(
            f"Message too long! Max ≈ {max_capacity // 8 - len(DELIMITER)} characters "
            f"for this image, but got {len(message)} characters."
        )

    encoded_pixels = []
    bit_index = 0

    for pixel in pixels:
        channels = list(pixel)
        new_channels = []
        for ch in channels:
            if bit_index < total_bits:
                new_ch = (ch & 0b11111110) | int(binary_msg[bit_index])
                new_channels.append(new_ch)
                bit_index += 1
            else:
                new_channels.append(ch)
        encoded_pixels.append(tuple(new_channels))

    out_img = Image.new("RGB", img.size)
    out_img.putdata(encoded_pixels)
    out_img.save(output_target, format="PNG")

    return {
        "message_length": len(message),
        "bits_used": total_bits,
        "max_capacity": max_capacity,
        "utilisation_pct": round(total_bits / max_capacity * 100, 2),
    }


# ──────────────────────────────────────────────
#  DECODE
# ──────────────────────────────────────────────

def decode(image_source) -> str:
    """
    Extract a hidden message from a stego image.

    Args:
        image_source : Image path OR file-like object containing a hidden message

    Returns:
        The secret message string, or an empty string if none found.
    """
    img = Image.open(image_source).convert("RGB")
    pixels = list(img.getdata())

    binary_data = []
    for pixel in pixels:
        for channel in pixel:
            binary_data.append(str(channel & 1))
    binary_data = "".join(binary_data)

    decoded = binary_to_text(binary_data)

    if DELIMITER in decoded:
        return decoded.split(DELIMITER)[0]
    else:
        return ""
