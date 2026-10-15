# DomainLens --- User Flow

## 1. Tujuan

Dokumen ini mendefinisikan alur pengguna tingkat produk untuk
pemeriksaan domain. Detail UI dan implementasi akan ditentukan kemudian.

## 2. Alur Pemeriksaan Utama

1.  Pengguna membuka DomainLens.
2.  Pengguna memasukkan nama domain.
3.  Sistem memvalidasi format input.
4.  Pengguna memilih pemeriksaan ringkas atau kategori pemeriksaan
    tertentu.
5.  Sistem menjalankan pemeriksaan yang didukung.
6.  Sistem mengumpulkan hasil dan status setiap pemeriksaan.
7.  Sistem menampilkan ringkasan dalam Simple Mode atau detail dalam
    Technical Mode.
8.  Pengguna dapat membuka rincian, mengunduh laporan, atau menjalankan
    pemeriksaan lain.

## 3. Perilaku Input

-   Input kosong harus ditolak dengan pesan yang jelas.
-   Input dengan format domain yang tidak valid harus mendapat
    penjelasan.
-   Input dapat berupa domain saja (`example.com`) atau URL lengkap (`https://example.com/path`). Normalisasi mengikuti `input-security-policy.md` (default HTTPS, tolak IP literal dan port non-standar 80/443).
-   Input tidak boleh digunakan untuk mengakses alamat internal atau
    layanan sensitif.
-   Redirect dan resolusi DNS harus diperiksa agar tidak melewati
    perlindungan akses jaringan.

## 4. Tampilan Hasil

### Simple Mode

Menampilkan ringkasan, temuan utama, penjelasan singkat, waktu
pemeriksaan, dan langkah lanjutan yang relevan.

### Technical Mode

Menampilkan hasil per kategori, record atau nilai yang ditemukan, status
pemeriksaan, serta detail teknis yang relevan.

## 5. Alur Kegagalan

Jika pemeriksaan tertentu gagal: 1. Tampilkan status kegagalan untuk
pemeriksaan tersebut. 2. Jelaskan penyebab yang diketahui atau
kemungkinan penyebab dengan bahasa yang tidak memastikan hal yang belum
terbukti. 3. Tetap tampilkan hasil pemeriksaan lain yang berhasil. 4.
Berikan opsi untuk mengulang pemeriksaan jika sesuai.

Kondisi yang perlu dibedakan: - Domain tidak valid. - Record tidak
ditemukan. - Timeout. - Koneksi ditolak atau tidak dapat dijangkau. -
Sertifikat tidak dapat diperiksa. - Respons HTTP tidak tersedia. -
Sumber data eksternal tidak tersedia. - Batas permintaan tercapai.

## 6. Riwayat dan Laporan

-   Tahap 1: Pengguna dapat mengekspor hasil pemeriksaan dalam format JSON (schema version `1.0`) yang dihasilkan oleh frontend. Riwayat pemeriksaan disimpan secara lokal di browser (localStorage) tanpa database server.

## 7. Akun

-   Pemeriksaan dasar tidak mewajibkan akun.
-   `TODO`: Tentukan apakah fitur riwayat tersinkronisasi dan monitoring
    memerlukan akun pada tahap berikutnya.
