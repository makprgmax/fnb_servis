import torch
from peft import PeftModel
import transformers
import textwrap
from transformers import LlamaTokenizer, LlamaForCausalLM, GenerationConfig
from transformers.generation.utils import GreedySearchDecoderOnlyOutput


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = LlamaTokenizer.from_pretrained(base_model)

model = LlamaForCausalLM.from_pretrained(
    base_model,
    load_in_8bit=True,
    device_map="auto",
)

model = PeftModel.from_pretrained(model, "tloen/alpaca-lora-7b", torch_dtype=torch.float16)

model.config.pad_token_id = tokenizer.pad_token_id = 0 
model.config.bos_token_id = 1
model.config.eos_token_id = 2

model = model.eval()
model = torch.compile(model)

PROMPT_TEMPLATE = f"""
Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
[INSTRUCTION]
### Input:
[INPUT]
### Response:
"""


def create_prompt(instruction: str, inp: str) -> str:
    return PROMPT_TEMPLATE.replace("[INSTRUCTION]", instruction).replace("[INPUT]", inp)


def generate_response(prompt: str, model: PeftModel) -> GreedySearchDecoderOnlyOutput:
    encoding = tokenizer(prompt, return_tensors="pt")
    input_ids = encoding["input_ids"].to(DEVICE)

    generation_config = GenerationConfig(
        temperature=0.1,
        top_p=0.75,
        repetition_penalty=1.1,
    )
    with torch.inference_mode():
        return model.generate(
            input_ids=input_ids,
            generation_config=generation_config,
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=128,
        )


def format_response(response: GreedySearchDecoderOnlyOutput) -> str:
    decoded_output = tokenizer.decode(response.sequences[0])
    response = decoded_output.split("### Response:")[1].strip()
    return "\n".join(textwrap.wrap(response))


def ask_alpaca(instruction: str, inp: str, model: PeftModel = model) -> str:
    prompt = create_prompt(instruction, inp)
    response = generate_response(prompt, model)
    print(format_response(response))