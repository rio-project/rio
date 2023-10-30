import uvicorn

import website

if __name__ == "__main__":
    uvicorn.run(
        website.fastapi_app,
        port=8001,
    )
