import sys
sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse

from fastapi import Depends, APIRouter, Request, Form
import models
from DataBase import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()

    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user": user})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, title: str = Form(...), description: str = Form(...),
                      priority: int = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int, title: str = Form(...),
                           description: str = Form(...), priority: int = Form(...),
                           db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()

    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    todo.complete = not todo.complete

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)



#
# @router.get('/test') # create request with conected HTML
# async def test(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})
#
#
# @router.get("/")
# async def read_all(db: Session = Depends(get_db)):
#     return db.query(models.Todos).all()
#
#
# @router.get("/user")
# async def read_all_by_user(user: dict = Depends(get_current_user),
#                            db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     return db.query(models.Todos) \
#         .filter(models.Todos.owner_id == user.get("id")) \
#         .all()
#
#
# # ______________________________________________
# @router.get("/{todo_id}")
# async def read_todo(todo_id: int,
#                     user: dict = Depends(get_current_user),
#                     db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     todo_model = db.query(models.Todos) \
#         .filter(models.Todos.id == todo_id) \
#         .filter(models.Todos.owner_id == user.get("id")) \
#         .first()
#     if todo_model is not None:
#         return todo_model
#     raise http_xception()
#
#
#
# # ______________________________________________идентификатор пользователя(post reques)
# @router.post('/')
# async def create_todo(todo: ToDo,
#                       user: dict = Depends(get_current_user),
#                       db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     models_Todo = models.Todos()
#     models_Todo.title = todo.title
#     models_Todo.description = todo.description
#     models_Todo.priority = todo.priority
#     models_Todo.complete = todo.complete
#     # ______________________________________________идентификатор пользователя(post reques)
#     models_Todo.owner_id = user.get("id")
#
#     db.add(models_Todo)
#     db.commit()
#
#     return {
#         "status": 201,
#         'transaction': 'successfully'
#     }
#
#
# @router.put("/{todo_id}")
# async def update_tod(todo_id: int,
#                      todo: ToDo,
#                      user: dict = Depends(get_current_user),
#                      db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     todo_model = db.query(models.Todos) \
#         .filter(models.Todos.id == todo_id) \
#         .filter(models.Todos.owner_id == user.get("id")) \
#         .first()
#     # _________________________________________________________________put reques (идентификатор пользователя)
#     if todo_model is None:
#         raise http_xception()
#
#     todo_model.title = todo.title
#     todo_model.description = todo.description
#     todo_model.priority = todo.priority
#     todo_model.complete = todo.complete
#
#     db.add(todo_model)
#     db.commit()
#
#
# # ______________________________________________________delete request
#
# @router.delete('/{todo_id}')
# async def delete_todo(todo_id: int,
#                       user: dict = Depends(get_current_user),
#                       db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     todo_model = db.query(models.Todos) \
#         .filter(models.Todos.id == todo_id) \
#         .filter(models.Todos.owner_id == user.get("id")) \
#         .delete()
#
#     db.commit()
#     SuccessfulResponses(204)
#     return todo_model
#
#
# # ______________________________________________________delete request
#
# def SuccessfulResponses(status_code: int):
#     return {
#         "status": status_code,
#         'transaction': 'successfully',
#     }
#
#
# def http_xception():
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
