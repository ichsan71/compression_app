# 🗜️ Komparasi Kompresi Citra (Streamlit)

Aplikasi web untuk membandingkan hasil kompresi citra: kualitas JPEG pada
berbagai level, perbandingan antar format (JPEG/PNG/WebP/AVIF), dan mode batch
untuk banyak gambar. Setiap hasil dievaluasi dengan metrik **ukuran file,
rasio kompresi, MSE, PSNR,** dan **SSIM**.

## Fitur

- **Kualitas JPEG** — kompres satu gambar pada beberapa level *quality* (10–100), lihat tabel metrik + grafik ukuran/PSNR + pratinjau visual.
- **Antar Format** — bandingkan JPEG vs PNG vs WebP vs AVIF pada *quality* yang sama.
- **Batch** — unggah banyak gambar sekaligus, dapatkan tabel agregat, total penghematan, dan ekspor CSV.

## Jalankan lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

Buka http://localhost:8501

## Deploy ke Streamlit Community Cloud

1. Buat repository GitHub baru dan push semua file ini:

   ```bash
   git init
   git add .
   git commit -m "Komparasi kompresi citra"
   git branch -M main
   git remote add origin https://github.com/<username>/<repo>.git
   git push -u origin main
   ```

2. Buka <https://share.streamlit.io> → **New app**.
3. Pilih repo & branch `main`, set **Main file path** ke `app.py`.
4. Klik **Deploy**. Streamlit Cloud otomatis membaca `requirements.txt`.

## Struktur

```
.
├── app.py                  # aplikasi utama
├── requirements.txt        # dependensi
├── README.md
├── .gitignore
└── .streamlit/config.toml  # tema & batas upload
```

## Catatan

- **AVIF** hanya aktif jika `pillow-avif-plugin` berhasil terpasang. Jika tidak, format AVIF disembunyikan otomatis.
- **PNG** bersifat *lossless* sehingga PSNR-nya tak terhingga (∞) — berguna sebagai acuan kualitas maksimum.
- Batas ukuran unggah diatur di `.streamlit/config.toml` (default 50 MB).

## Algoritma & metrik

| Metrik | Arti | Lebih baik |
|--------|------|-----------|
| MSE    | Mean Squared Error antara piksel asli & hasil | kecil |
| PSNR   | Peak Signal-to-Noise Ratio (dB) | besar |
| SSIM   | Structural Similarity Index (0–1) | mendekati 1 |
| Rasio  | ukuran asli ÷ ukuran hasil | besar |

JPEG/WebP/AVIF adalah kompresi *lossy* (berbasis transformasi + kuantisasi),
sedangkan PNG adalah *lossless* (DEFLATE).
