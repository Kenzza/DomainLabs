# DomainLens --- Security and Limitations

## 1. Tujuan

Dokumen ini menetapkan batas keamanan produk dan keterbatasan hasil
pemeriksaan pada tingkat requirement.

## 2. Batas Penggunaan

DomainLens dirancang untuk pemeriksaan domain dan layanan publik yang
diizinkan. Produk tidak mencakup eksploitasi, percobaan kata sandi, atau
pemindaian agresif.

## 3. Perlindungan Backend

Karena backend akan melakukan permintaan jaringan berdasarkan input
pengguna, perlindungan terhadap penyalahgunaan harus menjadi requirement
wajib.

-   Validasi dan normalisasi input domain.
-   Cegah akses ke loopback, alamat privat, link-local, metadata cloud,
    dan alamat sensitif lainnya.
-   Validasi hasil DNS sebelum koneksi dilakukan.
-   Periksa kembali alamat tujuan setelah setiap redirect.
-   Batasi protokol, port, ukuran respons, jumlah redirect, dan waktu
    pemeriksaan sesuai kebutuhan.
-   Terapkan rate limiting dan batas penggunaan.
-   Jangan mengungkapkan secret atau API key privat ke browser.
-   Jangan mengembalikan data internal atau pesan error sensitif kepada
    pengguna.
-   Catat error secukupnya tanpa menyimpan data sensitif yang tidak
    diperlukan.

Detail implementasi keamanan akan ditentukan pada tahap arsitektur.

## 4. Keterbatasan Interpretasi

-   Pemeriksaan dari server DomainLens dapat berbeda dari pengalaman
    pengguna pada jaringan lain.
-   Firewall, CDN, pembatasan geografis, DNS resolver, dan konfigurasi
    jaringan dapat memengaruhi hasil.
-   Informasi registrasi, ASN, organisasi, dan geolokasi bergantung pada
    sumber data dan ketersediaannya.
-   Geolokasi IP bukan bukti lokasi fisik yang pasti.
-   Hasil DNS, HTTP, dan TLS tidak dapat membuktikan keamanan menyeluruh
    suatu website.
-   Hasil yang gagal atau tidak lengkap harus ditandai dengan jelas.

## 5. Privasi dan Retensi

-   Tahap 1 tidak menggunakan database backend atau menyimpan riwayat analisis secara permanen. Riwayat disimpan secara lokal di browser pengguna.
-   Log operasional backend bersifat minimal untuk keperluan troubleshooting reliability dan keamanan, serta tidak menyimpan kredensial atau hasil analisis permanen. Retention log disesuaikan dengan ketentuan hosting provider.

## 6. Ketersediaan dan Biaya

-   Paket gratis dapat memiliki batas penggunaan, kuota, waktu tidur
    layanan, atau ketentuan yang berubah.
-   Monitoring berkelanjutan mungkin membutuhkan layanan yang selalu
    aktif.
-   Hosting kandidat untuk Stage 1: Netlify Free (Frontend) dan Render Free (Backend). *Status: Kandidat, menunggu verifikasi batas paket, outbound DNS/TLS, dan perilaku cold start.*
-   Jangan menjanjikan layanan gratis tanpa batas atau uptime tertentu
    sebelum diverifikasi.
