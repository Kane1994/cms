from django.contrib.contenttypes.models import ContentType
from django.test import Client, RequestFactory, TestCase
from watson import search

from cms.apps.pages.models import ContentBase, Page

from ..models.base import \
    PublishedBaseSearchAdapter as CMSPublishedBaseSearchAdapter
from ..models.base import \
    SearchMetaBaseSearchAdapter as CMSSearchMetaBaseSearchAdapter
from ..models.base import PageBase, PublishedBase, SearchMetaBase


# Test models.
class TestPublishedBaseModel(PublishedBase):
    pass


class TestSearchMetaBaseModel(SearchMetaBase):
    pass


class PageBaseModel(PageBase):
    def get_absolute_url(self):
        return '/'

class TestContentBase(ContentBase):
            pass


# Test search adapters.
class PublishedBaseSearchAdapter(CMSPublishedBaseSearchAdapter):
    pass


class SearchMetaBaseSearchAdapter(CMSSearchMetaBaseSearchAdapter):
    pass


class ModelsBaseTest(TestCase):

    def test_publishedbasesearchadapter_get_live_queryset(self):
        search_adapter = PublishedBaseSearchAdapter(TestPublishedBaseModel)
        self.assertEqual(search_adapter.get_live_queryset().count(), 0)

        TestPublishedBaseModel.objects.create()
        self.assertEqual(search_adapter.get_live_queryset().count(), 1)

    def test_searchmetabase_get_context_data(self):
        obj = TestSearchMetaBaseModel.objects.create()
        self.assertDictEqual(obj.get_context_data(), {
            'meta_description': '',
            'robots_follow': True,
            'robots_index': True,
            'title': 'TestSearchMetaBaseModel object',
            'robots_archive': True,
            'header': 'TestSearchMetaBaseModel object',
            'og_title': '',
            'og_description': '',
            'og_image': None,
            'twitter_card': None,
            'twitter_title': '',
            'twitter_description': '',
            'twitter_image': None
        })

    def test_searchmetabase_render(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.pages = []

        class Context(dict):
            pass

        context = Context()
        context['page_obj'] = Context()
        context['page_obj'].has_other_pages = lambda: False

        obj = TestSearchMetaBaseModel.objects.create()
        response = obj.render(request, 'pagination/pagination.html', context)

        self.assertEqual(response.status_code, 200)

    def test_searchmetabasesearchadapter_get_live_queryset(self):
        search_adapter = SearchMetaBaseSearchAdapter(TestSearchMetaBaseModel)
        self.assertEqual(search_adapter.get_live_queryset().count(), 0)

        TestSearchMetaBaseModel.objects.create()
        self.assertEqual(search_adapter.get_live_queryset().count(), 1)

    def test_pagebasemodel_get_context_data(self):
        obj = PageBaseModel.objects.create()
        self.assertDictEqual(obj.get_context_data(), {
            'meta_description': '',
            'robots_follow': True,
            'robots_index': True,
            'title': '',
            'robots_archive': True,
            'header': '',
            'og_title': '',
            'og_description': '',
            'og_image': None,
            'twitter_card': None,
            'twitter_title': '',
            'twitter_description': '',
            'twitter_image': None
        })

    def test_get_preview_url(self):
        with search.update_index():
            page_obj = Page.objects.create(
                title='Foo',
                content_type=ContentType.objects.get_for_model(TestContentBase),
                is_online=False,
            )

            content_obj = TestContentBase.objects.create(page=page_obj)

        print('#############')
        print('preview URL', page_obj.get_preview_url())
        print('absolute URL', page_obj.get_absolute_url())
        print('#############')

        request = self.client.get(page_obj.get_absolute_url())
        self.assertEqual(request.status_code, 404)

        request = self.client.get(page_obj.get_preview_url())
        self.assertEqual(request.status_code, 200)
