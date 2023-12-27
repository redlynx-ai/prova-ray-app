from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from ray import serve

app = FastAPI()

def cpu_intensive_task():
    for i in range(1000000):
        yield f"{i ** 2}\n"  # Yielding each calculation result as a separate line

@serve.deployment
@serve.ingress(app)
class FastAPIDeployment:
    @app.get("/hello")
    def say_hello(self, name: str):
        return StreamingResponse(cpu_intensive_task(), media_type="text/plain")

prova = FastAPIDeployment.bind()
