# CayRus — status pengerjaan

Rujukan: PRD "CayRus: Aplikasi Hafalan Kosakata Rusia–Indonesia (PWA)" (disetujui 8 Nov 2026).

## Milestone

| # | Milestone | Status |
| --- | --- | --- |
| M1 | Data dasar | Selesai 8 Nov 2026 |
| M2 | Batch kata W01–W10 | Berjalan |
| M3 | Batch kata kerja V01–V03 | Belum |
| M4 | Grammar + bank soal | Belum |
| M5 | Aplikasi PWA | Belum |
| M6 | Pengujian | Belum |
| M7 | Serah terima (push ke achmadcahyaperwira/Cayrus) | Belum |

## Batch

| Batch | Entri | Ditulis | Kata kerja terhubung ke V | Status |
| --- | --- | --- | --- | --- |
| W01 | 184 | 139 | 45 | Belum |
| W02 | 184 | 127 | 57 | Belum |
| W03 | 184 | 140 | 44 | Belum |
| W04 | 184 | 147 | 37 | Belum |
| W05 | 184 | 133 | 51 | Belum |
| W06 | 184 | 135 | 49 | Belum |
| W07 | 184 | 137 | 47 | Belum |
| W08 | 184 | 135 | 49 | Belum |
| W09 | 184 | 129 | 55 | Belum |
| W10 | 185 | 173 | 12 | Belum |

Kata kerja yang ada di file kata kerja mendapat terjemahan dan contoh di batch V (data dipakai bersama).

## Cara melanjutkan

1. Data dasar dibuat ulang dengan `python3 tools/build_base.py <folder-openrussian>` (sumber: github.com/Badestrand/russian-dictionary).
2. Batch ditulis di `work/batches/Wnn.tsv` (id, terjemahan, contoh RU, contoh ID, catatan) dan `Wnn.fix.json` (perbaikan bentuk berstatus g).
3. Kalimat untuk melanjutkan di percakapan: "lanjut dari batch <nama batch berikutnya>".
