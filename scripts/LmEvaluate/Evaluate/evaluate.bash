#b=EgoSchema
#b=LongTimeScope
#b=LongVideoBench
#b=LVBench
#b=MLVU
#b=Video_MME
b=EgoLifeQA
#b=EgoR1Bench
#b=XLeBench
#b=All


#m=Qwen3-VL-8B-Instruct
m=Qwen2.5-VL-7B-Instruct
#m=LLaVA_Video_7B_Qwen2
#m=LLaVA-NeXT-Video-7B-hf
#m=llava-onevision-qwen2-7b-ov
#m=InternVideo2.5-Chat-8B
#m=InternVL3_5-8B
#m=LongVA-7B-DPO
#m=EgoGPT-7b-EgoIT-EgoLife
#m=All

python $(dirname "${BASH_SOURCE[0]}")/evaluate.py $b $m --max_qa 64 --num_segments 64