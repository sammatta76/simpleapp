
import fastapi
from fastapi.responses import RedirectResponse

app = fastapi.FastAPI()



info = dict()


@app.get("/")
async def read_root():
    return {"message": "Ahla bi Nakhle"}

@app.get("/expired")
async def exp():
    return {"message": "subscription expired"}


@app.get("/fetch-url/{name}/")
async def fetch_url(name: str):
    answer = validate(name)
    if not answer:
        return RedirectResponse(url="/expired")
    url_path = info.get(name, "Hello")
    google_url = "https://www.google.com"
    print("redirected")
    return RedirectResponse(url=google_url)
    # return {"message": f"Fetching data from URL: {url_path}"}


async def validate(name):
    name = name.lower()
    if name == "teki":
        return False
    return True