# DomainLens — Input Normalization, SSRF Protection, and Inspection Limits

## 1. Purpose

Dokumen ini menjelaskan kebijakan awal untuk normalisasi input domain/URL, validasi keamanan SSRF (Server-Side Request Forgery), dan pembatasan sumber daya pemeriksaan pada DomainLens.

Dokumen ini menjadi acuan perencanaan sebelum implementasi dimulai.

**Important:** Nilai batas pada dokumen ini merupakan usulan awal untuk prototipe yang harus diuji. Nilai tersebut belum menjadi konfigurasi produksi final.

---

## 2. Confirmed Project Decisions

Keputusan berikut telah disepakati:

- Frontend menggunakan Next.js.
- Backend menggunakan Python dan FastAPI.
- Frontend dan backend merupakan proyek terpisah.
- Komunikasi frontend dan backend menggunakan REST API.
- Pengguna dapat memasukkan domain saja atau URL lengkap.
- DomainLens menyediakan Simple Mode dan Technical Mode dengan sumber data pemeriksaan yang sama.
- Pemeriksaan dilakukan secara manual pada tahap awal.
- Tidak ada akun pengguna atau database pada Stage 1.
- Riwayat pemeriksaan disimpan secara lokal di browser.
- Kegagalan satu modul tidak boleh menghilangkan hasil modul lain yang berhasil.
- Pemeriksaan ditujukan untuk domain dan website publik yang pengguna berwenang untuk periksa.
- DomainLens bukan alat eksploitasi atau pemindaian agresif.

---

## 3. Input Normalization Policy

### 3.1 Supported Input

DomainLens menerima dua bentuk input utama.

**Domain only:**

`example.com`

**Full URL:**

`https://example.com/about?lang=id`

Backend wajib melakukan validasi secara mandiri. Validasi di frontend hanya membantu pengalaman pengguna dan tidak boleh dianggap sebagai batas keamanan.

### 3.2 Input Parsing

Backend harus menggunakan parser URL dan validasi hostname yang sesuai. Jangan mengandalkan regular expression saja untuk menentukan apakah input aman.

Proses validasi minimal harus mencakup:

1. Memeriksa apakah input kosong.
2. Menghapus whitespace yang tidak diperlukan pada awal dan akhir input.
3. Memeriksa karakter kontrol atau karakter yang tidak diperbolehkan.
4. Menentukan apakah input berupa domain atau URL lengkap.
5. Mem-parse URL jika input mengandung skema atau komponen URL.
6. Memvalidasi skema, hostname, port, dan komponen URL lainnya.
7. Menormalisasi input sebelum menjalankan pemeriksaan.
8. Menolak input yang malformed, ambigu, atau tidak didukung.

Backend tidak boleh langsung mengirim request HTTP ke input mentah dari pengguna.

### 3.3 Mapping Input to Inspection Modules

Setiap modul menggunakan bagian input yang sesuai.

| Module | Input yang digunakan |
|---|---|
| DNS Lookup | Hostname yang telah divalidasi |
| IP Intelligence | IP hasil resolusi hostname atau IP yang telah divalidasi, sesuai kebijakan yang nantinya ditetapkan |
| Website Inspector | URL yang telah dinormalisasi, termasuk path dan query jika diizinkan |
| TLS & Security | Hostname dan port efektif untuk koneksi TLS |
| Network Diagnostics | Target yang telah divalidasi dan metode pemeriksaan yang telah ditetapkan |

Contoh input:

`https://example.com/about?lang=id`

Pemetaan konseptual:

- DNS Lookup memeriksa `example.com`.
- IP Intelligence menggunakan hasil resolusi yang sesuai.
- Website Inspector memeriksa URL lengkap yang telah divalidasi.
- TLS & Security memeriksa hostname `example.com` menggunakan port efektif yang sesuai.
- Network Diagnostics mengikuti kebijakan target dan metode pemeriksaan yang nantinya disepakati.

### 3.4 URL Normalization Decisions Still Required

Keputusan berikut belum final dan harus ditentukan sebelum implementasi:

- Skema default untuk input domain tanpa skema, misalnya `https://`.
- Apakah input berupa alamat IP literal diperbolehkan.
- Apakah port nonstandar diperbolehkan.
- Bagaimana domain internasional (IDN) dikonversi dan divalidasi menggunakan Punycode.
- Apakah trailing dot pada hostname diterima dan bagaimana normalisasinya.
- Apakah URL dengan username atau password, seperti `https://user:pass@example.com`, harus ditolak. Usulan awal: tolak.
- Bagaimana fragment URL seperti `#section` diperlakukan. Fragment tidak dikirim sebagai bagian dari HTTP request.
- Bagaimana path dan query dipertahankan saat normalisasi.
- Apakah skema selain HTTP dan HTTPS ditolak. Usulan awal: hanya HTTP dan HTTPS yang diperbolehkan untuk Website Inspector.
- Bagaimana request ke hostname yang tidak memiliki DNS publik yang valid ditangani.

Keputusan ini harus dicatat sebelum implementasi agar perilaku frontend, backend, dan dokumentasi konsisten.

### 3.5 Default Scheme for Domain-Only Input

**Status: DECIDED**

When the user provides a domain without an explicit URL scheme, DomainLens must default to HTTPS.

Example:

- Input: `example.com`
- Normalized URL: `https://example.com`

Rules:

- DomainLens must not automatically fall back to HTTP when HTTPS fails.
- HTTPS failures must be reported using an appropriate result status and explanation.
- Users may explicitly provide an HTTP URL, such as `http://example.com`, when they want to inspect HTTP.
- Explicitly provided schemes must still pass backend validation and SSRF protection.
- Frontend normalization does not replace backend validation.

This policy applies to the default URL used for website inspection. DNS lookup and IP intelligence continue to operate on the validated hostname, while TLS inspection uses the validated hostname and effective port.

### 3.6 Allowed Ports for Website Inspector

**Status: DECIDED**

During Stage 1, Website Inspector only allows the following protocol and port combinations:

| Protocol | Allowed Port |
|---|---:|
| HTTP | 80 |
| HTTPS | 443 |

Rules:

- HTTP requests must use port 80.
- HTTPS requests must use port 443.
- Explicit nonstandard ports must be rejected.
- A URL containing a disallowed port must be rejected before any outbound connection is attempted.
- The backend must independently validate the scheme and port.
- URL normalization must not silently replace a disallowed port with a permitted port.
- TLS inspection must use the validated hostname and permitted effective port.
- These restrictions do not replace SSRF destination validation.

Examples:

- `http://example.com` — allowed for validation and inspection.
- `https://example.com` — allowed for validation and inspection.
- `https://example.com:8443` — rejected.
- `http://example.com:8080` — rejected.
- `example.com` — normalized to `https://example.com`.

This policy applies to Website Inspector and the corresponding TLS connection. DNS Lookup continues to operate on the validated hostname.

The port policy may be reconsidered in a future stage if nonstandard web ports become a confirmed requirement and additional security controls are established.

### 3.7 IP Literal Input Policy

**Status: DECIDED**

DomainLens Stage 1 accepts domain names as user-provided targets and rejects IP literals as direct input.

Rules:

- Direct IPv4 and IPv6 address inputs must be rejected.
- The backend must detect IP literals during input parsing, including IP addresses provided as URL hostnames.
- Input validation must not rely solely on regular expressions.
- Valid domain names may be resolved to IPv4 and IPv6 addresses for DNS Lookup and IP Intelligence.
- Resolved IP addresses must be validated against the SSRF destination policy before any outbound connection.
- Rejecting direct IP input does not imply that a hostname is safe.
- The frontend and backend must provide consistent, understandable validation messages.

Examples:

- `example.com` — accepted for validation.
- `8.8.8.8` — rejected as direct IP input.
- `127.0.0.1` — rejected as direct IP input.
- `2001:4860:4860::8888` — rejected as direct IP input.
- `https://example.com` — accepted for validation.
- `https://8.8.8.8` — rejected as an IP literal target.

This restriction applies to user-provided targets. It does not prevent DomainLens from displaying IP addresses discovered through a validated domain's DNS results.

### 3.8 Internationalized Domain Names (IDN)

**Status: DECIDED**

DomainLens Stage 1 accepts valid Internationalized Domain Names (IDNs).

Rules:

- Users may provide domain names containing international characters.
- The backend must validate and normalize IDN hostnames using an appropriate, tested IDN-processing library.
- The normalized hostname must use an appropriate ASCII-compatible Punycode representation for DNS and network operations.
- The implementation must follow a consistent IDN processing standard and reject invalid or disallowed hostname labels.
- The original user input may be retained for display, while the normalized hostname is used for technical processing.
- The normalized hostname must still pass the normal hostname, DNS, and SSRF validation rules.
- IDN support does not include a guarantee that a domain is free from visually confusing characters, brand impersonation, or homograph attacks.

Example:

- User input: a valid internationalized domain name.
- Processing: validate the domain and normalize its hostname to Punycode.
- DNS lookup: use the validated normalized hostname.
- Website and TLS inspection: use the validated hostname consistently for connection handling, HTTP Host, TLS SNI, and certificate hostname verification.

The exact IDN library and normalization standard must be selected during technical implementation planning. Custom Punycode conversion logic must not be implemented from scratch.



---

## 4. SSRF Protection Policy

### 4.1 Security Principle

Semua input pengguna harus dianggap tidak tepercaya.

DomainLens melakukan request dari server backend. Oleh karena itu, input berbahaya dapat berusaha membuat backend mengakses jaringan internal, layanan lokal, atau endpoint metadata cloud.

Backend wajib memvalidasi tujuan koneksi sebelum menjalankan pemeriksaan jaringan atau HTTP.

Validasi di frontend tidak cukup untuk mencegah SSRF.

### 4.2 Destination Validation

Sebelum membuat koneksi, backend harus:

1. Memvalidasi format URL dan hostname.
2. Memastikan skema yang digunakan diperbolehkan.
3. Memastikan port yang digunakan sesuai kebijakan.
4. Melakukan resolusi DNS melalui mekanisme yang dikendalikan backend.
5. Memeriksa seluruh alamat IPv4 dan IPv6 hasil resolusi.
6. Menolak tujuan yang mengarah ke alamat atau rentang jaringan yang tidak diperbolehkan.
7. Memastikan koneksi aktual menggunakan tujuan yang telah divalidasi.
8. Menerapkan timeout dan batas sumber daya.
9. Menghindari kebocoran informasi internal melalui pesan error.

### 4.3 Blocked Destinations

Secara default, backend harus menolak tujuan yang mengarah ke:

- Loopback, termasuk `127.0.0.1` dan `::1`.
- Alamat IPv4 private.
- Alamat IPv6 unique-local atau rentang internal yang setara.
- Alamat link-local.
- Alamat multicast.
- Alamat unspecified atau alamat khusus lain yang tidak layak menjadi target publik.
- Endpoint metadata cloud, termasuk alamat metadata yang umum digunakan.
- Alamat tujuan internal atau sensitif lain yang ditentukan melalui kebijakan keamanan.

Daftar ini harus diterapkan berdasarkan klasifikasi alamat IP yang benar, bukan hanya pemeriksaan string sederhana.

Implementasi harus mempertimbangkan variasi representasi IPv4/IPv6 serta alamat yang dipetakan ke IPv4.

### 4.4 DNS Rebinding and Time-of-Check/Time-of-Use

Backend tidak boleh hanya memvalidasi hasil DNS satu kali lalu membiarkan HTTP client melakukan resolusi ulang tanpa kontrol.

Risiko yang harus diperhitungkan:

- Hostname awal mengarah ke IP publik, tetapi resolusi berikutnya mengarah ke IP internal.
- Jawaban DNS berisi campuran alamat publik dan alamat yang dilarang.
- Tujuan koneksi berubah di antara tahap validasi dan koneksi aktual.

Mitigasi harus memastikan bahwa alamat yang digunakan untuk membuat koneksi konsisten dengan hasil validasi. Jika memungkinkan, koneksi harus menggunakan IP yang telah divalidasi sambil tetap mempertahankan hostname yang benar untuk HTTP Host, TLS SNI, dan validasi sertifikat.

Jika hostname memiliki hasil resolusi yang tidak aman atau ambigu, backend harus menolak pemeriksaan tersebut sesuai kebijakan yang ditetapkan.

### 4.5 Redirect Validation

Setiap redirect HTTP harus diperlakukan sebagai tujuan baru yang belum tepercaya.

Untuk setiap redirect:

1. Parse dan validasi URL tujuan.
2. Pastikan skemanya diperbolehkan.
3. Validasi hostname dan port.
4. Resolusi DNS ulang jika diperlukan.
5. Validasi seluruh alamat IP tujuan.
6. Tolak redirect menuju alamat internal atau alamat yang dilarang.
7. Batasi jumlah redirect.
8. Hentikan proses jika terjadi redirect loop atau rangkaian redirect yang tidak valid.

Jangan menganggap tujuan redirect aman hanya karena URL awal telah lolos validasi.

### 4.6 Protocol and Port Restrictions

- Website Inspector hanya boleh menggunakan protokol yang secara eksplisit diperbolehkan.
- Skema seperti `file://`, `ftp://`, dan protokol lain yang tidak diperlukan harus ditolak.
- Port harus divalidasi berdasarkan kebijakan yang telah ditetapkan.
- Backend tidak boleh menyediakan akses proxy umum ke alamat atau port arbitrer.
- Fitur analisis domain tidak boleh berubah menjadi sarana untuk mengakses layanan internal.

**TODO:** Tentukan apakah pemeriksaan HTTP hanya diperbolehkan pada port standar 80 dan 443 atau juga port lain yang telah disetujui.

### 4.7 Error Handling

Backend tidak boleh menampilkan stack trace, kredensial, konfigurasi internal, atau detail jaringan sensitif kepada pengguna.

Pesan error harus menjelaskan kegagalan secara aman, misalnya:

- Hostname tidak valid.
- Tujuan tidak diperbolehkan.
- Resolusi DNS gagal.
- Pemeriksaan mengalami timeout.
- Tujuan redirect tidak diperbolehkan.
- Layanan pemeriksaan sedang tidak tersedia.

Detail teknis yang diperlukan untuk debugging dapat dicatat melalui logging internal yang terkontrol, tanpa menyimpan informasi sensitif secara berlebihan.

---

## 5. Prototype Inspection Limits

Nilai berikut merupakan usulan awal untuk prototipe dan wajib diuji.

| Parameter | Usulan awal | Status |
|---|---|---|
| Timeout per pemeriksaan | 10 detik | Harus diuji |
| Maksimum redirect HTTP | 5 redirect | Harus diuji |
| Maksimum data respons HTTP yang dibaca | 2 MiB | Harus diuji |
| Rate limit | 10 permintaan per menit per IP pengguna | Harus diuji |

Nilai di atas bukan jaminan bahwa layanan telah siap untuk produksi.

### 5.1 Timeout

Setiap pemeriksaan harus memiliki batas waktu agar target yang lambat atau tidak merespons tidak membuat proses berjalan tanpa batas.

Hal yang perlu ditentukan:

- Apakah 10 detik berlaku untuk setiap modul atau setiap request jaringan.
- Apakah analisis keseluruhan memiliki timeout total.
- Bagaimana pembatalan pemeriksaan diterapkan ketika batas waktu terlampaui.
- Apakah setiap modul boleh menggunakan timeout yang berbeda setelah pengujian.

### 5.2 Redirect Limit

Maksimum lima redirect diusulkan untuk mencegah rangkaian redirect yang terlalu panjang.

Backend harus menghentikan pemeriksaan ketika batas tercapai. Redirect loop juga harus ditangani dengan aman.

Batas ini tidak menggantikan validasi SSRF pada setiap tujuan redirect.

### 5.3 HTTP Response Size Limit

Maksimum 2 MiB adalah batas awal jumlah data respons HTTP yang dibaca oleh Website Inspector.

Backend harus menghentikan pembacaan ketika batas tercapai, tanpa harus mengunduh seluruh respons terlebih dahulu.

Implementasi harus mempertimbangkan:

- Respons dengan ukuran yang tidak diketahui.
- Header `Content-Length` yang tidak tersedia atau tidak dapat dipercaya.
- Respons yang dikompresi.
- Batas ukuran setelah dekompresi.
- Pembacaan streaming.
- Penggunaan memori ketika beberapa pemeriksaan berjalan bersamaan.

Batas 2 MiB belum tentu sesuai untuk semua jenis respons. Nilainya perlu diuji terhadap situs yang umum diperiksa.

### 5.4 Rate Limit

Usulan awal adalah maksimal 10 permintaan per menit per IP pengguna.

Rate limit harus diterapkan di backend, bukan hanya di frontend.

Hal yang perlu ditentukan:

- Apakah yang dihitung adalah request API atau setiap pemeriksaan modul.
- Apakah satu analisis yang menjalankan beberapa modul dihitung sebagai satu permintaan atau beberapa permintaan.
- Bagaimana rate limit diterapkan ketika backend berjalan pada beberapa instance.
- Bagaimana alamat IP klien ditentukan di belakang reverse proxy.
- Proxy mana yang dipercaya untuk meneruskan informasi IP klien.
- Bagaimana respons rate limit disampaikan kepada pengguna.

Backend tidak boleh mempercayai header seperti `X-Forwarded-For` dari sembarang klien. Header tersebut hanya boleh digunakan sesuai konfigurasi proxy tepercaya.

---

## 6. Partial Module Failure

DomainLens menjalankan beberapa modul pemeriksaan dalam satu proses analisis.

Kegagalan satu modul tidak boleh otomatis menggagalkan seluruh analisis.

Setiap modul harus mengembalikan statusnya sendiri. Status konseptual yang telah direncanakan:

- `success`
- `not_found`
- `failed`
- `timeout`
- `unavailable`
- `rate_limited`

Contoh:

- DNS berhasil, tetapi pemeriksaan TLS mengalami timeout.
- Informasi IP berhasil diperoleh, tetapi data registrasi domain tidak tersedia.
- Website Inspector gagal membaca respons, tetapi hasil DNS tetap dapat ditampilkan.

Frontend harus menampilkan hasil yang berhasil beserta status kegagalan modul lainnya.

---

## 7. Additional Resource Limits to Decide

Batas berikut belum ditetapkan dan harus diputuskan sebelum implementasi atau deployment publik:

- Timeout total untuk satu analisis.
- Jumlah maksimum pemeriksaan yang berjalan secara bersamaan.
- Ukuran maksimum body request API.
- Ukuran maksimum JSON response API.
- Jumlah retry dan kondisi yang mengizinkan retry.
- Batas penggunaan memori.
- Cache hasil DNS dan HTTP serta TTL yang digunakan.
- Batas jumlah request keluar dari backend.
- Kebijakan logging dan masa penyimpanan log.
- Batas penggunaan layanan pihak ketiga dan kuota layanan gratis.
- Batas ukuran laporan yang dapat diekspor.

Nilai final harus disesuaikan dengan hasil pengujian, kapasitas hosting, dan risiko keamanan.

---

## 8. Security Test Cases

Sebelum DomainLens dibuka untuk publik, lakukan pengujian minimal berikut.

### 8.1 Input Validation

- Input kosong.
- Domain dengan format tidak valid.
- URL malformed.
- URL dengan username atau password.
- Skema yang tidak didukung.
- Port tidak valid.
- Karakter kontrol atau whitespace yang mencurigakan.
- Domain internasional.
- Hostname dengan trailing dot.
- Input berupa IP literal.
- URL yang mengandung query dan fragment.

### 8.2 SSRF Protection

- Tujuan loopback IPv4 dan IPv6.
- Tujuan private IPv4.
- Tujuan link-local.
- Tujuan multicast atau alamat khusus.
- Tujuan metadata cloud.
- Hostname yang mengembalikan alamat publik dan alamat internal secara bersamaan.
- Redirect dari situs publik menuju alamat internal.
- Redirect loop.
- Perubahan hasil DNS di antara validasi dan koneksi.
- Port yang tidak diizinkan.
- Representasi alamat IP alternatif yang dapat melewati validasi sederhana.

### 8.3 Resource Limits

- Server yang tidak merespons.
- Server yang merespons sangat lambat.
- Rangkaian redirect melebihi batas.
- Respons HTTP lebih besar dari 2 MiB.
- Respons dengan ukuran yang tidak diketahui.
- Banyak request dalam waktu singkat.
- Beberapa analisis berjalan bersamaan.
- Salah satu modul gagal sementara modul lain berhasil.

### 8.4 Error and Privacy Handling

- Stack trace tidak muncul dalam respons publik.
- Detail jaringan internal tidak bocor.
- Token atau kredensial tidak dicatat secara tidak sengaja.
- Rate limit berfungsi dengan benar.
- Header IP klien hanya dipercaya dari proxy yang dikonfigurasi.
- Hasil kegagalan ditampilkan secara jelas dan tidak disamarkan sebagai hasil sukses.

---

## 9. Deployment Readiness

Sebelum deployment publik, pastikan:

- [ ] Normalisasi domain dan URL sudah ditetapkan.
- [ ] Skema dan port yang diizinkan sudah ditentukan.
- [ ] Validasi IPv4 dan IPv6 telah diuji.
- [ ] Perlindungan SSRF telah diuji, termasuk redirect dan DNS rebinding.
- [ ] Batas timeout dan ukuran respons telah diuji.
- [ ] Rate limit telah diuji pada lingkungan deployment yang sebenarnya.
- [ ] CORS hanya mengizinkan origin frontend yang sesuai.
- [ ] HTTPS digunakan pada deployment produksi.
- [ ] Secret dan konfigurasi sensitif tidak disimpan di frontend.
- [ ] Error publik tidak membocorkan detail internal.
- [ ] Batas dan kuota hosting gratis telah diperiksa.
- [ ] Semua keputusan keamanan yang masih terbuka telah diselesaikan atau dicatat secara eksplisit.

---

## 10. Open Decisions

Daftar keputusan yang masih perlu diselesaikan:

1. Skema default untuk domain tanpa skema.
2. Dukungan input IP literal.
3. Kebijakan port nonstandar.
4. Penanganan IDN dan Punycode.
5. Penanganan trailing dot dan fragment URL.
6. Kebijakan path dan query untuk Website Inspector.
7. Timeout total analisis.
8. Batas konkurensi.
9. Strategi rate limit pada hosting dengan reverse proxy atau beberapa instance.
10. Strategi resolusi DNS dan pencegahan DNS rebinding.
11. Sumber data IP Intelligence dan batas kuotanya.
12. Kebijakan cache, retry, dan logging.
13. Dukungan outbound networking pada hosting backend yang dipilih.

Keputusan yang belum final harus tetap berstatus TODO sampai disepakati.

---

## 11. Implementation Rule

Sebelum menulis kode:

1. Baca seluruh dokumen di folder `docs`.
2. Cocokkan dokumen ini dengan `security-and-limitations.md`, `technical-architecture.md`, dan `api-specification.md`.
3. Tandai keputusan yang belum final.
4. Jangan mengubah usulan prototipe menjadi nilai produksi tanpa pengujian dan persetujuan.
5. Jangan mengimplementasikan pemeriksaan jaringan yang belum memiliki kebijakan keamanan jelas.
6. Jangan memulai coding sampai tahap perencanaan dan keputusan yang diperlukan telah disepakati.

## 12. Additional Input Normalization Rules

### 12.1 Trailing Dot

**Status: DECIDED**

A valid hostname ending with a terminal dot may be accepted and normalized for application processing.

Example:

- Input: `example.com.`
- Normalized hostname: `example.com`

Only a valid terminal dot may be removed. The backend must not alter unrelated URL components during normalization.

### 12.2 URL Fragments

**Status: DECIDED**

URL fragments must not be included in HTTP requests.

Example:

- Input: `https://example.com/docs#installation`
- HTTP request URL: `https://example.com/docs`

The fragment must not affect DNS resolution, TLS hostname validation, or the HTTP request target.

### 12.3 URL Paths and Queries

**Status: DECIDED**

For Website Inspector, the validated URL path and query string must be preserved.

Example:

- Input: `https://example.com/search?q=domain`
- Request URL: `https://example.com/search?q=domain`

The backend must validate the complete URL before making a request. Query parameters must not be interpreted as instructions or used to bypass destination validation.

### 12.4 URL Credentials

**Status: DECIDED**

URLs containing embedded usernames or passwords must be rejected.

Example:

- `https://user:password@example.com` — rejected.

The backend must not log or expose embedded credentials in public error messages.

### 12.5 Supported Schemes

**Status: DECIDED**

Website Inspector supports only HTTP and HTTPS.

- A domain-only input defaults to HTTPS.
- An explicitly supplied HTTP URL remains HTTP.
- An explicitly supplied HTTPS URL remains HTTPS.
- Unsupported schemes must be rejected.
- The backend must not silently change a disallowed scheme to another scheme.
- Scheme and port validation must occur before any outbound connection.

### 12.6 URL Parsing and Canonicalization

The backend must use a suitable URL parser and tested hostname-processing libraries. Regular expressions alone are insufficient for complete URL validation.

The backend must reject malformed, ambiguous, or unsupported inputs. Normalization must not change the intended destination in a way that bypasses security validation.

---

## 13. Additional Resource Limits

**Status: PROPOSED FOR PROTOTYPE TESTING**

The following are initial engineering proposals, not final production settings.

| Parameter | Initial proposal |
|---|---|
| Per-network-check timeout | 10 seconds |
| Total analysis timeout | 30 seconds |
| Maximum HTTP redirects | 5 |
| Maximum HTTP response data read | 2 MiB |
| Maximum concurrent analyses per backend instance | 5 |
| Automatic retries | 0 |
| Maximum API request body | 16 KiB |
| Analysis rate limit | 10 requests per minute per client IP |

These limits must be tested against actual target websites and the selected hosting environment.

### 13.1 Total Analysis Timeout

The backend must enforce a total deadline for one analysis request.

A module must not continue indefinitely after the analysis deadline has expired. Completed module results should be preserved when possible.

The response must identify modules that could not finish within the available time.

### 13.2 Concurrency

The backend should limit the number of simultaneous analyses per instance.

The initial proposed limit is five concurrent analyses. The implementation must avoid creating unbounded tasks or outbound connections.

The limit must be revisited if deployment uses multiple instances or if testing identifies memory or resource pressure.

### 13.3 API Request Size

The initial maximum request body is 16 KiB.

The backend must reject oversized request bodies before expensive analysis begins. The API must validate JSON structure and required fields instead of accepting arbitrary payloads.

### 13.4 Automatic Retries

Automatic retries are disabled for the initial prototype.

This avoids multiplying outbound requests, extending response times, or increasing load on target websites. A future retry policy may be considered for specific transient failures, subject to rate limits and resource budgets.

### 13.5 Rate Limit Semantics

The proposed rate limit is ten analysis API requests per minute per client IP.

One request to start an analysis counts as one request, regardless of the number of modules it runs.

The implementation must:

- Apply limits on the backend.
- Return a consistent rate-limit response.
- Avoid trusting client-supplied IP headers by default.
- Trust forwarded IP information only from explicitly configured proxies.
- Account for the limitations of in-memory rate limiting when multiple backend instances are used.

The selected hosting platform must be evaluated to determine whether a shared rate-limit store is necessary.

### 13.6 Resource Limit Validation

Before public deployment, test timeout handling, concurrency, response-size limits, request-size limits, and rate limiting under the selected hosting configuration.

A prototype value must not be treated as a production guarantee without test evidence.

---

## 14. HTTP Inspection Method

**Status: RECOMMENDED FOR STAGE 1**

Website Inspector should use a controlled HTTP GET request to inspect the response from the validated target URL.

Rules:

- Follow the redirect limit and revalidate every redirect destination.
- Read the response as a stream rather than downloading an unlimited body.
- Stop reading when the configured response-data limit is reached.
- Do not execute website JavaScript.
- Do not download or retain complete website content unless a specific feature requires it.
- Apply the configured timeout and concurrency controls.
- Avoid forwarding credentials, cookies, or authorization headers from the user's browser.
- Handle HTTP error status codes as inspection results when a valid response was received, rather than automatically treating them as transport failures.

A GET request may have side effects on some websites. DomainLens must therefore be described as a diagnostic tool, not as a guarantee that every inspected endpoint is free of side effects.

---

## 15. Privacy and Logging Policy

**Status: RECOMMENDED FOR STAGE 1**

DomainLens Stage 1 does not require a user account or database.

The backend should avoid storing analysis history or raw target URLs in persistent logs by default.

Operational logs should:

- Record only the information needed to troubleshoot service reliability and security.
- Avoid storing credentials, authorization headers, or unnecessary query parameters.
- Avoid exposing internal IP addresses, stack traces, or implementation details to public API responses.
- Use short and documented retention periods for operational logs.
- Keep secrets and environment-specific configuration out of frontend code and public responses.

Browser-local history must remain separate from server-side operational logging.

The final logging configuration must be reviewed against the logging behavior of the chosen hosting provider.

---

## 16. Open Technical Validation Items

The following items require verification or implementation planning:

1. Confirm that the selected hosting platform supports the required outbound DNS, HTTP, and TLS operations.
2. Verify timeout and concurrency behavior under the free hosting plan.
3. Confirm how client IP addresses are obtained safely behind the hosting provider's proxy.
4. Determine whether rate limiting must be shared across backend instances.
5. Select and configure the DNS resolution and connection mechanism that prevents DNS rebinding.
6. Verify the chosen IDN library and normalization behavior.
7. Test IPv4, IPv6, mixed DNS answers, redirect chains, and malformed URLs.
8. Confirm whether operational logs can be configured with appropriate retention and redaction.
9. Validate the proposed resource limits before selecting production values.

These are technical verification tasks, not reasons to silently assume a hosting capability exists.

---

## 17. Implementation Gate

Before implementation begins:

- Read all relevant project documents.
- Resolve conflicts between the security policy, technical architecture, business logic, and API specification.
- Identify which limits are confirmed decisions and which remain proposals.
- Define acceptance tests for every SSRF protection rule.
- Verify the deployment platform's networking and resource constraints.
- Do not disable security validation to make a failed inspection appear successful.
- Do not claim a target is safe merely because the available checks succeeded.

No implementation should begin until the planning stage is explicitly approved.

