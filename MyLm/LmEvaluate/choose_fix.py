def single_fixing(res_json_name, bar):
    import os, json, tqdm, numpy as np
    from MyLm import call
    res = json.load(open(os.path.join("./res", res_json_name), "r"))[0]
    qa_json_path = ("/mnt/data/raw_data/EgoLife/EgoLifeQA/EgoLifeQA.json" if res["benchmark"] == "EgoLifeQA" else "/mnt/data/raw_data/Ego-R1-bench/merge.json") if res["benchmark"] in ["EgoLifeQA", "EgoR1Bench"] else "/mnt/data/raw_data/egoschema/merged.json"
    qa_data = json.load(open(qa_json_path, "r"))
    # print(res_json_name, res["benchmark"], res["method"])
    for key, v in (res["records"].items()):
        result_strong = v["result_strong"]
        if res["benchmark"] == "EgoSchema":
            qa = [ item for item in qa_data if item["q_uid"] == key][0]

            """
            "q_uid": "0074f737-11cb-497d-8d07-77c3a8127391",
            "google_drive_id": "1ZdZ8aUcBNzndj135bqFrxb9L816EMGp1",
            "question": "Taking into account all the actions performed by c, what can you deduce about the primary objective and focus within the video content?",
            "option 0": "C is cooking.",
            "option 1": "C is doing laundry.",
            "option 2": "C is cleaning the kitchen.",
            "option 3": "C is cleaning dishes.",
            "option 4": "C is cleaning the bathroom.",
            "answer": 3
                """
            question = qa["question"]
            options = [qa[f"option {i}"] for i in range(5) if f"option {i}" in qa]

            answer_string = options[int(qa["answer"])]
            answer_letter = chr(65 + int(qa["answer"]))
        else:

            qa = [ item for item in qa_data if item["ID"] == key][0]

            """
            "question": "Who used the screwdriver first?",
            "question_chinese": "谁最先使用过螺丝刀？",
            "choice_a": "Tasha",
            "choice_a_chinese": "Tasha",
            "choice_b": "Alice",
            "choice_b_chinese": "Alice",
            "choice_c": "Shure",
            "choice_c_chinese": "Shure",
            "choice_d": "Lucia",
            "choice_d_chinese": "Lucia",
            "answer": "B",
            """
            question = qa["question"]
            options = [qa["choice_a"], qa["choice_b"], qa["choice_c"], qa["choice_d"]]

            answer_string = options[ord(qa["answer"].strip().upper()) - 65] if qa["answer"].strip().upper() in ["A","B","C","D","E","F"] and (ord(qa["answer"].strip().upper()) - 65) < len(options) else qa["answer"].strip()
            answer_letter = qa["answer"].strip().upper()

        score = res["records"][key]["score"]
        # print(f"Query: {question}, Options: {options}, answer_string: {qa['answer']}.{answer_string}, Result_strong: {result_strong}")

        
        llm_choose_force = call("Qwen3-Ours",
            content={"content":[
                {"user":f"Given the question '{question}', options: {(', '.join([chr(65+i) + '. ' + str(option) for i, option in enumerate(options)]))}, and the response: {result_strong}, which option is most similar to the answer? Respond with the option letter only. Choose one even if you think none match well. Only respond with the letter."}
            ]})
        # print(f"LLM choose prompt: Given the question '{question}', options: {(', '.join([chr(65+i) + '. ' + str(option) for i, option in enumerate(options)]))}, and the response: {result_strong}, which option is most similar to the answer? Respond with the option letter only. Choose one even if you think none match well. Only respond with the letter.")
        # print(f"LLM choose force: {llm_choose_force.strip()}")
        score["llm_choose_force"] = (llm_choose_force.strip()[0].upper() == answer_letter)
        # print(f"LLM choose force score: {score['llm_choose_force']}")

        llm_choose = call("Qwen3-Ours",
            content={"content":[
                {"user":f"Given the question '{question}', options: {(', '.join([chr(65+i) + '. ' + str(option) for i, option in enumerate(options)]))}, and the response: {result_strong}, which option is most similar to the answer? Respond with the option letter only. If you think none match well, respond with 'N', otherwise choose one. Only respond with the letter."}
            ]})

        # print(f"LLM choose prompt: Given the question '{question}', options: {(', '.join([chr(65+i) + '. ' + str(option) for i, option in enumerate(options)]))}, and the response: {result_strong}, which option is most similar to the answer? Respond with the option letter only. If you think none match well, respond with 'N', otherwise choose one. Only respond with the letter.")
        # print(f"LLM choose: {llm_choose.strip()}")
        score["llm_choose"] = (llm_choose.strip()[0].upper() == answer_letter)
        # print(f"LLM choose score: {score['llm_choose']}")


        res["records"][key]["score"] = score
    
        # break
        bar.update(1)
    json.dump([res], open(os.path.join("./res", res_json_name.replace(".json", "_fix.json")), "w"), indent=4)

def fixing_main():
    import os, json, tqdm
    
    StaticsFiles=[
        #EgoSchema
        #Qwen3
        "20260214_122625.json", #Qwen3 EgoSchema
        #Qwen2.5
        "20260214_141823_scored.json", #Qwen2.5 EgoSchema
        #InternVL3.5
        "20260214_130303.json", #InternVL3.5 EgoSchema 8B???????????????????????????????????????
        #InternVideo2.5
        "20260214_181514.json", #InternVideo2.5 EgoSchema
        #EgoGPT
        "20260214_165636.json", #EgoGPT EgoSchema
        #LongVA
        "20260214_170259.json", #LongVA EgoSchema
        #LLaVA_Video
        "20260215_003854.json", #LLaVA_Video EgoSchema
        #llava_ov
        "20260215_071919.json", #llava_ov EgoSchema

        #EgoLifeQA
        #Qwen3
        "20260207_083909_merged.json", #Qwen3 EgoLifeQA
        #Qwen2.5
        "20260207_142148_merged.json", #Qwen2.5 EgoLifeQA
        #InternVL3.5
        "20260207_160128_merged.json", #InternVL3.5 EgoLifeQA 8B???????????????????????????????????????
        #InternVideo2.5
        "20260207_130053_merged.json", #InternVideo2.5 EgoLifeQA
        #EgoGPT
        "20260207_125414_merged.json", #EgoGPT EgoLifeQA
        #LongVA
        "20260207_134011_merged.json", #LongVA EgoLifeQA
        #LLaVA_Video
        "20260208_155749_merged.json", #LLaVA_Video EgoLifeQA
        #llava_ov
        "20260208_121000_merged.json", #llava_ov EgoLifeQA

        #EgoR1Bench
        #Qwen3
        "20260207_060339_merged.json", #Qwen3 EgoR1Bench
        #Qwen2.5
        "20260207_075507_merged.json", #Qwen2.5 EgoR1Bench
        #InternVL3.5
        "20260207_093705_merged.json", #InternVL3.5 EgoR1Bench 8B???????????????????????????????????????
        #InternVideo2.5
        "20260207_122304_merged.json", #InternVideo2.5 EgoR1Bench
        #EgoGPT
        "20260207_123817_merged.json", #EgoGPT EgoR1Bench
        #LongVA
        "20260207_131519_merged.json", #LongVA EgoR1Bench
        #LLaVA_Video
        "20260208_114647_merged.json", #llava_ov EgoR1Bench
        #llava_ov
        "20260208_135726_merged.json", #LLaVA_Video EgoR1Bench
    ]
    StaticsFiles = [
        "20260216_214804.json", #InternVL3.5 EgoR1Bench 38B
        "20260217_074933.json", #InternVL3.5 EgoLifeQA 38B
    ]
    bar = tqdm.tqdm(range(800))#(500+500+300)*8))
    for res_json_name in (StaticsFiles):
        single_fixing(res_json_name, bar)
        # break


if __name__ == "__main__":
    fixing_main()
    