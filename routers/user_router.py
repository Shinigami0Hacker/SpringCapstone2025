from fastapi import APIRouter, Request, UploadFile, File, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import  JSONResponse
from fastapi.templating import Jinja2Templates
from routers import admin_router
from tinydb import TinyDB, Query
from models.api import transcript
import re
import asyncio
import asyncio
from utils.normalize import strip_accents
from routers.admin_router import DYNAMIC_SESSION_CONFIGURATION
from utils.matcher import pipe

locker = asyncio.Lock()

CURRENT_CONFIGURE_FILE = None

schema_db = TinyDB('./database/schema_db.json')
session_db = TinyDB('./database/session_db.json')
temporary_db = TinyDB('./database/temporary_db.json')

templates = Jinja2Templates(directory="./statics/templates")
Session = Query()
Table = Query()
Schema = Query()
router = APIRouter()

@router.get("/working/{session_id}")
def working_screen(request: Request, session_id: str):
    if not (admin_router.CURRENT_RUNNING_SESSION_ID == session_id):
        return templates.TemplateResponse("./pages/users/working-fallback.html", {"request": request})

    searched_session = session_db.search(Session.session_id == session_id)[0]
    session_name, schema_id, temporary_table_id, model_id = searched_session['name'], searched_session['schema_id'], searched_session['table_temporary_id'], searched_session['model_id']
    temporary_table = temporary_db.search(Table.table_id == temporary_table_id)
    
    column_name = temporary_table[0]['data'].keys()
    data = temporary_table[0]['data']
    
    return templates.TemplateResponse("./pages/users/working-screen.html", {"request": request, "session_name": session_name , "session_id": session_id, "schema_id": schema_id, "temporary_table_id": temporary_table_id, "column_name": column_name, "column_data": data, "model_id": model_id})
    

@router.post("/working/{session_id}")
async def upload_audio(_: Request, session_id: str, file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        transcription = transcript(admin_router.MODEL_IN_USE, file_bytes)
        if not transcription:
            return JSONResponse(
            content={"error": "The audio not contain speech"},status_code=400)
        searched_session = session_db.search(Session.session_id == admin_router.CURRENT_RUNNING_SESSION_ID)[0]
        
        schema_id, table_id = searched_session['schema_id'], searched_session['table_temporary_id']
        temporary_table_id = searched_session['table_temporary_id']
        tmp_table = temporary_db.search(Table.table_id == temporary_table_id)[0]
        column_name = list(tmp_table['data'].keys())
        
        content = schema_db.search(Schema.id == schema_id)[0]['schema_content']
        extracted_data =  pipe(transcription, content, admin_router.DYNAMIC_SESSION_CONFIGURATION)
        if not all(x is None for x in extracted_data):
            for x in range(len(extracted_data)):
                tmp_table['data'][column_name[x]].append(extracted_data[x])
                temporary_db.update(tmp_table, lambda x: x["table_id"] == table_id)
        return JSONResponse(
            content={"transcription": transcription},status_code=200)
    finally:
        await file.close()

@router.get("/working/{session_id}/get")
async def working_screen(_: Request, session_id: str):
    searched_session = session_db.search(Session.session_id == session_id)[0]
    temporary_table_id = searched_session['table_temporary_id']
    temporary_table = temporary_db.search(Table.table_id == temporary_table_id)
    data = list(temporary_table[0]['data'].values())
    return data

@router.post("/working/{session_id}/update")
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

@router.post("/working/{session_id}/delete/row")
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


@router.post("/working/{session_id}/add/row")
async def add_row(request: Request, session_id: str):
    data = await request.json()
    table_id = data["table_id"]
    record  = data["record"]
    tmp_table = temporary_db.search(Table.table_id == table_id)[0]
    column_name = list(tmp_table['data'].keys())
    for i in range(len(record)):
        tmp_table['data'][column_name[i]].append(record[i])
    temporary_db.update(tmp_table, lambda x: x["table_id"] == table_id)
    return Response(status_code=200)



