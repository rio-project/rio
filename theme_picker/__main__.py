import uvicorn

import theme_picker

if __name__ == "__main__":
    uvicorn.run(
        theme_picker.app,
        port=8001,
    )
