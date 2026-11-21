# 阶段一补充案例（既有 DeepSeek 预测）

这些槽来自 `reports/stage1-acceptance/predictions.jsonl`，不是 Cursor 对话。
官方分数仍是首行 `best_subspan_em`。诊断标记不替换该分数。
这里不收录文档正文。

## S1-01

- slot_id：`ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:1:original`
- 问题：who was the first coronated king of manipur at kangla
- 参考答案：Pakhangba；Pamheiba
- 方法 / 位置：original / 1
- 官方 score：1.0
- token：原始 3289，压缩 3289，目标 3289，实测比 1.0
- API usage：输入 3293，输出 98；finish_reason=stop
- 时间：2026-11-06T10:10:59.495705+00:00
- 诊断：无诊断标记

首行：

> Based on the provided search results, the first coronated king of Manipur at Kangla was **Pakhangba**, who ascended the throne in 33 AD according to the royal chronicle "Cheitharol Kummaba" [Document 1]. The search results also mention that "Kanglei which is now called 'Kangla' was the first capital" and that Pakhangpa gave birth to the seven clans of Meitei society [Document 2].

## S1-02

- slot_id：`ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:1:bm25_2x`
- 问题：who was the first coronated king of manipur at kangla
- 参考答案：Pakhangba；Pamheiba
- 方法 / 位置：bm25_2x / 1
- 官方 score：1.0
- token：原始 3289，压缩 1644，目标 1644，实测比 2.0006082725060828
- API usage：输入 1648，输出 119；finish_reason=stop
- 时间：2026-11-06T10:11:00.998094+00:00
- 诊断：无诊断标记

首行：

> Based on the provided search results, the first coronated king of Manipur at Kangla was **Pakhangba**. According to Document [1], "'Kangla' was the royal palace since the reign of Pakhangba who ascended the throne in 33 AD, according to 'Cheitharol Kummaba', the royal Chronicle of Manipur." Document [2] also states that "Kanglei which is now called 'Kangla' was the first capital" and references the reign of "Konchin Tukthapa Ipu Athoupa Pakhangpa."

## S1-03

- slot_id：`ef848352f36bc278ab99b295486d00f8fa68d2a26552caa8c12a67932b85b9fc:1:bm25_4x`
- 问题：who was the first coronated king of manipur at kangla
- 参考答案：Pakhangba；Pamheiba
- 方法 / 位置：bm25_4x / 1
- 官方 score：0.0
- token：原始 3289，压缩 822，目标 822，实测比 4.0012165450121655
- API usage：输入 826，输出 90；finish_reason=stop
- 时间：2026-11-06T10:11:02.468859+00:00
- 诊断：无诊断标记

首行：

> Based on the provided search results, the specific name of the first coronated king of Manipur at Kangla is not explicitly stated. However, Document [1] mentions that "Kanglei which is now called 'Kangla' was the first capital" and that mythological origins begin with the reign of "Konchin Tukthapa Ipu Athoupa Pakhangpa," who gave birth to the seven clans of Meitei society.

## S1-04

- slot_id：`0b6dde118f5c85bc3f4d120a9bd287bf2fbdda405bda05bf3d8587c10efc9be7:1:original`
- 问题：character in macbeth who is murdered and appears as a ghost
- 参考答案：Lord Banquo；Banquo
- 方法 / 位置：original / 1
- 官方 score：1.0
- token：原始 2898，压缩 2898，目标 2898，实测比 1.0
- API usage：输入 2902，输出 106；finish_reason=stop
- 时间：2026-11-06T10:11:37.731101+00:00
- 诊断：无诊断标记

首行：

> The character in Macbeth who is murdered and appears as a ghost is Banquo. According to the search results, Banquo is at first an ally to Macbeth, and the witches prophesy that Banquo will not be king himself but that his descendants will be. Later, Macbeth sees Banquo as a threat and has him murdered by two hired assassins, though Banquo's son Fleance escapes. Banquo's ghost returns in a later scene (the Banquet Scene), causing Macbeth to react with alarm during a public feast.

## S1-05

- slot_id：`0b6dde118f5c85bc3f4d120a9bd287bf2fbdda405bda05bf3d8587c10efc9be7:1:bm25_2x`
- 问题：character in macbeth who is murdered and appears as a ghost
- 参考答案：Lord Banquo；Banquo
- 方法 / 位置：bm25_2x / 1
- 官方 score：1.0
- token：原始 2898，压缩 1449，目标 1449，实测比 2.0
- API usage：输入 1453，输出 98；finish_reason=stop
- 时间：2026-11-06T10:11:39.249113+00:00
- 诊断：无诊断标记

首行：

> Based on the search results, the character in Macbeth who is murdered and appears as a ghost is **Banquo**. Document [1] states that Macbeth "has him murdered by two hired assassins" and that "Banquo's ghost returns in a later scene [Banquet Scene], causing Macbeth to react with alarm during a public feast." Document [4] also describes the ghost of Banco (Banquo) sitting in Macbeth's place at the table and Macbeth raving at the ghost.

## S1-06

- slot_id：`0b6dde118f5c85bc3f4d120a9bd287bf2fbdda405bda05bf3d8587c10efc9be7:1:bm25_4x`
- 问题：character in macbeth who is murdered and appears as a ghost
- 参考答案：Lord Banquo；Banquo
- 方法 / 位置：bm25_4x / 1
- 官方 score：1.0
- token：原始 2898，压缩 724，目标 724，实测比 4.002762430939226
- API usage：输入 728，输出 74；finish_reason=stop
- 时间：2026-11-06T10:11:40.551604+00:00
- 诊断：无诊断标记

首行：

> Based on the search results, the character in Macbeth who is murdered and later appears as a ghost is **Banquo**. According to Document [1], Macbeth sees Banquo as a threat and has him murdered by two hired assassins, and "Banquo's ghost returns in a later scene [Banquet Scene], causing Macbeth to react with alarm during a public feast."

## S1-07

- slot_id：`64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:10:original`
- 问题：who sang the song how far is heaven
- 参考答案：Los Lonely Boys
- 方法 / 位置：original / 10
- 官方 score：0.0
- token：原始 2928，压缩 2928，目标 2928，实测比 1.0
- API usage：输入 2932，输出 200；finish_reason=stop
- 时间：2026-11-06T10:13:56.871121+00:00
- 诊断：无诊断标记

首行：

> Based on the provided search results, I cannot definitively answer who sang a song titled "How Far Is Heaven." None of the documents mention a song with that exact title.

## S1-08

- slot_id：`64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:10:bm25_2x`
- 问题：who sang the song how far is heaven
- 参考答案：Los Lonely Boys
- 方法 / 位置：bm25_2x / 10
- 官方 score：1.0
- token：原始 2928，压缩 1463，目标 1464，实测比 2.001367053998633
- API usage：输入 1467，输出 116；finish_reason=stop
- 时间：2026-11-06T10:13:58.357211+00:00
- 诊断：首行有明确否认，但官方分数为 1

首行：

> Based on the provided search results, none of the documents contain information about a song titled "How Far Is Heaven." The results discuss songs such as "If Heaven Wasn't So Far Away" (recorded by Rhett Akins and later Justin Moore), "Heaven" (by Los Lonely Boys and by Warrant), "The Nearest Thing to Heaven" (by Bunny Walters), "Far from Heaven" (a film), and "Little Bit of Heaven" (by Lisa Stansfield), but none mention "How Far Is Heaven" or identify who sang it.

## S1-09

- slot_id：`64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:10:bm25_4x`
- 问题：who sang the song how far is heaven
- 参考答案：Los Lonely Boys
- 方法 / 位置：bm25_4x / 10
- 官方 score：1.0
- token：原始 2928，压缩 732，目标 732，实测比 4.0
- API usage：输入 736，输出 87；finish_reason=stop
- 时间：2026-11-06T10:13:59.910357+00:00
- 诊断：首行有明确否认，但官方分数为 1

首行：

> Based on the provided search results, none of the documents contain information about a song titled "How Far Is Heaven." The results mention songs such as "If Heaven Wasn't So Far Away," "Heaven" by Los Lonely Boys, "The Nearest Thing to Heaven," and "Over the Hills and Far Away," but none of these match the song in your question. Therefore, the search results do not provide an answer.

## S1-10

- slot_id：`64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:5:original`
- 问题：who sang the song how far is heaven
- 参考答案：Los Lonely Boys
- 方法 / 位置：original / 5
- 官方 score：0.0
- token：原始 2928，压缩 2928，目标 2928，实测比 1.0
- API usage：输入 2932，输出 164；finish_reason=stop
- 时间：2026-11-06T10:13:03.556744+00:00
- 诊断：参考答案不在首行、拼成一行后才会被同一评分函数记为 1

首行：

> Based on the provided search results, there is no song titled "How Far Is Heaven." However, the search results do contain information about several songs with "Heaven" in the title, including:

## S1-11

- slot_id：`64a3debb5e078f5b6b41d180d4beb9288e39cb6ef737a178b56d56d3fbd644c5:20:original`
- 问题：who sang the song how far is heaven
- 参考答案：Los Lonely Boys
- 方法 / 位置：original / 20
- 官方 score：0.0
- token：原始 2928，压缩 2928，目标 2928，实测比 1.0
- API usage：输入 2932，输出 224；finish_reason=stop
- 时间：2026-11-06T10:15:51.439908+00:00
- 诊断：参考答案不在首行、拼成一行后才会被同一评分函数记为 1

首行：

> Based on the search results, I cannot definitively answer who sang a song titled "How Far Is Heaven." The provided documents discuss several songs with "Heaven" in the title, but none is exactly "How Far Is Heaven."

## S1-12

- slot_id：`eea8ae864c0ece22a4ce2d354c1df5d58e295152b12ccfb69ced409696fd971d:1:original`
- 问题：when did the astros change from the national league to the american league
- 参考答案：2013；March 31, 2013
- 方法 / 位置：original / 1
- 官方 score：1.0
- token：原始 2841，压缩 2841，目标 2841，实测比 1.0
- API usage：输入 2845，输出 62；finish_reason=stop
- 时间：2026-11-06T10:12:37.688222+00:00
- 诊断：无诊断标记

首行：

> The Astros moved to the American League West division in 2013, after spending their first 51 seasons in the National League. It was announced that 2012 would be the last season for the Astros in the NL, and the move was a condition for the sale to the new ownership group.

## S1-13

- slot_id：`eea8ae864c0ece22a4ce2d354c1df5d58e295152b12ccfb69ced409696fd971d:1:bm25_4x`
- 问题：when did the astros change from the national league to the american league
- 参考答案：2013；March 31, 2013
- 方法 / 位置：bm25_4x / 1
- 官方 score：0.0
- token：原始 2841，压缩 708，目标 710，实测比 4.012711864406779
- API usage：输入 712，输出 61；finish_reason=stop
- 时间：2026-11-06T10:12:40.288409+00:00
- 诊断：无诊断标记

首行：

> The Astros moved to the American League after the 2017 American League Championship Series, where they defeated the Boston Red Sox 3–1 in the ALDS; this was the Astros' fifth appearance in a League Championship Series and their first since transferring from the National League to the American League.
