from typing import  Any, Union, Type
from enum import Enum

from pydantic import BaseModel, validator, validate_arguments, FilePath, HttpUrl, Field

from .main import app


class Photo(BaseModel):
    name: str
    file: Any

    @validator("file")
    def valid_file(self, v, vv):
        """
        Meta valid file
        """
        return v


class Item(BaseModel):
    url: HttpUrl
    label: str
    title: str
    caption: str = Field(max_length=70)
    thumb: str

    @validator('thumb', pre=True)
    def cart_bg(cls, v, vv):
        """
        This change image for bg
        """
        return v


class GroupItem(BaseModel):
    type_name: str
    items: list[Item]


class F (str, Enum):
    lenta = ' Лента'
    calendar = 'Календарь мероприятий'
    history = 'История города'
    good = 'Поздравь Иркутск'
    galery = 'Галерея'

class Tabs(BaseModel):
    name: str
    url:str

class Elems(BaseModel):
    label: str
    title: str
    caption: str
    url: str
    image_url: str


class CalendarElems(Elems):
    pass

class HistoryElems(Elems):

    @classmethod
    async def from_orm(cls):
        pool = app.state.pool
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT id,title FROM special_project ;")
                (r,) = await cur.fetchone()
        cls(
            label = r.title ,
            title = r.title ,
            caption = r.
            url: str
            image_url: str
        )

class PrideElems(Elems):
    pass

class GaleryElems(Elems):
    pass

class Card(BaseModel):
    obj: Any
    type: str