from django.conf import settings

import pytest

from news.forms import CommentForm


FORM = 'form'
NEWS = 'news'

pytestmark = pytest.mark.django_db


def test_news_count(client, news_list, home_url):
    response = client.get(home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list, home_url):
    response = client.get(home_url)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, comments_list, detail_url):
    response = client.get(detail_url)
    assert NEWS in response.context
    news_instance = response.context[NEWS]
    comments = list(news_instance.comment_set.all())
    sorted_comments = sorted(comments, key=lambda comment: comment.created)
    assert comments == sorted_comments


def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert FORM not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert FORM in response.context
    assert isinstance(response.context[FORM], CommentForm)
