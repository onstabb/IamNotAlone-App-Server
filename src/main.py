import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import config
from admin.api import admin
from api import api_router
from authorization.service import create_admin
from database import init_db, close_db
from location.database import geonames_db
from scheduling import scheduler


logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app_instance: FastAPI):
    init_db(host=config.DB_URI, db=config.DB_NAME)
    scheduler.start()
    geonames_db.connect(datasource=config.DB_GEONAMES_DATA_SOURCE,)
    create_admin()
    yield
    close_db()
    scheduler.shutdown()
    geonames_db.close()


app = FastAPI(title="I'm not alone", lifespan=lifespan)
app.include_router(api_router)
app.mount('/static', StaticFiles(directory=config.STATIC_PATH, check_dir=True), name="static")
admin.mount_to(app)
