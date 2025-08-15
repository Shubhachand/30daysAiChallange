import uuid
import aiofiles
from fastapi import UploadFile

async def save_temp_upload(file: UploadFile) -> str:
    temp_path = f"temp_{uuid.uuid4()}.webm"
    async with aiofiles.open(temp_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    return temp_path
