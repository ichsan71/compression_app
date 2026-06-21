# Studi Komparasi Algoritma Kompresi Gambar JPEG

Aplikasi Python (Streamlit) untuk membandingkan tiga algoritma kompresi pada
file gambar JPEG, sesuai laporan studi komparasi.

## Tiga algoritma

| # | Algoritma | Format Output | Keterangan |
|---|-----------|---------------|------------|
| 1 | Vector Quantization (VQ) | .jpeg | Codebook warna (median cut), 64 codeword |
| 2 | Block Truncation Coding (BTC) | .jpeg | Blok 4x4, pertahankan mean & std per kanal |
| 3 | Progressive JPEG Encoding | .jpeg | DCT multi-scan, quality 75 |

## Fitur

- Antarmuka unggah gambar JPEG (satu atau banyak file).
- Menampilkan gambar beserta ukuran file sebelum dan sesudah kompresi.
- Persentase pengurangan ukuran (space savings), compression ratio, dan PSNR.
- Tabel komparasi, grafik batang, tombol unduh hasil, dan ekspor CSV.

## Struktur project

```
app.py             Aplikasi utama (antarmuka Streamlit)
compression_lib.py Library 3 algoritma kompresi (VQ, BTC, Progressive JPEG)
utils.py           Fungsi metrik (ukuran, CR, space savings, PSNR)
requirements.txt   Dependensi
```

## Metrik evaluasi

- Ukuran File (KB)
- Compression Ratio (CR) = Ukuran Asli / Ukuran Terkompresi
- Space Savings (%) = ((Asli - Terkompresi) / Asli) x 100
- PSNR (dB) = 10 x log10(MAX^2 / MSE), MAX = 255 (>40 dB Excellent, >30 dB Good)

## Jalankan lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

Buka http://localhost:8501

## Deploy ke Streamlit Community Cloud

1. Push folder ini ke GitHub:

   ```bash
   git init
   git add .
   git commit -m "Studi komparasi kompresi JPEG"
   git branch -M main
   git remote add origin https://github.com/<username>/<repo>.git
   git push -u origin main
   ```

2. Buka https://share.streamlit.io -> New app.
3. Pilih repo, branch `main`, main file `app.py`, lalu Deploy.
