# Daftar review CayRus

Dibuat otomatis oleh `tools/validate.py`. Status: 83 butir [uncertain], 71 butir perlu dicek, 532 sel yang dibetulkan manual (status generated). Data lengkap ada di `data/review.json`.

Cara membaca: `ref` = id entri (w… kata, v… baris kata kerja, p… pasangan), `kolom` = bagian tabel, `nilai` = yang tampil di aplikasi, `alternatif` = bentuk dari sumber lain.

## A. Bentuk [uncertain] (tampil dengan tanda ? kuning)

| ref | kata | kolom | nilai | alternatif | alasan |
| --- | --- | --- | --- | --- | --- |
| v030 | работать | pair | работать/отработать | отрабатывать, поработать, сработать | pasangan aspek di file berbeda dengan OpenRussian |
| v039 | найти | pair | искать/найти | находить, поискать | pasangan aspek di file berbeda dengan OpenRussian |
| v046 | ходить | pair | ходить/пойти | сходить | pasangan aspek di file berbeda dengan OpenRussian |
| v085 | играть | pair | играть/поиграть | сыграть | pasangan aspek di file berbeda dengan OpenRussian |
| v096 | искать | pair | искать/найти | находить, поискать | pasangan aspek di file berbeda dengan OpenRussian |
| v215 | носить | pair | носить/понести | износить, наносить, нести, относить, сносить | pasangan aspek di file berbeda dengan OpenRussian |
| v229 | закричать | pair | кричать/закричать | крикнуть | pasangan aspek di file berbeda dengan OpenRussian |
| v345 | болеть | pair | болеть/заболеть | заболевать | pasangan aspek di file berbeda dengan OpenRussian |
| v394 | готовиться | pair | готовиться/приготовиться | готовить/приготовить | file menulis готовить/приготовить |
| v421 | летать | pair | летать/полететь | лететь, полетать | pasangan aspek di file berbeda dengan OpenRussian |
| v444 | тянуться | pair | тянуться/вытянуться | вытягиваться, потянуться, протянуться | pasangan aspek di file berbeda dengan OpenRussian |
| v461 | сомневаться | pair | сомневаться/засомневаться | усомниться | pasangan aspek di file berbeda dengan OpenRussian |
| v468 | костить | pair | костить/скостить | раскостить, скащивать | pasangan aspek di file berbeda dengan OpenRussian |
| w0213 | свет | decl.pl.nom | све́ты |  | OpenRussian dan pymorphy3 berbeda |
| w0213 | свет | decl.pl.gen | све́тов |  | OpenRussian dan pymorphy3 berbeda |
| w0213 | свет | decl.pl.dat | све́там |  | OpenRussian dan pymorphy3 berbeda |
| w0213 | свет | decl.pl.acc | све́ты |  | OpenRussian dan pymorphy3 berbeda |
| w0213 | свет | decl.pl.ins | све́тами |  | OpenRussian dan pymorphy3 berbeda |
| w0213 | свет | decl.pl.pre | све́тах |  | OpenRussian dan pymorphy3 berbeda |
| w0451 | грудь | decl.sg.gen | гру́ди |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w0451 | грудь | decl.sg.dat | гру́ди |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w0451 | грудь | decl.sg.acc | грудь |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w0451 | грудь | decl.sg.ins | грудью |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w0451 | грудь | decl.sg.pre | гру́ди |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w0451 | грудь | decl.pl.dat | грудям |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w0451 | грудь | decl.pl.acc | гру́ди |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w0451 | грудь | decl.pl.ins | грудями |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w0451 | грудь | decl.pl.pre | грудях |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w0462 | кой | lemma | кой |  | kata arkais (кой = какой) |
| w0756 | придтись | lemma | придтись |  | ejaan tidak baku; bentuk baku прийтись |
| w1117 | пыль | decl.pl.nom | пы́ли |  | OpenRussian dan pymorphy3 berbeda |
| w1117 | пыль | decl.pl.gen | пы́лей |  | OpenRussian dan pymorphy3 berbeda |
| w1117 | пыль | decl.pl.dat | пы́лям |  | OpenRussian dan pymorphy3 berbeda |
| w1117 | пыль | decl.pl.acc | пы́ли |  | OpenRussian dan pymorphy3 berbeda |
| w1117 | пыль | decl.pl.ins | пы́лями |  | OpenRussian dan pymorphy3 berbeda |
| w1117 | пыль | decl.pl.pre | пы́лях |  | OpenRussian dan pymorphy3 berbeda |
| w1168 | пошлый | lemma | пошлый |  | arti 'vulgar'; periksa apakah maksudnya прошлый (sudah ada #269) |
| w1314 | мясо | decl.pl.nom | мя́са |  | OpenRussian dan pymorphy3 berbeda |
| w1314 | мясо | decl.pl.gen | мяс |  | OpenRussian dan pymorphy3 berbeda |
| w1314 | мясо | decl.pl.dat | мя́сам |  | OpenRussian dan pymorphy3 berbeda |
| w1314 | мясо | decl.pl.acc | мя́са |  | OpenRussian dan pymorphy3 berbeda |
| w1314 | мясо | decl.pl.ins | мя́сами |  | OpenRussian dan pymorphy3 berbeda |
| w1314 | мясо | decl.pl.pre | мя́сах |  | OpenRussian dan pymorphy3 berbeda |
| w1529 | честной | lemma | честной |  | kemungkinan maksudnya честный |
| w1529 | честной | decl.m.nom | че́стной |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.m.gen | че́стного |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.m.dat | че́стному |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.m.acc.anim | че́стного |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.m.acc.inan | че́стной |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.m.ins | че́стным |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.m.pre | че́стном |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.n.nom | че́стное |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.n.gen | че́стного |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.n.dat | че́стному |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.n.acc | че́стное |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.n.ins | че́стным |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.n.pre | че́стном |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.f.nom | че́стная |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.f.gen | че́стной |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.f.dat | че́стной |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.f.acc | че́стную |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.f.ins | че́стной, честною |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.f.pre | че́стной |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.pl.nom | че́стные |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.pl.gen | че́стных |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.pl.dat | че́стным |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.pl.acc.anim | че́стных |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.pl.acc.inan | че́стные |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.pl.ins | че́стными |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1529 | честной | decl.pl.pre | че́стных |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| w1551 | серьезно | lemma | серьезно |  | ejaan tanpa ё: серьёзно |
| w1652 | твердый | lemma | твердый |  | ejaan tanpa ё: твёрдый |
| w1800 | лед | lemma | лед |  | ejaan tanpa ё: лёд |
| w1864 | столовый | lemma | столовый |  | kemungkinan maksudnya столовая (ruang makan) |
| ws102 | насчет | lemma | насчет |  | ejaan tanpa ё: насчёт |
| p258.ipf | видать | pres.1sg | видаю |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| p258.ipf | видать | pres.2sg | видаешь |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| p258.ipf | видать | pres.3sg | видает |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| p258.ipf | видать | pres.1pl | видаем |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| p258.ipf | видать | pres.2pl | видаете |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| p258.ipf | видать | pres.3pl | видают |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| p258.ipf | видать | imp.sg | видай |  | OpenRussian kosong; bentuk dari pymorphy3 saja |
| p258.ipf | видать | imp.pl | видайте |  | OpenRussian kosong; bentuk dari pymorphy3 saja |

## B. Perlu dicek (kata yang disambung dari potongan baris PDF, pasangan aspek yang dibetulkan)

| ref | kata | kolom | nilai | alternatif | alasan |
| --- | --- | --- | --- | --- | --- |
| собственный |  | lemma | собственный | собстве- нный | kata terpotong tanda hubung di PDF, disambung otomatis |
| действительно |  | lemma | действительно | действи- тельно | kata terpotong tanda hubung di PDF, disambung otomatis |
| рассказывать |  | lemma | рассказывать | рассказы- вать | kata terpotong tanda hubung di PDF, disambung otomatis |
| происходить |  | lemma | происходить | происхо- дить | kata terpotong tanda hubung di PDF, disambung otomatis |
| единственный |  | lemma | единственный | единст- венный | kata terpotong tanda hubung di PDF, disambung otomatis |
| необходимый |  | lemma | необходимый | необхо- димый | kata terpotong tanda hubung di PDF, disambung otomatis |
| представлять |  | lemma | представлять | предста- влять | kata terpotong tanda hubung di PDF, disambung otomatis |
| существовать |  | lemma | существовать | существо- вать | kata terpotong tanda hubung di PDF, disambung otomatis |
| почувствовать |  | lemma | почувствовать | почувст- вовать | kata terpotong tanda hubung di PDF, disambung otomatis |
| государственный |  | lemma | государственный | государс- твенный | kata terpotong tanda hubung di PDF, disambung otomatis |
| возвращаться |  | lemma | возвращаться | возвраща ться | kata terpotong tanda hubung di PDF, disambung otomatis |
| правительство |  | lemma | правительство | правите- льство | kata terpotong tanda hubung di PDF, disambung otomatis |
| разговаривать |  | lemma | разговаривать | разговари- вать | kata terpotong tanda hubung di PDF, disambung otomatis |
| удовольствие |  | lemma | удовольствие | удовольст -вие | kata terpotong tanda hubung di PDF, disambung otomatis |
| председатель |  | lemma | председатель | председа- тель | kata terpotong tanda hubung di PDF, disambung otomatis |
| деятельность |  | lemma | деятельность | деятель- ность | kata terpotong tanda hubung di PDF, disambung otomatis |
| пространство |  | lemma | пространство | простран- ство | kata terpotong tanda hubung di PDF, disambung otomatis |
| производство |  | lemma | производство | производ -ство | kata terpotong tanda hubung di PDF, disambung otomatis |
| обстоятельство |  | lemma | обстоятельство | обстояте- льство | kata terpotong tanda hubung di PDF, disambung otomatis |
| представитель |  | lemma | представитель | предста- витель | kata terpotong tanda hubung di PDF, disambung otomatis |
| одновременно |  | lemma | одновременно | одновре- менно | kata terpotong tanda hubung di PDF, disambung otomatis |
| нормальный |  | lemma | нормальный | нормаль- ный | kata terpotong tanda hubung di PDF, disambung otomatis |
| направление |  | lemma | направление | направле -ние | kata terpotong tanda hubung di PDF, disambung otomatis |
| пользоваться |  | lemma | пользоваться | пользова -ться | kata terpotong tanda hubung di PDF, disambung otomatis |
| общественный |  | lemma | общественный | обществе -нный | kata terpotong tanda hubung di PDF, disambung otomatis |
| предприятие |  | lemma | предприятие | предприя тие | kata terpotong tanda hubung di PDF, disambung otomatis |
| понравиться |  | lemma | понравиться | понрави- ться | kata terpotong tanda hubung di PDF, disambung otomatis |
| руководитель |  | lemma | руководитель | руководи -тель | kata terpotong tanda hubung di PDF, disambung otomatis |
| образование |  | lemma | образование | образова- ние | kata terpotong tanda hubung di PDF, disambung otomatis |
| определенный |  | lemma | определённый | определё -нный | kata terpotong tanda hubung di PDF, disambung otomatis |
| усмехнуться |  | lemma | усмехнуться | усмехну- ться | kata terpotong tanda hubung di PDF, disambung otomatis |
| автомобиль |  | lemma | автомобиль | автомо- биль | kata terpotong tanda hubung di PDF, disambung otomatis |
| человечество |  | lemma | человечество | челове- чество | kata terpotong tanda hubung di PDF, disambung otomatis |
| национальный |  | lemma | национальный | национа- льный | kata terpotong tanda hubung di PDF, disambung otomatis |
| предложение |  | lemma | предложение | предложе -ние | kata terpotong tanda hubung di PDF, disambung otomatis |
| международный |  | lemma | международный | междуна- родный | kata terpotong tanda hubung di PDF, disambung otomatis |
| здравствовать |  | lemma | здравствовать | здравст- вовать | kata terpotong tanda hubung di PDF, disambung otomatis |
| руководство |  | lemma | руководство | руковод- ство | kata terpotong tanda hubung di PDF, disambung otomatis |
| воспоминание |  | lemma | воспоминание | воспоми- нание | kata terpotong tanda hubung di PDF, disambung otomatis |
| практически |  | lemma | практически | практиче- ски | kata terpotong tanda hubung di PDF, disambung otomatis |
| существование |  | lemma | существование | существо- вание | kata terpotong tanda hubung di PDF, disambung otomatis |
| принадлежать |  | lemma | принадлежать | принадле -жать | kata terpotong tanda hubung di PDF, disambung otomatis |
| преступление |  | lemma | преступление | преступ- ление | kata terpotong tanda hubung di PDF, disambung otomatis |
| иностранный |  | lemma | иностранный | иностра- нный | kata terpotong tanda hubung di PDF, disambung otomatis |
| родственник |  | lemma | родственник | родствен- ник | kata terpotong tanda hubung di PDF, disambung otomatis |
| представление |  | lemma | представление | предста- вление | kata terpotong tanda hubung di PDF, disambung otomatis |
| неожиданный |  | lemma | неожиданный | неожидан- ный | kata terpotong tanda hubung di PDF, disambung otomatis |
| превратиться |  | lemma | превратиться | преврати- ться | kata terpotong tanda hubung di PDF, disambung otomatis |
| познакомиться |  | lemma | познакомиться | познакоми -ться | kata terpotong tanda hubung di PDF, disambung otomatis |
| необходимость |  | lemma | необходимость | необходи- мость | kata terpotong tanda hubung di PDF, disambung otomatis |
| сумасшедший |  | lemma | сумасшедший | сумасшед- ший | kata terpotong tanda hubung di PDF, disambung otomatis |
| интересовать |  | lemma | интересовать | интересо- вать | kata terpotong tanda hubung di PDF, disambung otomatis |
| соответствующий |  | lemma | соответствующий | соответст- вующий | kata terpotong tanda hubung di PDF, disambung otomatis |
| официальный |  | lemma | официальный | официаль -ный | kata terpotong tanda hubung di PDF, disambung otomatis |
| обыкновенный |  | lemma | обыкновенный | обыкнове- нный | kata terpotong tanda hubung di PDF, disambung otomatis |
| значительный |  | lemma | значительный | значитель -ный | kata terpotong tanda hubung di PDF, disambung otomatis |
| приближаться |  | lemma | приближаться | приближа- ться | kata terpotong tanda hubung di PDF, disambung otomatis |
| сомневаться |  | lemma | сомневаться | сомнева- ться | kata terpotong tanda hubung di PDF, disambung otomatis |
| замечательный |  | lemma | замечательный | замечате- льный | kata terpotong tanda hubung di PDF, disambung otomatis |
| исследование |  | lemma | исследование | исследо- вание | kata terpotong tanda hubung di PDF, disambung otomatis |
| любопытство |  | lemma | любопытство | любопыт- ство | kata terpotong tanda hubung di PDF, disambung otomatis |
| продолжаться |  | lemma | продолжаться | продолжа- ться | kata terpotong tanda hubung di PDF, disambung otomatis |
| строительство |  | lemma | строительство | строитель -ство | kata terpotong tanda hubung di PDF, disambung otomatis |
| v102 | приехать | pair | приезжать/приехать | ехать/поехать | file menulis ехать/поехать |
| v125 | проходить | pair | проходить/пройти | происходить/произойти | file menulis происходить/произойти |
| v132 | существовать | pair | ipf_only |  | kolom pasangan aspek kosong di file; aspek dari OpenRussian |
| v177 | придтись | pair | приходиться/прийтись | приходиться/прийтись | ejaan tidak baku dari прийтись |
| v182 | протянуть | pair | протягивать/протянуть | протянуть/протягивать | urutan НСВ/СВ di file terbalik |
| v186 | взглянуть | pair | взглядывать/взглянуть | взглянуть/взглядывать | urutan НСВ/СВ di file terbalik |
| v201 | нести | pair | нести/понести | нести/понесит | salah ketik di file diperbaiki |
| v419 | успокоиться | pair | успокаиваться/успокоиться | успокоиться/успокаиваться | urutan НСВ/СВ di file terbalik |

## C. Dibetulkan manual (status generated, tanda G abu-abu)

Bentuk dari kamus bertentangan atau kosong, lalu saya isi dengan bentuk baku. Ringkasan per entri:

| ref | kata | jumlah sel |
| --- | --- | --- |
| p001 | быть | 4 |
| p082 | приезжать/приехать | 2 |
| p112 | хватать/хватить | 11 |
| p136 | петь/спеть | 8 |
| p147 | уезжать/уехать | 2 |
| p163 | двигаться/двинуться | 2 |
| p197 | вытаскивать/вытащить | 2 |
| p245 | выдерживать/выдержать | 2 |
| p251 | пожимать/пожать | 8 |
| p283 | стоить | 11 |
| p301 | звучать/прозвучать | 13 |
| p345 | тянуться/вытянуться | 2 |
| p372 | сходить/сойти | 6 |
| p380 | тащить/вытащить | 2 |
| p385 | дожидаться/дождаться | 8 |
| p399 | хотеться | 1 |
| w0004 | он | 3 |
| w0006 | я | 1 |
| w0015 | она | 2 |
| w0018 | они | 2 |
| w0022 | мы | 1 |
| w0024 | ты | 1 |
| w0025 | вы | 1 |
| w0035 | один | 26 |
| w0040 | себя | 1 |
| w0046 | кто | 2 |
| w0049 | год | 1 |
| w0063 | наш | 26 |
| w0112 | что | 1 |
| w0132 | никто | 1 |
| w0135 | ваш | 26 |
| w0143 | три | 1 |
| w0182 | ряд | 1 |
| w0193 | деньги | 6 |
| w0242 | пол | 3 |
| w0249 | зачем | 1 |
| w0281 | пять | 4 |
| w0289 | оно | 3 |
| w0344 | оба | 11 |
| w0345 | собственный | 2 |
| w0357 | четыре | 1 |
| w0376 | великий | 4 |
| w0403 | десять | 4 |
| w0407 | двадцать | 4 |
| w0485 | ветер | 6 |
| w0490 | лучший | 26 |
| w0506 | данный | 4 |
| w0564 | прежний | 26 |
| w0578 | особый | 4 |
| w0613 | счастье | 12 |
| w0660 | двое | 4 |
| w0677 | член | 2 |
| w0734 | сорок | 2 |
| w0742 | шесть | 4 |
| w0744 | тридцать | 4 |
| w0758 | уверенный | 3 |
| w0866 | тень | 1 |
| w0877 | лето | 6 |
| w0904 | бок | 12 |
| w0908 | стул | 6 |
| w0944 | высший | 30 |
| w0968 | семь | 4 |
| w0980 | очередной | 1 |
| w1014 | кулак | 2 |
| w1035 | мировой | 1 |
| w1047 | малый | 4 |
| w1071 | трое | 4 |
| w1167 | восемь | 4 |
| w1195 | деревянный | 4 |
| w1202 | пятьдесят | 4 |
| w1243 | ближайший | 26 |
| w1250 | существо | 1 |
| w1255 | Америка | 6 |
| w1284 | участок | 2 |
| w1322 | дальний | 1 |
| w1350 | внешний | 4 |
| w1372 | рад | 4 |
| w1382 | жертва | 1 |
| w1401 | полтора | 10 |
| w1423 | установить | 1 |
| w1435 | пятнадцать | 4 |
| w1458 | церковь | 1 |
| w1485 | взрослый | 1 |
| w1513 | мороз | 1 |
| w1522 | остальное | 12 |
| w1554 | горе | 6 |
| w1565 | шофёр | 12 |
| w1588 | полк | 1 |
| w1632 | нижний | 1 |
| w1657 | вынужденный | 3 |
| w1680 | домашний | 1 |
| w1773 | особенный | 1 |
| w1843 | строгий | 1 |
| w1851 | полчаса | 12 |
| w1854 | двенадцать | 4 |
| w1864 | столовый | 4 |
| w1927 | девять | 3 |
| w1938 | север | 2 |
| ws053 | нечего | 2 |
