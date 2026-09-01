"""
Steganography Tool - LSB (Least Significant Bit) Method
Hides secret text messages inside PNG images.

Usage:
  Encode: python steganography.py encode <image.png> <"secret message"> <output.png>
  Decode: python steganography.py decode <image.png>
  Demo:   python steganography.py demo
"""

from PIL import Image
import sys
import os


# ─────────────────────────────────────────────
#  CORE FUNCTIONS
# ─────────────────────────────────────────────

DELIMITER = "<<END>>"  # Marks the end of the hidden message


def text_to_binary(text: str) -> str:
    """Convert a string to its binary representation."""
    return "".join(format(ord(char), "08b") for char in text)


def binary_to_text(binary: str) -> str:
    """Convert a binary string back to readable text."""
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return "".join(chr(int(b, 2)) for b in chars if len(b) == 8)


def encode_message(image_path: str, message: str, output_path: str) -> None:
    """
    Hide a secret message inside an image using LSB steganography.

    Args:
        image_path  : Path to the original (carrier) image (PNG recommended)
        message     : The secret text to hide
        output_path : Where to save the new image containing the hidden message
    """
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    # Append delimiter so the decoder knows where to stop
    full_message = message + DELIMITER
    binary_message = text_to_binary(full_message)
    total_bits = len(binary_message)

    # Each pixel holds 3 channels (R, G, B) → 3 bits per pixel
    max_capacity = len(pixels) * 3
    if total_bits > max_capacity:
        raise ValueError(
            f"Message too long! "
            f"Need {total_bits} bits, but image only holds {max_capacity} bits.\n"
            f"Maximum message length ≈ {max_capacity // 8 - len(DELIMITER)} characters."
        )

    print(f"[INFO] Image capacity : {max_capacity} bits ({max_capacity // 8} bytes)")
    print(f"[INFO] Message size   : {total_bits} bits ({total_bits // 8} bytes)")
    print(f"[INFO] Utilisation    : {total_bits / max_capacity * 100:.2f}%")

    encoded_pixels = []
    bit_index = 0

    for pixel in pixels:
        r, g, b = pixel
        channels = [r, g, b]
        new_channels = []

        for channel in channels:
            if bit_index < total_bits:
                # Replace the LSB of this channel with the next message bit
                new_value = (channel & 0b11111110) | int(binary_message[bit_index])
                new_channels.append(new_value)
                bit_index += 1
            else:
                new_channels.append(channel)

        encoded_pixels.append(tuple(new_channels))

    # Save the new image
    encoded_img = Image.new("RGB", img.size)
    encoded_img.putdata(encoded_pixels)
    encoded_img.save(output_path)
    print(f"[✓] Message hidden successfully → saved to '{output_path}'")


def decode_message(image_path: str) -> str:
    """
    Extract a hidden message from a steganographic image.

    Args:
        image_path : Path to the image containing a hidden message

    Returns:
        The extracted secret message as a string.
    """
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    binary_data = ""
    for pixel in pixels:
        for channel in pixel:  # R, G, B
            binary_data += str(channel & 1)  # Extract LSB

    # Decode bits to text and stop at delimiter
    decoded_text = binary_to_text(binary_data)
    if DELIMITER in decoded_text:
        secret = decoded_text.split(DELIMITER)[0]
        return secret
    else:
        return "[!] No hidden message found (or wrong image)."


# ─────────────────────────────────────────────
#  DEMO: Create a test image and run encode/decode
# ─────────────────────────────────────────────

def run_demo():
    """Create a simple test image, hide a message, then extract it."""
    print("\n" + "="*55)
    print("  STEGANOGRAPHY DEMO")
    print("="*55)

    # 1. Create a small colourful test image
    test_img_path = "test_carrier.png"
    output_img_path = "stego_output.png"
    secret_message = "Hello! This message is hidden inside the image. 🕵️"

    width, height = 200, 200
    img = Image.new("RGB", (width, height))
    pixels = []
    for y in range(height):
        for x in range(width):
            r = (x * 255) // width
            g = (y * 255) // height
            b = 128
            pixels.append((r, g, b))
    img.putdata(pixels)
    img.save(test_img_path)
    print(f"\n[1] Created test image : '{test_img_path}' ({width}x{height} px)")

    # 2. Encode the secret message
    print(f"\n[2] Hiding message     : \"{secret_message}\"")
    encode_message(test_img_path, secret_message, output_img_path)

    # 3. Decode and verify
    print(f"\n[3] Extracting from    : '{output_img_path}'")
    extracted = decode_message(output_img_path)
    print(f"[✓] Extracted message  : \"{extracted}\"")

    # 4. Verify pixel difference is minimal
    original = list(Image.open(test_img_path).getdata())
    modified = list(Image.open(output_img_path).getdata())
    changed = sum(1 for a, b in zip(original, modified) if a != b)
    print(f"\n[4] Pixels changed     : {changed} / {len(original)} "
          f"({changed / len(original) * 100:.2f}%) — visually identical!")

    print("\n" + "="*55)
    print("  Demo complete! Check the two PNG files.")
    print("="*55 + "\n")

    # Cleanup test files
    for f in [test_img_path, output_img_path]:
        if os.path.exists(f):
            os.remove(f)


# ─────────────────────────────────────────────
#  CLI INTERFACE
# ─────────────────────────────────────────────

def print_usage():
    print("""
Usage:
  python steganography.py encode <input.png> "<message>" <output.png>
  python steganography.py decode <image.png>
  python steganography.py demo

Examples:
  python steganography.py encode photo.png "Top secret!" hidden.png
  python steganography.py decode hidden.png
  python steganography.py demo
""")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print_usage()

    elif args[0] == "demo":
        run_demo()

    elif args[0] == "encode":
        if len(args) != 4:
            print("[!] Encode needs: <input.png> <message> <output.png>")
            print_usage()
        else:
            _, input_img, message, output_img = args
            encode_message(input_img, message, output_img)

    elif args[0] == "decode":
        if len(args) != 2:
            print("[!] Decode needs: <image.png>")
            print_usage()
        else:
            result = decode_message(args[1])
            print(f"[✓] Hidden message: \"{result}\"")

    else:
        print(f"[!] Unknown command: '{args[0]}'")
        print_usage()
