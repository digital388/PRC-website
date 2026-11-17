import shutil
import tempfile
from io import BytesIO

from PIL import Image

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import FlagshipProgram


class PageTests(TestCase):
    def test_pages_render(self):
        for url_name in ['home', 'institution', 'province', 'constitution', 'archives']:
            with self.subTest(page=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Pokhara Research Centre")

    def test_home_content(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Ideas For Accountable Governance")
        self.assertContains(response, "Province Cell Repository")


class FlagshipProgramTests(TestCase):
    def test_built_in_cards_shown_when_table_empty(self):
        response = self.client.get(reverse('province'))
        self.assertContains(response, "Our Flagship Programs")
        self.assertContains(response, "Youth In Policy")
        self.assertContains(response, "Capacity Building Program for Women")
        # The two built-in cards keep their original Explore links.
        self.assertContains(response, 'href="/province/ypg-fellowship/"')
        self.assertContains(response, 'href="#"')

    def test_admin_managed_card_is_rendered(self):
        program = FlagshipProgram.objects.create(
            title_en="ZZ Test Flagship",
            title_np="परीक्षण कार्यक्रम",
            description_en="A test description",
            image="flagship/test.png",
            link="/province/",
            link_label_en="Explore",
        )
        response = self.client.get(reverse('province'))
        self.assertContains(response, program.title_en)
        self.assertContains(response, program.title_np)
        self.assertContains(response, program.image.url)
        self.assertContains(response, 'href="/province/"')
        # Once the table has rows, the hardcoded fallback cards step aside.
        self.assertNotContains(response, "Youth In Policy")


class FlagshipProgramAdminTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)

        User = get_user_model()
        User.objects.create_superuser("admin", "admin@example.com", "pw")
        self.client.login(username="admin", password="pw")

    def _png(self):
        buf = BytesIO()
        Image.new("RGB", (2, 2), "white").save(buf, format="PNG")
        return SimpleUploadedFile("logo.png", buf.getvalue(), content_type="image/png")

    def test_admin_can_add_flagship_program(self):
        add_url = reverse("admin:website_flagshipprogram_add")
        self.assertEqual(self.client.get(add_url).status_code, 200)

        response = self.client.post(add_url, {
            "title_en": "Admin Added Program",
            "title_np": "प्रशासनबाट थपिएको",
            "description_en": "Added through the admin.",
            "description_np": "",
            "image": self._png(),
            "link": "/province/ypg-fellowship/",
            "link_label_en": "Explore",
            "link_label_np": "थप हेर्नुहोस्",
            "order": 0,
        })
        self.assertEqual(response.status_code, 302)
        program = FlagshipProgram.objects.get(title_en="Admin Added Program")
        self.assertTrue(program.image.name.startswith("flagship/"))

        page = self.client.get(reverse("province"))
        self.assertContains(page, "Admin Added Program")
        self.assertContains(page, 'href="/province/ypg-fellowship/"')
        self.assertNotContains(page, "Youth In Policy")
