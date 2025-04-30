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
import re

locker = Lock()

IS_RUNNING = False
CURRENT_RUNNING_SESSION_ID = ""
DYNAMIC_SESSION_CONFIGURATION = None
CURRENT_MODEL_ID = None
MODEL_IN_USE = None

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

def update_dynamic_variable(data):
    """
    DYNAMIC_SESSION_CONFIGURATION - data type = list[list]
    """
    global DYNAMIC_SESSION_CONFIGURATION
    with locker:
        DYNAMIC_SESSION_CONFIGURATION = data
    
def change_model_use(model_id):
    global MODEL_IN_USE
    result = model_db.search(Model.model_id == int(model_id))[0]
    with locker:
        MODEL_IN_USE = WhisperModel(
        result["path"],
        compute_type="int8",
        device="cpu",
        cpu_threads=4)

def initiate_session(session_id, model_id):
    global CURRENT_RUNNING_SESSION_ID, IS_RUNNING, CURRENT_MODEL_ID
    change_model_use(model_id)
    with locker:
        CURRENT_MODEL_ID = model_id
        CURRENT_RUNNING_SESSION_ID = session_id
        IS_RUNNING = True

@router.post("/verification")
def vefify(response: Response, secret: Annotated[str, Form()]):
    if (secret == os.environ["SECRET_DEVICE_TOKEN"]):
        response.set_cookie("SECRET_DEVICE_TOKEN", secret, secure=True)
        return RedirectResponse("/admin/dashboard", headers=response.headers, status_code=302)
    return Response(
        status_code=401,
        content="Unauthorized"
    )

@router.post("/session/upload/dynamic")
async def upload_dynamic_configuration(request: Request):
    data = await request.json()
    update_dynamic_variable(data)
    return Response(status_code=200)

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
    print(IS_RUNNING)
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

@router.get("/session")
async def session(request: Request):
    dynamic = []
    if IS_RUNNING:
        searched_session = session_db.search(Session.session_id == CURRENT_RUNNING_SESSION_ID)
        if searched_session:
            schema_id = searched_session[0]['schema_id']
            schema_content = schema_db.search(Schema.id == schema_id)[0]['schema_content']
            dynamic = [None] * len(schema_content) 
            for index, field in enumerate(schema_content):
                if field.get("kind") == "in":
                    predefined_value = field.get("predefined")
                    if isinstance(predefined_value, str):
                        match = re.search(r"@session\('([^']+)'\)", predefined_value)
                        if match:
                            extracted_name = match.group(1)
                            dynamic[index] =  extracted_name.title()
    return templates.TemplateResponse("./pages/admin/session.html", {"request": request, "path": "session", "is_running": IS_RUNNING, "session_id": CURRENT_RUNNING_SESSION_ID, "dynamic": dynamic, "nums": len(dynamic)})

@router.post("/session/history/{session_id}")
async def update_record(request: Request, session_id: str):
    data = await request.json()
    table_id = data["table_id"]
    col_index = data["col"]
    row_index = data["row"]
    value = data["value"]
    tmp_table = temporary_db.search(Table.table_id == table_id)[0]
    column_name = list(tmp_table['data'].keys())
    tmp_table['data'][column_name[col_index]][row_index] = value
    temporary_db.update(tmp_table, lambda x: x["table_id"] == table_id)
    return Response(status_code=200)

@router.get("/session/history/{session_id}")
async def working_screen(request: Request, session_id: str):
    searched_session = session_db.search(Session.session_id == session_id)[0]
    session_name, schema_id, temporary_table_id, model_id = searched_session['name'], searched_session['schema_id'], searched_session['table_temporary_id'], searched_session['model_id']
    temporary_table = temporary_db.search(Table.table_id == temporary_table_id)
    column_name = temporary_table[0]['data'].keys()
    return templates.TemplateResponse("./pages/admin/history.html", {"request": request, "session_name": session_name ,"session_id": session_id,"schema_id": schema_id, "temporary_table_id": temporary_table_id, "column_name": column_name, "model_id": model_id})

@router.get("/session/history/{session_id}/get")
async def working_screen(_: Request, session_id: str):
    searched_session = session_db.search(Session.session_id == session_id)[0]
    temporary_table_id = searched_session['table_temporary_id']
    temporary_table = temporary_db.search(Table.table_id == temporary_table_id)
    data = list(temporary_table[0]['data'].values())
    return data


@router.post("/session/history/{session_id}/delete/row")
async def delete_row(request: Request, session_id: str):
    data = await request.json()
    table_id = data["table_id"]
    row_index = data["row"]
    tmp_table = temporary_db.search(Table.table_id == table_id)[0]
    column_name = list(tmp_table['data'].keys())
    for name in column_name:
        tmp_table['data'][name].pop(row_index)

    temporary_db.update(tmp_table, lambda x: x["table_id"] == table_id)
    return Response(status_code=200)

@router.post("/session/history/{session_id}/add/row")
async def add_row(request: Request, session_id: str):
    data = await request.json()
    table_id = data["table_id"]
    record  = data["record"]
    tmp_table = temporary_db.search(Table.table_id == table_id)[0]
    column_name = list(tmp_table['data'].keys())
    for i in range(len(record)):
        tmp_table['data'][column_name[i]].append(record[i])
    temporary_db.update(tmp_table, lambda x: x["table_id"] == table_id)
    temporary_db.update(tmp_table, lambda x: x["table_id"] == table_id)
    return Response(status_code=200)


@router.post("/session/end")
async def session(_: Request):
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
    
    initiate_session(session_id, model_id)
    return Response(
        content=session_id,
        status_code=200
    )

@router.get("/session/alls")
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

