"""
compression_lib.py
Library implementasi 3 algoritma kompresi sesuai laporan studi:
  Algoritma 1 : JPEG Standard (DCT)      - Quality 90 (High)
  Algoritma 2 : WebP Modern Codec        - Quality 75 (Balanced)
  Algoritma 3 : JPEG Aggressive (DCT)    - Quality 50 (Max Compress)

Setiap fungsi menerima objek PIL.Image dan mengembalikan data hasil
kompresi dalam bentuk bytes (agar mudah dipakai di aplikasi Streamlit
maupun disimpan ke file).
"""

import io
from PIL import Image


def _to_bytes(img: Image.Image, format_file: str, params: dict) -> bytes:
    if img.mode != "RGB":
        img = img.convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format_file, **params)
    return buffer.getvalue()


def compress_jpeg_high(img: Image.Image) -> bytes:
    """Algoritma 1: JPEG Standard - Quality 90."""
    return _to_bytes(img, "JPEG", {"quality": 90, "optimize": True})


def compress_webp(img: Image.Image) -> bytes:
    """Algoritma 2: WebP Modern Codec - Quality 75."""
    return _to_bytes(img, "WEBP", {"quality": 75, "method": 6})


def compress_jpeg_aggressive(img: Image.Image) -> bytes:
    """Algoritma 3: JPEG Aggressive - Quality 50."""
    return _to_bytes(img, "JPEG", {"quality": 50, "optimize": True})


# Daftar algoritma: (nama, fungsi, ekstensi output)
ALGORITMA = [
    ("Algo 1: JPEG Standard (Q=90)", compress_jpeg_high, "jpeg"),
    ("Algo 2: WebP Codec (Q=75)", compress_webp, "webp"),
    ("Algo 3: JPEG Aggressive (Q=50)", compress_jpeg_aggressive, "jpeg"),
]
