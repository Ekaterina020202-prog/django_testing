from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from yanews import settings


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст коментария'
    }


@pytest.fixture
def pk_for_args(news):
    return news.id,


@pytest.fixture
def news_list():
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
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments_list.append(comment)
    return comments_list


@pytest.fixture
def detail_url(pk_for_args):
    return reverse('news:detail', args=pk_for_args)


@pytest.fixture
def delete_url(pk_for_args):
    return reverse('news:delete', args=pk_for_args)


@pytest.fixture
def edit_url(pk_for_args):
    return reverse('news:edit', args=pk_for_args)


@pytest.fixture
def url_to_comments(detail_url):
    return detail_url + '#comments'
