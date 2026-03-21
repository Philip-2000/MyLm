def fix(json_file):
    import os, json, tqdm
    
    res_json_name=os.path.basename(json_file)
    res=json.load(open(json_file))[0]
    
    for k,v in res["records"].items():
        if "llm_choose" not in v["score"]:
            print(f"LLM choose score missing for {k}")
        
if __name__ == "__main__":
    fix("./res/20260217_110547.json")