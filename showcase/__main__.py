import uvicorn

import showcase

if __name__ == "__main__":
    uvicorn.run(
        showcase.app,
        port=8001,
    )
