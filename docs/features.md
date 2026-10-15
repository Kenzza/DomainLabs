# DomainLens --- Feature Scope

## 1. Tujuan

Dokumen ini mencatat fitur DomainLens yang disepakati pada tingkat
produk. Detail teknis implementasi belum ditetapkan.

## 2. Tahap 1 --- DomainLens Core

### 2.1 Domain Intelligence

-   Menerima input nama domain.
-   Memeriksa DNS records yang relevan: A, AAAA, CNAME, MX, NS, TXT, dan
    SOA jika tersedia.
-   Menampilkan IP yang ditemukan dan informasi jaringan publik yang
    relevan.
-   Menjelaskan jika record tidak ditemukan atau tidak dapat diperoleh.

### 2.2 Website Inspector

-   Memeriksa status HTTP.
-   Menampilkan redirect chain yang teramati.
-   Menampilkan waktu respons.
-   Menampilkan response headers yang relevan dan aman untuk
    ditampilkan.

### 2.3 TLS & HTTPS Check

-   Memeriksa sertifikat TLS/HTTPS.
-   Menampilkan informasi masa berlaku dan nama domain pada sertifikat
    jika tersedia.
-   Memeriksa sejumlah konfigurasi HTTPS dan header keamanan yang
    relevan.
-   Menjelaskan keterbatasan pemeriksaan agar hasil tidak dianggap
    sebagai audit keamanan penuh.

### 2.4 IP Intelligence

-   Menampilkan informasi IP publik yang relevan.
-   Menampilkan ASN, organisasi jaringan, reverse DNS, atau perkiraan
    lokasi jika data tersedia dari sumber yang sesuai.
-   Menjelaskan bahwa geolokasi IP merupakan perkiraan.

### 2.5 Simple Mode dan Technical Mode

-   Simple Mode: ringkasan, bahasa sederhana, dan temuan utama.
-   Technical Mode: detail teknis, record, status, dan data respons yang
    relevan.
-   Kedua mode menggunakan hasil pemeriksaan yang sama.

### 2.6 Ringkasan dan Ekspor

-   Menampilkan waktu pemeriksaan dan cakupan pemeriksaan.
-   Membedakan sukses, gagal, timeout, dan data yang tidak tersedia.
-   Menyediakan ekspor laporan dalam format JSON dengan schema version `1.0` (dibuat oleh frontend).

## 3. Tahap 2 --- DomainLens Intelligence

-   Domain Investigation Flow yang menghubungkan domain, DNS, IP, HTTP,
    dan TLS.
-   Penjelasan temuan dengan bahasa sederhana.
-   Perbandingan dua hasil pemeriksaan.
-   Riwayat pemeriksaan yang dapat disimpan atau diekspor.
-   Ringkasan potensi masalah dengan prioritas dan alasan yang jelas.

## 4. Tahap 3 --- DomainLens Monitor

-   Monitoring berkala domain pilihan.
-   Notifikasi jika website tidak dapat dijangkau atau sertifikat
    mendekati kedaluwarsa.
-   Deteksi perubahan DNS dan IP.
-   Dashboard untuk beberapa domain.
-   Riwayat insiden dan laporan perubahan.

Fitur ini memerlukan keputusan lanjutan tentang penyimpanan,
penjadwalan, notifikasi, kuota, dan hosting yang berjalan terus-menerus.

## 5. Tidak Termasuk Ruang Lingkup

-   Eksploitasi atau pengujian penetrasi otomatis.
-   Percobaan kata sandi.
-   Pemindaian port agresif atau pemindaian dalam skala besar.
-   Klaim keamanan absolut bahwa domain pasti aman atau berbahaya.
-   Monitoring 24/7 pada tahap pertama.
-   Pemeriksaan dari banyak lokasi dunia pada tahap pertama.

## 6. Aturan Kualitas Hasil

-   Jangan menyamakan record yang tidak ditemukan dengan kegagalan
    seluruh domain.
-   Jangan menyimpulkan bahwa website bermasalah hanya karena satu
    pemeriksaan gagal.
-   Jangan menyimpulkan penyebab gangguan yang belum terbukti.
-   Tampilkan konteks dan waktu pemeriksaan.
-   Jelaskan jika hasil dipengaruhi keterbatasan jaringan, sumber data,
    atau lingkungan server.
