import random

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.db import models
from django.test import TestCase
from django.utils import six
from django.utils.timezone import now
from watson import search

from cms.apps.pages.models import Page, PageBase, ContentBase
from cms.apps.pages.admin import page_admin
from cms.apps.media.admin import FileAdmin
from cms.apps.media.models import File, ImageRefField
from cms.admin import get_related_objects_admin_urls

class TestModelBase(models.Model):
    image = ImageRefField(
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

class TestModelOne(TestModelBase):
    pass

class TestModelTwo(TestModelBase):
    pass

class TestContentBase(TestModelBase, ContentBase):
    page = models.OneToOneField(
        Page,
        primary_key=True,
        editable=False,
        related_name='+',
    )

class TestContentBaseInline(TestModelBase):
    page = models.ForeignKey(
        Page,
    )

class TestModelOneInline(TestModelBase):
    parent = models.ForeignKey(
        TestModelOne,
    )

class TestContentBaseInlineAdmin(admin.StackedInline):
    model = TestContentBaseInline

class TestModelOneInlineAdmin(admin.StackedInline):
    model = TestModelOneInline


@admin.register(TestModelOne)
class TestModelOneAdmin(admin.ModelAdmin):
    inlines = [TestModelOneInlineAdmin]

@admin.register(TestModelTwo)
class TestModelTwoAdmin(admin.ModelAdmin):
    pass

page_admin.register_content_inline(TestContentBaseInline, TestContentBaseInlineAdmin)

class TestFileUsedOn(TestCase):
    maxDiff = 2000

    def setUp(self):
        self.site = AdminSite(name='test_admin')

        self.test_file = File.objects.create(
            title="Foo",
            file=SimpleUploadedFile(
                f"{now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg",
                b"data",
                content_type="image/jpeg"
            )
        )

        self.other_test_file = File.objects.create(
            title="Bar",
            file=SimpleUploadedFile(
                f"{now().strftime('%Y-%m-%d_%H-%M-%S')}-2.jpg",
                b"data",
                content_type="image/jpeg"
            )
        )

        self.test_model_1a = TestModelOne.objects.create(
            image=self.test_file,
        )

        self.test_model_1b = TestModelOne.objects.create(
            image=self.test_file,
        )

        self.test_model_1_other = TestModelOne.objects.create(
            image=self.other_test_file,
        )

        self.test_model_2a = TestModelTwo.objects.create(
            image=self.test_file,
        )

        # We will define these ourselves later
        self.test_page_model = None
        self.test_content_base_inline = None
        self.test_model_1a_inline = None
        self.test_content_base = None

        self.expected_outcome_test_file = [
            {
                'title': str(obj),
                'model_name': obj._meta.verbose_name,
                'admin_url': reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk]),
            } for obj in [self.test_model_1a, self.test_model_1b, self.test_model_2a]
        ]

        self.expected_outcome_other_test_file = [
            {
                'title': str(obj),
                'model_name': obj._meta.verbose_name,
                'admin_url': reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk]),
            } for obj in [self.test_model_1_other]
        ]

    def tearDown(self):
        self.test_file.file.delete(False)
        self.other_test_file.file.delete(False)
        self.test_file.delete()
        self.other_test_file.delete()

        self.test_model_1a.delete()
        self.test_model_1b.delete()
        self.test_model_1_other.delete()
        self.test_model_2a.delete()

        if self.test_content_base_inline:
            self.test_content_base_inline.delete()
            self.test_model_1a_inline.delete()
            self.test_page_model.delete()
            self.test_content_base.delete()

    def test_get_related_objects_admin_urls(self):
        # We have an instance of File (eg: self.test_file)
        # We have a Model with an ImageRefField (referencing the file)
        # We need to check that we can get the expected related objects when passing the file reference to get_related_objects_admin_urls()

        self.assertEqual(get_related_objects_admin_urls(self.test_file), self.expected_outcome_test_file)
        self.assertEqual(get_related_objects_admin_urls(self.other_test_file), self.expected_outcome_other_test_file)

    def test_inlines(self):
        with search.update_index():
            self.test_page_model = Page.objects.create(
                title='Test page',
                content_type=ContentType.objects.get_for_model(TestContentBase),
            )

            self.test_content_base = TestContentBase.objects.create(
                page=self.test_page_model,
                image=self.test_file,
            )

        self.test_model_1a_inline = TestModelOneInline.objects.create(
            parent=self.test_model_1a,
            image=self.test_file
        )

        # Clear out the old images from the previous test to esnure
        # that they do not interfere.
        self.test_model_1a.image = None
        self.test_model_1a.save()
        self.test_model_1b.image = None
        self.test_model_1b.save()
        self.test_model_2a.image = None
        self.test_model_2a.save()

        self.expected_outcome_test_file = [
            {
                'title': str(self.test_content_base),
                'model_name': self.test_content_base._meta.verbose_name,
                'admin_url': reverse(f'admin:{self.test_page_model._meta.app_label}_{self.test_page_model._meta.model_name}_change', args=[self.test_page_model.pk]),
            },
            {
                'title': str(self.test_model_1a_inline),
                'model_name': self.test_model_1a_inline._meta.verbose_name,
                'admin_url': reverse(f'admin:{self.test_model_1a._meta.app_label}_{self.test_model_1a._meta.model_name}_change', args=[self.test_model_1a.pk]),
            },
        ]

        self.assertEqual(get_related_objects_admin_urls(self.test_file), self.expected_outcome_test_file)

        # Now clear the contentbase image so we can add an inline to the
        # contentbase that has an image set and see it the contentbase's
        # parent gets returned.
        self.test_content_base.image = None
        self.test_content_base.save()
        self.test_model_1a_inline.image = None
        self.test_model_1a_inline.save()

        self.test_content_base_inline = TestContentBaseInline.objects.create(
            page=self.test_page_model,
            image=self.test_file,
        )

        self.expected_outcome_test_file = [
            {
                'title': str(self.test_content_base_inline),
                'model_name': self.test_content_base_inline._meta.verbose_name,
                'admin_url': reverse(f'admin:{self.test_page_model._meta.app_label}_{self.test_page_model._meta.model_name}_change', args=[self.test_page_model.pk]),
            }
        ]

        self.assertEqual(get_related_objects_admin_urls(self.test_file), self.expected_outcome_test_file)
