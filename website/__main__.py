import uvicorn

import website

if __name__ == "__main__":
    uvicorn.run(
        website.app.as_fastapi(),
        host="0.0.0.0",
        port=8001,
    )
