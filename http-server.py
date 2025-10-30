from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, status, Header
from fastapi.responses import JSONResponse
from pathlib import Path
import aiofiles
import os

app = FastAPI()


BASE_DIR = Path("/home/bigpoppa/python/files").resolve()
API_TOKEN = "simpleToken"

def verify_token(authorization: str = Header(None)):
    if not authorization: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    scheme, _,token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )
    
    

@app.get("/hello")
async def say_hello(
    name: str | None = "User",
    _=Depends(verify_token) 
):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"Message": f"Hello {name}"}
    )
    
    
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    rel_dir: str = Form("")
):
    # Resolve target directory
    dest_dir = (BASE_DIR / rel_dir).resolve()
    if not str(dest_dir).startswith(str(BASE_DIR)):
        raise HTTPException(status_code=403, detail="Invalid path")

    # Ensure directory exists
    dest_dir.mkdir(parents=True, exist_ok=True)


    dest_path = dest_dir / file.filename
    temp_path = dest_path.with_suffix(dest_path.suffix + ".part")

    
    size = 0
    try:
        async with aiofiles.open(temp_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                await f.write(chunk)
                size += len(chunk)

        os.replace(temp_path, dest_path)  # Atomic move
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

    return JSONResponse(
        status_code=201,
        content={"path": str(dest_path.relative_to(BASE_DIR)), "size": size},
    )