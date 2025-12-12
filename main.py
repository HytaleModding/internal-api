import uvicorn
import os
from fastapi import FastAPI, HTTPException, Depends, Header
from contextlib import asynccontextmanager
from models import ServerStatistics
from database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_pool()
    yield
    await db.close()

app = FastAPI(lifespan=lifespan)

def verify_api_key(authorization: str = Header()):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.replace("Bearer ", "")
    if token != os.getenv('API_KEY'):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return token

@app.get("/guild/stats")
async def get_guild_stats(api_key: str = Depends(verify_api_key)):
    try:
        stats = await db.get_latest_server_stats(1440173445039132724)
        if not stats:
            raise HTTPException(status_code=404, detail="No stats found")
        
        return {
            "active_members": stats['total_members'] - stats['offline_members'],
            "total_members": stats['total_members'],
            "member_statuses": {
                "online": stats['online_members'],
                "away": stats['idle_members'],
                "dnd": stats['dnd_members'],
                "offline": stats['offline_members']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)