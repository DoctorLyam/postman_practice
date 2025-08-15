# app/main.py

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, validator, Extra
from app.data import animals

app = FastAPI()

REQUIRED_HEADER = "x-api-key"
RESERVED_IDS = {animal["id"] for animal in animals}


class Animal(BaseModel, extra=Extra.forbid):
    id: int
    name: str
    species: str
    size: str
    can_fly: bool

    @validator("id")
    def id_not_reserved(cls, v):
        if v in RESERVED_IDS:
            raise ValueError("Этот id уже занят")
        return v


def validate_header(request: Request):
    if REQUIRED_HEADER not in request.headers:
        raise HTTPException(status_code=400, detail="Отсутствует обязательный хедер")


@app.get("/health")
def health_check(request: Request):
    validate_header(request)
    return {"status": "ok"}


@app.get("/animals")
def get_animals(request: Request, id: int = None):
    validate_header(request)
    if id is None:
        return animals
    for animal in animals:
        if animal["id"] == id:
            return animal
    raise HTTPException(status_code=404, detail="Животное с таким id не найдено")


@app.post("/animals", status_code=201)
async def create_animal(request: Request):
    validate_header(request)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Невозможно прочитать JSON")

    # Попробуем провалидировать через Pydantic
    try:
        animal = Animal(**payload)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except TypeError:
        raise HTTPException(status_code=400, detail="Отсутствует необходимый параметр в теле запроса")
    except Exception as e:
        detail = str(e)
        if "extra fields not permitted" in detail:
            raise HTTPException(status_code=400, detail="В запросе присутствуют лишние сущности")
        if "value is not a valid" in detail or "not of expected type" in detail:
            raise HTTPException(status_code=400, detail="Один из параметров не соответствует ожидаемому формату")
        raise HTTPException(status_code=400, detail="Ошибка валидации")

    return {
        **animal.dict(),
        "message": "Введи этот текст в ответ к задаче: Я создал некую тварь"
    }
