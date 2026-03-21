def single_scoring(res_json_name, ENCODER):
    import os, json, tqdm, numpy as np
    from MyLm import call
    res = json.load(open(os.path.join("./res", res_json_name), "r"))[0]
    qa_json_path = "/mnt/data/raw_data/egoschema/merged.json"
    qa_data = json.load(open(qa_json_path, "r"))
    for key, v in  tqdm.tqdm(res["records"].items()):
        result_strong = v["result_strong"]
        score = {}

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

        score["correct"] = v["result"][0].strip().upper() == chr(65 + int(qa["answer"]))
            
        # print(f"Query: {question}, Options: {options}, answer_string: {qa['answer']}.{answer_string}, Result_strong: {result_strong}")

        encodes = ENCODER.encode(options)
        answer_encode = ENCODER.encode([answer_string])[0]
        result_strong_encode = ENCODER.encode([result_strong])[0]
        closest_idx = (ENCODER.similarity(result_strong_encode, encodes)).flatten(start_dim=0).argmax().item()
        score["closest"] = (closest_idx == int(qa["answer"]))
        score["similarity"] = float(ENCODER.similarity(answer_encode, result_strong_encode))

        llm_choose_force = call("Qwen3-Ours",
            content={"content":[
                {"user":f"Given the options: {(', '.join([chr(65+i) + '. ' + str(option) for i, option in enumerate(options)]))}, and the response: {result_strong}, which option is most similar to the answer? Respond with the option letter only. Choose one even if you think none match well. Only respond with the letter."}
            ]})
        score["llm_choose_force"] = (llm_choose_force.strip()[0].upper() == chr(65 + int(qa["answer"])))

        llm_choose = call("Qwen3-Ours",
            content={"content":[
                {"user":f"Given the options: {(', '.join([chr(65+i) + '. ' + str(option) for i, option in enumerate(options)]))}, and the response: {result_strong}, which option is most similar to the answer? Respond with the option letter only. If you think none match well, respond with 'N', otherwise choose one. Only respond with the letter."}
            ]})
        score["llm_choose"] = (llm_choose.strip()[0].upper() == chr(65 + int(qa["answer"])))

        llm_judge = call("Qwen3-Ours",
            content={"content":[
                {"user":f"Given the answer: {answer_string}, and the response: {result_strong}, does the response correctly answer the question based on the answer? Respond with 'Yes' or 'No' only."}
            ]})
        score["llm_judge"] = (llm_judge.strip().lower() == "yes")

        res["records"][key]["score"] = score
    
    json.dump([res], open(os.path.join("./res", res_json_name.replace(".json", "_scored.json")), "w"), indent=4)

def scoring_main():
    from sentence_transformers import SentenceTransformer
    import os, json, tqdm
    ENCODER = SentenceTransformer('/mnt/data/models/Qwen3-Embedding-0.6B')
    for res_json_name in (["20260217_133357.json"]):
        single_scoring(res_json_name, ENCODER)
        # break

if __name__ == "__main__":
    scoring_main()
    