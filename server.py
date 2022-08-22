import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.asgi:application", reload=True)
