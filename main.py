from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from ray import serve

app = FastAPI()

def cpu_intensive_task():
    result = 0
    for _ in range(1000000):
        result += _ ** 2
    return str(result)

@serve.deployment
@serve.ingress(app)
class FastAPIDeployment:
    @app.get("/hello")
    def say_hello(self, name: str):
        result = cpu_intensive_task()  # Replace with a CPU-intensive operation
        return StreamingResponse(result)

prova = FastAPIDeployment.bind()
