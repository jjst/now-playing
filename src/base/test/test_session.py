from requests.exceptions import ConnectTimeout
from base.session import build_session

import pytest
from unittest.mock import Mock

settings = Mock(
    requests=Mock(default_timeout_seconds=0.001),
)


def test_session_timeout():
    session = build_session(settings)
    with pytest.raises(ConnectTimeout):
        session.get('https://github.com/')
