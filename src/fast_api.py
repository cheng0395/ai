from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from chat import get_response
from db import get_chat_history

app = FastAPI()

class RequestBody(BaseModel):
    api_key: str
    user_input: str
    session_id: str

@app.post("/get_response")
async def get_response_endpoint(body: RequestBody):
    try:
        response = get_response(body.api_key, body.user_input, body.session_id)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_chat_history/{user_id}")
async def get_chat_history_endpoint(user_id: str):
    history = get_chat_history(user_id)
    return history

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)