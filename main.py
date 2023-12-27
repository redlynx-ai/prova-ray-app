from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from ray import serve
import time

app = FastAPI()

@serve.deployment
@serve.ingress(app)
class FastAPIDeployment:
    @app.get("/hello")
    def say_hello(self, name: str):
        def stream():
            for char in f"Hello, {name}!":
            # for char in ["a"] * 1000:
                # time.sleep(0.1)
                yield char

        return StreamingResponse(stream())

# serve.run(FastAPIDeployment.bind(), route_prefix="/", name="my_app1") # run with python main.py
prova = FastAPIDeployment.bind()