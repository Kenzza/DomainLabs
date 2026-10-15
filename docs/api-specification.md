# DomainLens --- Spesifikasi API

**Status:** Draft spesifikasi\
**Versi:** 0.1\
**Tujuan:** Menetapkan kontrak awal antara frontend Next.js dan backend
FastAPI sebelum implementasi.\
**Penting:** Dokumen ini adalah spesifikasi perencanaan. Tidak ada kode
aplikasi yang dibuat oleh dokumen ini. Nilai dan kebijakan yang belum
disepakati dicatat pada bagian TODO.

## 1. Keputusan final yang telah disepakati

  -----------------------------------------------------------------------
  ID                      Keputusan               Status
  ----------------------- ----------------------- -----------------------
  API-DEC-01              Frontend menggunakan    Disepakati
                          Next.js dan dipisahkan  
                          dari backend.           

  API-DEC-02              Backend menggunakan     Disepakati
                          Python + FastAPI.       

  API-DEC-03              Input analisis menerima Disepakati
                          domain atau URL         
                          lengkap.                

  API-DEC-04              Stage 1 tidak memakai   Disepakati
                          database; riwayat, bila 
                          digunakan, disimpan di  
                          browser pengguna.       

  API-DEC-05              Frontend direncanakan   Pilihan hosting awal;
                          di Netlify Free dan     verifikasi deployment
                          backend di Render Free, masih terbuka
                          dengan batas paket      
                          diverifikasi sebelum    
                          deploy.                 

  API-DEC-06              Simple Mode dan         Disepakati dalam
                          Technical Mode          rancangan produk
                          menampilkan kedalaman   
                          berbeda dari hasil      
                          pemeriksaan yang sama.  

  API-DEC-07              Kegagalan satu modul    Prinsip rancangan yang
                          tidak otomatis          disepakati
                          membatalkan hasil modul 
                          lain yang berhasil.     

  API-DEC-08              Stage 1 menjalankan     Disepakati
                          pemeriksaan manual;     
                          monitoring terjadwal    
                          ditunda.                
  -----------------------------------------------------------------------

## 2. Ruang lingkup

Spesifikasi ini mencakup kontrak konseptual untuk: - Pemeriksaan
kesehatan API. - Permintaan analisis domain/URL. - Hasil DNS dan IP
Intelligence. - Hasil HTTP Inspector. - Hasil TLS & Security. - Hasil
Network Diagnostics. - Status parsial, error, dan batas keamanan. -
Penyajian data pada Simple Mode dan Technical Mode.

Endpoint, skema, dan field di dokumen ini adalah rancangan awal yang
harus ditinjau sebelum diimplementasikan. TODO yang berpengaruh pada
keamanan atau kontrak tidak boleh diasumsikan selesai.

## 3. Konvensi umum API

-   Prefix kandidat: `/api/v1`.
-   Format request dan response: JSON dengan UTF-8.
-   Deployment publik harus menggunakan HTTPS.
-   Waktu yang dikembalikan API, jika ada, memakai ISO 8601 dengan zona
    waktu eksplisit, idealnya UTC.
-   Backend tidak boleh mengembalikan stack trace, secret, atau detail
    jaringan internal kepada klien.
-   Nama status di bawah merupakan kandidat konsisten untuk setiap
    modul.
-   Jangan mengembalikan data yang tidak diperoleh; gunakan `null`,
    daftar kosong, atau status yang sesuai dan bedakan maknanya melalui
    kontrak final.
-   Kontrak final harus menentukan ukuran request/response maksimum dan
    aturan validasi.

## 4. Endpoint

### 4.1 `GET /api/health`

Tujuan: memeriksa kesehatan dasar API.

Respons konseptual `200 OK`:

``` json
{
  "status": "ok"
}
```

Endpoint ini tidak boleh membocorkan versi library yang sensitif,
environment variable, path internal, alamat privat, atau informasi
konfigurasi rahasia.

### 4.2 `POST /api/v1/analyze`

Tujuan: menjalankan satu analisis manual terhadap target yang diterima.

Contoh request konseptual:

``` json
{
  "target": "https://example.com/about",
  "checks": ["dns", "ip", "http", "tls"]
}
```

Aturan: - `target` wajib berupa domain atau URL lengkap. - `checks`
menentukan modul yang diminta. Daftar nilai yang diterima perlu
ditetapkan final. - Jika `checks` tidak disediakan, apakah backend
menjalankan semua pemeriksaan default masih TODO. - Backend memvalidasi
input sendiri; validasi frontend hanya membantu UX. - Input URL lengkap
tidak berarti path atau query string akan digunakan untuk semua modul.
Target efektif untuk DNS, IP, dan TLS biasanya berupa hostname,
sedangkan HTTP dapat memerlukan URL yang telah dinormalisasi. Aturan
persisnya masih harus ditetapkan dan didokumentasikan. - URL dengan
username/password tertanam harus ditolak. - Protokol yang didukung untuk
pemeriksaan HTTP harus dibatasi pada HTTP dan HTTPS. - Port nonstandar,
alamat IP literal, URL dengan fragmen, dan query string perlu ditangani
menurut kebijakan yang disepakati. Jangan menganggap semua bentuk input
tersebut valid. - Jangan menerima skema arbitrer seperti `file:`,
`ftp:`, `gopher:`, atau skema non-HTTP lainnya untuk pemeriksaan web.

Respons analisis yang selesai, termasuk ketika sebagian modul gagal,
diharapkan memuat hasil per modul. Kode HTTP dan struktur respons final
untuk validasi gagal, seluruh pemeriksaan gagal, atau permintaan
dibatasi masih perlu diputuskan.

## 5. Bentuk respons analisis konseptual

Contoh ini hanya menunjukkan pola status per modul, bukan schema final:

``` json
{
  "target": {
    "input": "https://example.com/about",
    "normalized_host": "example.com",
    "normalized_url": "https://example.com/about"
  },
  "started_at": "2026-01-01T00:00:00Z",
  "completed_at": "2026-01-01T00:00:03Z",
  "checks": {
    "dns": {
      "status": "success",
      "data": {},
      "message": null
    },
    "ip": {
      "status": "success",
      "data": {},
      "message": null
    },
    "http": {
      "status": "timeout",
      "data": null,
      "message": "Pemeriksaan melewati batas waktu."
    },
    "tls": {
      "status": "unavailable",
      "data": null,
      "message": "Pemeriksaan TLS tidak tersedia untuk target ini."
    }
  }
}
```

Data di atas adalah ilustrasi. Nilai kosong bukan hasil pemeriksaan
nyata. Backend perlu mendefinisikan schema Pydantic untuk request,
respons, dan error sebelum coding.

## 6. Status pemeriksaan

Kandidat status bersama:

  -----------------------------------------------------------------------
  Status                              Arti
  ----------------------------------- -----------------------------------
  `success`                           Pemeriksaan berhasil dan
                                      menghasilkan data yang dapat
                                      digunakan.

  `not_found`                         Data yang dicari tidak ditemukan;
                                      bukan otomatis berarti konfigurasi
                                      salah.

  `failed`                            Pemeriksaan gagal karena kesalahan
                                      yang tidak lebih spesifik.

  `timeout`                           Pemeriksaan melewati batas waktu
                                      yang ditentukan.

  `unavailable`                       Pemeriksaan tidak dapat dilakukan
                                      dalam kondisi tersebut, misalnya
                                      modul atau sumber data tidak
                                      tersedia.

  `rate_limited`                      Permintaan dibatasi oleh kebijakan
                                      laju.
  -----------------------------------------------------------------------

Definisi final perlu menentukan kapan `not_found` berbeda dari `success`
dengan daftar kosong, serta kapan kegagalan harus diwakili sebagai
status modul atau error request keseluruhan.

## 7. Kontrak data modul

### 7.1 DNS

Data kandidat: - Record type. - Record value. - TTL jika tersedia. -
Status resolusi dan pesan keterbatasan.

Jenis record dalam cakupan produk: A, AAAA, CNAME, MX, NS, TXT, dan SOA
jika tersedia.

TODO: - Format persis tiap record, termasuk MX priority dan SOA
fields. - Perilaku CNAME dan apakah jawaban mengikuti alias. - Resolver
yang digunakan dan penanganan DNSSEC bila kelak dibutuhkan. - Batas
jumlah record dan cara menyajikan TXT yang panjang.

### 7.2 IP Intelligence

Data kandidat: - Alamat IP hasil resolusi. - ASN. - Organisasi
jaringan. - Reverse DNS. - Perkiraan geolokasi bila sumber data
tersedia.

TODO: - Sumber data, lisensi, atribusi, kuota, dan fallback. - Apakah
geolokasi ditampilkan pada Stage 1. - Kebijakan ketika domain
menghasilkan banyak alamat IP. - Cara menyampaikan data yang tidak
tersedia atau sumber yang gagal.

### 7.3 HTTP Inspector

Data kandidat: - Status HTTP. - Waktu respons. - Redirect chain yang
dibatasi. - Header respons terpilih. - URL efektif setelah redirect bila
aman dan tersedia.

TODO: - Apakah request menggunakan `HEAD`, `GET`, atau strategi
fallback. - Daftar header yang ditampilkan. - Batas body yang dibaca;
hindari mengunduh body penuh jika tidak diperlukan. - Kebijakan
redirect, port, timeout, ukuran respons, dan kode error. - Apakah path
input diperiksa persis atau hanya origin/root URL.

### 7.4 TLS & Security

Data kandidat: - Status validasi sertifikat. - Kecocokan hostname. -
Masa berlaku dan tanggal kedaluwarsa. - Informasi issuer/subject yang
aman untuk ditampilkan. - Hasil pemeriksaan header keamanan terpilih.

TODO: - Field sertifikat final. - Perilaku jika target hanya mendukung
HTTP atau menggunakan port nonstandar. - Daftar header keamanan yang
diperiksa. - Definisi hasil parsial dan peringatan. - Kebijakan versi
TLS/cipher; jangan mengklaim audit TLS penuh bila tidak benar-benar
dilakukan.

### 7.5 Network Diagnostics

Data kandidat: - Status resolusi DNS. - Informasi waktu yang diukur dan
definisinya. - Status konektivitas dari server pemeriksa.

TODO: - Uji latensi yang tepat dan definisi titik awal/akhir
pengukuran. - Apakah ICMP/ping digunakan atau hanya koneksi TCP/HTTP;
jangan menyebutnya ping jika bukan ICMP. - Batasan paket gratis hosting
untuk koneksi outbound. - Cara membedakan hasil server-side dari kondisi
jaringan pengguna.

## 8. Validasi target dan keamanan SSRF

Backend wajib menganggap `target` sebagai input tidak tepercaya.

Persyaratan minimum: 1. Parse dan normalisasi domain/URL menggunakan
parser yang sesuai, bukan regex saja. 2. Tolak username/password dalam
URL. 3. Batasi protokol web ke HTTP/HTTPS. 4. Tentukan aturan domain
internasional/IDN, trailing dot, port, IP literal, karakter kontrol, dan
URL malformed. 5. Resolve hostname dan validasi seluruh alamat IPv4/IPv6
yang mungkin digunakan. 6. Blokir loopback, private, link-local,
multicast, alamat metadata cloud, dan rentang sensitif lain. 7. Cegah
DNS rebinding dan TOCTOU: alamat yang digunakan untuk koneksi harus
konsisten dengan hasil validasi, bukan hanya memvalidasi sekali lalu
melakukan resolve ulang tanpa kontrol. 8. Validasi ulang setiap redirect
dan setiap koneksi tujuan baru. 9. Batasi redirect, timeout,
concurrency, total waktu analisis, ukuran respons, dan jumlah data
hasil. 10. Jangan mendukung protokol atau port arbitrer sebagai proxy
umum. 11. Terapkan rate limiting dan batas penggunaan yang sesuai untuk
layanan publik. 12. Konfigurasikan CORS hanya untuk origin frontend yang
diperlukan pada production. 13. Jangan menaruh secret di frontend atau
repository. 14. Jangan menampilkan stack trace atau detail internal. 15.
Uji alamat privat, IPv6, redirect ke alamat privat, domain dengan
beberapa hasil DNS, DNS rebinding, timeout, dan respons besar.

Nilai numerik batas keamanan belum ditentukan dan harus menjadi TODO
sebelum implementasi publik.

## 9. Error request vs status modul

Rancangan perilaku: - Input tidak valid harus ditolak sebelum
pemeriksaan dimulai. - Permintaan yang valid dapat mengembalikan hasil
parsial apabila satu modul timeout atau gagal. - Error internal tidak
boleh dikirim sebagai stack trace. - Pembatasan laju harus ditandai
secara jelas. - Kegagalan backend secara keseluruhan perlu dibedakan
dari kegagalan satu pemeriksaan.

TODO: - Kode HTTP final untuk input invalid, target ditolak oleh
kebijakan keamanan, rate limit, backend error, dan hasil parsial. -
Schema error bersama (misalnya `code`, `message`, `request_id`). -
Apakah hasil parsial menggunakan `200 OK` dengan status per modul atau
kode lain; tentukan konsisten berdasarkan semantik final. - Apakah perlu
request ID untuk debugging tanpa menyimpan data pribadi yang berlebihan.

## 10. Frontend dan API

-   Frontend mengambil base URL backend dari konfigurasi environment
    publik yang sesuai untuk Next.js.
-   URL API bukan secret; secret tidak boleh ditempatkan pada variabel
    yang diekspos ke browser.
-   Frontend harus menangani loading, error request, timeout, hasil
    parsial, serta status tiap modul.
-   Simple Mode menggunakan pesan penjelasan berbasis data yang
    tersedia.
-   Technical Mode menampilkan detail yang benar-benar dikembalikan API.
-   Jangan menyimpulkan "aman" atau "berbahaya" secara mutlak dari satu
    indikator.
-   Frontend harus tetap responsif saat API mengalami cold start.
-   CORS, HTTPS, dan konfigurasi origin perlu diuji pada deployment.

## 11. Stage 1: riwayat dan ekspor

-   Tidak ada database untuk Stage 1.
-   Riwayat, bila diaktifkan, disimpan di browser pengguna.
-   Pengguna harus dapat menghapus riwayat lokal.
-   Jangan mengirim riwayat ke backend tanpa persetujuan dan desain
    privasi yang jelas.
-   Format ekspor laporan belum final.
-   Skema data ekspor harus diberi versi bila diperlukan agar perubahan
    API tidak merusak file lama.

## 12. Pengujian kontrak API

Minimal: - Domain valid dan URL HTTPS valid. - URL HTTP valid. - URL
malformed dan protokol tidak diizinkan. - URL dengan kredensial
tertanam. - Domain tidak ditemukan. - DNS berhasil, HTTP timeout. - HTTP
redirect normal dan redirect menuju alamat terlarang. - TLS valid,
kedaluwarsa, atau hostname mismatch. - Hasil sebagian dan kegagalan
keseluruhan. - Rate limit. - IPv4/IPv6 dan target yang resolve ke
beberapa alamat. - Respons besar, timeout, dan rantai redirect
panjang. - Kontrak Pydantic sesuai dengan penggunaan frontend. - Simple
Mode dan Technical Mode menampilkan hasil yang konsisten. - Riwayat
lokal dapat dihapus dan ekspor mengikuti schema.

## 13. TODO --- keputusan yang belum final

1.  Daftar `checks` final dan pemeriksaan default jika field tidak
    dikirim.
2.  Aturan normalisasi domain vs URL: apakah path/query dipakai oleh
    HTTP Inspector dan apa yang dilakukan modul DNS/IP/TLS.
3.  Kebijakan port nonstandar dan IP literal.
4.  Dukungan IDN/punycode dan bentuk domain yang diterima.
5.  Field final untuk respons DNS, IP, HTTP, TLS, dan Diagnostics.
6.  Sumber data IP Intelligence serta lisensi/kuotanya.
7.  Metode HTTP (`HEAD`/`GET`), header yang ditampilkan, dan batas body.
8.  Definisi dan metode pengukuran latency/connectivity.
9.  Nilai numerik timeout, redirect, ukuran respons, concurrency, dan
    rate limit.
10. Kode HTTP dan schema error final.
11. Aturan untuk hasil parsial dan kegagalan keseluruhan.
12. Format ekspor laporan.
13. Kebijakan logging dan retensi.
14. Origin final untuk CORS.
15. Uji kemampuan outbound dan batas paket Netlify/Render pada waktu
    deployment.
16. Perlu/tidaknya cache hasil pada Stage 1.
17. Apakah ringkasan prioritas/skor dibutuhkan atau tidak.
18. Versi API dan kebijakan kompatibilitas saat kontrak berubah.

## 14. Langkah selanjutnya

1.  Tinjau spesifikasi ini bersama `technical-architecture.md` dan
    dokumen kebutuhan lain.
2.  Putuskan TODO yang berpengaruh pada keamanan dan perilaku API.
3.  Finalisasi schema request/response dan kode error.
4.  Susun rencana pengujian dan urutan implementasi.
5.  Setelah dokumen disetujui, buat prompt Hermes Agent yang
    mengharuskan membaca dokumen `docs/` terlebih dahulu.
6.  Jangan mulai coding sampai keputusan yang memengaruhi keamanan dan
    kontrak API sudah cukup jelas.
