"""LSB steganography engine. Paths or file-like objects both work (Pillow takes either)."""
from PIL import Image

HEADER = 4  # bytes: big-endian message length, replaces the <<END>> delimiter


def get_image_capacity(src) -> int:
    """Max message size in bytes."""
    w, h = Image.open(src).size
    return w * h * 3 // 8 - HEADER


def encode(src, message, out) -> dict:
    data = message.encode()
    data = len(data).to_bytes(HEADER, "big") + data
    img = Image.open(src).convert("RGB")
    px = bytearray(img.tobytes())
    bits = len(data) * 8
    if bits > len(px):
        raise ValueError(
            f"Message too long! Max ≈ {len(px) // 8 - HEADER} bytes for this image, "
            f"got {len(data) - HEADER}."
        )
    for i in range(bits):
        px[i] = (px[i] & 0xFE) | (data[i // 8] >> (7 - i % 8)) & 1
    Image.frombytes("RGB", img.size, bytes(px)).save(out, format="PNG")
    return {
        "message_length": len(message),
        "bits_used": bits,
        "max_capacity": len(px),
        "utilisation_pct": round(bits / len(px) * 100, 2),
    }


def decode(src) -> str:
    """Hidden message, or "" if none found."""
    px = Image.open(src).convert("RGB").tobytes()
    read = lambda start, n: bytes(
        int("".join(str(px[(start + k) * 8 + j] & 1) for j in range(8)), 2) for k in range(n)
    )
    n = int.from_bytes(read(0, HEADER), "big")
    if not n or n * 8 > len(px) - HEADER * 8:
        return ""
    try:
        return read(HEADER, n).decode()
    except UnicodeDecodeError:  # random image whose LSBs happened to look like a small length
        return ""


if __name__ == "__main__":
    import io
    src = io.BytesIO()
    Image.new("RGB", (50, 50), (10, 200, 30)).save(src, format="PNG")
    out, msg = io.BytesIO(), "Hello 🕵️ <<END>> still fine"
    encode(io.BytesIO(src.getvalue()), msg, out)
    assert decode(io.BytesIO(out.getvalue())) == msg
    assert decode(io.BytesIO(src.getvalue())) == ""  # clean image → nothing found
    print("ok")
