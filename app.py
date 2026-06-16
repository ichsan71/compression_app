"""
Aplikasi Komparasi Kompresi Citra (JPEG & Format Lain)
======================================================
Streamlit app untuk membandingkan hasil kompresi citra:
  1. Komparasi kualitas JPEG (quality 10-100)
  2. Komparasi antar format (JPEG / PNG / WebP / AVIF*)
  3. Batch (banyak gambar) -> tabel & grafik agregat

Metrik kualitas: ukuran file, rasio kompresi, MSE, PSNR, SSIM.

*AVIF aktif jika paket `pillow-avif-plugin` tersedia.

Deploy: GitHub -> Streamlit Community Cloud (main file: app.py)
"""

import io
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

# ---- Dukungan AVIF opsional --------------------------------------------------
try:
    import pillow_avif  # noqa: F401  (registrasi plugin AVIF ke Pillow)
    AVIF_OK = True
except Exception:
    AVIF_OK = False

# ---- Metrik (SSIM) -----------------------------------------------------------
try:
    from skimage.metrics import structural_similarity as ssim_fn
    SKIMAGE_OK = True
except Exception:
    SKIMAGE_OK = False


st.set_page_config(
    page_title="Komparasi Kompresi Citra",
    page_icon="🗜️",
    layout="wide",
)


# =============================================================================
# Fungsi inti
# =============================================================================
@dataclass
class Hasil:
    label: str
    data: bytes
    size: int
    mse: float
    psnr: float
    ssim: float


def to_rgb(img: Image.Image) -> Image.Image:
    """Pastikan gambar dalam mode RGB agar konsisten saat dibandingkan."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def compress(img: Image.Image, fmt: str, quality: int | None = None) -> bytes:
    """Kompres gambar ke format tertentu, kembalikan bytes."""
    buf = io.BytesIO()
    save_kwargs = {}
    fmt = fmt.upper()
    if fmt == "JPG":
        fmt = "JPEG"

    if fmt == "JPEG":
        save_kwargs = {"quality": int(quality), "optimize": True}
    elif fmt == "WEBP":
        save_kwargs = {"quality": int(quality)} if quality is not None else {"lossless": True}
    elif fmt == "AVIF":
        save_kwargs = {"quality": int(quality)} if quality is not None else {}
    elif fmt == "PNG":
        save_kwargs = {"optimize": True}  # PNG = lossless

    img.save(buf, format=fmt, **save_kwargs)
    return buf.getvalue()


def mse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2))


def psnr(a: np.ndarray, b: np.ndarray) -> float:
    m = mse(a, b)
    if m == 0:
        return float("inf")
    return 20 * math.log10(255.0) - 10 * math.log10(m)


def ssim(a: np.ndarray, b: np.ndarray) -> float:
    if not SKIMAGE_OK:
        return float("nan")
    # SSIM pada grayscale (lebih stabil & cepat)
    ga = np.asarray(Image.fromarray(a).convert("L"))
    gb = np.asarray(Image.fromarray(b).convert("L"))
    return float(ssim_fn(ga, gb, data_range=255))


def evaluate(original: Image.Image, compressed_bytes: bytes, label: str) -> Hasil:
    """Hitung semua metrik dengan membandingkan gambar hasil decode vs original."""
    orig_arr = np.asarray(original)
    comp_img = to_rgb(Image.open(io.BytesIO(compressed_bytes)))
    # samakan ukuran bila berbeda (jaga-jaga)
    if comp_img.size != original.size:
        comp_img = comp_img.resize(original.size)
    comp_arr = np.asarray(comp_img)
    return Hasil(
        label=label,
        data=compressed_bytes,
        size=len(compressed_bytes),
        mse=mse(orig_arr, comp_arr),
        psnr=psnr(orig_arr, comp_arr),
        ssim=ssim(orig_arr, comp_arr),
    )


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def fmt_psnr(v: float) -> str:
    return "∞" if math.isinf(v) else f"{v:.2f}"


def available_formats() -> list[str]:
    fmts = ["JPEG", "PNG", "WEBP"]
    if AVIF_OK:
        fmts.append("AVIF")
    return fmts


# =============================================================================
# UI
# =============================================================================
st.title("🗜️ Komparasi Kompresi Citra")
st.caption(
    "Bandingkan ukuran file dan kualitas (MSE, PSNR, SSIM) hasil kompresi "
    "JPEG pada berbagai level, antar format gambar, atau secara batch."
)

if not SKIMAGE_OK:
    st.warning("scikit-image tidak terpasang — nilai SSIM tidak akan dihitung.")
if not AVIF_OK:
    st.info("Format AVIF tidak aktif (paket `pillow-avif-plugin` tidak tersedia).")

tab1, tab2, tab3, tab_help = st.tabs(
    ["🎚️ Kualitas JPEG", "🔀 Antar Format", "📦 Batch", "ℹ️ Tentang"]
)


# -----------------------------------------------------------------------------
# TAB 1 — Komparasi kualitas JPEG
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Komparasi level kualitas JPEG")
    up = st.file_uploader(
        "Unggah gambar", type=["jpg", "jpeg", "png", "bmp", "webp"], key="t1"
    )
    qualities = st.multiselect(
        "Pilih level quality JPEG",
        options=list(range(10, 101, 5)),
        default=[20, 40, 60, 80, 95],
    )

    if up and qualities:
        original = to_rgb(Image.open(up))
        orig_bytes = up.getvalue()
        st.image(original, caption=f"Original — {human_size(len(orig_bytes))} "
                 f"({original.width}×{original.height})", width=420)

        hasil = [evaluate(original, compress(original, "JPEG", q), f"Q{q}")
                 for q in sorted(qualities)]

        rows = []
        for h, q in zip(hasil, sorted(qualities)):
            rows.append({
                "Quality": q,
                "Ukuran": human_size(h.size),
                "Bytes": h.size,
                "Rasio": f"{len(orig_bytes)/h.size:.2f}×",
                "MSE": round(h.mse, 2),
                "PSNR (dB)": fmt_psnr(h.psnr),
                "SSIM": "-" if math.isnan(h.ssim) else round(h.ssim, 4),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df.drop(columns=["Bytes"]), use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Ukuran file vs Quality**")
            st.line_chart(df.set_index("Quality")["Bytes"])
        with c2:
            st.markdown("**PSNR vs Quality**")
            psnr_vals = [h.psnr if not math.isinf(h.psnr) else np.nan for h in hasil]
            st.line_chart(pd.DataFrame({"PSNR": psnr_vals}, index=sorted(qualities)))

        st.markdown("### Pratinjau visual")
        cols = st.columns(min(len(hasil), 4))
        for i, (h, q) in enumerate(zip(hasil, sorted(qualities))):
            with cols[i % len(cols)]:
                st.image(Image.open(io.BytesIO(h.data)),
                         caption=f"Q{q} • {human_size(h.size)} • PSNR {fmt_psnr(h.psnr)}")
                st.download_button(f"⬇️ Q{q}", h.data, file_name=f"jpeg_q{q}.jpg",
                                   mime="image/jpeg", key=f"dl1_{q}")


# -----------------------------------------------------------------------------
# TAB 2 — Komparasi antar format
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("Komparasi antar format")
    up2 = st.file_uploader(
        "Unggah gambar", type=["jpg", "jpeg", "png", "bmp", "webp"], key="t2"
    )
    fmts = st.multiselect("Format yang dibandingkan", available_formats(),
                          default=available_formats())
    q2 = st.slider("Quality (untuk JPEG/WEBP/AVIF)", 10, 100, 80, 5)

    if up2 and fmts:
        original = to_rgb(Image.open(up2))
        orig_bytes = up2.getvalue()
        st.image(original, caption=f"Original — {human_size(len(orig_bytes))}", width=420)

        hasil = []
        for f in fmts:
            q = None if f == "PNG" else q2
            try:
                b = compress(original, f, q)
                hasil.append(evaluate(original, b, f))
            except Exception as e:
                st.error(f"Gagal kompres {f}: {e}")

        rows = [{
            "Format": h.label,
            "Ukuran": human_size(h.size),
            "Bytes": h.size,
            "Rasio": f"{len(orig_bytes)/h.size:.2f}×",
            "PSNR (dB)": fmt_psnr(h.psnr),
            "SSIM": "-" if math.isnan(h.ssim) else round(h.ssim, 4),
        } for h in hasil]
        df2 = pd.DataFrame(rows)
        st.dataframe(df2.drop(columns=["Bytes"]), use_container_width=True, hide_index=True)
        st.markdown("**Ukuran file per format**")
        st.bar_chart(df2.set_index("Format")["Bytes"])

        cols = st.columns(min(len(hasil), 4))
        for i, h in enumerate(hasil):
            ext = h.label.lower().replace("jpeg", "jpg")
            with cols[i % len(cols)]:
                st.image(Image.open(io.BytesIO(h.data)),
                         caption=f"{h.label} • {human_size(h.size)}")
                st.download_button(f"⬇️ {h.label}", h.data,
                                   file_name=f"out.{ext}", key=f"dl2_{h.label}")


# -----------------------------------------------------------------------------
# TAB 3 — Batch
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("Batch — banyak gambar")
    ups = st.file_uploader(
        "Unggah beberapa gambar", type=["jpg", "jpeg", "png", "bmp", "webp"],
        accept_multiple_files=True, key="t3",
    )
    cfmt = st.selectbox("Format target", available_formats(), index=0)
    cq = st.slider("Quality", 10, 100, 75, 5,
                   disabled=(cfmt == "PNG"), key="bq")

    if ups:
        rows = []
        for f in ups:
            try:
                original = to_rgb(Image.open(f))
                orig_bytes = f.getvalue()
                q = None if cfmt == "PNG" else cq
                h = evaluate(original, compress(original, cfmt, q), f.name)
                rows.append({
                    "File": f.name,
                    "Original": human_size(len(orig_bytes)),
                    "Kompresi": human_size(h.size),
                    "_orig": len(orig_bytes),
                    "_comp": h.size,
                    "Rasio": round(len(orig_bytes) / h.size, 2),
                    "Hemat %": round((1 - h.size / len(orig_bytes)) * 100, 1),
                    "PSNR (dB)": fmt_psnr(h.psnr),
                    "SSIM": "-" if math.isnan(h.ssim) else round(h.ssim, 4),
                })
            except Exception as e:
                st.error(f"{f.name}: {e}")

        if rows:
            df3 = pd.DataFrame(rows)
            tot_o = df3["_orig"].sum()
            tot_c = df3["_comp"].sum()
            m1, m2, m3 = st.columns(3)
            m1.metric("Total original", human_size(tot_o))
            m2.metric("Total kompresi", human_size(tot_c))
            m3.metric("Total hemat", f"{(1 - tot_c/tot_o)*100:.1f} %")

            st.dataframe(df3.drop(columns=["_orig", "_comp"]),
                         use_container_width=True, hide_index=True)
            st.bar_chart(df3.set_index("File")["Hemat %"])
            st.download_button(
                "⬇️ Unduh hasil (CSV)",
                df3.drop(columns=["_orig", "_comp"]).to_csv(index=False).encode(),
                file_name="hasil_komparasi.csv", mime="text/csv",
            )


# -----------------------------------------------------------------------------
# TAB Tentang
# -----------------------------------------------------------------------------
with tab_help:
    st.markdown(
        """
### Tentang aplikasi
Aplikasi ini membandingkan hasil kompresi citra menggunakan algoritma
kompresi standar yang disediakan oleh pustaka **Pillow**:

- **JPEG** — kompresi *lossy* berbasis DCT + kuantisasi (dikontrol oleh *quality*).
- **WebP / AVIF** — codec modern dengan rasio kompresi lebih baik.
- **PNG** — kompresi *lossless* (DEFLATE), sebagai pembanding tanpa kehilangan data.

#### Metrik kualitas
- **MSE** (Mean Squared Error) — makin kecil makin baik.
- **PSNR** (dB) — makin besar makin baik; > 40 dB umumnya sangat baik.
- **SSIM** (0–1) — kemiripan struktural; makin mendekati 1 makin baik.
- **Rasio kompresi** — ukuran asli ÷ ukuran hasil.

#### Cara deploy ke Streamlit Cloud
1. Push folder ini ke repository GitHub.
2. Buka https://share.streamlit.io → **New app**.
3. Pilih repo, branch, dan main file `app.py` → **Deploy**.
        """
    )
    st.caption("Dibangun dengan Streamlit, Pillow, NumPy, scikit-image.")
