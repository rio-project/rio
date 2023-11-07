import uvicorn

import website

if __name__ == "__main__":
    uvicorn.run(
        website.fastapi_app,
        host="0.0.0.0",
        port=8001,
    )
