from fastapi import FastAPI, Response, Request
from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello FastAPI"}


@app.get("/cookie")
def set_cookie(response: Response):
    response.set_cookie(
        key="practice_cookie",
        value="hello-cookie",
        max_age=3600, # 1시간
        samesite="lax",
    )
    return {"message": "cookie set"}
    
@app.get("/cookie/read")
def read_cookie(request: Request):
    return {"practice_cookie": request.cookies.get("practice_cookie")}


boards: dict[int, dict] = {
    1: {"id": 1, "name": "공부"},
    2: {"id": 2, "name": "와플"},
}

memos: dict[int, dict] = {
    1: {"id": 1, "board_id": 1, "title": "세미나 복습"},
    2: {"id": 2, "board_id": 2, "title": "과제 시작"},
}

class MemoCreate(BaseModel):
    title: str = Field(max_length=10)

class NotFoundError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

# Exception Handlers
@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
    # TODO 4: 404와 {"code": exc.code, "message": exc.message}를 반환하세요.
    return JSONResponse(
        status_code=404,
        # exc: 방금 raise된 에러 객체 자체를 담는 변수
        content={"code": exc.code, "message": exc.message},
    )

@app.exception_handler(RequestValidationError)
def validation_error_handler(request: Request, exc: RequestValidationError):
    # TODO 7: exc.errors()를 print하고,
    #         422와 {"code": "INVALID_REQUEST", "message": "요청 형식이 올바르지 않습니다."}를 반환하세요.
    print(exc.errors())
    return JSONResponse(
        status_code=422,
        content={"code": "INVALID_REQUEST", "message": "요청 형식이 올바르지 않습니다."}
    )

# Dependencies
def get_board(board_id: int) -> dict:
    # TODO 2: boards에서 board_id에 해당하는 보드를 찾아 반환하고,
    #         없으면 NotFoundError("BOARD_NOT_FOUND", "N번 보드가 없습니다.")를 발생시키세요.
    if board_id not in boards:
        raise NotFoundError("BOARD_NOT_FOUND", f"{board_id}번 보드가 없습니다.")
    return boards[board_id]

def get_memo(memo_id: int, board: dict = Depends(get_board)) -> dict:
    # TODO 3: get_board 의존성으로 보드를 주입받도록 매개변수를 추가하세요.
    #         memos에서 memo_id에 해당하는 메모를 찾아 반환하고,
    #         메모가 없거나 해당 보드의 메모가 아니면
    #         NotFoundError("MEMO_NOT_FOUND", "B번 보드에 N번 메모가 없습니다.")를 발생시키세요.
    memo = memos.get(memo_id) # memos 딕셔너리에서 memo_id로 찾기
    if memo is None or memo["board_id"] != board["id"]:
        raise NotFoundError("MEMO_NOT_FOUND", f"{board['id']}번 보드에 {memo_id}번 메모가 없습니다.")
    return memo

# Endpoints
@app.get("/boards/{board_id}/memos")
def list_memos(board: dict = Depends(get_board)):
    return [m for m in memos.values() if m["board_id"] == board["id"]]

@app.post("/boards/{board_id}/memos", status_code=201)
def create_memo(body: MemoCreate, board: dict = Depends(get_board)):
    memo_id = max(memos, default=0) + 1
    memos[memo_id] = {"id": memo_id, "board_id": board["id"], "title": body.title}
    return memos[memo_id]

@app.get("/boards/{board_id}/memos/{memo_id}")
def read_memo(memo: dict = Depends(get_memo)):
    # TODO 5: get_memo 의존성으로 메모를 주입받아 그대로 반환하세요.
    return memo

@app.delete("/boards/{board_id}/memos/{memo_id}", status_code=204)
def delete_memo(memo: dict = Depends(get_memo)):
    # TODO 6: get_memo 의존성으로 메모를 주입받아 memos에서 삭제하세요.
    # (hint: dict에서 지울 때 del dict[] 사용)
    del memos[memo["id"]]    