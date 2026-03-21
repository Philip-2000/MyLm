def single_scoring(res_json_name, ENCODER):
    import os, json, tqdm, numpy as np
    from MyLm import call
    res = json.load(open(os.path.join("./res", res_json_name), "r"))[0]
    qa_json_path = "/mnt/data/raw_data/EgoLife/EgoLifeQA/EgoLifeQA.json" if res["benchmark"] == "EgoLifeQA" else "/mnt/data/raw_data/Ego-R1-bench/merge.json"
    qa_data = json.load(open(qa_json_path, "r"))
    print(res_json_name, res["benchmark"], res["method"])
    for key, v in (res["records"].items()):
        result_strong = v["result_strong"]
        score = {}

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

        print(f"Query: {question}, Options: {options}, answer_string: {qa['answer']}.{answer_string}, Result_strong: {result_strong}")

        encodes = ENCODER.encode(options)
        answer_encode = ENCODER.encode([answer_string])[0]
        result_strong_encode = ENCODER.encode([result_strong])[0]
        closest_idx = (ENCODER.similarity(result_strong_encode, encodes)).flatten(start_dim=0).argmax().item()
        score["closest"] = (closest_idx == (ord(qa["answer"].strip().upper()) - 65))
        score["similarity"] = float(ENCODER.similarity(answer_encode, result_strong_encode))

        llm_choose_force = call("Qwen3-Ours",
            content={"content":[
                {"user":f"Given the options: {(', '.join([chr(65+i) + '. ' + str(option) for i, option in enumerate(options)]))}, and the response: {result_strong}, which option is most similar to the answer? Respond with the option letter only. Choose one even if you think none match well. Only respond with the letter."}
            ]})
        print(f"LLM choose prompt: Given the options: {(', '.join([chr(65+i) + '. ' + str(option) for i, option in enumerate(options)]))}, and the response: {result_strong}, which option is most similar to the answer? Respond with the option letter only. Choose one even if you think none match well. Only respond with the letter.")
        print(f"LLM choose force: {llm_choose_force.strip()}")
        score["llm_choose_force"] = (llm_choose_force.strip()[0].upper() == qa["answer"].strip()[0].upper())
        print(f"LLM choose force score: {score['llm_choose_force']}")

        llm_choose = call("Qwen3-Ours",
            content={"content":[
                {"user":f"Given the options: {(', '.join([chr(65+i) + '. ' + str(option) for i, option in enumerate(options)]))}, and the response: {result_strong}, which option is most similar to the answer? Respond with the option letter only. If you think none match well, respond with 'N', otherwise choose one. Only respond with the letter."}
            ]})

        print(f"LLM choose prompt: Given the options: {(', '.join([chr(65+i) + '. ' + str(option) for i, option in enumerate(options)]))}, and the response: {result_strong}, which option is most similar to the answer? Respond with the option letter only. If you think none match well, respond with 'N', otherwise choose one. Only respond with the letter.")
        print(f"LLM choose: {llm_choose.strip()}")
        score["llm_choose"] = (llm_choose.strip()[0].upper() == qa["answer"].strip()[0].upper())
        print(f"LLM choose score: {score['llm_choose']}")

        llm_judge = call("Qwen3-Ours",
            content={"content":[
                {"user":f"Given the answer: {answer_string}, and the response: {result_strong}, does the response correctly answer the question based on the answer? Respond with 'Yes' or 'No' only."}
            ]})

        print(f"LLM judge prompt: Given the answer: {answer_string}, and the response: {result_strong}, does the response correctly answer the question based on the answer? Respond with 'Yes' or 'No' only.")
        print(f"LLM judge: {llm_judge.strip()}")
        score["llm_judge"] = (llm_judge.strip().lower() == "yes")
        print(f"LLM judge score: {score['llm_judge']}")

        res["records"][key]["score"] = score
    
        break
    # json.dump([res], open(os.path.join("./res", res_json_name.replace(".json", "_scored.json")), "w"), indent=4)

def scoring_main():
    from sentence_transformers import SentenceTransformer
    import os, json, tqdm
    ENCODER = SentenceTransformer('/mnt/data/models/Qwen3-Embedding-0.6B')
    for res_json_name in tqdm.tqdm([f for f in os.listdir("./res") if f.startswith("20260207") or f.startswith("20260208") and f.endswith(".json")]):
        single_scoring(res_json_name, ENCODER)
        break

mapping = {}
def build_map():
    StaticsFiles=[

        # "20260131_175914.json",
        "20260210_034008.json",
        "20260210_041723.json",
        # "20260210_050403.json",
        # "20260210_051938.json",
        # "20260210_054512.json",
        # "20260210_061116.json",
        "20260210_065012.json",
        "20260210_070330.json",
        "20260210_071746.json",
        "20260210_073206.json",
        # "20260131_180136.json",
        # "20260131_182944.json",
        # "20260131_183044.json",
        # "20260131_195151.json",
        # "20260131_195256.json",

        "20260201_060652.json",
        "20260201_073840.json",
        "20260201_090135.json",
        "20260201_133951.json",
        "20260201_140157.json",
        "20260201_143043.json",
        "20260201_152011.json",
        "20260201_171711.json",
        "20260201_211754.json",
        "20260202_024511.json"
    ]
    import os, json
    for f in StaticsFiles:
        res = json.load(open(os.path.join("./res", f), "r"))[0]
        benchmark = res["benchmark"]
        method = res["method"]
        mapping[(benchmark, method)] = f

def matching(res_json_name):
    import os, json
    res = json.load(open(os.path.join("./res", res_json_name), "r"))[0]
    benchmark = res["benchmark"]
    method = res["method"]
    global mapping
    if not mapping:        build_map()
    if (benchmark, method) in mapping:
        return mapping[(benchmark, method)]
    else:
        raise AssertionError(f"No matching found for benchmark {benchmark} and method {method} in mapping.")


def single_mergin(res_json_name):
    import os, json
    f = matching(res_json_name)
    res_f = json.load(open(os.path.join("./res", f), "r"))[0]
    res = json.load(open(os.path.join("./res", res_json_name), "r"))[0]
    print(res_json_name, f, res["benchmark"], res["method"], res_f["benchmark"], res_f["method"])

    qa_json_path = "/mnt/data/raw_data/EgoLife/EgoLifeQA/EgoLifeQA.json" if res["benchmark"] == "EgoLifeQA" else "/mnt/data/raw_data/Ego-R1-bench/merge.json"
    qa_data = json.load(open(qa_json_path, "r"))

    for key, v in (res["records"].items()):
        res["records"][key]["result"] = res_f["records"][key]["result"]
        res["records"][key]["delay_s"] = res_f["records"][key]["delay_s"]
        res["records"][key]["delay_rate"] = res_f["records"][key]["delay_rate"]

        qa = [ item for item in qa_data if item["ID"] == key][0]
        answer = qa["answer"]
        res["records"][key]["score"]["correct"] = bool(res["records"][key]["result"][0].strip().lower() == answer[0].strip().lower())
    
    json.dump([res], open(os.path.join("./res", res_json_name.replace("_scored.json", "_merged.json")), "w"), indent=4)


def merging_main():
    import os, json, tqdm
    for res_json_name in tqdm.tqdm([f for f in os.listdir("./res") if (f.startswith("20260207") or f.startswith("20260208")) and f.endswith("_scored.json")]):
        if res_json_name.replace("_scored.json", "_merged.json") in os.listdir("./res"): continue
        single_mergin(res_json_name)
        # try:
        #     single_mergin(res_json_name)
        # except Exception as e:
        #     print(f"Error processing {res_json_name}: {e}")
        # break

if __name__ == "__main__":
    scoring_main()
    # merging_main()