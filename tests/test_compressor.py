from django.test import TestCase
from django.template.loader import Template, Context


APP2_LINK_TAG = """
{% load staticfiles compress %}
{% compress css %}
<link rel="stylesheet" type="text/x-scss" href="{% static 'css/app2.scss' %}">
{% endcompress %}
"""


class CompressorTest(TestCase):
    def test_compressor_can_compile_scss(self):
        actual = Template(APP2_LINK_TAG).render(Context())
        self.assertIn('4b368862ec8c.css', actual)
