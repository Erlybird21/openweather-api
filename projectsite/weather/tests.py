import os
from unittest.mock import Mock, patch

import requests
from django.test import TestCase
from django.urls import reverse

PAYLOAD = {
    "name": "Tokyo",
    "sys": {"country": "JP"},
    "main": {"temp": 21.5, "humidity": 60, "feels_like": 20.8},
    "weather": [{"description": "scattered clouds", "icon": "03d"}],
    "wind": {"speed": 3.6},
}

TEST_KEY = "test-key-123"


class WeatherViewTests(TestCase):
    def setUp(self):
        self.url = reverse("weather")

    def make_response(self, payload=None, status_code=200):
        response = Mock()
        response.status_code = status_code
        response.json.return_value = payload if payload is not None else PAYLOAD
        if status_code >= 400:
            error = requests.exceptions.HTTPError(
                f"{status_code} Client Error for url: "
                f"https://api.openweathermap.org/data/2.5/weather?appid={TEST_KEY}"
            )
            error.response = response
            response.raise_for_status.side_effect = error
        else:
            response.raise_for_status.return_value = None
        return response

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": TEST_KEY})
    @patch("weather.views.requests.get")
    def test_default_city_when_no_param(self, mock_get):
        mock_get.return_value = self.make_response()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Puerto Princesa")
        self.assertEqual(mock_get.call_args.kwargs["params"]["q"], "Puerto Princesa")

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": TEST_KEY})
    @patch("weather.views.requests.get")
    def test_successful_search_renders_weather(self, mock_get):
        mock_get.return_value = self.make_response()

        response = self.client.get(self.url, {"city": "Tokyo"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "21.5")
        self.assertContains(response, "Scattered Clouds")
        self.assertContains(response, "JP")
        self.assertEqual(mock_get.call_args.kwargs["params"]["q"], "Tokyo")
        self.assertEqual(mock_get.call_args.kwargs["params"]["units"], "metric")

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": ""})
    @patch("weather.views.requests.get")
    def test_missing_api_key_shows_friendly_error(self, mock_get):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not configured")
        self.assertNotContains(response, "appid")
        mock_get.assert_not_called()

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": TEST_KEY})
    @patch("weather.views.requests.get")
    def test_city_not_found_404(self, mock_get):
        mock_get.return_value = self.make_response(status_code=404)

        response = self.client.get(self.url, {"city": "Nowhereville123"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No weather found for &#x27;Nowhereville123&#x27;")

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": TEST_KEY})
    @patch("weather.views.requests.get")
    def test_invalid_api_key_401(self, mock_get):
        mock_get.return_value = self.make_response(status_code=401)

        response = self.client.get(self.url)

        self.assertContains(response, "rejected the API key")

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": TEST_KEY})
    @patch("weather.views.requests.get")
    def test_timeout_shows_network_message(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout()

        response = self.client.get(self.url)

        self.assertContains(response, "took too long to respond")

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": TEST_KEY})
    @patch("weather.views.requests.get")
    def test_error_page_never_leaks_key_or_url(self, mock_get):
        for status_code in (401, 404):
            with self.subTest(status_code=status_code):
                mock_get.return_value = self.make_response(status_code=status_code)

                response = self.client.get(self.url)

                content = response.content.decode()
                self.assertNotIn(TEST_KEY, content)
                self.assertNotIn("appid", content)
                self.assertNotIn("api.openweathermap.org", content)

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": TEST_KEY})
    @patch("weather.views.requests.get")
    def test_empty_city_param_makes_no_request(self, mock_get):
        response = self.client.get(self.url, {"city": "   "})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a city name")
        mock_get.assert_not_called()

    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": TEST_KEY})
    @patch("weather.views.requests.get")
    def test_unexpected_payload_shows_generic_error(self, mock_get):
        mock_get.return_value = self.make_response(payload={"cod": "200"})

        response = self.client.get(self.url)

        self.assertContains(response, "unexpected response")
