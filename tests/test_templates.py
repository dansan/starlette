import os

import pytest

from starlette.applications import Starlette
from starlette.templating import Jinja2Templates


def test_templates(tmpdir, test_client_factory):
    path = os.path.join(tmpdir, "index.html")
    with open(path, "w") as file:
        file.write("<html>Hello, <a href='{{ url_for('homepage') }}'>world</a></html>")

    app = Starlette(debug=True)
    templates = Jinja2Templates(directory=str(tmpdir))

    @app.route("/")
    async def homepage(request):
        return templates.TemplateResponse("index.html", {"request": request})

    client = test_client_factory(app)
    response = client.get("/")
    assert response.text == "<html>Hello, <a href='http://testserver/'>world</a></html>"
    assert response.template.name == "index.html"
    assert set(response.context.keys()) == {"request"}


def test_template_response_requires_request(tmpdir):
    templates = Jinja2Templates(str(tmpdir))
    with pytest.raises(ValueError):
        templates.TemplateResponse(None, {})


def test_template_env_url_for_args(tmpdir):
    templates = Jinja2Templates(directory=str(tmpdir))

    url_for_func = templates.env.globals["url_for"]
    with pytest.raises(TypeError, match="Invalid positional argument passed."):
        assert url_for_func({}, "user", "args2", name="tomchristie")
    with pytest.raises(TypeError, match="Missing route name as the second argument."):
        assert url_for_func({}, name="tomchristie")
