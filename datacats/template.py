# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os import makedirs
from os.path import dirname
from shutil import copyfile


def ckan_extension_template(name, target):
    """
    Create ckanext-(name) in target directory.
    """
    setupdir = '{0}/ckanext-{1}theme'.format(target, name)
    extdir = setupdir + '/ckanext/{0}theme'.format(name)
    templatedir = extdir + '/templates/'
    staticdir = extdir + '/static/datacats'

    makedirs(templatedir + '/home/snippets')
    makedirs(staticdir)

    here = dirname(__file__)
    copyfile(here + '/images/chart.png', staticdir + '/chart.png')
    copyfile(here + '/images/datacats-footer.png',
        staticdir + '/datacats-footer.png')

    filecontents = [
        (setupdir + '/setup.py', SETUP_PY),
        (setupdir + '/.gitignore', DOT_GITIGNORE),
        (setupdir + '/ckanext/__init__.py', NAMESPACE_PACKAGE),
        (extdir + '/__init__.py', ''),
        (extdir + '/plugins.py', PLUGINS_PY),
        (templatedir + '/home/snippets/promoted.html', PROMOTED_SNIPPET),
        (templatedir + '/footer.html', FOOTER_HTML),
        ]

    for filename, content in filecontents:
        with open(filename, 'w') as f:
            f.write(content.replace('##name##', name))

NAMESPACE_PACKAGE = '''# this is a namespace package
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)
'''

SETUP_PY = '''#!/usr/bin/env/python
from setuptools import setup

setup(
    name='ckanext-##name##theme',
    version='0.1',
    description='',
    license='AGPL3',
    author='',
    author_email='',
    url='',
    namespace_packages=['ckanext'],
    packages=['ckanext.##name##theme'],
    zip_safe=False,
    entry_points = """
        [ckan.plugins]
        ##name##_theme = ckanext.##name##theme.plugins:CustomTheme
    """
)
'''

PLUGINS_PY = '''
from ckan.plugins import toolkit, IConfigurer, SingletonPlugin, implements

class CustomTheme(SingletonPlugin):
    implements(IConfigurer)

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "static")
'''

DOT_GITIGNORE = '''
*.pyc
ckanext_##name##theme.egg-info/*
build/*
dist/*
'''

PROMOTED_SNIPPET = '''{% set intro = g.site_intro_text %}

<div class="module-content box">
  <header>
    {% if intro %}
      {{ h.render_markdown(intro) }}
    {% else %}
      <h1 class="page-heading">{{ _("New DataCats Environment") }}</h1>
      <p>
        {% trans %}
        Welcome to your new data catalog!
        <a href="/user/login">Log in</a> with the
        "admin" account password you created, then create a
        <a href="/dataset/new">new dataset</a> or a
        <a href="/organization/new">new organization</a>.
        {% endtrans %}
      </p>
      <p>
        {% trans %}
        Customize this site by editing the site configuration,
        templates and static files in your environment directory
        then reload your changes with: <code>datacats reload</code>
        {% endtrans %}
      </p>
    {% endif %}
  </header>

  {% block home_image %}
    <section class="featured media-overlay hidden-phone">
      <h2 class="media-heading">{% block home_image_caption %}{{ _("Feature \
datasets here") }}{% endblock %}</h2>
      {% block home_image_content %}
        <a class="media-image" href="#">
          <img src="{{ h.url_for_static('/datacats/chart.png') }}" \
alt="Example chart" width="420" height="220" />
        </a>
      {% endblock %}
    </section>
  {% endblock %}
</div>
'''

FOOTER_HTML = '''{% ckan_extends %}

{% block footer_attribution %}
  <!-- FIXME: I can't even CSS -->
  <style>
    .ckan-footer-logo {margin: 2px 0 0 120px}
    .datacats-footer-logo {margin: -43px 0 0 0}
  </style>
  <p>{% trans %}<strong>Powered by</strong> <a class="hide-text ckan-footer-logo"\
href="http://ckan.org">CKAN</a>{% endtrans %}
  <img class="datacats-footer-logo" src="{{ \
h.url_for_static('/datacats/datacats-footer.png') }}"/></p>
{% endblock %}
'''
