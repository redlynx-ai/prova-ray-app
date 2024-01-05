from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TextIteratorStreamer
from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from threading import Thread
from ray import serve
import torch


app = FastAPI()

# Ray Serve deployment
@serve.deployment
@serve.ingress(app)
class FastAPIDeployment:
    def __init__(self):
        # load model in 4-bit
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16
        )

        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2",
                                                     torch_dtype=torch.bfloat16,
                                                     quantization_config=quantization_config,
                                                     device_map="auto",
                                                     # attn_implementation="flash_attention_2"
                                                    )
    
    def generate(self, log):
        system = "You are a helpful cybersecurity assistant that reads events occured on a network and provide a long description of what they means and what security risk can be potentially related to."
        input_text = f"<s>[INST] {system} Event: {log} [/INST]"
        inputs = self.tokenizer(input_text, return_tensors="pt", padding='longest', truncation=True, max_length=1000)
        inputs = inputs.to("cuda")

        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True)

        # enable FlashAttention
        # with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=False): 
        generation_kwargs = dict(inputs, streamer=streamer, max_new_tokens=1000, do_sample=False, pad_token_id=self.tokenizer.pad_token_id)
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        for new_text in streamer:
            yield new_text

    @app.get("/")
    def main(self, log: str = ""):
        return StreamingResponse(self.generate(log))

prova = FastAPIDeployment.bind()
