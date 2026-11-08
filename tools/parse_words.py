import pdfplumber, re, json, sys

PDF = "/mnt/user-data/uploads/1000_and_2000_freq_russian_words.pdf"
OUT = sys.argv[1]
entries, service, orphans = [], {}, []
CYR = re.compile(r"^[А-Яа-яЁё\-\.]+$")
with pdfplumber.open(PDF) as pdf:
    for pno, page in enumerate(pdf.pages):
        part = 1 if pno < 2 else 2
        words = page.extract_words(x_tolerance=1.5, y_tolerance=2)
        used = set()
        nums = [i for i, w in enumerate(words) if re.fullmatch(r"\d{1,4}", w["text"])]
        for i in nums:
            n = words[i]
            # a rank is followed on the same line by a word starting within ~8pt
            cand = [j for j, w in enumerate(words)
                    if j != i and abs(w["top"] - n["top"]) < 3 and 0 <= w["x0"] - n["x1"] < (16 if len(n["text"])==1 else 9)
                    and CYR.match(w["text"])]
            if not cand:
                continue
            j = min(cand, key=lambda j: words[j]["x0"])
            text = words[j]["text"]
            used.update({i, j})
            # continuation on the next line(s): fragment starting with '-' or lowercase directly below
            below = [k for k, w in enumerate(words)
                     if k not in used and 8 < w["top"] - words[j]["top"] < 16
                     and abs(w["x0"] - words[j]["x0"]) < 14 and CYR.match(w["text"])
                     and (w["text"].startswith("-") or text.endswith("-") or w["text"] in ("ться", "тие", "нный"))]
            raw = text
            if below:
                k = below[0]
                raw = text + " " + words[k]["text"]
                text = (text.rstrip("-") + words[k]["text"].lstrip("-"))
                used.add(k)
            entries.append({"rank": int(n["text"]), "word": text.strip("."), "raw": raw,
                            "page": pno + 1, "part": part})
json.dump(entries, open(OUT, "w"), ensure_ascii=False, indent=1)
print(len(entries))
