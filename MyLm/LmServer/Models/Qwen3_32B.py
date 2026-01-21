
class Qwen3_32B:
    def __init__(self, model_dir):
        model_id = model_dir if model_dir.endswith("Qwen3-32B") else os.path.join(model_dir, "Qwen3-32B")

        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, dtype="auto", device_map="auto")

    def __call__(self, input_data):
        # raise NotImplementedError("Qwen3_32B.__call__ is not ok yet.")
        kwargs = input_data
        user_prompt = " ".join([a["user"] for a in input_data["content"] if "user" in a])
        system_prompt = " ".join([a["system"] for a in input_data["content"] if "system" in a])
        messages = [
            {"role": "user", "content": user_prompt}
        ] if system_prompt == "" else [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        # conduct text completion
        generated_ids = self.model.generate( **model_inputs, max_new_tokens=32768 )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

        # parsing thinking content
        try:# rindex finding 151668 (</think>)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0

        thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
        return content