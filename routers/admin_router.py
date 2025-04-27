from fastapi import APIRouter, UploadFile, Request, Depends, Form, File
import uuid
from faster_whisper import WhisperModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, Response, JSONResponse
from dependencies.auth import verify_device_token
from typing import Annotated
import os
from threading import Lock
from utils.matcher import *
from datetime import datetime
from tinydb import TinyDB, Query

locker = Lock()

IS_RUNNING = True
CURRENT_RUNNING_SESSION_ID = "23c55908-b8a1-4cc7-8c5f-cffd67ffec0f"
DYNAMIC_SESSION_CONFIGURATION= {}
MODEL_IN_USE = WhisperModel(
        "models/hubs/pho-whisper-tiny",
        compute_type="int8",
        device="cpu",
        cpu_threads=4)

router = APIRouter()

templates = Jinja2Templates(directory="./statics/templates")

schema_db = TinyDB('./database/schema_db.json')
session_db = TinyDB('./database/session_db.json')
model_db = TinyDB('./database/model_db.json')
temporary_db = TinyDB('./database/temporary_db.json')

Model = Query()
Schema = Query()
Session = Query()
Table = Query()

from faster_whisper import WhisperModel

def change_model_use(model_id):
    global MODEL_IN_USE
    result = model_db.search(Model.model_id == model_id)
    if not result:
        return
    
    with locker:
        MODEL_IN_USE = WhisperModel(
        result["path"],
        compute_type="int8",
        device="cpu",
        cpu_threads=4)

@router.post("/verification")
def vefify(response: Response, secret: Annotated[str, Form()]):
    if (secret == os.environ["SECRET_DEVICE_TOKEN"]):
        response.set_cookie("SECRET_DEVICE_TOKEN", secret, secure=True)
        return RedirectResponse("/admin/dashboard", headers=response.headers, status_code=302)
    return Response(
        status_code=401,
        content="Unauthorized"
    )

@router.get("/verification")
def verification(request: Request):
    return templates.TemplateResponse("./verification.html", {"request": request})

@router.post("/verification")
def verification(response: Response, secret: Annotated[str, Form()]):
    if (os.getenv("SECRET_DEVICE_TOKEN") == secret):
        response.set_cookie("SECRET_DEVICE_TOKEN", secret)
        return RedirectResponse("/admin")
    else:
        return Response(
            content="Unauthorized",
            status_code=401
        )

@router.get("/", dependencies=[
    Depends(verify_device_token)]
    )
def main(_: Request):
    return RedirectResponse(url="/admin/dashboard")

@router.get("/dashboard", dependencies=[
    Depends(verify_device_token)
    ])
async def dashboard(request: Request):
    return templates.TemplateResponse("./pages/admin/dashboard.html", {"request": request, "path": "dashboard", "is_running": IS_RUNNING ,"total_schema": len(schema_db), "total_session": len(session_db)})

@router.get("/schema")
async def advanced_prompt(request: Request):
    
    return templates.TemplateResponse("./pages/admin/schema.html", {"request": request, "path": "schema"})

@router.get("/schema/alls")
async def get_all_schemas():
    records = schema_db.all()
    return JSONResponse(content=records, status_code=200)

@router.post("/schema")
async def create_schema(
    name: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        file_bytes = await file.read()
        data, json_error =  await validate_json_file(file_bytes)
        if not data:
            return Response(
            content=json_error,
            status_code=400
        )
        is_syntax_valid, validation_errors = validate_schema(data)
        if not is_syntax_valid:
            return Response(
            content=validation_errors,
            status_code=400
        )
        if schema_db.search(Schema.name == name):
            return Response(
            media_type='text/plain',
            content="The name was taken.",
            status_code=400
        )
        payload = {
            "name": name,
            "id": str(uuid.uuid4()),
            "created_date": datetime.now().strftime('%d-%m-%Y'),
            "schema_content": data
        }
        schema_db.insert(payload)
    finally:
        file.close()

    return Response(
        content="Uploaded",
        status_code=200
    )

@router.post("/session/dynamic_config")
def upload_dynamic_configs(req: Request):
    pass


@router.get("/session")
async def session(request: Request):
    return templates.TemplateResponse("./pages/admin/session.html", {"request": request, "path": "session", "is_running": IS_RUNNING, "session_id": CURRENT_RUNNING_SESSION_ID})

@router.get("session/history/{session_id}")
async def working_screen(request: Request, session_id: str):
    searched_session = session_db.search(Session.session_id == session_id)[0]
    session_name, schema_id, temporary_table_id = searched_session['name'], searched_session['schema_id'], searched_session['table_temporary_id']
    temporary_table = temporary_db.search(Table.table_id == temporary_table_id)
    
    column_name = temporary_table[0]['data'].keys()
    data = temporary_table[0]['content']

@router.get("/session/end")
async def session(request: Request):
    global IS_RUNNING, MODEL_IN_USE, CURRENT_RUNNING_SESSION_ID, DYNAMIC_SESSION_CONFIGURATION
    with locker:
        IS_RUNNING = None
        MODEL_IN_USE = None
        CURRENT_RUNNING_SESSION_ID = None
        DYNAMIC_SESSION_CONFIGURATION = None
    return Response(
        status_code=200,
        content="Stopped!"
    )

@router.post("/session")
async def create_session(
    name: str = Form(...),
    schema_id: str = Form(...),
    model_id: str = Form(...),
):  
    
    global CURRENT_RUNNING_SESSION_ID
    if session_db.search(Schema.name == name):
        return Response(
        media_type='text/plain',
        content="The session name was taken.",
        status_code=400
    )
    if IS_RUNNING:
        return Response(
        media_type='text/plain',
        content="Another session is running. You can not create in this moment.",
        status_code=400
    )
    table_temporary_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    session_payload = {
        "name": name,
        "schema_id": schema_id,
        "model_id": model_id,
        "table_temporary_id": table_temporary_id,
        "session_id": session_id,
        "created_date": datetime.now().strftime('%d-%m-%Y'),
    }
    session_db.insert(session_payload)
    columns = list(map(lambda x: x["name"], schema_db.search(Schema.id == schema_id)[0]['schema_content']))
    temporary_payload = {
        "table_id": table_temporary_id,
        "data": {
            k: [] for k in columns
        }
    }
    temporary_db.insert(temporary_payload)
    CURRENT_RUNNING_SESSION_ID = session_id
    
    return Response(
        content=session_id,
        status_code=200
    )

@router.get("/session/alls")
async def get_all_sessions():
    records = session_db.all()
    return JSONResponse(content=records, status_code=200)


@router.get("/session/{}")
async def get_all_sessions():
    records = session_db.all()
    return JSONResponse(content=records, status_code=200)

@router.get("/hubs")
async def model_hub(request: Request):
    return templates.TemplateResponse("./pages/admin/hub.html", {"request": request, "path": "market"})

@router.get("/hubs/alls")
async def get_all_models():
    records = model_db.all()
    return JSONResponse(content=records, status_code=200)

