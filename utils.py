"""
utils.py
Fungsi-fungsi utilitas: perhitungan metrik evaluasi kompresi.

Metrik (sesuai BAB II laporan):
  - Ukuran File (KB)
  - Compression Ratio (CR) = Ukuran Asli / Ukuran Terkompresi
  - Space Savings (%)      = ((Asli - Terkompresi) / Asli) * 100
  - PSNR (dB)              = 10 * log10(MAX^2 / MSE), MAX = 255
"""

import io
import math
import numpy as np
from PIL import Image


def size_kb(data: bytes) -> float:
    """Ukuran data dalam kilobyte."""
    return len(data) / 1024


def compression_ratio(original: bytes, compressed: bytes) -> float:
    """CR = ukuran asli / ukuran terkompresi."""
    return len(original) / len(compressed)


def space_savings(original: bytes, compressed: bytes) -> float:
    """Persentase pengurangan ukuran file."""
    return (1 - len(compressed) / len(original)) * 100


def psnr(original_img: Image.Image, compressed_bytes: bytes) -> float:
    """Peak Signal-to-Noise Ratio (dB) antara gambar asli dan hasil kompresi."""
    a = np.asarray(original_img.convert("RGB"), dtype=np.float64)
    comp = Image.open(io.BytesIO(compressed_bytes)).convert("RGB")
    if comp.size != original_img.size:
        comp = comp.resize(original_img.size)
    b = np.asarray(comp, dtype=np.float64)

    mse = np.mean((a - b) ** 2)
    if mse == 0:
        return float("inf")
    return 10 * math.log10((255.0 ** 2) / mse)
