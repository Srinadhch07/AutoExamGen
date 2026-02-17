from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")

def token_count(text_data: list):
    input_tokens = 0
    for text in text_data:
        input_tokens += len(tokenizer.encode(text))
    return input_tokens

