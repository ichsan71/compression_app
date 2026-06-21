# LAPORAN PROJECT
## Studi Komparasi Algoritma Kompresi Gambar JPEG

**Tiga Algoritma:** Vector Quantization (VQ), Block Truncation Coding (BTC), Progressive JPEG Encoding
**Format File:** JPEG (.jpeg)
**Implementasi:** Python + Streamlit (deploy via GitHub ke Streamlit Community Cloud)

---

## ABSTRAK

Kompresi citra digital bertujuan mengurangi ukuran berkas gambar dengan tetap menjaga kualitas visual pada tingkat yang dapat diterima. Project ini membangun aplikasi berbasis web menggunakan Python dan Streamlit untuk membandingkan tiga algoritma kompresi pada berkas gambar berformat JPEG, yaitu Vector Quantization (VQ), Block Truncation Coding (BTC), dan Progressive JPEG Encoding. Setiap algoritma diukur berdasarkan ukuran berkas, rasio kompresi (Compression Ratio), penghematan ruang (Space Savings), dan kualitas visual melalui Peak Signal-to-Noise Ratio (PSNR). Aplikasi menampilkan gambar beserta ukuran berkas sebelum dan sesudah kompresi sehingga perbedaan ketiga algoritma dapat diamati secara langsung.

---

## BAB I — PENDAHULUAN

### 1.1 Latar Belakang

Pertumbuhan konten visual pada media sosial, aplikasi mobile, dan layanan cloud menyebabkan kebutuhan penyimpanan dan transmisi gambar yang efisien semakin meningkat. Kompresi citra menjadi teknik fundamental untuk menekan ukuran berkas tanpa menurunkan kualitas secara berlebihan. Terdapat banyak pendekatan kompresi, mulai dari yang berbasis transformasi (seperti DCT pada JPEG), berbasis kuantisasi vektor (Vector Quantization), hingga berbasis blok statistik (Block Truncation Coding).

Project ini berfokus pada studi komparasi tiga algoritma yang mewakili pendekatan berbeda: VQ yang bekerja pada ruang warna melalui codebook, BTC yang bekerja pada blok piksel dengan mempertahankan momen statistik, dan Progressive JPEG yang merupakan varian penyandian DCT secara bertahap (multi-scan).

### 1.2 Rumusan Masalah

1. Bagaimana cara kerja masing-masing algoritma VQ, BTC, dan Progressive JPEG dalam mengompresi citra?
2. Seberapa besar pengurangan ukuran berkas yang dihasilkan tiap algoritma?
3. Bagaimana pengaruh tiap algoritma terhadap kualitas visual (PSNR)?
4. Algoritma mana yang paling sesuai untuk skenario penggunaan tertentu?

### 1.3 Tujuan

- Mengimplementasikan tiga algoritma kompresi citra menggunakan Python.
- Membangun antarmuka grafis (web) untuk memudahkan proses kompresi dan perbandingan hasil.
- Menganalisis dan membandingkan hasil kompresi pada sejumlah berkas gambar JPEG.
- Mengukur dan menampilkan ukuran berkas serta persentase pengurangannya.

### 1.4 Manfaat

- Memahami cara kerja tiga keluarga algoritma kompresi yang berbeda.
- Menyediakan referensi empiris pemilihan algoritma sesuai kebutuhan.
- Mengembangkan kemampuan pemrograman Python untuk pengolahan citra.

### 1.5 Batasan Masalah

- Berkas masukan berupa gambar JPEG (.jpg / .jpeg); seluruh keluaran juga disimpan sebagai JPEG.
- Algoritma terbatas pada tiga pilihan: VQ, BTC, dan Progressive JPEG.
- Pengukuran kualitas menggunakan PSNR dan persepsi visual.
- Implementasi menggunakan pustaka Pillow, NumPy, Pandas, dan Streamlit.

---

## BAB II — LANDASAN TEORI

### 2.1 Kompresi Citra: Lossy vs Lossless

Kompresi citra dibagi menjadi *lossless* (data dapat dipulihkan sempurna, contoh PNG) dan *lossy* (sebagian data dibuang demi ukuran lebih kecil, contoh JPEG). Ketiga algoritma pada project ini tergolong *lossy*: VQ membuang variasi warna halus, BTC membuang variasi intensitas dalam blok, dan Progressive JPEG membuang koefisien frekuensi tinggi melalui kuantisasi DCT.

### 2.2 Algoritma 1 — Vector Quantization (VQ)

**Konsep.** Vector Quantization adalah teknik kuantisasi yang memetakan vektor masukan ke sekumpulan vektor representatif (disebut *codeword*) yang tersimpan dalam sebuah *codebook*. Alih-alih menyimpan setiap nilai asli, sistem cukup menyimpan indeks *codeword* terdekat. Pada citra, vektor dapat berupa nilai warna piksel (R, G, B) atau blok kecil piksel.

**Langkah kerja (pada ruang warna):**

1. **Pembentukan codebook.** Dari seluruh warna piksel pada citra, dipilih sejumlah K warna representatif (misalnya K = 64) menggunakan metode *median cut*. K menentukan ukuran codebook; makin kecil K, makin agresif kompresinya.
2. **Pemetaan (encoding).** Setiap piksel dipetakan ke *codeword* (warna) terdekat dalam codebook berdasarkan jarak Euclidean pada ruang RGB.
3. **Rekonstruksi (decoding).** Citra dibangun ulang dengan mengganti tiap indeks dengan warna *codeword*-nya.

**Dasar matematis.** Untuk himpunan *codeword* C = {c₁, c₂, …, c_K}, setiap vektor masukan x dipetakan ke:

> Q(x) = c_j sedemikian sehingga ‖x − c_j‖ minimum untuk semua j.

Tujuan pelatihan codebook adalah meminimalkan distorsi rata-rata D = (1/N) Σ ‖xᵢ − Q(xᵢ)‖². Median cut membagi ruang warna secara rekursif pada sumbu dengan rentang terbesar sehingga tiap partisi memuat jumlah piksel yang seimbang.

**Karakteristik.** VQ efektif untuk citra dengan jumlah warna dominan terbatas (ilustrasi, grafis, UI). Efek visual khasnya adalah *posterization* (gradasi warna menjadi bertingkat) ketika K kecil.

**Parameter pada implementasi:** codebook_size = 64, metode median cut. Hasil rekonstruksi disimpan sebagai JPEG quality 75.

### 2.3 Algoritma 2 — Block Truncation Coding (BTC)

**Konsep.** BTC adalah algoritma kompresi blok yang mempertahankan dua momen statistik tiap blok: rata-rata (*mean*) dan standar deviasi. Citra dibagi menjadi blok kecil (umumnya 4×4 piksel). Setiap blok direpresentasikan oleh dua nilai intensitas (a dan b) serta sebuah *bitmap* 1-bit yang menandai piksel mana memakai nilai tinggi dan mana memakai nilai rendah.

**Langkah kerja (per blok, per kanal warna):**

1. **Pembagian blok.** Citra dibagi menjadi blok berukuran n×n (n = 4).
2. **Hitung statistik blok.** Untuk tiap blok dihitung rata-rata m dan standar deviasi σ.
3. **Pembentukan bitmap.** Piksel dengan nilai ≥ m diberi bit 1 (kelompok "tinggi"), sisanya bit 0 (kelompok "rendah"). Misalkan q = jumlah piksel "tinggi" dan p = jumlah piksel "rendah" (p + q = n²).
4. **Hitung dua level rekonstruksi** a dan b sehingga rata-rata dan standar deviasi blok dipertahankan:

> a = m − σ·√(q/p)  (nilai rendah)
> b = m + σ·√(p/q)  (nilai tinggi)

5. **Rekonstruksi blok.** Piksel ber-bit 1 diisi nilai b, piksel ber-bit 0 diisi nilai a. Jika blok seragam (p = 0 atau q = 0), seluruh piksel diisi m.

**Dasar matematis.** Pemilihan a dan b di atas merupakan solusi yang menjaga dua persamaan momen blok:

> p·a + q·b = n²·m   (momen pertama / mean)
> p·a² + q·b² = n²·(m² + σ²)   (momen kedua / energi)

**Karakteristik.** BTC sangat sederhana dan cepat (tanpa transformasi). Pada blok dengan tepi tajam, hasilnya tetap baik; pada area bergradasi halus, dapat muncul efek blok. Karena tiap blok hanya menyimpan dua level + bitmap, detail intra-blok berkurang. Penerapan per kanal RGB menjaga informasi warna.

**Parameter pada implementasi:** ukuran blok 4×4, diterapkan terpisah pada kanal R, G, dan B. Hasil rekonstruksi disimpan sebagai JPEG quality 75.

### 2.4 Algoritma 3 — Progressive JPEG Encoding

**Konsep.** Progressive JPEG adalah varian penyandian standar JPEG. Pipeline dasarnya identik dengan JPEG baseline (konversi warna RGB→YCbCr, pembagian blok 8×8, Discrete Cosine Transform, kuantisasi, dan entropy coding), namun urutan penyandian koefisien berbeda. Pada baseline, tiap blok 8×8 dikodekan utuh secara berurutan; pada progressive, koefisien dikodekan dalam beberapa *scan* bertingkat.

**Langkah kerja:**

1. **Color space conversion.** RGB diubah ke YCbCr untuk memisahkan luminance dan chrominance.
2. **Block splitting & DCT.** Citra dibagi blok 8×8, tiap blok ditransformasi ke domain frekuensi via DCT.
3. **Quantization.** Koefisien DCT dibagi matriks kuantisasi sesuai parameter quality; koefisien frekuensi tinggi banyak dinolkan.
4. **Progressive entropy coding (multi-scan).** Koefisien dikodekan secara bertahap, umumnya kombinasi:
   - *Spectral selection:* koefisien frekuensi rendah dikirim lebih dulu, lalu frekuensi lebih tinggi.
   - *Successive approximation:* bit paling signifikan dikirim lebih dulu, lalu bit-bit penyempurna.

**Dasar matematis (DCT 2D pada blok 8×8):**

> F(u,v) = (1/4)·C(u)·C(v)· Σ_{x=0..7} Σ_{y=0..7} f(x,y)·cos[((2x+1)uπ)/16]·cos[((2y+1)vπ)/16]

dengan C(0) = 1/√2 dan C(k) = 1 untuk k > 0. Kuantisasi: F_q(u,v) = round(F(u,v) / Q(u,v)), dengan Q(u,v) bergantung pada parameter quality.

**Karakteristik.** Progressive JPEG memungkinkan gambar tampil bertahap (buram lalu menajam) saat dimuat — berguna untuk web. Ukuran berkasnya umumnya setara atau sedikit lebih kecil dibanding baseline pada quality yang sama, sambil tetap kompatibel sebagai JPEG.

**Parameter pada implementasi:** quality 75, mode progressive aktif (`progressive=True`, `optimize=True`).

### 2.5 Metrik Evaluasi

| Metrik | Formula | Keterangan |
|---|---|---|
| Ukuran File (KB) | len(bytes) / 1024 | Ukuran berkas hasil kompresi |
| Compression Ratio (CR) | Ukuran Asli / Ukuran Terkompresi | Makin besar makin baik |
| Space Savings (%) | ((Asli − Terkompresi) / Asli) × 100 | Persentase pengurangan ukuran |
| PSNR (dB) | 10 · log₁₀(MAX² / MSE), MAX = 255 | >40 dB Excellent, >30 dB Good |

dengan MSE = (1/N) Σ (asliᵢ − hasilᵢ)² dihitung pada seluruh piksel dan kanal.

**Catatan penting tentang ukuran file.** Ukuran berkas JPEG ditentukan oleh parameter *quality* saat penyimpanan dan kompleksitas citra, bukan semata oleh seberapa "rusak" pikselnya. Karena itu seluruh algoritma menyimpan keluaran pada JPEG quality yang sama (75), sehingga perbedaan ukuran benar-benar mencerminkan efek tiap algoritma terhadap konten citra. Jika berkas asli sudah sangat terkompresi, proses simpan-ulang dapat menambah sedikit overhead — hal ini wajar pada studi re-encoding.

---

## BAB III — METODOLOGI

### 3.1 Alat dan Bahan

**Perangkat lunak:** Python 3.8+; pustaka Pillow, NumPy, Pandas, Streamlit; browser modern; editor/IDE.

**Dataset:** sejumlah berkas gambar JPEG dengan variasi konten dan resolusi (lanskap, potret, arsitektur, makro, teks/grafis, dll.).

### 3.2 Struktur Direktori Project

```
kompresi app streamlit/
├── app.py                  # Antarmuka utama (Streamlit)
├── compression_lib.py      # Implementasi 3 algoritma (VQ, BTC, Progressive JPEG)
├── utils.py                # Fungsi metrik (ukuran, CR, space savings, PSNR)
├── requirements.txt        # Dependensi
├── README.md               # Petunjuk jalankan & deploy
└── .streamlit/config.toml  # Tema & batas upload
```

### 3.3 Alur Kerja Aplikasi

1. Pengguna membuka aplikasi melalui browser (Streamlit).
2. Pengguna mengunggah satu atau beberapa berkas gambar JPEG.
3. Sistem membaca gambar dan menampilkan gambar asli beserta ukurannya.
4. Sistem menjalankan tiga algoritma kompresi pada tiap gambar.
5. Hasil ditampilkan berdampingan dengan gambar asli (sebelum vs sesudah).
6. Sistem menghitung ukuran sebelum/sesudah, persentase pengurangan, rasio, dan PSNR.
7. Pengguna dapat melihat tabel komparasi, grafik, dan mengunduh hasil serta laporan CSV.

---

## BAB IV — IMPLEMENTASI

### 4.1 Instalasi Dependencies

```bash
pip install -r requirements.txt
# streamlit, pillow, numpy, pandas
```

### 4.2 Implementasi Algoritma — compression_lib.py

**Vector Quantization (VQ):**

```python
def compress_vq(img, codebook_size=64):
    rgb = img.convert("RGB")
    # quantize() membangun codebook & memetakan piksel ke codeword terdekat (VQ)
    vq = rgb.quantize(colors=codebook_size, method=Image.Quantize.MEDIANCUT)
    rekonstruksi = vq.convert("RGB")
    return _jpeg_bytes(rekonstruksi, quality=75)
```

**Block Truncation Coding (BTC):** tiap blok 4×4 mempertahankan mean & standar deviasi melalui dua level a dan b serta bitmap; diterapkan per kanal RGB (versi tervektorisasi NumPy untuk kecepatan).

```python
def _btc_channel(ch, block=4):
    # pad ke kelipatan block, susun ulang menjadi blok-blok
    # m = mean blok, sigma = std blok, mask = (piksel >= m)
    # q = jumlah piksel tinggi, p = jumlah piksel rendah
    # a = m - sigma*sqrt(q/p); b = m + sigma*sqrt(p/q)
    # rec = b jika mask else a; blok seragam -> m
    ...
```

**Progressive JPEG:**

```python
def compress_progressive(img, quality=75):
    return _jpeg_bytes(img, quality=quality, progressive=True)
```

### 4.3 Implementasi Metrik — utils.py

```python
def psnr(original_img, compressed_bytes):
    a = np.asarray(original_img.convert("RGB"), float)
    comp = Image.open(io.BytesIO(compressed_bytes)).convert("RGB")
    b = np.asarray(comp, float)
    mse = np.mean((a - b) ** 2)
    return float("inf") if mse == 0 else 10*np.log10(255.0**2 / mse)
```

Fungsi lain: `size_kb`, `compression_ratio`, `space_savings`.

### 4.4 Antarmuka — app.py

Antarmuka dibangun dengan Streamlit, dilengkapi gaya kustom (CSS) berupa header gradien, kartu informasi, dan kartu metrik (ukuran + delta pengurangan). Komponen utama: pengunggah berkas multi-file, tampilan gambar asli dan ketiga hasil secara berdampingan, tabel komparasi, grafik batang rata-rata ukuran dan pengurangan, serta tombol unduh hasil dan laporan CSV.

---

## BAB V — HASIL DAN PEMBAHASAN

### 5.1 Tabel Hasil Kompresi (template — isi setelah eksperimen)

| No. | File | Asli (KB) | VQ (KB) | BTC (KB) | Progressive (KB) | Best Algo | Reduksi terbaik (%) |
|----|------|-----------|---------|----------|------------------|-----------|----------------------|
| 1 | photo_001.jpg | [...] | [...] | [...] | [...] | [...] | [...] |
| 2 | photo_002.jpg | [...] | [...] | [...] | [...] | [...] | [...] |
| … | … | … | … | … | … | … | … |
| 10 | photo_010.jpg | [...] | [...] | [...] | [...] | [...] | [...] |
| | Rata-rata | [...] | [...] | [...] | [...] | — | [...] |

### 5.2 Rekapitulasi Performa Algoritma (template)

| Algoritma | Avg. Ukuran (KB) | Avg. Reduksi (%) | Avg. PSNR (dB) | Kualitas Visual | Catatan |
|---|---|---|---|---|---|
| VQ | [...] | [...] | [...] | bergantung K | Posterization pada K kecil |
| BTC | [...] | [...] | [...] | sedang | Efek blok di area halus |
| Progressive JPEG | [...] | [...] | [...] | baik | Kompatibel web, tampil bertahap |

### 5.3 Analisis

**Vector Quantization.** Efektivitas VQ sangat bergantung pada ukuran codebook (K). Pada citra dengan palet warna terbatas (grafis, ilustrasi, UI), VQ menghasilkan pengurangan baik dengan distorsi kecil. Pada foto dengan gradasi kaya, K = 64 dapat memunculkan posterization. PSNR cenderung menurun seiring mengecilnya K.

**Block Truncation Coding.** BTC unggul pada kesederhanaan dan kecepatan. Karena tiap blok hanya menyimpan dua level intensitas, detail tekstur halus dalam blok berkurang dan dapat muncul efek blok pada area bergradasi. Namun tepi/kontras tinggi tetap terjaga relatif baik karena mekanisme dua level mengikuti distribusi intensitas blok.

**Progressive JPEG.** Sebagai turunan JPEG, Progressive memberi keseimbangan kualitas-ukuran yang baik dan kompatibilitas luas. Keunggulan utamanya adalah penyajian bertahap saat pemuatan, cocok untuk web dan koneksi lambat. Ukuran umumnya setara atau sedikit lebih kecil dari baseline pada quality sama.

---

## BAB VI — KESIMPULAN DAN SARAN

### 6.1 Kesimpulan

1. Ketiga algoritma mewakili pendekatan berbeda: VQ (kuantisasi ruang warna via codebook), BTC (statistik blok mean–std), dan Progressive JPEG (penyandian DCT bertahap).
2. Tidak ada algoritma yang unggul mutlak; pemilihan bergantung pada karakteristik citra dan tujuan penggunaan.
3. VQ cocok untuk citra berpalet terbatas; BTC cocok ketika kecepatan dan kesederhanaan diutamakan; Progressive JPEG cocok untuk distribusi web yang menuntut kompatibilitas dan pemuatan bertahap.
4. Aplikasi Python–Streamlit berhasil mengotomatiskan proses kompresi, perhitungan metrik, dan visualisasi hasil secara interaktif.

### 6.2 Saran

1. Menambah metrik kualitas perseptual seperti SSIM/MS-SSIM untuk gambaran kualitas yang lebih akurat.
2. Menyediakan parameter yang dapat diatur pengguna (ukuran codebook VQ, ukuran blok BTC, quality JPEG) untuk eksperimen trade-off.
3. Memperluas dataset dan menambah algoritma pembanding (mis. JPEG2000, WebP, AVIF).
4. Mengembangkan rekomendasi otomatis algoritma terbaik berdasarkan konten citra.

---

## DAFTAR PUSTAKA

1. Wallace, G. K. (1991). *The JPEG still picture compression standard.* Communications of the ACM, 34(4), 30–44.
2. Gray, R. M. (1984). *Vector Quantization.* IEEE ASSP Magazine, 1(2), 4–29.
3. Delp, E. J., & Mitchell, O. R. (1979). *Image compression using Block Truncation Coding.* IEEE Transactions on Communications, 27(9), 1335–1342.
4. Sayood, K. (2017). *Introduction to Data Compression* (5th ed.). Morgan Kaufmann.
5. Salomon, D. (2007). *Data Compression: The Complete Reference* (4th ed.). Springer.
6. Pillow Development Team. (2023). *Pillow Documentation — Image File Formats.* https://pillow.readthedocs.io
7. Streamlit Inc. (2023). *Streamlit Documentation.* https://docs.streamlit.io

---

*— Akhir Laporan —*
