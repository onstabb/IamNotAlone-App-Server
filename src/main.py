import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import config
from api import api_router
from database import init_db, close_db
from location.database import geonames_db
from scheduling import scheduler

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="I'm not alone")
app.include_router(api_router)
app.mount('/static', StaticFiles(directory=config.STATIC_PATH, check_dir=True), name="static")


@app.on_event("startup")
def startup():
    init_db(host=config.DB_URI, db=config.DB_NAME)
    scheduler.start()
    geonames_db.connect()


@app.on_event("shutdown")
def shutdown():
    close_db()
    scheduler.shutdown()
    geonames_db.close()
