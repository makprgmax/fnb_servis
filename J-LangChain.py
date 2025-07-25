from transformers import GPTJForCausalLM, AutoTokenizer
from langchain.llms import HuggingFacePipeline
from transformers import pipeline


model = GPTJForCausalLM.from_pretrained("EleutherAI/gpt-j-6B")
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")

