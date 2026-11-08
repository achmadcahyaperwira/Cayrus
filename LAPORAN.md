# Laporan akhir CayRus

Tanggal: 8 November 2026 · Versi aplikasi 1.0.0 · Repo: https://github.com/achmadcahyaperwira/Cayrus

Semua kata dan kata kerja dari kedua file masuk aplikasi: **1.841 entri kata** dan **500 baris kata kerja** (398 pasangan aspek). Validator data lulus **22/22** pemeriksaan dan uji aplikasi otomatis lulus **34/34**. Tersisa **83 butir [uncertain]** untuk ditinjau (daftar lengkap di [REVIEW.md](REVIEW.md)).

## 1. Jumlah entri per kategori

File kata berisi 1.736 kata bernomor dan 111 kata tugas tanpa nomor. Setelah 5 kata ganda dan 2 kata tugas yang juga bernomor dihitung sekali, tersisa 1.840 lema unik (bukan 2.000). знать (#50 kata kerja, #569 kata benda "kaum bangsawan") dipisah menjadi dua entri, sehingga totalnya 1.841. Tidak ada kata yang ditambahkan dari luar file.

| Kelas kata | Entri |
| --- | --- |
| kata benda | 775 |
| kata kerja | 462 |
| kata sifat | 283 |
| adverbia | 159 |
| preposisi | 39 |
| konjungsi | 38 |
| partikel | 32 |
| bilangan | 21 |
| kata ganti | 19 |
| interjeksi | 7 |
| predikatif | 5 |
| lainnya | 1 |
| **Total** | **1.841** |

| Kata kerja | Jumlah |
| --- | --- |
| Baris dari file "500 Russian Verbs" | 500 |
| Pasangan НСВ/СВ | 346 |
| Hanya НСВ / hanya СВ / biaspektual | 41 / 9 / 2 |
| Pasangan sesuai file / dibetulkan (salah ketik, urutan) / [uncertain] / tidak tercantum di file | 369 / 5 / 12 / 12 |
| Contoh kalimat kata kerja | 734 |

12 pasangan "tidak tercantum di file" adalah kata kerja yang hanya ada di file kata (mis. хотеться, участвовать); tabel konjugasinya ditampilkan tanpa mengarang pasangan.

## 2. Status bentuk

| | Terverifikasi | Generated | [uncertain] |
| --- | --- | --- | --- |
| Bentuk kata (tabel deklinasi) | 16.777 | 596 | 53 |
| Bentuk kata kerja | 9.564 | 88 | 8 |

- Terverifikasi = bentuk dari data OpenRussian yang cocok dengan pymorphy3; aksen dari OpenRussian.
- Generated = dibetulkan manual karena kedua sumber bertentangan atau kosong (mis. tabel наш/ваш/один, спою́ bukan спе́ю, дожду́сь). Semua terjemahan Indonesia dan contoh kalimat juga berstatus generated, sesuai PRD.
- Di aplikasi, bentuk generated diberi label **G** dan bentuk [uncertain] diberi **?** kuning. Uji otomatis memastikan jumlah label sama dengan jumlah sel berstatus itu.

## 3. Butir [uncertain] (83 butir, 27 entri)

| ref | kata | butir |
| --- | --- | --- |
| p258 | видать | 8 |
| v030 | работать | 1 |
| v039 | найти | 1 |
| v046 | ходить | 1 |
| v085 | играть | 1 |
| v096 | искать | 1 |
| v215 | носить | 1 |
| v229 | закричать | 1 |
| v345 | болеть | 1 |
| v394 | готовиться | 1 |
| v421 | летать | 1 |
| v444 | тянуться | 1 |
| v461 | сомневаться | 1 |
| v468 | костить | 1 |
| w0213 | свет | 6 |
| w0451 | грудь | 9 |
| w0462 | кой | 1 |
| w0756 | придтись | 1 |
| w1117 | пыль | 6 |
| w1168 | пошлый | 1 |
| w1314 | мясо | 6 |
| w1529 | честной | 27 |
| w1551 | серьезно | 1 |
| w1652 | твердый | 1 |
| w1800 | лед | 1 |
| w1864 | столовый | 1 |
| ws102 | насчет | 1 |

Sebagian besar berasal dari lema janggal di file (честной, пошлый, столовый, кой, придтись, лед/твердый/серьезно/насчет tanpa ё), jamak yang jarang dipakai (свет, пыль, мясо), tekanan грудь, bentuk kini видать, dan 12 pasangan aspek dari file yang berbeda dengan kamus pembanding. Rinciannya, ditambah 71 butir "perlu dicek" dan daftar perbaikan manual, ada di [REVIEW.md](REVIEW.md).

## 4. Grammar dan soal

6 kasus, masing-masing berisi pertanyaan kasus, fungsi, preposisi, tabel akhiran kata benda dan kata sifat, dan 4 contoh. Ada **145 soal** (nom 25, gen 24, dat 24, acc 24, ins 24, pre 24) dalam 3 format: pilihan ganda, isian, dan pilih kasus. Semua soal dan contoh grammar hanya memakai bentuk terverifikasi.

## 5. Hasil validasi data (22/22)

- [x] entri kata = 1.841 — 1841
- [x] setiap kata di file kata ada di aplikasi (1.736 bernomor + 111 kata tugas) — 1840 lema sumber, hilang: []
- [x] setiap peringkat di file kata ada di aplikasi — 1736 peringkat
- [x] baris kata kerja = 500, peringkat 1–500 lengkap
- [x] setiap kata kerja di file kata kerja ada di aplikasi
- [x] setiap entri kata punya terjemahan Indonesia
- [x] setiap entri kata punya 1 contoh + terjemahan
- [x] setiap entri punya kata beraksen
- [x] setiap kata benda yang dideklinasi punya 6 kasus (tunggal & jamak, kecuali hanya-tunggal/jamak)
- [x] setiap kata benda punya gender
- [x] kata yang tidak dideklinasi tidak punya tabel
- [x] kata sifat/kata ganti/bilangan yang dideklinasi punya tabel
- [x] setiap pasangan НСВ/СВ lengkap (kini 6, lampau 4, masa depan 6, imperatif 2) + 2 contoh + kalimat pembeda
- [x] kata kerja satu aspek/biaspektual ditandai — {'ipf_only': 41, 'pair': 346, 'biaspectual': 2, 'pf_only': 9}
- [x] setiap baris kata kerja punya terjemahan
- [x] status hanya v/g/u — {'g': 684, 'v': 26341, 'u': 61}
- [x] setiap entri dengan bentuk [uncertain] tercatat di daftar review
- [x] modul grammar: 6 kasus, masing-masing ≥ 3 contoh
- [x] contoh grammar memakai bentuk terverifikasi
- [x] ≥ 15 soal per kasus — {'nom': 25, 'gen': 24, 'dat': 24, 'acc': 24, 'ins': 24, 'pre': 24}
- [x] 3 format soal ada di setiap kasus
- [x] soal hanya memakai bentuk berstatus terverifikasi

## 6. Hasil uji aplikasi (34/34)

Diuji di Chrome headless dengan layar 375 × 812 (mode HP). Tangkapan layar ada di `work/screens/`.

- [x] service worker aktif
- [x] halaman dikendalikan service worker setelah muat ulang
- [x] semua aset tersimpan di cache
- [x] manifest: name, short_name, start_url, display standalone, ikon 192/512/maskable
- [x] Chrome (profil biasa): tidak ada error installability
- [x] kamus: daftar 1.841 entri dengan virtual list (< 60 baris di DOM)
- [x] pencarian Kiril 'книг' menemukan книга (CPU 4× lebih lambat)
- [x] pencarian arti Indonesia 'rumah' menemukan дом
- [x] filter status [uncertain] berjalan
- [x] tab kata kerja: 500 baris
- [x] detail terbuka < 200 ms (CPU 4×, termasuk jeda alat uji)
- [x] kata benda: tabel 6 kasus × tunggal/jamak
- [x] kata benda: aksen tampil (кни́га)
- [x] kata sifat: 4 kolom + akusatif hidup/mati + bentuk pendek
- [x] kata tak berubah ditandai 'tidak dideklinasi' tanpa tabel
- [x] bentuk generated tidak tampil sebagai terverifikasi (один: semua sel G berlabel)
- [x] bentuk [uncertain] berlabel '?' (w0213)
- [x] kata kerja: pasangan говорить/сказать + kini, lampau, masa depan majemuk, imperatif
- [x] kata kerja: tombol СВ menampilkan masa depan sederhana (скажу́)
- [x] kata kerja: 2 contoh + kalimat pembeda aspek
- [x] kata kerja satu aspek ditandai (иметь)
- [x] kata kerja dari daftar kata membuka tabel konjugasi (знать)
- [x] progres hafalan tersimpan di IndexedDB
- [x] grammar: 6 kasus
- [x] halaman kasus: fungsi, preposisi, tabel akhiran, ≥3 contoh
- [x] latihan 15 soal selesai, umpan balik per soal, skor tersimpan
- [x] halaman Tentang: data offline siap
- [x] offline: aplikasi terbuka setelah jaringan diputus
- [x] offline: detail kata (город) tampil
- [x] offline: latihan grammar berjalan
- [x] offline: progres tetap ada setelah muat ulang (2 kartu)
- [x] tidak ada gulir horizontal di lebar 375 px
- [x] tidak ada permintaan ke domain lain
- [x] tidak ada error JavaScript di konsol

## 7. Catatan dan batasan

- Pemasangan dan mode offline sudah diuji otomatis di Chrome. Uji manual di HP Android dan iPhone Anda tetap perlu dilakukan setelah GitHub Pages aktif.
- GitHub Pages harus diaktifkan sekali di Settings → Pages; saya tidak punya akses untuk mengubah pengaturan repo.
- Baris #386 сходить di file mencampur dua arti. Baris ini ditautkan ke pasangan сходить/сойти dengan catatan arti СВ "pergi sebentar".
- Bentuk lokatif khusus -у́ (в лесу́, на полу́) hanya tercantum bila ada di sumber; contoh grammar "в лесу" diganti dengan contoh lain yang terverifikasi.
- Data OpenRussian berlisensi CC BY-SA 4.0; atribusi ada di halaman Tentang dan README.
