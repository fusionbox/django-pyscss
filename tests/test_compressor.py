from django.template import Template, Context

from tests.utils import CollectStaticTestCase


APP2_LINK_TAG = """
{% load staticfiles compress %}
{% compress css %}
<link rel="stylesheet" type="text/x-scss" href="{% static 'css/app2.scss' %}">
{% endcompress %}
"""

IMPORT_APP2_STYLE_TAG = """
{% load staticfiles compress %}
{% compress css %}
<style type="text/x-scss">
@import "css/app2.scss";
</style>
{% endcompress %}
"""


class CompressorTest(CollectStaticTestCase):
    def test_compressor_can_compile_scss(self):
        actual = Template(APP2_LINK_TAG).render(Context())
        # 4b368862ec8c is the cache key that compressor gives to the compiled
        # version of app2.scss.
        self.assertIn('4b368862ec8c.css', actual)

    def test_compressor_can_compile_scss_from_style_tag(self):
        actual = Template(IMPORT_APP2_STYLE_TAG).render(Context())
        self.assertIn('4b368862ec8c.css', actual)
