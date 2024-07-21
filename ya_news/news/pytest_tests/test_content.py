import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm
from news.models import News, Comment

FORM = 'form'
NEWS = 'news'

pytestmark = pytest.mark.django_db


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def news_list():
    # Создаем список новостей
    today = datetime.today()
    news_list = News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news_list


@pytest.fixture
def comments_list(news, author):
    now = timezone.now()
    comments_list = []
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments_list.append(comment)
    return comments_list


def test_news_count(client, news_list, home_url):
    response = client.get(home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list, home_url):
    response = client.get(home_url)
    news_list = response.context['object_list']
    all_dates = [news.date for news in news_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, comments_list, detail_url):
    response = client.get(detail_url)
    assert NEWS in response.context
    news = response.context[NEWS]
    comments = list(news.comment_set.all())
    sorted_comments = sorted(comments, key=lambda comment: comment.created)
    assert comments == sorted_comments


def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert FORM not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert FORM in response.context
    assert isinstance(response.context[FORM], CommentForm)
