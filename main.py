from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from ray import serve
import torch

app = FastAPI()

def gpu_intensive_task():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    for i in torch.arange(1000000, device=device):
        yield f"{device} --> {(i ** 2).item()}\n"

@serve.deployment
@serve.ingress(app)
class FastAPIDeployment:
    @app.get("/hello")
    def say_hello(self, name: str):
        return StreamingResponse(gpu_intensive_task(), media_type="text/plain")

prova = FastAPIDeployment.bind()
