from .schems import F, Elems
from aiomysql.pool import Pool

async def get_element(el: Elems, db: Pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id,title FROM special_project ;")
            (r,) = await cur.fetchone()
