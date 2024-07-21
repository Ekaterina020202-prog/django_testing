from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status',
    (
        ('home_url', 'client', HTTPStatus.OK),
        ('detail_url', 'client', HTTPStatus.OK),
        ('login_url', 'client', HTTPStatus.OK),
        ('logout_url', 'client', HTTPStatus.OK),
        ('signup_url', 'client', HTTPStatus.OK),
        ('edit_url', 'admin_client', HTTPStatus.NOT_FOUND),
        ('edit_url', 'author_client', HTTPStatus.OK),
        ('delete_url', 'admin_client', HTTPStatus.NOT_FOUND),
        ('delete_url', 'author_client', HTTPStatus.OK),
    ),
)
def test_pages_availability(request,
                            url_fixture,
                            client_fixture,
                            expected_status
                            ):
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_fixture',
    (
        'edit_url',
        'delete_url',
    ),
)
def test_redirect_for_anonymous_client(
        request,
        client,
        login_url,
        url_fixture
):
    url = request.getfixturevalue(url_fixture)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
