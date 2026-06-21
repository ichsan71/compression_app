"""
compression_lib.py
Implementasi 3 algoritma kompresi citra. Semua hasil disimpan dalam
format/ekstensi JPEG (.jpeg).

  Algoritma 1 : Vector Quantization (VQ)
  Algoritma 2 : Block Truncation Coding (BTC)
  Algoritma 3 : Progressive JPEG Encoding

Setiap fungsi menerima objek PIL.Image dan mengembalikan data hasil
kompresi dalam bentuk bytes.
"""

import io
import numpy as np
from PIL import Image


def _jpeg_bytes(img: Image.Image, quality: int = 95, progressive: bool = False) -> bytes:
    """Simpan gambar (RGB) ke JPEG dan kembalikan bytes."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality, optimize=True, progressive=progressive)
    return buf.getvalue()


# -----------------------------------------------------------------------------
# Algoritma 1: Vector Quantization (VQ)
# -----------------------------------------------------------------------------
def compress_vq(img: Image.Image, codebook_size: int = 64) -> bytes:
    """
    Vector Quantization pada ruang warna.
    Membentuk codebook berisi `codebook_size` vektor warna representatif
    (median cut), lalu memetakan setiap piksel ke codeword terdekat.
    Hasil rekonstruksi disimpan sebagai JPEG.
    """
    rgb = img.convert("RGB")
    # quantize() membangun codebook & memetakan piksel ke codeword terdekat (VQ)
    vq = rgb.quantize(colors=codebook_size, method=Image.Quantize.MEDIANCUT)
    rekonstruksi = vq.convert("RGB")
    return _jpeg_bytes(rekonstruksi, quality=75)


# -----------------------------------------------------------------------------
# Algoritma 2: Block Truncation Coding (BTC)
# -----------------------------------------------------------------------------
def _btc_channel(ch: np.ndarray, block: int = 4) -> np.ndarray:
    """BTC pada satu kanal: tiap blok dipertahankan mean & standar deviasinya."""
    h, w = ch.shape
    ph = (block - h % block) % block
    pw = (block - w % block) % block
    padded = np.pad(ch, ((0, ph), (0, pw)), mode="edge").astype(np.float64)
    H, W = padded.shape
    bi, bj = H // block, W // block

    # susun ulang menjadi (bi, bj, block*block)
    blocks = (padded.reshape(bi, block, bj, block)
                    .swapaxes(1, 2)
                    .reshape(bi, bj, block * block))

    m = blocks.mean(axis=2, keepdims=True)
    sigma = blocks.std(axis=2, keepdims=True)
    mask = blocks >= m                       # bitmap 1-bit
    q = mask.sum(axis=2, keepdims=True)      # jumlah piksel "tinggi"
    p = block * block - q                    # jumlah piksel "rendah"

    pp = np.maximum(p, 1)
    qq = np.maximum(q, 1)
    a = m - sigma * np.sqrt(q / pp)          # nilai rendah
    b = m + sigma * np.sqrt(p / qq)          # nilai tinggi
    rec = np.where(mask, b, a)
    # blok seragam (semua sama) -> pakai mean
    rec = np.where((q == 0) | (p == 0), m, rec)

    rec = (rec.reshape(bi, bj, block, block)
              .swapaxes(1, 2)
              .reshape(H, W))
    return np.clip(rec[:h, :w], 0, 255).astype(np.uint8)


def compress_btc(img: Image.Image, block: int = 4) -> bytes:
    """
    Block Truncation Coding: membagi gambar menjadi blok `block`x`block`,
    tiap blok direpresentasikan oleh dua level (a, b) + bitmap, lalu
    direkonstruksi dan disimpan sebagai JPEG. Diterapkan per kanal RGB.
    """
    arr = np.asarray(img.convert("RGB"))
    kanal = [_btc_channel(arr[:, :, c], block) for c in range(3)]
    hasil = np.stack(kanal, axis=2)
    return _jpeg_bytes(Image.fromarray(hasil), quality=75)


# -----------------------------------------------------------------------------
# Algoritma 3: Progressive JPEG Encoding
# -----------------------------------------------------------------------------
def compress_progressive(img: Image.Image, quality: int = 75) -> bytes:
    """
    Progressive JPEG: koefisien DCT dikodekan secara bertahap (multi-scan)
    sehingga gambar dapat ditampilkan progresif. Disimpan sebagai JPEG.
    """
    return _jpeg_bytes(img, quality=quality, progressive=True)


# Daftar algoritma: (nama, fungsi, ekstensi output)
ALGORITMA = [
    ("Algo 1: Vector Quantization", compress_vq, "jpeg"),
    ("Algo 2: Block Truncation Coding", compress_btc, "jpeg"),
    ("Algo 3: Progressive JPEG", compress_progressive, "jpeg"),
]
