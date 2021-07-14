import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import aiomysql

from route import route


app = FastAPI()

app.include_router(route)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*',],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def _startup():
    app.state.pool = await aiomysql.create_pool(host='172.23.0.4', port=3306,
                                       user='root', password='root', db='irk',charset ='utf8')
    print("startup done")


@app.on_event("shutdown")
def _shutdown():
    app.state.pool.close()
    print("shutdown done")


if __name__ == "__main__":
    uvicorn.run("main:app", debug=True, reload=True, log_level="debug", host="localhost",port=8080)
