import uvicorn

import theme_picker

if __name__ == "__main__":
    uvicorn.run(
        theme_picker.fastapi_app,
        port=8001,
    )
