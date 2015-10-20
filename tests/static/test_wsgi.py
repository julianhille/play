from pytest import mark, raises
from webtest import AppError


@mark.parametrize('route', ['/admin', '/'])
def test_admin_route_get(testapp_static, route):
    response = testapp_static.get(route)
    assert response.status_code == 200
    assert '<body' in str(response.body)
    assert '<html' in str(response.body)


@mark.parametrize('route', ['/admin', '/'])
def test_admin_route_post(testapp_static, route):
    with raises(AppError) as context:
        testapp_static.post_json(route, {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


@mark.parametrize('route', ['/admin', '/'])
def test_admin_route_put(testapp_static, route):
    with raises(AppError) as context:
        testapp_static.put_json(route, {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)


@mark.parametrize('route', ['/admin', '/'])
def test_admin_route_patch(testapp_static, route):
    with raises(AppError) as context:
        testapp_static.patch_json(route, {})
    assert '405 METHOD NOT ALLOWED' in str(context.value)
