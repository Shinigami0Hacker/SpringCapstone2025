from fastapi import APIRouter, Request, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import Response, JSONResponse
from fastapi.templating import Jinja2Templates
from routers.admin_router import MODEL_IN_USE
from routers.admin_router import CURRENT_RUNNING_SESSION_ID
from tinydb import TinyDB, Query
from models.api import transcript
import re
import asyncio
import asyncio
from utils.normalize import strip_accents
from routers.admin_router import DYNAMIC_SESSION_CONFIGURATION
import Levenshtein

locker = asyncio.Lock()

CURRENT_CONFIGURE_FILE = None
transcript_queue = asyncio.Queue()

schema_db = TinyDB('./database/schema_db.json')
session_db = TinyDB('./database/session_db.json')
temporary_db = TinyDB('./database/temporary_db.json')

templates = Jinja2Templates(directory="./statics/templates")
Session = Query()
Table = Query()

router = APIRouter()


def set_running_session():
    global my_value
    with locker:
        my_value += 1
        return {"new_value": my_value}

def number_convertor(string_numbers):
    number_map = {
        "không": 0,
        "một":1,
        "hai":2,
        "ba":3,
        "bốn":4,
        "năm":5,
        "sáu":6,
        "bảy":7,
        "tám":8,
        "chín":9,
        "chấm": ".",
        "phẩy": ","
    }
    second_layer_mapping = {
         strip_accents(k)
          : v for k, v in number_map.items()
    }
    result = ""
    unmatch_words = []
    for i, string_number in enumerate(string_numbers.split()):
        converted_number = number_map.get(string_number.strip())
        if converted_number:
            result += str(converted_number)
        else:
             unmatch_words.append((i, string_number))

    if unmatch_words:
        for index, unmatch_words in unmatch_words:
            converted_number_layer2 = second_layer_mapping.get(string_number.strip())
            if converted_number_layer2:
                result = result[:index] + converted_number_layer2 + result[index:]
    
    return result

def pipe(transciprt):
    transciprt = transciprt.strip()
    data = debug_matching_service(transciprt)
    for entry in data:    
        name_part = correction(name_part).title()
        type_part = correction(type_part).title()
        number_part = number_convertor(number_part)
    return (name_part, type_part, number_part)

def matching_single_column():
    for x in range():
        pass

def debug_matching_service(transcript):
    nums_column = 3
    regex = r"^tên\s+(.+?)\s+(?:loại|loai|lai|loan)\s+(.+?)\s+số\s+(?:kí|ký|ky|kỹ)\s+(.+?)\s+hết\.?$"
    m = re.match(regex, transcript)
    result = []
    if m:
        for i in range(nums_column):
                extracted_word = m.group(i + 1)
                if extracted_word:
                    result.append(extracted_word)
    return result

def generate_patttern_input(v, pronunciation):
    if isinstance(pronunciation, list):
        for word in pronunciation:
            print(v)


@router.get("/working/{session_id}")
def working_screen(request: Request, session_id: str):
    searched_session = session_db.search(Session.session_id == session_id)[0]
    session_name, schema_id, temporary_table_id, model_id = searched_session['name'], searched_session['schema_id'], searched_session['table_temporary_id'], searched_session['model_id']
    set_running_session(

    )
    temporary_table = temporary_db.search(Table.table_id == temporary_table_id)
    column_name = temporary_table[0]['data'].keys()
    data = temporary_table[0]['data']
    
    if CURRENT_RUNNING_SESSION_ID == session_id:
        return templates.TemplateResponse("./pages/users/working-screen.html", {"request": request, "session_name": session_name ,"schema_id": schema_id, "temporary_table_id": temporary_table_id, "column_name": column_name, "column_data": data, "model_id": model_id})
    else:
        return templates.TemplateResponse("./pages/users/working-fallback.html", {"request": request})

@router.post("/working/{session_id}")
async def upload_audio(file: UploadFile = File(...),):
    try:
        file_bytes = await file.read()
        transcription = transcript(MODEL_IN_USE, file_bytes)
        extracted_data =  pipe(transcription)
        print(extracted_data)
        if extracted_data:
            await transcript_queue.put(
                extracted_data
            )
        return JSONResponse(
            content={
                "transcription": transcription
            },
            status_code=200
        )
    finally:
        file.close()

@router.websocket("/queue")
async def metrics_socket(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            try:
                transcript = await asyncio.wait_for(transcript_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                transcript = None
            if transcript:
                await websocket.send_json({"extracted_data": transcript})
    except WebSocketDisconnect:
            print("WebSocket disconnected")

