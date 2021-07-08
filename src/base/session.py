import requests_cache
from requests.adapters import HTTPAdapter

from base.config import settings


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def build_session(settings):
    session = requests_cache.CachedSession(
        backend='memory',
        expire_after=settings.requests.cache_ttl_seconds,
        allowable_methods=('GET', 'POST')
    )
    adapter = TimeoutHTTPAdapter(timeout=settings.requests.default_timeout_seconds)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


session = build_session(settings)
