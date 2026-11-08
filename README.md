# CayRus — hafalan kosakata Rusia–Indonesia

Aplikasi web (PWA) untuk menghafal kosakata Rusia beserta perubahan bentuknya. Bisa dipasang di HP Android dan iOS, dan berjalan penuh tanpa internet setelah dibuka sekali.

**Buka aplikasi:** https://achmadcahyaperwira.github.io/Cayrus/ (setelah GitHub Pages diaktifkan, lihat di bawah)

## Isi

- **1.841 entri kata** dari daftar "1000 & 2000 самых встречаемых слов": kata beraksen, terjemahan Indonesia, kelas kata, gender, tabel 6 падеж (tunggal dan jamak), tabel kata sifat (м/ср/ж/мн + bentuk pendek), kata ganti, bilangan, dan 1 contoh kalimat.
- **500 kata kerja** dari "500 Russian Verbs" (398 pasangan aspek): НСВ (kini, lampau, masa depan, imperatif) dan СВ (lampau, masa depan sederhana, imperatif), 2 contoh yang memperlihatkan beda aspek.
- **Grammar 6 падеж**: fungsi, preposisi, tabel akhiran, contoh, dan 145 soal latihan (pilihan ganda, isian, pilih kasus).
- **Hafalan**: flashcard RU→ID dan ID→RU dengan pengulangan berjarak, tanpa batas kartu baru per hari. Dek: Level 1–4 (peringkat #1–500, #501–1000, #1001–1500, #1501–2000), Kata Tugas, dan 500 Kata Kerja. **Progres dek** menunjukkan kata yang Hafal, Dipelajari, dan Sudah tahu; ketuk dek untuk melihat daftar katanya.

Label status pada setiap bentuk: tanpa tanda = terverifikasi (OpenRussian + pymorphy3), **G** = dibuat (generated), **?** = belum pasti. Daftar butir yang perlu ditinjau ada di [REVIEW.md](REVIEW.md). Laporan lengkap: [LAPORAN.md](LAPORAN.md).

## Mengaktifkan GitHub Pages (sekali saja)

1. Buka repo ini di GitHub → **Settings** → **Pages**.
2. Di **Build and deployment**, pilih **Deploy from a branch**, branch `main`, folder `/ (root)`, lalu **Save**.
3. Tunggu 1–2 menit sampai alamat `https://achmadcahyaperwira.github.io/Cayrus/` aktif.

## Memasang di HP

**Android (Chrome):** buka alamat di atas, tunggu sampai halaman *Tentang* menampilkan "Data offline: siap", lalu menu ⋮ → **Instal aplikasi** atau **Tambahkan ke layar utama**.

**iPhone/iPad (Safari):** buka alamat di atas, tunggu "Data offline: siap", lalu tombol **Bagikan** → **Tambahkan ke Layar Utama** → **Tambah**. Selalu buka dari ikon layar utama. Data situs yang lama tidak dibuka bisa dihapus iOS; memasang ke layar utama mengurangi risiko ini.

Progres hafalan dan skor disimpan hanya di perangkat (IndexedDB). Tanpa akun, iklan, atau pelacakan.

## Struktur repo

| Lokasi | Isi |
| --- | --- |
| `index.html`, `app.js`, `app.css`, `sw.js`, `manifest.webmanifest`, `icons/`, `fonts/` | aplikasi |
| `data/` | `words.json`, `verbs.json`, `grammar.json`, `questions.json`, `review.json` |
| `tools/` | skrip pembuat data (`build_base.py`, `merge.py`, `build_grammar.py`), validator, dan uji otomatis |
| `work/` | hasil antara, batch terjemahan, laporan uji, tangkapan layar |

Membuat ulang data: `python3 tools/build_base.py <folder data OpenRussian>` → `python3 tools/merge.py` → `python3 tools/build_grammar.py` → `python3 tools/validate.py`. Uji aplikasi: `python3 tools/test_app.py`.

## Lisensi dan sumber

- Bentuk kata dan aksen: data [OpenRussian](https://github.com/Badestrand/russian-dictionary) (openrussian.org), lisensi [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Data turunan di `data/` ikut berlisensi CC BY-SA 4.0.
- Pemeriksaan bentuk: [pymorphy3](https://github.com/no-plagiarism/pymorphy3) dengan kamus OpenCorpora (hanya dipakai saat membuat data).
- Huruf: Noto Sans, [SIL Open Font License 1.1](fonts/OFL.txt).
