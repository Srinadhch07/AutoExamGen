from langchain_community.llms import LlamaCpp

llm = LlamaCpp(
    model_path="D:/vasuki/models/qwen2.5-3b-instruct-q4_k_m.gguf",
    temperature=0.2,        
    max_tokens=2048,
    top_p=0.9,
    repeat_penalty=1.1,
    n_ctx=2048,
    verbose=False,
)