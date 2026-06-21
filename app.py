"""
app.py - Aplikasi utama (Streamlit)
Studi Komparasi Algoritma Kompresi Gambar JPEG

Membandingkan 3 algoritma kompresi pada file gambar JPEG:
  Algo 1 : Vector Quantization (VQ)
  Algo 2 : Block Truncation Coding (BTC)
  Algo 3 : Progressive JPEG Encoding

Menampilkan gambar beserta ukuran file sebelum dan sesudah kompresi,
serta persentase pengurangan ukuran, compression ratio, dan PSNR.
"""

import pandas as pd
import streamlit as st
from PIL import Image

from compression_lib import ALGORITMA
from utils import size_kb, compression_ratio, space_savings, psnr

st.set_page_config(
    page_title="Komparasi Kompresi JPEG",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---- Gaya tampilan ----------------------------------------------------------
st.markdown(
    """
    <style>
      .block-container { padding-top: 2.2rem; max-width: 1200px; }
      .hero {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: #ffffff; padding: 2rem 2.4rem; border-radius: 16px;
        margin-bottom: 1.6rem;
      }
      .hero h1 { color:#fff; font-size: 1.9rem; margin: 0 0 .4rem 0; }
      .hero p { color:#dbeafe; font-size: 1rem; margin: 0; max-width: 760px; }
      .algo-pill {
        display:inline-block; background: rgba(255,255,255,.15);
        color:#fff; padding:.3rem .8rem; border-radius:999px;
        font-size:.82rem; margin:.5rem .4rem 0 0;
      }
      .card {
        background:#ffffff; border:1px solid #e5e7eb; border-radius:14px;
        padding:1.1rem 1.2rem; box-shadow:0 1px 3px rgba(0,0,0,.05);
      }
      .filename { font-weight:700; font-size:1.05rem; color:#111827; }
      .muted { color:#6b7280; font-size:.85rem; }
      .size-orig { font-size:.9rem; color:#374151; }
      .badge-down {
        display:inline-block; background:#dcfce7; color:#166534;
        padding:.15rem .55rem; border-radius:8px; font-weight:600; font-size:.85rem;
      }
      .badge-up {
        display:inline-block; background:#fee2e2; color:#991b1b;
        padding:.15rem .55rem; border-radius:8px; font-weight:600; font-size:.85rem;
      }
      .stDownloadButton button { border-radius:10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>Studi Komparasi Algoritma Kompresi Gambar JPEG</h1>
      <p>Bandingkan tiga algoritma kompresi citra terhadap ukuran file dan
      kualitas visual (PSNR). Unggah satu atau beberapa gambar JPEG untuk memulai.</p>
      <span class="algo-pill">Vector Quantization</span>
      <span class="algo-pill">Block Truncation Coding</span>
      <span class="algo-pill">Progressive JPEG</span>
    </div>
    """,
    unsafe_allow_html=True,
)

files = st.file_uploader(
    "Unggah gambar JPEG (.jpg / .jpeg)",
    type=["jpg", "jpeg"],
    accept_multiple_files=True,
)

if not files:
    st.info("Belum ada file yang diunggah. Pilih satu atau beberapa gambar JPEG di atas.")
    st.stop()

# ---- Proses tiap file -------------------------------------------------------
ringkasan = []

st.markdown(f"**{len(files)} file** siap diproses.")
st.write("")

for idx, f in enumerate(files):
    data_asli = f.getvalue()
    img = Image.open(f)
    kb_asli = size_kb(data_asli)

    with st.container():
        st.markdown(
            f'<span class="filename">{f.name}</span> '
            f'<span class="muted">&nbsp;|&nbsp; {img.width} x {img.height} px '
            f'&nbsp;|&nbsp; ukuran asli {kb_asli:.1f} KB</span>',
            unsafe_allow_html=True,
        )

        kolom = st.columns(len(ALGORITMA) + 1)

        # Gambar asli
        with kolom[0]:
            st.image(img, use_container_width=True)
            st.markdown('<p class="muted">Asli (sebelum kompresi)</p>',
                        unsafe_allow_html=True)
            st.markdown(f'<p class="size-orig">{kb_asli:.1f} KB</p>',
                        unsafe_allow_html=True)

        baris = {"File": f.name, "Asli (KB)": round(kb_asli, 1)}
        hasil_kompresi = []

        for i, (nama, fungsi, ext) in enumerate(ALGORITMA, start=1):
            data = fungsi(img)
            kb = size_kb(data)
            ss = space_savings(data_asli, data)
            cr = compression_ratio(data_asli, data)
            ps = psnr(img, data)
            hasil_kompresi.append((nama, data, kb))

            with kolom[i]:
                st.image(data, use_container_width=True)
                st.markdown(f'<p class="muted">{nama}</p>', unsafe_allow_html=True)
                st.metric(
                    label="Ukuran",
                    value=f"{kb:.1f} KB",
                    delta=f"{-ss:.1f}%",
                    delta_color="inverse",
                )
                st.markdown(
                    f'<p class="muted">Rasio {cr:.2f}x &nbsp;|&nbsp; '
                    f'PSNR {"inf" if ps == float("inf") else f"{ps:.1f}"} dB</p>',
                    unsafe_allow_html=True,
                )
                st.download_button(
                    "Unduh hasil",
                    data,
                    file_name=f"algo{i}_{f.name.rsplit('.', 1)[0]}.{ext}",
                    key=f"dl_{idx}_{i}",
                    use_container_width=True,
                )

            baris[f"Algo {i} (KB)"] = round(kb, 1)
            baris[f"Algo {i} reduksi (%)"] = round(ss, 1)

        best = min(hasil_kompresi, key=lambda x: x[2])
        baris["Best Algo"] = best[0]
        ringkasan.append(baris)

    st.divider()

# ---- Rekap & komparasi ------------------------------------------------------
st.subheader("Tabel Komparasi")
df = pd.DataFrame(ringkasan)
st.dataframe(df, use_container_width=True, hide_index=True)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Rata-rata ukuran per algoritma (KB)**")
    rata = {f"Algo {i}": df[f"Algo {i} (KB)"].mean() for i in (1, 2, 3)}
    st.bar_chart(pd.Series(rata, name="KB"))
with col_b:
    st.markdown("**Rata-rata pengurangan per algoritma (%)**")
    rata_ss = {f"Algo {i}": df[f"Algo {i} reduksi (%)"].mean() for i in (1, 2, 3)}
    st.bar_chart(pd.Series(rata_ss, name="Pengurangan (%)"))

st.download_button(
    "Unduh laporan CSV",
    df.to_csv(index=False).encode(),
    file_name="compression_results.csv",
    mime="text/csv",
)

st.caption(
    "Keterangan: Algo 1 = Vector Quantization, Algo 2 = Block Truncation Coding, "
    "Algo 3 = Progressive JPEG. Best Algo dipilih berdasarkan ukuran file terkecil."
)
