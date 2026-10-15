# DomainLens --- Dokumen Arsitektur Teknis

**Status:** Draft perencanaan\
**Versi:** 0.1\
**Tujuan:** Menjadi acuan teknis sebelum implementasi dimulai. Dokumen
ini tidak berarti aplikasi sudah dibuat atau keputusan yang belum
diverifikasi sudah final.

## 1. Ringkasan

DomainLens adalah website untuk membantu pengguna memeriksa dan memahami
informasi domain serta konektivitas layanan publik. Aplikasi memiliki
dua mode tampilan:

-   **Simple Mode:** ringkasan dan penjelasan dengan bahasa yang mudah
    dipahami.
-   **Technical Mode:** detail teknis, record, status pemeriksaan,
    header, dan data terkait.

Kedua mode menggunakan hasil pemeriksaan yang sama; perbedaannya hanya
pada kedalaman informasi yang ditampilkan.

## 2. Keputusan arsitektur yang telah disepakati

  -----------------------------------------------------------------------
  Area                    Keputusan awal          Status
  ----------------------- ----------------------- -----------------------
  Frontend                Next.js, project        Disepakati
                          terpisah                

  Backend                 Python + FastAPI        Disepakati
                          (`dnspython`, `httpx`,  
                          `ssl`)                  

  Bahasa UI               Bahasa Indonesia        Disepakati

  Komunikasi              REST API melalui HTTPS  Disepakati

  Penyimpanan Stage 1     Tanpa database; riwayat Disepakati
                          lokal di browser        

  Ekspor Laporan          JSON (schema version    Disepakati
                          1.0)                    

  IP Intelligence         ipapi.co (free tier)    Kandidat untuk diuji;
                                                  memerlukan verifikasi
                                                  kuota dan atribusi

  Rate Limiting           10 req/min/IP (HTTP 429 Disepakati
                          + Retry-After)          

  Frontend hosting        Netlify Free            Kandidat, menunggu
                                                  verifikasi batas paket

  Backend hosting         Render Free             Kandidat, menunggu
                                                  verifikasi cold start
                                                  dan outbound

  Akun pengguna           Tidak diperlukan        Disepakati
  -----------------------------------------------------------------------

## 3. Diagram komponen

``` text
Browser pengguna
    |
    | HTTPS / REST API
    v
Frontend Next.js (Netlify)
    |
    | HTTPS request ke API backend
    v
Backend FastAPI (Render)
    |
    +--> Modul DNS
    +--> Modul IP Intelligence
    +--> Modul HTTP Inspector
    +--> Modul TLS & Security
    +--> Modul Network Diagnostics
    |
    +--> Resolver DNS dan sumber data publik yang diperlukan
```

Frontend bertanggung jawab atas antarmuka, input pengguna, tampilan
status pemeriksaan, pemformatan hasil untuk Simple/Technical Mode, dan
riwayat lokal. Backend bertanggung jawab atas validasi target,
pelaksanaan pemeriksaan, normalisasi data, batas waktu, pembatasan
permintaan, dan pengamanan akses jaringan.

Backend tidak boleh menjadi proxy umum yang memungkinkan pengguna
mengakses alamat arbitrer. Setiap permintaan pemeriksaan harus melewati
validasi dan kebijakan keamanan.

## 4. Struktur repository yang diusulkan

Struktur ini merupakan usulan dan dapat disesuaikan setelah lingkungan
pengembangan ditentukan.

``` text
DomainLens/
├── docs/
│   ├── project-overview.md
│   ├── features.md
│   ├── user-flow.md
│   ├── business-logic.md
│   ├── security-and-limitations.md
│   └── technical-architecture.md
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   └── package.json
└── backend/
    ├── app/
    │   ├── main.py
    │   ├── api/
    │   ├── schemas/
    │   ├── services/
    │   └── core/
    ├── tests/
    └── requirements.txt
```

Jangan membuat struktur atau file implementasi ini secara otomatis
sebelum dokumen kebutuhan ditinjau dan keputusan yang masih terbuka
diselesaikan. Direktori dan nama modul dapat berubah.

## 5. Tanggung jawab modul backend

### 5.1 Domain Intelligence

-   Menerima domain yang sudah divalidasi.
-   Memeriksa record A, AAAA, CNAME, MX, NS, TXT, dan SOA jika relevan
    dan tersedia.
-   Mengembalikan record yang ditemukan beserta status dan pesan
    keterbatasan.
-   Tidak menganggap record yang tidak ditemukan sebagai bukti tunggal
    kesalahan konfigurasi.

### 5.2 IP Intelligence

-   Menampilkan alamat IP publik yang terkait dengan hasil resolusi.
-   Mengambil ASN, organisasi jaringan, reverse DNS, dan perkiraan
    geolokasi hanya jika sumber data yang dipilih tersedia.
-   Menjelaskan bahwa geolokasi IP bersifat perkiraan dan dapat tidak
    akurat.
-   Sumber data dan kebijakan penggunaan masing-masing masih perlu
    dipilih.

### 5.3 Website Inspector

-   Memeriksa status HTTP, waktu respons, redirect chain, dan header
    yang dipilih.
-   Membatasi timeout, ukuran respons, protokol, dan jumlah redirect.
-   Memvalidasi setiap target redirect sebelum mengaksesnya.

### 5.4 TLS & Security

-   Memeriksa validitas sertifikat, tanggal kedaluwarsa, dan kecocokan
    hostname.
-   Memeriksa sejumlah header keamanan yang telah ditentukan.
-   Tidak mengklaim bahwa website sepenuhnya aman hanya karena TLS valid
    atau header tertentu tersedia.

### 5.5 Network Diagnostics

-   Menjalankan pemeriksaan resolusi DNS dan konektivitas yang layak
    dilakukan dari server.
-   Menjelaskan bahwa hasil server-side dapat berbeda dari pengalaman
    pengguna akibat resolver, CDN, firewall, lokasi, atau kebijakan
    jaringan.
-   Jenis uji latensi dan batasannya perlu ditentukan sebelum
    implementasi.

### 5.6 Report & History

-   Membuat hasil yang dapat diekspor tanpa membutuhkan akun.
-   Menyimpan riwayat Stage 1 di browser pengguna, jika pengguna memilih
    menggunakan fitur tersebut.
-   Tidak mengirim riwayat browser ke server secara default.
-   Format ekspor (misalnya JSON, CSV, atau PDF) belum diputuskan.

## 6. Kontrak API awal

Kontrak di bawah adalah rancangan konseptual, bukan spesifikasi endpoint
final.

### Endpoint kandidat

  -----------------------------------------------------------------------
  Endpoint kandidat                   Tujuan
  ----------------------------------- -----------------------------------
  `GET /api/health`                   Memeriksa kesehatan dasar API tanpa
                                      mengungkap detail internal

  `POST /api/v1/analyze`              Meminta satu analisis domain dan
                                      mengembalikan hasil pemeriksaan
                                      yang tersedia
  -----------------------------------------------------------------------

Contoh permintaan konseptual:

``` json
{
  "target": "example.com",
  "checks": ["dns", "ip", "http", "tls"]
}
```

Contoh struktur respons konseptual:

``` json
{
  "target": "example.com",
  "started_at": "ISO-8601 timestamp",
  "completed_at": "ISO-8601 timestamp",
  "checks": {
    "dns": {
      "status": "success",
      "data": {}
    },
    "http": {
      "status": "timeout",
      "data": null,
      "message": "Pemeriksaan melewati batas waktu."
    }
  }
}
```

Nilai di atas hanya ilustrasi struktur. Skema final, kode status HTTP,
format error, validasi Pydantic, cara menangani pemeriksaan parsial, dan
batas ukuran request/response harus dirinci sebelum coding.

Status hasil sebaiknya membedakan sekurang-kurangnya: `success`,
`not_found`, `failed`, `timeout`, `unavailable`, dan `rate_limited`.
Satu pemeriksaan yang gagal tidak boleh otomatis menggagalkan hasil
modul lain.

## 7. Alur permintaan

1.  Pengguna memasukkan domain atau URL.
2.  Frontend melakukan validasi dasar untuk membantu pengguna, bukan
    sebagai pengganti validasi backend.
3.  Frontend mengirim permintaan ke API backend.
4.  Backend menormalisasi target dan menerapkan kebijakan keamanan.
5.  Backend memvalidasi hasil resolusi DNS dan alamat tujuan sebelum
    membuat koneksi.
6.  Backend menjalankan pemeriksaan yang diminta dengan timeout dan
    batas sumber daya.
7.  Setiap modul mengembalikan status dan data secara terpisah.
8.  Backend menggabungkan hasil menjadi respons terstruktur tanpa
    mengekspos stack trace atau detail internal.
9.  Frontend menampilkan ringkasan Simple Mode atau detail Technical
    Mode dari hasil yang sama.
10. Jika pengguna mengaktifkan riwayat lokal, hasil yang sesuai disimpan
    di browser; pengguna harus memiliki cara untuk menghapusnya.

## 8. Keamanan backend dan SSRF

Karena backend membuat koneksi ke target berdasarkan input pengguna,
pencegahan Server-Side Request Forgery (SSRF) wajib menjadi bagian
desain.

Persyaratan minimum: - Terima hanya format target yang didukung;
tentukan secara eksplisit apakah input berupa domain saja atau URL
lengkap. - Batasi protokol untuk pemeriksaan web ke HTTP/HTTPS. Modul
DNS harus memakai resolver yang ditentukan dan tidak menerima protokol
arbitrer. - Tolak alamat loopback, private, link-local, multicast,
alamat metadata cloud, dan rentang sensitif lain yang tidak boleh
diakses. - Resolusi nama harus divalidasi; periksa seluruh alamat hasil
resolusi, termasuk skenario IPv4/IPv6 dan DNS rebinding. - Validasi
ulang setiap redirect dan setiap koneksi baru. - Hindari perbedaan
antara alamat yang divalidasi dan alamat yang benar-benar digunakan
untuk koneksi. - Tetapkan timeout per pemeriksaan, batas redirect, batas
byte, batas konkurensi, dan batas total waktu analisis. - Terapkan rate
limiting dan perlindungan terhadap penyalahgunaan endpoint. - CORS hanya
mengizinkan origin frontend yang diperlukan pada deployment; jangan
menggunakan wildcard dengan kredensial. - Simpan secret di environment
backend, bukan di frontend atau repository. - Jangan mengembalikan stack
trace, alamat internal, credential, atau pesan exception mentah kepada
pengguna. - Catat metrik operasional minimum tanpa menyimpan input/hasil
sensitif lebih lama dari yang dibutuhkan. - Uji kasus domain yang
resolve ke alamat privat, redirect ke alamat privat, IPv6, nama yang
berubah saat resolve, timeout, respons besar, dan rantai redirect
panjang.

Daftar ini adalah baseline perencanaan dan perlu ditinjau kembali
terhadap implementasi serta lingkungan hosting sebenarnya. Jangan
membuka endpoint publik sebelum pengujian keamanan dasar lulus.

## 9. Deployment dan biaya

### Frontend --- Netlify Free

-   Deploy frontend dari repository Git.
-   Simpan URL API backend sebagai environment variable publik yang
    memang boleh diakses browser, misalnya `NEXT_PUBLIC_API_BASE_URL`.
-   Jangan meletakkan secret backend dalam environment variable
    frontend.
-   Verifikasi kuota build, bandwidth, penggunaan, dan ketentuan paket
    terkini sebelum publikasi.

### Backend --- Render Free

-   Deploy service FastAPI dari repository Git.
-   Konfigurasi command build/start dan versi Python secara eksplisit
    setelah dipilih.
-   Atur environment variable server-side.
-   Uji perilaku cold start, batas durasi request, batas penggunaan, dan
    akses outbound ke DNS/HTTP/TLS.
-   Verifikasi apakah batas paket gratis saat deployment mendukung jenis
    pemeriksaan yang dibutuhkan.

### Catatan biaya

Targetnya adalah biaya awal serendah mungkin, tetapi biaya nol tidak
dapat dijamin selamanya. Paket gratis dapat berubah, memiliki kuota,
tidur saat tidak digunakan, atau membatasi penggunaan tertentu. Jangan
menjanjikan SLA atau availability produksi dari paket gratis.

## 10. Database, cache, dan privasi

Untuk Stage 1: - Tidak ada database. - Riwayat disimpan lokal di browser
jika fitur riwayat diaktifkan. - Jangan menyimpan hasil pemeriksaan
permanen di backend secara default. - Cache hasil pemeriksaan belum
diputuskan. Jika nanti ditambahkan, tetapkan TTL, batas ukuran, dan
aturan agar data tidak menyesatkan ketika DNS/TLS berubah. - Tentukan
kebijakan log, masa retensi, dan informasi apa yang masuk ke log sebelum
deploy publik. - Sediakan cara menghapus riwayat lokal.

## 11. Pengujian dan kriteria kesiapan

Sebelum Stage 1 dianggap siap: - Unit test untuk validasi input,
parser/normalisasi hasil, dan status pemeriksaan. - Integration test
untuk domain yang berhasil, record tidak ditemukan, timeout, DNS gagal,
HTTP redirect, TLS tidak valid, serta kegagalan parsial. - Pengujian
keamanan SSRF untuk alamat privat/internal, redirect berbahaya,
IPv4/IPv6, dan DNS rebinding. - Pengujian batas timeout, jumlah
redirect, ukuran respons, dan rate limit. - Pengujian kontrak API agar
frontend dan backend memakai skema yang sama. - Pengujian tampilan
Simple Mode dan Technical Mode dari hasil yang sama. - Pengujian export
dan penghapusan riwayat lokal. - Pengujian deployment terhadap cold
start dan kegagalan layanan. - UI harus membedakan data yang tidak
tersedia dari data yang bernilai kosong atau gagal diperiksa. - Tidak
boleh ada klaim mutlak "aman" atau "berbahaya" yang tidak didukung
hasil.

## 12. Keputusan yang masih perlu diverifikasi (TODO)

Keputusan berikut sengaja belum diisi agar tidak mengarang kebutuhan: 1.
Apakah input menerima domain saja, URL lengkap, atau keduanya? 2. Bahasa
UI awal: Bahasa Indonesia, Inggris, atau pilihan bahasa? 3. Pilihan
pustaka DNS, HTTP, dan TLS serta lisensi/maintenance-nya. 4. Sumber data
ASN, organisasi jaringan, reverse DNS, dan geolokasi; kuota, lisensi,
dan atribusi. 5. Definisi persis tes latensi/konektivitas dan bagaimana
hasil diberi label. 6. Format ekspor laporan: JSON, CSV, PDF, atau
beberapa format. 7. Apakah Stage 1 membutuhkan skor/ringkasan prioritas,
atau cukup status dan penjelasan per pemeriksaan? 8. Skema final
endpoint, payload, error, kode status, dan batas request. 9. Angka awal
timeout, batas redirect, batas ukuran respons, concurrency, dan rate
limit. 10. Kebijakan logging dan retensi data backend. 11. Origin final
frontend untuk konfigurasi CORS. 12. Versi Node.js/Python, package
manager, dan strategi lockfile. 13. Struktur repository: monorepo dengan
`frontend/` dan `backend/`, atau dua repository terpisah. 14. Verifikasi
batas paket dan kemampuan outbound DNS/HTTP/TLS Netlify/Render pada saat
deployment. 15. Identitas visual, desain halaman, aksesibilitas, dan
kebutuhan responsive detail. 16. Format final ekspor dan cara menangani
hasil pemeriksaan yang sebagian gagal. 17. Apakah dibutuhkan cache hasil
di Stage 1. 18. Rencana pemantauan error/uptime yang tidak membutuhkan
database atau layanan berbayar.

## 13. Rencana kerja setelah dokumen disetujui

1.  Review dokumen kebutuhan yang sudah ada bersama dokumen arsitektur
    ini.
2.  Putuskan TODO yang memengaruhi desain API, keamanan, dan biaya.
3.  Buat spesifikasi API dan model respons final.
4.  Buat rencana struktur repository dan strategi pengujian.
5.  Tentukan aturan UI/UX dan desain visual berdasarkan kebutuhan fitur.
6.  Siapkan prompt implementasi untuk Hermes Agent yang mewajibkan
    membaca seluruh dokumen relevan sebelum mengubah file.
7.  Mulai implementasi hanya setelah ruang lingkup Stage 1 dan keputusan
    yang berdampak besar disetujui.

## 14. Instruksi untuk Hermes Agent nantinya

Saat implementasi dimulai: - Baca seluruh dokumen di `docs/` terlebih
dahulu, terutama overview, features, user flow, business logic, security
and limitations, dan dokumen ini. - Jangan menganggap TODO sebagai
keputusan final. Tanyakan jika keputusan tersebut memengaruhi
implementasi, atau catat usulan untuk disetujui. - Jangan langsung
membuat ulang project, mengganti stack, atau memodifikasi fitur yang
tidak terkait. - Implementasikan dalam langkah kecil dan uji setiap
bagian. - Jangan membuka endpoint pemeriksaan publik sebelum validasi
SSRF dan batas sumber daya diterapkan serta diuji. - Dokumentasikan
setiap keputusan teknis baru dan perbarui dokumen yang relevan.
