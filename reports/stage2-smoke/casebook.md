# Stage-two compression traces

Run `a1bd26fe3d82dea3f65d`; split `smoke`; compressor `NousResearch/Llama-2-7b-chat-hf` on `npu:0`.

## ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:1:llmlingua_2x

- origin tokens: 3289; target: 1644; compressed: 1572; actual ratio 2.09x; budget met: True
- retained documents: 11/20; attempts: 2
- restrict switch: False; dynamic ratios: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
- recovery: changed=False, spans=None, answer tokens=95

| doc | doc_id | condition score | retained |
| ---: | --- | ---: | --- |
| 0 | d6247f4706224f80b49dca232e4f8f7cbdc5ef32e9f3da822870783a17a6402a | 3.314 | True |
| 12 | 10928048 | 3.260 | True |
| 18 | 10928045 | 3.107 | True |
| 5 | 10928020 | 3.068 | True |
| 3 | 18294723 | 3.010 | True |
| 6 | 10928038 | 3.010 | True |
| 7 | 10928043 | 2.959 | True |
| 9 | 2497408 | 2.912 | True |
| 11 | 12872786 | 2.904 | True |
| 4 | 3046649 | 2.902 | True |
| 1 | 10928010 | 2.832 | True |
| 15 | 8174660 | 2.805 | False |
| 10 | 3046644 | 2.691 | False |
| 2 | 3046645 | 2.666 | False |
| 17 | 10928040 | 2.664 | False |
| 16 | 3046647 | 2.537 | False |
| 13 | 9263899 | 2.453 | False |
| 14 | 3046643 | 2.414 | False |
| 8 | 9184846 | 2.408 | False |
| 19 | 13421636 | 2.369 | False |

Compressed text preview:

```text
Document [1](Title: Kangla Palace) In ancient times, 'la' was the royal palace since the reign of Pakba whoended the throne in 33 AD, to "Cheitharol Kummaba", the royal Chronicle ofur.

Document [2: History ofur) was made a union territory in956 and a fullged state in72.Maiream Koireng Singh became the first Chief Minister in972 of the Stateur. This has been dated to recorded history from 1500BC. 
```

Answer before recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **Nara Singh Maharaj** (1844–50), as mentioned in Document [5]: "to the royal chronicle, the 'Cheol Kumbaba', Nara Singh Maharaj (1844–50) was created here at the 'anglen'. This is a sacred place where theings ofur performed their coronation ceremony/erat-thouni."`

Answer after recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **Nara Singh Maharaj** (1844–50), as mentioned in Document [5]: "to the royal chronicle, the 'Cheol Kumbaba', Nara Singh Maharaj (1844–50) was created here at the 'anglen'. This is a sacred place where theings ofur performed their coronation ceremony/erat-thouni."`

Scores: before=0.0, after=0.0

## ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:5:llmlingua_2x

- origin tokens: 3289; target: 1644; compressed: 1574; actual ratio 2.09x; budget met: True
- retained documents: 11/20; attempts: 2
- restrict switch: False; dynamic ratios: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
- recovery: changed=False, spans=None, answer tokens=86

| doc | doc_id | condition score | retained |
| ---: | --- | ---: | --- |
| 4 | d6247f4706224f80b49dca232e4f8f7cbdc5ef32e9f3da822870783a17a6402a | 3.311 | True |
| 12 | 10928048 | 3.260 | True |
| 18 | 10928045 | 3.107 | True |
| 5 | 10928020 | 3.068 | True |
| 6 | 10928038 | 3.010 | True |
| 2 | 18294723 | 3.002 | True |
| 7 | 10928043 | 2.959 | True |
| 9 | 2497408 | 2.912 | True |
| 3 | 3046649 | 2.904 | True |
| 11 | 12872786 | 2.904 | True |
| 0 | 10928010 | 2.824 | True |
| 15 | 8174660 | 2.805 | False |
| 10 | 3046644 | 2.691 | False |
| 1 | 3046645 | 2.678 | False |
| 17 | 10928040 | 2.664 | False |
| 16 | 3046647 | 2.537 | False |
| 13 | 9263899 | 2.453 | False |
| 14 | 3046643 | 2.414 | False |
| 8 | 9184846 | 2.408 | False |
| 19 | 13421636 | 2.369 | False |

Compressed text preview:

```text
Document [1](Title: History of Manipur) was made a territory in956 and a full state972.Maiream Koireng Singh became the first Chief Minister in972 of the State ofur. This has been dated to recorded history from 1500BC. Mythologicalins begin with the reign of the "Konchin Tukthapa Ipu Athoupa Pakhangpa" (Phangpa was the name given to him meaning "The one who knows his father"). He gave birth to the
```

Answer before recovery: `Based on the search results, the first coronated king of Manipur at Kangla was **Pamheiba** (also known as Garibaniwaz). According to Document 4, the "Manglen" at Kangla is believed to have been developed by Maharaj Garibaniwaz in 1738, and this is the sacred place where the kings of Manipur performed their coronation ceremony.`

Answer after recovery: `Based on the search results, the first coronated king of Manipur at Kangla was **Pamheiba** (also known as Garibaniwaz). According to Document 4, the "Manglen" at Kangla is believed to have been developed by Maharaj Garibaniwaz in 1738, and this is the sacred place where the kings of Manipur performed their coronation ceremony.`

Scores: before=1.0, after=1.0

## ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:10:llmlingua_2x

- origin tokens: 3289; target: 1644; compressed: 1588; actual ratio 2.07x; budget met: True
- retained documents: 11/20; attempts: 2
- restrict switch: False; dynamic ratios: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
- recovery: changed=False, spans=None, answer tokens=82

| doc | doc_id | condition score | retained |
| ---: | --- | ---: | --- |
| 12 | 10928048 | 3.260 | True |
| 9 | d6247f4706224f80b49dca232e4f8f7cbdc5ef32e9f3da822870783a17a6402a | 3.258 | True |
| 18 | 10928045 | 3.107 | True |
| 4 | 10928020 | 3.061 | True |
| 5 | 10928038 | 3.014 | True |
| 2 | 18294723 | 3.002 | True |
| 6 | 10928043 | 2.955 | True |
| 8 | 2497408 | 2.930 | True |
| 3 | 3046649 | 2.904 | True |
| 11 | 12872786 | 2.904 | True |
| 0 | 10928010 | 2.824 | True |
| 15 | 8174660 | 2.805 | False |
| 10 | 3046644 | 2.691 | False |
| 1 | 3046645 | 2.678 | False |
| 17 | 10928040 | 2.664 | False |
| 16 | 3046647 | 2.537 | False |
| 13 | 9263899 | 2.453 | False |
| 14 | 3046643 | 2.414 | False |
| 7 | 9184846 | 2.406 | False |
| 19 | 13421636 | 2.369 | False |

Compressed text preview:

```text
Document [1](Title: History of Manipur) was made a territory in956 and a full state972.Maiream Koireng Singh became the first Chief Minister in972 of the State ofur. This has been dated to recorded history from 1500BC. Mythologicalins begin with the reign of the "Konchin Tukthapa Ipu Athoupa Pakhangpa" (Phangpa was the name given to him meaning "The one who knows his father"). He gave birth to the
```

Answer before recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **Nongda Lairen Pakhangba**. Document [1] states that "Kangla" was the first capital, and Document [9] notes that "'Kangla' was the royal palace since the time of Nongda Lairen Pakhangba who ascended the throne in 33 AD."`

Answer after recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **Nongda Lairen Pakhangba**. Document [1] states that "Kangla" was the first capital, and Document [9] notes that "'Kangla' was the royal palace since the time of Nongda Lairen Pakhangba who ascended the throne in 33 AD."`

Scores: before=1.0, after=1.0

## ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:15:llmlingua_2x

- origin tokens: 3289; target: 1644; compressed: 1571; actual ratio 2.09x; budget met: True
- retained documents: 11/20; attempts: 2
- restrict switch: False; dynamic ratios: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
- recovery: changed=False, spans=None, answer tokens=103

| doc | doc_id | condition score | retained |
| ---: | --- | ---: | --- |
| 11 | 10928048 | 3.260 | True |
| 14 | d6247f4706224f80b49dca232e4f8f7cbdc5ef32e9f3da822870783a17a6402a | 3.256 | True |
| 18 | 10928045 | 3.107 | True |
| 4 | 10928020 | 3.061 | True |
| 5 | 10928038 | 3.014 | True |
| 2 | 18294723 | 3.002 | True |
| 6 | 10928043 | 2.955 | True |
| 8 | 2497408 | 2.930 | True |
| 10 | 12872786 | 2.912 | True |
| 3 | 3046649 | 2.904 | True |
| 0 | 10928010 | 2.824 | True |
| 15 | 8174660 | 2.805 | False |
| 9 | 3046644 | 2.682 | False |
| 1 | 3046645 | 2.678 | False |
| 17 | 10928040 | 2.664 | False |
| 16 | 3046647 | 2.537 | False |
| 12 | 9263899 | 2.459 | False |
| 13 | 3046643 | 2.420 | False |
| 7 | 9184846 | 2.406 | False |
| 19 | 13421636 | 2.369 | False |

Compressed text preview:

```text
Document [1](Title: History of Manipur) was made a territory in956 and a full state972.Maiream Koireng Singh became the first Chief Minister in972 of the State ofur. This has been dated to recorded history from 1500BC. Mythologicalins begin with the reign of the "Konchin Tukthapa Ipu Athoupa Pakhangpa" (Phangpa was the name given to him meaning "The one who knows his father"). He gave birth to the
```

Answer before recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **Ningthou Kangba** (also spelled Ningouangba). According to Document [8], "Ningouangba (15th century BC) is regarded the first and most king of Manipur." Document [11] further states that Kangla "was the royal palace since the [time] of [Ningthou] Kangba who [ascended] throne in 3 AD."`

Answer after recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **Ningthou Kangba** (also spelled Ningouangba). According to Document [8], "Ningouangba (15th century BC) is regarded the first and most king of Manipur." Document [11] further states that Kangla "was the royal palace since the [time] of [Ningthou] Kangba who [ascended] throne in 3 AD."`

Scores: before=0.0, after=0.0

## ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:20:llmlingua_2x

- origin tokens: 3289; target: 1644; compressed: 1573; actual ratio 2.09x; budget met: True
- retained documents: 11/20; attempts: 2
- restrict switch: False; dynamic ratios: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
- recovery: changed=False, spans=None, answer tokens=84

| doc | doc_id | condition score | retained |
| ---: | --- | ---: | --- |
| 19 | d6247f4706224f80b49dca232e4f8f7cbdc5ef32e9f3da822870783a17a6402a | 3.273 | True |
| 11 | 10928048 | 3.260 | True |
| 17 | 10928045 | 3.105 | True |
| 4 | 10928020 | 3.061 | True |
| 5 | 10928038 | 3.014 | True |
| 2 | 18294723 | 3.002 | True |
| 6 | 10928043 | 2.955 | True |
| 8 | 2497408 | 2.930 | True |
| 10 | 12872786 | 2.912 | True |
| 3 | 3046649 | 2.904 | True |
| 0 | 10928010 | 2.824 | True |
| 14 | 8174660 | 2.791 | False |
| 9 | 3046644 | 2.682 | False |
| 1 | 3046645 | 2.678 | False |
| 16 | 10928040 | 2.656 | False |
| 15 | 3046647 | 2.541 | False |
| 12 | 9263899 | 2.459 | False |
| 13 | 3046643 | 2.420 | False |
| 7 | 9184846 | 2.406 | False |
| 18 | 13421636 | 2.369 | False |

Compressed text preview:

```text
Document [1](Title: History of Manipur) was made a territory in956 and a full state972.Maiream Koireng Singh became the first Chief Minister in972 of the State ofur. This has been dated to recorded history from 1500BC. Mythologicalins begin with the reign of the "Konchin Tukthapa Ipu Athoupa Pakhangpa" (Phangpa was the name given to him meaning "The one who knows his father"). He gave birth to the
```

Answer before recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **Nongda Lairen Pakhangba**. According to Document [2], Kangla was the palace "since the [time] of [Nongda Lairen] Pakhangba who ascended the throne in 33 AD, according to 'Cheitharol Kummaba', the royal Chronicle of Manipur."`

Answer after recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **Nongda Lairen Pakhangba**. According to Document [2], Kangla was the palace "since the [time] of [Nongda Lairen] Pakhangba who ascended the throne in 33 AD, according to 'Cheitharol Kummaba', the royal Chronicle of Manipur."`

Scores: before=1.0, after=1.0

## ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:1:llmlingua_4x

- origin tokens: 3289; target: 822; compressed: 802; actual ratio 4.10x; budget met: True
- retained documents: 7/20; attempts: 1
- restrict switch: False; dynamic ratios: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
- recovery: changed=False, spans=None, answer tokens=101

| doc | doc_id | condition score | retained |
| ---: | --- | ---: | --- |
| 0 | d6247f4706224f80b49dca232e4f8f7cbdc5ef32e9f3da822870783a17a6402a | 3.314 | True |
| 12 | 10928048 | 3.260 | True |
| 18 | 10928045 | 3.107 | True |
| 5 | 10928020 | 3.068 | True |
| 3 | 18294723 | 3.010 | True |
| 6 | 10928038 | 3.010 | True |
| 7 | 10928043 | 2.959 | True |
| 9 | 2497408 | 2.912 | False |
| 11 | 12872786 | 2.904 | False |
| 4 | 3046649 | 2.902 | False |
| 1 | 10928010 | 2.832 | False |
| 15 | 8174660 | 2.805 | False |
| 10 | 3046644 | 2.691 | False |
| 2 | 3046645 | 2.666 | False |
| 17 | 10928040 | 2.664 | False |
| 16 | 3046647 | 2.537 | False |
| 13 | 9263899 | 2.453 | False |
| 14 | 3046643 | 2.414 | False |
| 8 | 9184846 | 2.408 | False |
| 19 | 13421636 | 2.369 | False |

Compressed text preview:

```text
Document [1](Title: Kangla Palace) In ancient, 'la' was the royal palace since the of Pakba whoended the throne in 33 AD, to "Cheith Kummaba", the royalicle ofur.

 [:ur (ely state)) a ofples that had traditional religious significance.la means "dry land" in the old Mei language. The Kingdom of Kangleak was established by King Loiyba in 1110 who ruled1741121. Heated the kingdom byating most theiti
```

Answer before recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **King Loiyumba** (also spelled Loiyba), who established the Kingdom of Kangleipak and ruled from 1110 to 1121. According to Document [1], "The Kingdom of Kangleak was established by King Loiyba in 1110 who ruled 1741121" (the text is garbled, but indicates 1110–1121).`

Answer after recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **King Loiyumba** (also spelled Loiyba), who established the Kingdom of Kangleipak and ruled from 1110 to 1121. According to Document [1], "The Kingdom of Kangleak was established by King Loiyba in 1110 who ruled 1741121" (the text is garbled, but indicates 1110–1121).`

Scores: before=0.0, after=0.0

## ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:5:llmlingua_4x

- origin tokens: 3289; target: 822; compressed: 803; actual ratio 4.10x; budget met: True
- retained documents: 7/20; attempts: 1
- restrict switch: False; dynamic ratios: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
- recovery: changed=False, spans=None, answer tokens=51

| doc | doc_id | condition score | retained |
| ---: | --- | ---: | --- |
| 4 | d6247f4706224f80b49dca232e4f8f7cbdc5ef32e9f3da822870783a17a6402a | 3.311 | True |
| 12 | 10928048 | 3.260 | True |
| 18 | 10928045 | 3.107 | True |
| 5 | 10928020 | 3.068 | True |
| 6 | 10928038 | 3.010 | True |
| 2 | 18294723 | 3.002 | True |
| 7 | 10928043 | 2.959 | True |
| 9 | 2497408 | 2.912 | False |
| 3 | 3046649 | 2.904 | False |
| 11 | 12872786 | 2.904 | False |
| 0 | 10928010 | 2.824 | False |
| 15 | 8174660 | 2.805 | False |
| 10 | 3046644 | 2.691 | False |
| 1 | 3046645 | 2.678 | False |
| 17 | 10928040 | 2.664 | False |
| 16 | 3046647 | 2.537 | False |
| 13 | 9263899 | 2.453 | False |
| 14 | 3046643 | 2.414 | False |
| 8 | 9184846 | 2.408 | False |
| 19 | 13421636 | 2.369 | False |

Compressed text preview:

```text
Document [3](Title: Manipur (pr state)) a ofples that had traditional religious significance. Kangla means "dry land" in the old Me language. The of Kangleak was established by King Loiyumba in 1110 who ruled10741121. Heated the kingdom byating theities in the surrounding hills and isited with having ened a of written constitution for his state. After subugating all the villages within their valle
```

Answer before recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **King Loiyumba**, who established Kangleak (Kangla) in 1110 and ruled from 1074 to 1121.`

Answer after recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **King Loiyumba**, who established Kangleak (Kangla) in 1110 and ruled from 1074 to 1121.`

Scores: before=0.0, after=0.0

## ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:10:llmlingua_4x

- origin tokens: 3289; target: 822; compressed: 802; actual ratio 4.10x; budget met: True
- retained documents: 7/20; attempts: 1
- restrict switch: False; dynamic ratios: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
- recovery: changed=False, spans=None, answer tokens=61

| doc | doc_id | condition score | retained |
| ---: | --- | ---: | --- |
| 12 | 10928048 | 3.260 | True |
| 9 | d6247f4706224f80b49dca232e4f8f7cbdc5ef32e9f3da822870783a17a6402a | 3.258 | True |
| 18 | 10928045 | 3.107 | True |
| 4 | 10928020 | 3.061 | True |
| 5 | 10928038 | 3.014 | True |
| 2 | 18294723 | 3.002 | True |
| 6 | 10928043 | 2.955 | True |
| 8 | 2497408 | 2.930 | False |
| 3 | 3046649 | 2.904 | False |
| 11 | 12872786 | 2.904 | False |
| 0 | 10928010 | 2.824 | False |
| 15 | 8174660 | 2.805 | False |
| 10 | 3046644 | 2.691 | False |
| 1 | 3046645 | 2.678 | False |
| 17 | 10928040 | 2.664 | False |
| 16 | 3046647 | 2.537 | False |
| 13 | 9263899 | 2.453 | False |
| 14 | 3046643 | 2.414 | False |
| 7 | 9184846 | 2.406 | False |
| 19 | 13421636 | 2.369 | False |

Compressed text preview:

```text
Document [3](Title: Manipur (prely state)) a ofples that had traditional religious significance. Kangla means "dry land" in the old Me language. The Kingdom of Kangleak was established by King Loiyumba in 1110 who ruled between10741121. Heated the kingdom byating theities in the surrounding hills and isited with having ened a of written constitution for his state. After subugating all the villages
```

Answer before recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **King Loiyumba**. According to Document [3], "The Kingdom of Kangleak was established by King Loiyumba in 1110 who ruled between 1074-1121."`

Answer after recovery: `Based on the provided search results, the first coronated king of Manipur at Kangla was **King Loiyumba**. According to Document [3], "The Kingdom of Kangleak was established by King Loiyumba in 1110 who ruled between 1074-1121."`

Scores: before=0.0, after=0.0
