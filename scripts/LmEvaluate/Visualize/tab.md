
<!--
| Column 1 | EgoLifeQA | EgoR1Bench |
| --- | --- | --- |
| InternVideo2.5-Chat-8B | 28.12% | ? |
| InternVL3_5-8B | 34.38% | ? |
| Qwen3-VL-8B-Instruct | 36.72% | ? |
| Qwen2.5-VL-7B-Instruct | 28.13% | ? |
| LLaVA-Video-7B-Qwen2 | 34.38% | ? |
| llava-onevision-qwen2-7b-ov | 37.50% | ? |

帮我整理一下这一页中的所有数据，形成一张表格
纵向应当有七个内容行，分别是上面那个表中的六个模型，以及下方有一个表中出现的那个MINE（代表我的方法）

横向应该有以下这些列：
EgoLifeQA | | | A1_JAKE | A2_ALICE | A3_TASHA | A4_LUCIA | A5_KATRINA | A6_SHURE  | | EgoR1Bench | | |A1_JAKE_DAY1 | A2_ALICE_DAY1 | A3_TASHA_DAY1 | A4_LUCIA_DAY1 | A5_KATRINA_DAY1 | A6_SHURE_DAY1 | |EgoR1Bench_DAY1 | |

每个模型对应的行中，应当填写上面表格中的EgoLifeQA的准确率，以及下方表格中的EgoR1Bench的准确率；下方那些表格中的Accuracy列对应于EgoR1Bench列中的各个用户的准确率，而Day1 Accuracy列对应于EgoR1Bench_DAY1列中的各个用户的准确率

注意我的方法中，Longer 的内容不对应于任何东西，请不要填入这张表中；只需要填入 Day1 的准确率即可

然后表中未被填入的元素就用“--”表示

-->


| Model                      | EgoLifeQA |    EgoR1Bench | EgoR1Bench_DAY1 |      -     | A1_JAKE | A2_ALICE | A3_TASHA | A4_LUCIA | A5_KATRINA | A6_SHURE |    -      | A1_JAKE_DAY1 | A2_ALICE_DAY1 | A3_TASHA_DAY1 | A4_LUCIA_DAY1 | A5_KATRINA_DAY1 | A6_SHURE_DAY1 |
|----------------------------|-----------|------------|---------|----------|----------|----------|------------|----------|------------|------------|------------|--------------|----------------|----------------|----------------|------------------|----------------|
| InternVideo2.5-Chat-8B     | 28.12%    |      31.3%       |     35.7%      |       -            |  24.0%  |  30.0%   |  42.0%   |  34.0%   |   28.0%    |  36.0%   |      -        |    10.0%     |     44.4%      |     46.9%      |     38.1%      |      33.3%      |     37.9%      |    |
| InternVL3_5-8B             | 34.38%    |     37.0%       |       41.3%      |      -        |  42.0%  |  36.0%   |  38.0%   |  38.0%   |   32.0%    |  36.0%   |       -        |    50.0%     |     66.7%      |     43.8%      |     47.6%      |      33.3%      |     24.1%           |
| Qwen3-VL-8B-Instruct      | 36.72%    |      34.3%       |      33.3%      |      -         |  26.0%  |  44.0%   |  40.0%   |  34.0%   |   34.0%    |  28.0%   |      -          |    25.0%     |     44.4%      |     37.5%      |     42.9%      |      33.3%      |     24.1%      |
| Qwen2.5-VL-7B-Instruct    | 28.13%    |      31.3%       |      35.7%      |      -     |  22.0%  |  42.0%   |  32.0%   |  38.0%   |   18.0%    |  36.0%   |      -         |    20.0%    |     44.4%      |     31.2%      |     52.4%      |      33.3%      |     37.9%      |
| LLaVA-Video-7B-Qwen2      | 34.38%    |      33.3%       |      33.3%      |      -         |  24.0%  |  34.0%   |  32.0%   |  38.0%   |   34.0%    |  38.0%   |      -        |    15.0%     |     33.3%      |     34.4%      |     23.8%      |      53.3%      |     41.4%      |
| llava-onevision-qwen2-7b-ov | 37.50%  |      35.0%       |     39.7%      |      -     |  30.0%  |  32.0%   |  40.0%   |  34.0%   |   30.0%    |  44.0%   |      -          |    30.0%     |     33.3%      |     43.8%      |     33.3%      |      33.3%      |     51.7%      |
| MINE                      |    46.57%     |      --     |   33.76%    |   -     |   --     |   --     |    48.50%      |   49.98%     |      69.39%     |    63.83%     |      -     |    25.79%    |     21.11%     |    29.05%     |    33.33%     |     42.86%      |    26.67%     |




<!--
These are all EgoR1Bench results:



Method: Qwen2.5-VL-7B-Instruct
Person            Accuracy  Day1 Accuracy
----------------------------------------
A1_JAKE              22.0%          20.0%
A2_ALICE             42.0%          44.4%
A3_TASHA             32.0%          31.2%
A4_LUCIA             38.0%          52.4%
A5_KATRINA           18.0%          33.3%
A6_SHURE             36.0%          37.9%
----------------------------------------
Overall              31.3%          35.7%
Method: InternVideo2.5-Chat-8B
Person            Accuracy  Day1 Accuracy
----------------------------------------
A1_JAKE              24.0%          10.0%
A2_ALICE             30.0%          44.4%
A3_TASHA             42.0%          46.9%
A4_LUCIA             34.0%          38.1%
A5_KATRINA           28.0%          33.3%
A6_SHURE             36.0%          37.9%
----------------------------------------
Overall              32.3%          35.7%
Method: LLaVA-Video-7B-Qwen2
Person            Accuracy  Day1 Accuracy
----------------------------------------
A1_JAKE              24.0%          15.0%
A2_ALICE             34.0%          33.3%
A3_TASHA             32.0%          34.4%
A4_LUCIA             38.0%          23.8%
A5_KATRINA           34.0%          53.3%
A6_SHURE             38.0%          41.4%
----------------------------------------
Overall              33.3%          33.3%
Method: InternVL3_5-8B
Person            Accuracy  Day1 Accuracy
----------------------------------------
A1_JAKE              42.0%          50.0%
A2_ALICE             36.0%          66.7%
A3_TASHA             38.0%          43.8%
A4_LUCIA             38.0%          47.6%
A5_KATRINA           32.0%          33.3%
A6_SHURE             36.0%          24.1%
----------------------------------------
Overall              37.0%          41.3%
Method: llava-onevision-qwen2-7b-ov
Person            Accuracy  Day1 Accuracy
----------------------------------------
A1_JAKE              30.0%          30.0%
A2_ALICE             32.0%          33.3%
A3_TASHA             40.0%          43.8%
A4_LUCIA             34.0%          33.3%
A5_KATRINA           30.0%          33.3%
A6_SHURE             44.0%          51.7%
----------------------------------------
Overall              35.0%          39.7%
Method: Qwen3-VL-8B-Instruct
Person            Accuracy  Day1 Accuracy
----------------------------------------
A1_JAKE              26.0%          25.0%
A2_ALICE             44.0%          44.4%
A3_TASHA             40.0%          37.5%
A4_LUCIA             34.0%          42.9%
A5_KATRINA           34.0%          33.3%
A6_SHURE             28.0%          24.1%
----------------------------------------
Overall              34.3%          33.3%
x



| MINE-EgoR1Bench |  Day1 | Longer | | DAY1 Sec | Longer Sec | Full Sec |
| ---- | --------------- | ---------- | -- | --------- | ------------ | ---- |
| A1_JAKE    | 25.79% | 30.00% | | 24702 | 61953 | 187013 |
| A2_ALICE   | 21.11% | 27.14% | | 23737 | 53517 | 164641 |
| A3_TASHA   | 29.05% | 21.88% | | 23073 | 48362 | 144285 |
| A4_LUCIA   | 33.33% | 47.62% | | 24537 | 24147 | 156966 |
| A5_KATRINA | 42.86% | 50.00% | | 22627 | 15407 | 143221 |
| A6_SHURE   | 26.67% | 25.93% | | 22488 | 53146 | 158366 |
| AVERAGE    | 29.80% | 33.76% | | 23698 | 42488 | 150982 |

| MINE-EgoLifeQA |  Day1 | Longer | | DAY1 Sec | Longer Sec | Full Sec |
| ---- | --------------- | ---------- | -- | --------- | ------------ | ---- |
| A1_JAKE    | -- | 31.63% | | 24702 | 19765 | 187013 |

-->



Next Step:
1. More detailed responding logs:
    - which memory items are retrieved?
    - what happened in the referenced memory in question (ground truth), 
      - video
      - transcript
2. More Parralleled execution solution (each person on one PPU)
3. More detailed time consumption analysis, (currently, it's 6 times of time needed than the program's report) 

Later Steps:

4. Stronger Testing:
    - Not to input options with the question, let LLM output an open-ended answer, then use a LLM or use a matching algorithm to select the best option from the choices.
    - Zero-information baseline: let LLM answer the question without any information retrieval, see how much it can get right.
5. Testing EgoLife Algorithm and EgoR1 algorithms
6. Design more complex structures
