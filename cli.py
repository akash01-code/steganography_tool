"""LSB steganography. Usage: steganography.py encode in.png "msg" out.png | decode img.png | test"""
import sys
from PIL import Image


def encode(src, msg, out):
    data = msg.encode()
    data = len(data).to_bytes(4, "big") + data  # length prefix, no delimiter
    img = Image.open(src).convert("RGB")
    px = bytearray(img.tobytes())
    if len(data) * 8 > len(px):
        raise ValueError(f"Too long: need {len(data) * 8} bits, image holds {len(px)}")
    for i in range(len(data) * 8):
        px[i] = (px[i] & 0xFE) | (data[i // 8] >> (7 - i % 8)) & 1
    Image.frombytes("RGB", img.size, bytes(px)).save(out)  # out must be lossless (PNG)


def decode(src):
    px = Image.open(src).convert("RGB").tobytes()
    read = lambda start, n: bytes(
        int("".join(str(px[(start + k) * 8 + j] & 1) for j in range(8)), 2) for k in range(n)
    )
    n = int.from_bytes(read(0, 4), "big")
    if n * 8 > len(px) - 32:
        raise ValueError("No hidden message found")
    return read(4, n).decode()


def _selftest():
    import tempfile
    d = tempfile.mkdtemp()
    Image.new("RGB", (50, 50), (10, 200, 30)).save(f"{d}/a.png")
    m = "Hello 🕵️ <<END>> still fine"
    encode(f"{d}/a.png", m, f"{d}/b.png")
    assert decode(f"{d}/b.png") == m
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["encode"] and len(a) == 4: encode(*a[1:])
    elif a[:1] == ["decode"] and len(a) == 2: print(decode(a[1]))
    elif a == ["test"]: _selftest()
    else: sys.exit(__doc__)
