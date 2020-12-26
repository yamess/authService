import uvicorn

if __name__ == "__main__":
    uvicorn.run("authbase.server:app", host="dev.localhost.com", port=8002, reload=True)
