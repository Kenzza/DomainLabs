# DomainLens --- Project Overview

## 1. Status Dokumen

-   Status: Draft konsep produk
-   Tujuan: Menjadi sumber utama untuk tujuan, ruang lingkup, prinsip,
    dan keputusan produk DomainLens.
-   Catatan: Dokumen ini belum menjadi spesifikasi teknis final.
    Keputusan teknologi, arsitektur, database, dan detail API belum
    ditetapkan.

## 2. Ringkasan Produk

DomainLens adalah website toolkit untuk memeriksa, memahami, dan
menganalisis domain serta konektivitas jaringan dari satu tempat.

Produk ini menggabungkan pemeriksaan domain dan DNS, informasi IP
publik, respons HTTP, sertifikat TLS/HTTPS, penjelasan hasil, dan
laporan. Fokusnya bukan hanya menampilkan data mentah, tetapi membantu
pengguna memahami arti hasil pemeriksaan.

## 3. Tujuan

-   Menyediakan beberapa pemeriksaan domain dan website dalam satu
    tempat.
-   Membantu pengguna umum memahami hasil teknis melalui penjelasan
    sederhana.
-   Menyediakan detail yang relevan untuk developer dan pelajar IT.
-   Menghubungkan hasil pemeriksaan agar pengguna dapat menelusuri
    hubungan domain, DNS, IP, HTTP, dan TLS.
-   Memprioritaskan solusi gratis atau open-source selama masih layak
    dan aman.
-   Menyediakan fondasi yang dapat dikembangkan menjadi fitur riwayat
    dan monitoring.

## 4. Target Pengguna

### Pengguna umum

Membutuhkan informasi yang mudah dimengerti ketika memeriksa domain,
konektivitas, atau masalah akses website.

### Developer dan pelajar IT

Membutuhkan hasil teknis seperti DNS records, respons HTTP, informasi
sertifikat, dan data pemeriksaan yang lebih terperinci.

## 5. Prinsip Pengalaman Pengguna

-   Satu hasil pemeriksaan dapat ditampilkan dalam dua tingkat
    penjelasan.
-   Simple Mode mengutamakan ringkasan dan bahasa yang mudah dimengerti.
-   Technical Mode menampilkan detail teknis yang relevan.
-   Hasil pemeriksaan harus membedakan kondisi sukses, gagal, timeout,
    dan data yang tidak tersedia.
-   DomainLens tidak boleh menyatakan suatu website aman atau berbahaya
    secara pasti tanpa bukti yang memadai.
-   Tampilan harus responsif, mudah digunakan, dan dirancang khusus
    untuk fungsi analisis.

## 6. Pembeda Produk

1.  **Domain Investigation Flow:** menghubungkan domain, DNS, IP, HTTP,
    dan TLS dalam alur investigasi.
2.  **Explain the Results:** menjelaskan arti temuan, kemungkinan
    penyebab, dan langkah pemeriksaan lanjutan tanpa mengklaim penyebab
    yang belum terbukti.
3.  **Comparison and History:** membandingkan hasil pemeriksaan untuk
    menemukan perubahan.

## 7. Strategi Pengembangan

### Tahap 1 --- DomainLens Core

Pemeriksaan DNS, IP lookup, HTTP, TLS, dua mode tampilan, ringkasan
hasil, dan ekspor laporan.

### Tahap 2 --- DomainLens Intelligence

Alur investigasi terpadu, penjelasan temuan yang lebih baik,
perbandingan hasil, dan riwayat pemeriksaan.

### Tahap 3 --- DomainLens Monitor

Monitoring berkala, notifikasi, deteksi perubahan, dan dashboard
beberapa domain.

Monitoring ditunda sampai fondasi pemeriksaan stabil dan kebutuhan
layanan yang berjalan terus-menerus dapat dipenuhi.

## 8. Strategi Biaya

-   Mengutamakan layanan gratis dan pustaka open-source.
-   Tidak mewajibkan akun untuk pemeriksaan dasar.
-   Menghindari ketergantungan pada API berbayar jika bukan kebutuhan
    utama.
-   Riwayat awal dapat menggunakan penyimpanan lokal atau ekspor.
-   Biaya nol tidak dijamin untuk selamanya; paket gratis dapat memiliki
    batas penggunaan atau ketentuan yang berubah.

## 9. Batasan Produk

-   DomainLens berfokus pada pemeriksaan domain dan layanan publik yang
    diizinkan.
-   Tidak melakukan eksploitasi, percobaan kata sandi, atau pemindaian
    agresif.
-   Tidak mengklaim bahwa hasil pemeriksaan menjamin keamanan sebuah
    website.
-   Hasil dari server DomainLens tidak selalu sama dengan kondisi
    koneksi dari perangkat pengguna.
-   Pemeriksaan lintas banyak lokasi dan monitoring 24/7 tidak termasuk
    tahap pertama.

## 10. Kriteria Keberhasilan Versi Pertama

-   Pengguna dapat menjalankan pemeriksaan dasar tanpa akun.
-   DNS, HTTP, dan TLS memberikan hasil yang benar atau status kegagalan
    yang jelas.
-   Simple Mode mudah dipahami.
-   Technical Mode menyediakan detail teknis yang relevan.
-   Laporan dapat diekspor dan tetap bisa dipahami di luar dashboard.
-   Website responsif di desktop dan perangkat seluler.
-   Backend membatasi permintaan dan mencegah akses ke jaringan internal
    melalui input pengguna.
-   Tidak ada rahasia server atau API key privat yang terekspos ke
    browser.

## 11. Keputusan Produk Stage 1 (Final & Kandidat)

-   **Framework & Arsitektur:** Frontend Next.js, Backend Python + FastAPI. (Final)
-   **Hosting Kandidat:** Netlify Free (Frontend) dan Render Free (Backend). *Status: Kandidat, menunggu verifikasi batas paket dan outbound.* (Kandidat)
-   **Database:** Tidak digunakan. Riwayat disimpan lokal di browser. (Final)
-   **Ekspor Laporan:** Format JSON dengan schema version `1.0`. (Final)
-   **IP Intelligence:** Menggunakan `ipapi.co` (free tier). *Status: Kandidat untuk diuji; kuota aktual dan atribusi menunggu verifikasi.* (Kandidat)
-   **Bahasa UI:** Bahasa Indonesia sebagai bahasa default. (Final)
-   **Rate Limit:** 10 permintaan per menit per IP klien (HTTP 429). (Final)

## 12. Keputusan yang Masih Menunggu Verifikasi

-   Verifikasi batas paket dan kemampuan outbound DNS/TLS pada Netlify/Render.
-   Verifikasi kuota aktual, ketentuan penggunaan, dan atribusi `ipapi.co`.
-   Verifikasi durasi cold start aktual pada Render Free tier.
