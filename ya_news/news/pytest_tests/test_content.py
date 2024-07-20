import pytest
from django.urls import reverse

from yanews import settings

FORM = 'form'
NEWS = 'news'


@pytest.mark.django_db
def test_news_count(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, comments_list, detail_url):
    response = client.get(detail_url)
    assert NEWS in response.context
    news = response.context[NEWS]
    first_comment, second_comment, *_ = news.comment_set.all()
    assert first_comment.created < second_comment.created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert FORM not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert FORM in response.context
