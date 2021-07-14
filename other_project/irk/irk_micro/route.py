
from  fastapi.routing import APIRouter
from .shems import  Card, HistoryElems, F


def test_gen_data(mod,type: str, diff: int) -> list[Card]:
    vars = [
        Card(
            type = type,
            obj = mod(
                    label = 'test'+str(i),
                    title = "title"+str(i),
                    caption = 'caption'+ str(i),
                    url = 'url' +str(i),
                    image_url = 'image_url' + str(i)
                )
        )
        for i in range(diff, 5 + diff)
    ]
    return vars


route_tabs = APIRouter(prefix='/tab')


@route_tabs.get('/lenta/')
async def get_history(page: int = 0):
    return test_gen_data(HistoryElems, 'short', page)




@route_tabs.get('/{name}/')
async def get_history(name: str ,page: int = 0):
    return test_gen_data(HistoryElems,'Chort', page)


route = APIRouter(prefix='/api')
route.include_router(route_tabs)

@route.get('/tabs')
async def get_tabs() ->list[Tabs]:
    head = [
        'Лента Лента',
        'Календарь мероприятий Календарь мероприятий',
        'История города История города',
        'Поздравь Иркутск Поздравь Иркутск',
        'Галерея Галерея',
    ]
    return [Tabs(name = i.value, url = i.name ) for i in F]


