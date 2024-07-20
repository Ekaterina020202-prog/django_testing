import random
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    comments_count_before = Comment.objects.count()
    client.post(detail_url, data=form_data)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


@pytest.mark.django_db
def test_user_can_create_comment(author_client,
                                 detail_url,
                                 form_data,
                                 news,
                                 author):
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_after - comments_count_before == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, '
                              f'{random.choice(BAD_WORDS)}, еще текст'}
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_author_can_delete_comment(author_client,
                                   delete_url,
                                   url_to_comments,
                                   comment):
    comments_count_before = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count_after = Comment.objects.count()
    assert comments_count_before - comments_count_after == 1


def test_user_cant_delete_comment_of_another_user(admin_client,
                                                  delete_url,
                                                  comment):
    comments_count_before = Comment.objects.count()
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_author_can_edit_comment(author_client,
                                 edit_url,
                                 url_to_comments,
                                 form_data,
                                 comment):
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(admin_client,
                                                edit_url,
                                                form_data,
                                                comment):
    old_text = comment.text
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text
