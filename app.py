"""
app.py - Aplikasi utama (Streamlit)
Studi Komparasi Algoritma Kompresi Gambar JPEG

Membandingkan 3 algoritma kompresi pada file gambar JPEG (minimal 10 file):
  Algo 1 : JPEG Standard (Q=90)
  Algo 2 : WebP Codec (Q=75)
  Algo 3 : JPEG Aggressive (Q=50)

Menampilkan gambar beserta ukuran file sebelum dan sesudah kompresi,
serta persentase pengurangan ukuran (space savings), compression ratio,
dan PSNR.
"""

import pandas as pd
import streamlit as st
from PIL import Image

from compression_lib import ALGORITMA
from utils import size_kb, compression_ratio, space_savings, psnr

st.set_page_config(page_title="Komparasi Kompresi JPEG", layout="wide")

st.title("Studi Komparasi Algoritma Kompresi Gambar JPEG")
st.write(
    "Membandingkan tiga algoritma kompresi: "
    "Vector Quantization (VQ), Block Truncation Coding (BTC), dan "
    "Progressive JPEG Encoding. Unggah satu atau beberapa file gambar JPEG."
)

files = st.file_uploader(
    "Unggah gambar JPEG",
    type=["jpg", "jpeg"],
    accept_multiple_files=True,
)

if not files:
    st.info("Belum ada file. Silakan unggah gambar JPEG.")
    st.stop()

st.write(f"Jumlah file diunggah: {len(files)}")

ringkasan = []

for idx, f in enumerate(files):
    data_asli = f.getvalue()
    img = Image.open(f)
    kb_asli = size_kb(data_asli)

    st.subheader(f.name)
    st.caption(f"Resolusi {img.width} x {img.height} px")

    kolom = st.columns(len(ALGORITMA) + 1)

    # Gambar asli (sebelum kompresi)
    with kolom[0]:
        st.image(img, caption="Asli (sebelum)", use_container_width=True)
        st.write(f"Ukuran: {kb_asli:.1f} KB")

    baris = {"File": f.name, "Asli (KB)": round(kb_asli, 1)}
    hasil_kompresi = []

    # Tiap algoritma (sesudah kompresi)
    for i, (nama, fungsi, ext) in enumerate(ALGORITMA, start=1):
        data = fungsi(img)
        kb = size_kb(data)
        ss = space_savings(data_asli, data)
        cr = compression_ratio(data_asli, data)
        ps = psnr(img, data)
        hasil_kompresi.append((nama, data, ext, kb, ss, cr, ps))

        with kolom[i]:
            st.image(data, caption=nama, use_container_width=True)
            st.write(f"Ukuran: {kb:.1f} KB")
            st.write(f"Pengurangan: {ss:.1f}%")
            st.write(f"PSNR: {'inf' if ps == float('inf') else f'{ps:.2f}'} dB")
            st.download_button(
                "Unduh", data,
                file_name=f"algo{i}_{f.name.rsplit('.', 1)[0]}.{ext}",
                key=f"dl_{idx}_{i}",
            )

        baris[f"Algo {i} (KB)"] = round(kb, 1)
        baris[f"Algo {i} reduksi (%)"] = round(ss, 1)

    # Algoritma terbaik = ukuran terkecil
    best = min(hasil_kompresi, key=lambda x: x[3])
    baris["Best Algo"] = best[0]
    ringkasan.append(baris)
    st.divider()

# ---- Tabel komparasi & rekap ------------------------------------------------
st.header("Tabel Komparasi")
df = pd.DataFrame(ringkasan)
st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Rata-rata ukuran per algoritma (KB)")
rata = {f"Algo {i}": df[f"Algo {i} (KB)"].mean() for i in (1, 2, 3)}
st.bar_chart(pd.Series(rata, name="KB"))

st.subheader("Rata-rata pengurangan per algoritma (%)")
rata_ss = {f"Algo {i}": df[f"Algo {i} reduksi (%)"].mean() for i in (1, 2, 3)}
st.bar_chart(pd.Series(rata_ss, name="Pengurangan (%)"))

st.download_button(
    "Unduh laporan CSV",
    df.to_csv(index=False).encode(),
    file_name="compression_results.csv",
    mime="text/csv",
)
