"""M4: modul grammar + bank soal dari bentuk berstatus v.

Pemakaian: python3 tools/build_grammar.py
Masukan : data/words.json, work/grammar_src.json, work/accent_lookup.json
Hasil   : data/grammar.json, data/questions.json, work/grammar_report.json
"""
import json, re, hashlib, collections
from pathlib import Path
import pymorphy3

ROOT = Path(__file__).resolve().parent.parent
M = pymorphy3.MorphAnalyzer()
ACUTE = "́"
LOOK = json.load(open(ROOT / "work" / "accent_lookup.json"))
words = {e["id"]: e for e in json.load(open(ROOT / "data" / "words.json"))["entries"]}
by_lemma = {}
for e in words.values():
    if e["pos"] == "noun" and e.get("decl"):
        by_lemma.setdefault(e["lemma"], e)
src = json.load(open(ROOT / "work" / "grammar_src.json"))
CASE_NAME = {c["id"]: c["name"] for c in src["cases"]}
CASES = ["nom", "gen", "dat", "acc", "ins", "pre"]
problems = []


def norm(s):
    return s.replace(ACUTE, "").replace("ё", "е").lower().strip()


def accent_token(t):
    if ACUTE in t or sum(c in "аеёиоуыэюяАЕЁИОУЫЭЮЯ" for c in t) <= 1 or "ё" in t.lower():
        return t
    c = [x for x in LOOK.get(norm(t), []) if ACUTE in x or "ё" in x]
    if c and len({x.replace("ё", "е") for x in c}) == 1:
        a = c[0]
        return a[:1].upper() + a[1:] if t[:1].isupper() else a
    return t


TOKEN = re.compile(r"[А-Яа-яЁё́]+")


def accent_sentence(s):
    return TOKEN.sub(lambda m: accent_token(m.group(0)), s)


def cell(entry, num, case):
    d = entry["decl"]
    return (d.get(num) or {}).get(case)


def gloss(entry):
    t = entry["translation"]["text"]
    t = re.split(r"[;,]", t)[0]
    return re.sub(r"\s*\(.*?\)", "", t).strip()


# --- modul grammar ------------------------------------------------------------
out_cases = []
for c in src["cases"]:
    exs = []
    for ex in c["examples"]:
        r = ex["ref"]
        e = words[r["entry"]]
        f = cell(e, r["num"], r["case"])
        if not f or f[1] != "v":
            problems.append(f"grammar {c['id']}: contoh '{ex['ru']}' memakai bentuk non-v ({f})")
        elif not ({norm(x) for x in f[0].split(",")} & {norm(t) for t in TOKEN.findall(ex["ru"])}):
            problems.append(f"grammar {c['id']}: bentuk {f[0]} tidak ada di '{ex['ru']}'")
        exs.append({"ru": accent_sentence(ex["ru"]), "id": ex["id"], "ref": r, "form": f[0].split(",")[0] if f else None})
    prepositions = [dict(p, example=accent_sentence(p["example"])) for p in c["prepositions"]]
    out_cases.append({k: c[k] for k in ("id", "name", "nameId", "question", "summary", "functions", "endings")}
                     | {"prepositions": prepositions, "examples": exs})

# --- pola soal ------------------------------------------------------------------
T = {
 "nom": [
  ("Где ___?", "Di mana {}?", "книга телефон сумка ключ машина мама брат", "Kata yang ditanyakan dengan где? adalah subjek, jadi memakai Именительный (bentuk kamus)."),
  ("___ спит.", "{} sedang tidur.", "ребёнок кошка собака брат отец", "Subjek kalimat memakai Именительный."),
  ("Вот ___.", "Ini dia {}.", "дом школа вокзал автобус станция", "Setelah вот (ini dia) dipakai Именительный."),
  ("Это ___.", "Ini {}.", "журнал газета письмо озеро музей", "Setelah это (ini) dipakai Именительный."),
  ("___ работает в городе.", "{} bekerja di kota.", "врач учитель инженер", "Subjek kalimat memakai Именительный."),
 ],
 "gen": [
  ("У меня нет ___.", "Saya tidak punya {}.", "машина телефон ключ сумка брат сестра", "Setelah нет (tidak ada) dipakai Родительный."),
  ("Это книга ___.", "Ini buku milik {}.", "брат сестра учитель друг отец мама", "Kepemilikan (milik siapa?) dinyatakan dengan Родительный."),
  ("Он вышел из ___.", "Dia keluar dari {}.", "дом комната магазин школа театр музей", "из (dari dalam) selalu diikuti Родительный."),
  ("Дай мне стакан ___.", "Beri aku segelas {}.", "вода молоко чай", "Takaran (segelas apa?) diikuti Родительный."),
  ("Около ___ есть парк.", "Di dekat {} ada taman.", "вокзал университет озеро", "около (di dekat) diikuti Родительный."),
 ],
 "dat": [
  ("Я позвонил ___.", "Saya menelepon {}.", "брат мама друг врач сестра бабушка", "позвонить кому? — penerima memakai Дательный."),
  ("Я иду к ___.", "Saya pergi ke {}.", "врач друг бабушка сосед директор", "к (ke/menuju orang) selalu diikuti Дательный."),
  ("Мы гуляли по ___.", "Kami berjalan-jalan di {}.", "парк улица город лес сад берег", "по (sepanjang/di permukaan) diikuti Дательный."),
  ("Я дал книгу ___.", "Saya memberikan buku kepada {}.", "студент сын дочь отец подруга", "дать кому? — penerima memakai Дательный."),
  ("___ нравится музыка.", "{} menyukai musik.", "сестра отец", "Dengan нравиться, orang yang menyukai memakai Дательный."),
 ],
 "acc": [
  ("Я читаю ___.", "Saya sedang membaca {}.", "книга газета письмо журнал", "Objek langsung memakai Винительный."),
  ("Я вижу ___.", "Saya melihat {}.", "брат сестра друг кошка собака отец", "Objek langsung makhluk hidup: maskulin = bentuk Родительный, feminin berakhiran -у/-ю."),
  ("Мы идём в ___.", "Kami pergi ke {}.", "школа парк магазин театр музей университет", "в + Винительный menyatakan arah (ke mana?)."),
  ("Я жду ___.", "Saya menunggu {}.", "автобус поезд мама подруга", "ждать kata benda tertentu → objek dalam Винительный."),
  ("Я вернусь через ___.", "Saya akan kembali dalam satu {}.", "неделя месяц", "через (dalam waktu …) diikuti Винительный."),
  ("Он купил ___.", "Dia membeli {}.", "машина хлеб", "Objek langsung memakai Винительный."),
 ],
 "ins": [
  ("Я пишу ___.", "Saya menulis dengan {}.", "ручка", "Alat (dengan apa?) dinyatakan dengan Творительный tanpa preposisi."),
  ("Он режет хлеб ___.", "Dia memotong roti dengan {}.", "нож", "Alat (dengan apa?) dinyatakan dengan Творительный tanpa preposisi."),
  ("Я гуляю с ___.", "Saya berjalan-jalan bersama {}.", "друг собака сестра мама брат подруга", "с (bersama) diikuti Творительный."),
  ("Он стал ___.", "Dia menjadi {}.", "врач учитель писатель инженер директор", "стать кем? — profesi/peran memakai Творительный."),
  ("Самолёт летит над ___.", "Pesawat terbang di atas {}.", "город лес море озеро гора", "над (di atas) diikuti Творительный."),
  ("Кошка сидит под ___.", "Kucing duduk di bawah {}.", "стол стул окно машина", "под untuk tempat (di mana?) diikuti Творительный."),
  ("Я пью чай с ___.", "Saya minum teh dengan {}.", "молоко хлеб", "с (dengan) diikuti Творительный."),
 ],
 "pre": [
  ("Я живу в ___.", "Saya tinggal di {}.", "город дом Москва деревня квартира", "в untuk tempat (di mana?) diikuti Предложный."),
  ("Мы говорим о ___.", "Kami membicarakan {}.", "книга фильм работа брат город", "о (tentang) diikuti Предложный."),
  ("Книга лежит на ___.", "Buku itu ada di atas {}.", "стол стул окно", "на untuk tempat (di atas) diikuti Предложный."),
  ("Он работает на ___.", "Dia bekerja di {}.", "завод станция вокзал", "на untuk tempat kerja seperti завод/станция diikuti Предложный."),
  ("Мы были в ___.", "Kami berada di {}.", "театр музей университет", "в untuk tempat (di mana?) diikuti Предложный."),
  ("Я думаю о ___.", "Saya memikirkan {}.", "мама сестра сын", "о (tentang) diikuti Предложный."),
  ("Мы отдыхали на ___.", "Kami berlibur di {}.", "море озеро", "на + Предложный untuk tempat terbuka (laut, danau)."),
 ],
}
TYPES = ["mcq", "fill", "pick_case"]


def h(s):
    return int(hashlib.md5(s.encode()).hexdigest(), 16)


questions = []
stats = collections.Counter()
for case in CASES:
    combos = []
    for ti, (ru, idn, nouns, expl) in enumerate(T[case]):
        for lem in nouns.split():
            e = by_lemma.get(lem)
            if not e:
                problems.append(f"{case}: kata {lem} tidak ada")
                continue
            f = cell(e, "sg", case)
            if not f or f[1] != "v":
                problems.append(f"{case}: {lem} bentuk {f} bukan v, dilewati")
                continue
            combos.append((ti, lem, e, f, ru, idn, expl))
    # selang-seling antar pola agar bervariasi
    by_t = collections.defaultdict(list)
    for c in combos:
        by_t[c[0]].append(c)
    order = []
    while any(by_t.values()):
        for ti in sorted(by_t):
            if by_t[ti]:
                order.append(by_t[ti].pop(0))
    for n, (ti, lem, e, f, ru, idn, expl) in enumerate(order[:25]):
        qtype = TYPES[n % 3]
        variants = [x.strip() for x in f[0].split(",")]
        ans = variants[0]
        shown = ans[:1].upper() + ans[1:] if ru.startswith("___") else ans
        g = gloss(e)
        prompt_id = idn.format(g)
        prompt_id = prompt_id[:1].upper() + prompt_id[1:]
        q = {"id": f"q-{case}-{n + 1:02d}", "case": case, "type": qtype,
             "target": {"entry": e["id"], "lemma": e["accented"][0], "number": "sg", "case": case},
             "explanation": f"{expl} Bentuk {CASE_NAME[case]} tunggal dari {e['accented'][0]}: {ans}."}
        if qtype == "pick_case":
            q["prompt"] = {"ru": accent_sentence(ru.replace("___", "[" + shown + "]")), "id": prompt_id}
            q["answer"] = case
            q["options"] = CASES
        else:
            hint = f" — (kata: {g})" if (case == "nom" and qtype == "fill") else f" — ({e['accented'][0]})"
            q["prompt"] = {"ru": accent_sentence(ru), "id": prompt_id + hint}
            q["answer"] = ans
            q["accept"] = variants
            if qtype == "mcq":
                pool = []
                for c2 in CASES:
                    f2 = cell(e, "sg", c2)
                    if f2 and f2[1] == "v":
                        v2 = f2[0].split(",")[0].strip()
                        if norm(v2) != norm(ans) and norm(v2) not in {norm(p) for p in pool}:
                            pool.append(v2)
                if len(pool) < 3:
                    problems.append(f"{q['id']}: pengecoh kurang ({pool})")
                opts = pool[:3] + [ans]
                opts.sort(key=lambda o: h(q["id"] + o))
                if ru.startswith("___"):
                    opts = [o[:1].upper() + o[1:] for o in opts]
                    q["answer"] = shown
                    q["accept"] = [v[:1].upper() + v[1:] for v in variants]
                q["options"] = opts
        # cek: kalimat lengkap hanya berisi kata yang dikenal
        full = ru.replace("___", ans)
        for t in TOKEN.findall(full):
            if not M.word_is_known(norm(t)):
                problems.append(f"{q['id']}: kata tidak dikenal '{t}'")
        questions.append(q)
        stats[(case, qtype)] += 1

per_case = collections.Counter(q["case"] for q in questions)
for case in CASES:
    if per_case[case] < 15:
        problems.append(f"{case}: hanya {per_case[case]} soal (< 15)")
json.dump({"intro": src["intro"], "cases": out_cases}, open(ROOT / "data" / "grammar.json", "w"), ensure_ascii=False, indent=1)
json.dump({"questions": questions}, open(ROOT / "data" / "questions.json", "w"), ensure_ascii=False, indent=1)
rep = {"per_case": dict(per_case), "per_type": {f"{a}/{b}": v for (a, b), v in stats.items()}, "problems": problems}
json.dump(rep, open(ROOT / "work" / "grammar_report.json", "w"), ensure_ascii=False, indent=1)
print("soal per kasus:", dict(per_case))
print("per jenis:", collections.Counter(q["type"] for q in questions))
print("masalah:", len(problems))
for p in problems:
    print("  ", p)
