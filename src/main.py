import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src import config
from src.api import api_router
from src.database import init_db, close_db
from src.geodata.database import geonames_db
from src.scheduling import scheduler

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="I'm not alone")
app.include_router(api_router)
app.mount('/static', StaticFiles(directory=config.STATIC_PATH, check_dir=True), name="static")


@app.on_event("startup")
def startup():
    init_db(host=config.DB_HOST, db=config.DB_NAME)
    scheduler.start()
    geonames_db.connect(config.DB_GEONAMES_DATA_SOURCE)


@app.on_event("shutdown")
def shutdown():
    close_db()
    scheduler.shutdown()
    geonames_db.close()