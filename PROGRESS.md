# CayRus — status pengerjaan

Rujukan: PRD "CayRus: Aplikasi Hafalan Kosakata Rusia–Indonesia (PWA)" (disetujui 8 Nov 2026).

## Milestone

| # | Milestone | Status |
| --- | --- | --- |
| M1 | Data dasar | Selesai 8 Nov 2026 (koreksi kelas kata: мочь → kata kerja, правда → kata benda) |
| M2 | Batch kata W01–W10 | Selesai 8 Nov 2026 |
| M3 | Batch kata kerja V01–V03 | Berikutnya |
| M4 | Grammar + bank soal | Belum |
| M5 | Aplikasi PWA | Belum |
| M6 | Pengujian | Belum |
| M7 | Serah terima (push ke achmadcahyaperwira/Cayrus) | Belum |

## Batch

| Batch | Entri | Ditulis | Kata kerja terhubung ke V | Status |
| --- | --- | --- | --- | --- |
| W01 | 184 | 138 | 46 | Selesai: 138 terjemahan + contoh, 41 perbaikan bentuk, 6 [uncertain] tersisa |
| W02 | 184 | 127 | 57 | Selesai: 127 terjemahan + contoh, 29 perbaikan bentuk, 0 [uncertain] tersisa |
| W03 | 184 | 140 | 44 | Selesai: 140 terjemahan + contoh, 22 perbaikan bentuk, 10 [uncertain] tersisa (грудь, кой) |
| W04 | 184 | 146 | 38 | Selesai: 146 terjemahan + contoh, 30 perbaikan bentuk (сто → bilangan, член bernyawa), 1 [uncertain] (придтись) |
| W05 | 184 | 133 | 51 | Selesai: 133 terjemahan + contoh, 26 perbaikan bentuk, 0 [uncertain] |
| W06 | 184 | 135 | 49 | Selesai: 135 terjemahan + contoh, 25 perbaikan bentuk, 7 [uncertain] (jamak пыль, lema пошлый) |
| W07 | 184 | 135 | 49 | Selesai: 135 terjemahan + contoh, 30 perbaikan bentuk, 6 [uncertain] (jamak мясо) |
| W08 | 184 | 135 | 49 | Selesai: 135 terjemahan + contoh, 26 perbaikan bentuk, 29 [uncertain] (semua dari lema janggal честной) |
| W09 | 184 | 129 | 55 | Selesai: 129 terjemahan + contoh, 33 perbaikan bentuk (страсть → kata benda), 2 [uncertain] (lema лед, столовый) |
| W10 | 185 | 173 | 12 | Selesai: 173 terjemahan + contoh (termasuk 109 kata tugas), 8 perbaikan, 1 [uncertain] (lema насчет) |

## Batch kata kerja

| Batch | Pasangan | Baris | Status |
| --- | --- | --- | --- |
| V01 | 130 | 213 | Selesai: terjemahan + 253 contoh, 33 perbaikan bentuk, 8 catatan pasangan |
| V02 | 130 | — | Belum — batch berikutnya |
| V03 | 127 | — | Belum |

Kata kerja yang ada di file kata kerja mendapat terjemahan dan contoh di batch V (data dipakai bersama).

## Izin

- Push otomatis ke achmadcahyaperwira/Cayrus di akhir setiap sesi (izin pengguna, 8 Nov 2026).

## Cara melanjutkan

1. Data dasar dibuat ulang dengan `python3 tools/build_base.py <folder-openrussian>` (sumber: github.com/Badestrand/russian-dictionary).
2. Data dasar lalu `python3 tools/merge.py` menghasilkan `data/words.json`, `data/review.json`.
3. Batch ditulis di `work/batches/Wnn.tsv` (id, terjemahan, contoh RU, contoh ID, catatan) dan `Wnn.fix.json` (perbaikan bentuk berstatus g).
4. Kalimat untuk melanjutkan di percakapan: "lanjut dari batch <nama batch berikutnya>".
