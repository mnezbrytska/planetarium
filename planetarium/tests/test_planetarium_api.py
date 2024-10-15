import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import (
    AstronomyShow,
    ShowSession,
    PlanetariumDome,
    ShowTheme
)
from planetarium.serializers import (
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer
)

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")
SHOW_SESSION_URL = reverse("planetarium:showsession-list")

def sample_astronomy_show(**params):
    defaults = {
        "title": "Sample Astronomy Show",
        "description": "Sample description",
    }
    defaults.update(params)
    return AstronomyShow.objects.create(**defaults)

def sample_show_session(**params):
    dome = PlanetariumDome.objects.create(
        name="Main Dome",
        rows=10,
        seats_in_row=10
    )
    defaults = {
        "show_time": "2024-10-15 14:00:00",
        "astronomy_show": sample_astronomy_show(),
        "planetarium_dome": dome,
    }
    defaults.update(params)
    return ShowSession.objects.create(**defaults)

def image_upload_url(show_id):
    """Return URL for uploading image to Astronomy Show"""
    return reverse("planetarium:astronomyshow-upload-image", args=[show_id])

def detail_url(show_id):
    return reverse("planetarium:astronomyshow-detail", args=[show_id])


class UnauthenticatedAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to access the list of shows"""
        res = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_astronomy_shows(self):
        """Test retrieving a list of astronomy shows"""
        sample_astronomy_show()
        sample_astronomy_show()

        res = self.client.get(ASTRONOMY_SHOW_URL)

        shows = AstronomyShow.objects.order_by("id")
        serializer = AstronomyShowListSerializer(shows, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_astronomy_show_detail(self):
        """Test retrieving a specific astronomy show by ID"""
        show = sample_astronomy_show()
        show.show_themes.add(ShowTheme.objects.create(name="Educational"))

        url = detail_url(show.id)
        res = self.client.get(url)

        serializer = AstronomyShowDetailSerializer(show)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "adminpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_astronomy_show(self):
        """Test creating a new astronomy show as admin"""
        payload = {
            "title": "Black Holes",
            "description": "A deep dive into the mysteries of black holes."
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        show = AstronomyShow.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(show, key))


class AstronomyShowImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@admin.com", "adminpass"
        )
        self.client.force_authenticate(self.user)
        self.show = sample_astronomy_show()

    def tearDown(self):
        self.show.image.delete()

    def test_upload_image_to_astronomy_show(self):
        """Test uploading an image to an astronomy show"""
        url = image_upload_url(self.show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.show.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.show.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.show.id)
        res = self.client.post(
            url, {"image": "notanimage"}, format="multipart"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class ShowSessionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_show_sessions(self):
        """Test retrieving a list of show sessions"""
        sample_show_session()
        sample_show_session()

        res = self.client.get(SHOW_SESSION_URL)

        sessions = ShowSession.objects.order_by("id")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(sessions))


class AdminShowSessionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@admin.com", "adminpass"
        )
        self.client.force_authenticate(self.user)

    def test_create_show_session(self):
        """Test creating a new show session"""
        dome = PlanetariumDome.objects.create(
            name="Main Dome",
            rows=10, seats_in_row=10
        )
        show = sample_astronomy_show()
        payload = {
            "show_time": "2024-10-15 14:00:00",
            "astronomy_show": show.id,
            "planetarium_dome": dome.id,
        }
        res = self.client.post(SHOW_SESSION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        session = ShowSession.objects.get(id=res.data["id"])
        self.assertEqual(session.astronomy_show.id, show.id)
        self.assertEqual(session.planetarium_dome.id, dome.id)
