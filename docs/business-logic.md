# DomainLens --- Business Logic

## 1. Prinsip Umum

-   Setiap kategori pemeriksaan memiliki statusnya sendiri.
-   Kegagalan satu kategori tidak otomatis menggagalkan semua kategori.
-   Sistem hanya boleh menyampaikan kesimpulan yang didukung oleh hasil
    yang tersedia.
-   Waktu dan konteks pemeriksaan harus dicatat pada laporan.
-   Hasil harus menyatakan keterbatasan jika pemeriksaan tidak lengkap.

## 2. Status Pemeriksaan

Status produk yang perlu dibedakan:

-   **Berhasil:** pemeriksaan selesai dan menghasilkan data.
-   **Tidak ditemukan:** pemeriksaan selesai tetapi data atau record
    tertentu tidak ditemukan.
-   **Gagal:** pemeriksaan tidak dapat diselesaikan.
-   **Timeout:** pemeriksaan melewati batas waktu yang ditentukan.
-   **Tidak tersedia:** pemeriksaan atau sumber datanya tidak tersedia
    pada kondisi tersebut.
-   **Dibatasi:** permintaan tidak dilanjutkan karena batas penggunaan
    atau aturan keamanan.

Status teknis modul yang disepakati mengikuti `input-security-policy.md` dan `api-specification.md`: `success`, `not_found`, `failed`, `timeout`, `unavailable`, `rate_limited`.

## 3. Interpretasi Temuan

-   Temuan tidak boleh otomatis diberi label "berbahaya" hanya karena
    satu konfigurasi tidak ditemukan.
-   Ketiadaan sebuah record tidak selalu merupakan kesalahan
    konfigurasi.
-   Status HTTP harus dijelaskan sesuai maknanya; misalnya, 403
    menunjukkan akses ditolak oleh server, bukan bukti bahwa domain
    sedang down.
-   Sertifikat yang valid bukan jaminan seluruh website aman.
-   Hasil dari lingkungan server DomainLens tidak selalu mewakili
    koneksi dari perangkat pengguna.
-   Informasi geolokasi IP harus disebut sebagai perkiraan.

## 4. Skor dan Tingkat Prioritas

-   Tahap 1 tidak menggunakan skor keamanan agregat. Laporan menyajikan status dan detail per modul secara terpisah agar transparan dan tidak menyesatkan.

## 5. Riwayat dan Perbandingan

Untuk fitur tahap 2: - Bandingkan hasil dari dua waktu pemeriksaan. -
Bedakan perubahan nyata dari data yang tidak tersedia pada salah satu
pemeriksaan. - Catat waktu pemeriksaan dan cakupan kategori yang
dijalankan. - `TODO`: Tentukan masa simpan, struktur penyimpanan, dan
aturan penghapusan riwayat.

## 6. Monitoring

Monitoring termasuk tahap 3 dan belum menjadi kebutuhan versi pertama.

Sebelum implementasi, tentukan: - Interval pemeriksaan. - Batas jumlah
domain per pengguna. - Kebijakan notifikasi. - Penyimpanan hasil dan
masa retensi. - Penanganan false positive dan gangguan sementara. -
Batas penggunaan sesuai kemampuan hosting.
