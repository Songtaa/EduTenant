from app.db.session import master_async_engine

def get_master_engine():
    return master_async_engine