import sys
sys.path.append("..")

from starlette.responses import RedirectResponse

from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from DataBase import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


SECRET_KEY = "123rasulQq"
ALGORITHM = "HS256"

templates = Jinja2Templates(directory="templates")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.User)\
        .filter(models.User.username == username)\
        .first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):

    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not found")


@router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)

    response.set_cookie(key="access_token", value=token, httponly=True)

    return True


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, email: str = Form(...), username: str = Form(...),
                        firstname: str = Form(...), lastname: str = Form(...),
                        password: str = Form(...), password2: str = Form(...),
                        db: Session = Depends(get_db)):

    validation1 = db.query(models.User).filter(models.User.username == username).first()

    validation2 = db.query(models.User).filter(models.User.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg = "Invalid registration request"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

    user_model = models.User()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname

    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


























# import sys
#
# from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
# from pydantic import BaseModel
# from typing import Optional
# import models
# from passlib.context import CryptContext
# from sqlalchemy.orm import Session
# from DataBase import SessionLocal, engine
# from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
# from datetime import timedelta, datetime
# from jose import jwt, JWTError
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
#
# from starlette.responses import RedirectResponse
#
# sys.path.append("..")
# SECRET_KEY = '123rasulQq'  # мой пароль
# ALGORITHM = 'HS256'  # алгоритм который мой токен будет шифроваться
#
# templates = Jinja2Templates(directory="templates")  # connect HTML to app with Jinja2
#
#
# # class CreateUser(BaseModel):  # модель создания Польвотеля
# #     username: str
# #     email: Optional[str]
# #     first_name: str
# #     last_name: str
# #     password: str
# #     phone_number: Optional[str]
# #
#
# # ______________________________________________________
#
#
# oauth2_bearer = OAuth2PasswordBearer(
#     tokenUrl="auth/token-url")  # мы собираемся иззвлечь любые данные или что нибудь из заголовка авторизации
# # ______________________________________________________
#
#
# bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# models.Base.metadata.create_all(bind=engine)  # это создаёт нашу базу данных и сделает всё необходимое для таблици
#
# router = APIRouter(
#     prefix="/auth",
#     tags=["auth"],
#     responses={401: {"user": "Not authorized"}}
# )
#
#
# class LoginForm:
#     def __init__(self, request: Request):  # когда му отправляем в каждой HTML-форме
#         self.request: Request = request
#         self.username: Optional[str] = None  # мы можем получить имя пользователя и пароль
#         self.password: Optional[str] = None
#
#     async def create_auth_form(self):  # когда мы делаем auth-form нам нужен адрес почты и пороль
#         """
#         когда мы отправляем имя пользователя и пароль
#             мы получаем емаил и пороль
#         когда мы получаем текстовое поле имейла, мы просто меняем его на имя ползователя ,чтобы затем мы могли запустить наш
#         приложения
#         """
#         form = await self.request.form()
#         self.username = form.get("email")
#         self.password = form.get("password")
#
#
# def get_db():  # безконечная связь с базой данных
#     global db
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()
#
#
# def get_password_hash(password):  # хеширует пароль
#     return bcrypt_context.hash(password)
#
#
# def verify_password(plain_password,
#                     hashed_password):  # проверяем порольпользователя , сравниваем хешированный пароль с обычным
#     return bcrypt_context.verify(plain_password, hashed_password)
#
#
# def authenticate_user(user: str, password: str,
#                       db):  # Авторизацыи пользователя , Это функция проверяет пароль и username
#     user = db.query(models.User) \
#         .filter(models.User.username == user) \
#         .first()
#
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user
#
#
# def create_access_token(username: str, user_id: int,  # создаём токен из зашифрованного данного
#                         expires_delta: Optional[timedelta] = None):
#     encode = {"sub": username, 'id': user_id, }
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=60)
#     encode.update({'exp': expire})
#     return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
#
#
# # @app.post("decode/token") #декодировани веб токена JWT
#
#
# async def get_current_user(request: Request):
#     try:
#         token = request.cookies.get("access_token")
#         if token is None:
#             return None
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         user_id: int = payload.get("id")
#         if username is None or user_id is None:
#             await logout(request)
#         return {"username": username, "id": user_id}
#     except JWTError:
#         raise HTTPException(status_code=404, detail="Not found")
#
#
# # @router.post('/create/user')  # создания пользователя и пушем в таблицу
# # async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
# #     create_user_model = models.User()
# #     create_user_model.email = create_user.email
# #     create_user_model.first_name = create_user.first_name
# #     create_user_model.last_name = create_user.last_name
# #     create_user_model.phone_number = create_user.phone_number
# #
# #     hash_password = get_password_hash(create_user.password)
# #
# #     create_user_model.hashed_password = hash_password
# #     create_user_model.username = create_user.username
# #     create_user_model.is_active = True
# #
# #     db.add(create_user_model)
# #     db.commit()
#
#
# @router.post('/token-url')  # проверяем пароль и имя пользователя
# async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
#                                  db: Session = Depends(get_db)):
#     user = authenticate_user(form_data.username, form_data.password, db)
#     if not user:
#         return False
#     token_expires = timedelta(minutes=60)
#     token = create_access_token(user.username,
#                                 user.id,
#                                 expires_delta=token_expires)
#     response.set_cookie(key="access_token", value=token, httponly=True)
#     return True
#
#
# @router.get("/", response_class=HTMLResponse)
# async def authenticate_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": Request})
#
#
# @router.post("/", response_class=HTMLResponse)
# async def login(request: Request, db: Session = Depends(get_db)):
#     """
#     https://www.udemy.com/course/fastapi-the-complete-course/learn/lecture/29972622#questions
#     мы проверяем файл cookie пользователя в токене достурпа жернала где в нутри слово передаётся в ответ
#     установка данныч в файл cookie если пользователь True с токеном
#     Есди сообшения не верное мы отправляем мы обновляем страницу входа и передаём сообшения о нек полном име пользователя и пароль
#     Если проверка верна мы возврашаем ответ с набором файла cookie
#
#     Если что-то в пути ломается  Exept и try захватывает ошибку и обновляет страницу и сообшает о ошибке
#     """
#     try:
#         form = LoginForm(request)
#         await form.create_auth_form()
#         response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
#
#         validete_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)
#
#         if not validete_user_cookie:
#             msg = " Incorrect User name or Password "
#             return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
#         return response
#     except HTTPException:
#         msg = "Unknown Error"
#         return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
#
#
# @router.get("/logout")
# async def logout(request: Request):
#     msg = "Logout Successful"
#     response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
#     response.delete_cookie(key="access_token")
#     return response
#
#
# @router.get("/register", response_class=HTMLResponse)
# async def register(request: Request):
#     return templates.TemplateResponse("register.html", {"request": Request})
#
#
# @router.post('/register', response_class=HTMLResponse)
# async def register_user(request: Request, email: str = Form(...), username: str = Form(...),
#                         firstname: str = Form(...), lastname: str = Form(...),
#                         password: str = Form(...), password2: str = Form(...),
#                         db: Session = Depends(get_db)):
#     validation1 = db.query(models.User).filter(models.User.username == username).first()
#
#     validation2 = db.query(models.User).filter(models.User.email == email).first()
#
#     if password != password2 or validation1 is None or validation2 is None:
#         msg = "Invalid registration request"
#         return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
#
#     user_model = models.User()
#     user_model.username = username
#     user_model.email = email
#     user_model.first_name = firstname
#     user_model.last_name = lastname
#
#     hash_password = get_password_hash(password)
#     user_model.hashed_password = hash_password
#     user_model.is_active = True
#
#     db.add(user_model)
#     db.commit()
#
#     msg = "User successfully created"
#     return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
#
#     # Exceptions
# #
# #
# def get_user_exception():
#     credential_exceptions = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     return credential_exceptions
#
# #
# # def token_exception():
# #     token_exception_response = HTTPException(
# #         status_code=status.HTTP_401_UNAUTHORIZED,
# #         detail="Incorrect username or password",
# #         headers={"WWW-Authenticate": "Bearer"},
# #     )
# #     return token_exception_response
