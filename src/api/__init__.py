import connexion

import aioredis

from api import encoder
from api.tracing import configure_tracer
from api.cors import install_cors_middleware


def create_app():
    app = connexion.AioHttpApp(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('spec.yaml', arguments={'title': 'Now Playing API'})

    install_cors_middleware(app.app)

    configure_tracer(app)
    return app


async def create_redis_pool(app):
    """Create Redis connection pool"""
    redis_url = app["redis_url"]
    pool = await aioredis.from_url(redis_url)
    app["redis_pool"] = pool


async def close_redis_pool(app):
    """Close Redis connection pool"""
    pool = app["redis_client"]
    await pool.close()
