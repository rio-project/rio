import pytest
from utils import create_mockapp

import rio


async def test_session_attachments():
    async with create_mockapp() as app:
        session = app.session

        list1 = ["foo", "bar"]
        list2 = []

        session.attachments.add(list1)
        assert session.attachments[list] is list1

        session.attachments.add(list2)
        assert session.attachments[list] is list2


async def test_access_nonexistent_session_attachment():
    async with create_mockapp() as app:
        session = app.session

        with pytest.raises(KeyError):
            session.attachments[list]


async def test_default_attachments():
    class Settings(rio.UserSettings):
        foo: int

    dict_attachment = {"foo": "bar"}
    settings_attachment = Settings(3)

    async with create_mockapp(
        default_attachments=[dict_attachment, settings_attachment]
    ) as app:
        session = app.session

        # Default attachments shouldn't be copied, unless they're UserSettings
        assert session.attachments[dict] is dict_attachment

        assert session.attachments[Settings] == settings_attachment
        assert session.attachments[Settings] is not settings_attachment
