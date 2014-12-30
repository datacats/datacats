from os import makedirs

def ckan_extension_template(name, target_src):
    """
    Create ckanext-(name) in target_src directory.
    """
    setupdir = '{0}/ckanext-{1}'.format(target_src, name)
    extdir = setupdir + '/ckanext/{0}'.format(name)
    templatedir = extdir + '/templates/'
    staticdir = extdir + '/static/datacats'

    makedirs(templatedir + '/home/snippets')
    makedirs(staticdir)

    filecontents = [
        (setupdir + '/setup.py', SETUP_PY),
        (setupdir + '/.gitignore', DOT_GITIGNORE),
        (setupdir + '/ckanext/__init__.py', NAMESPACE_PACKAGE),
        (extdir + '/__init__.py', ''),
        (templatedir + '/home/snippets/promoted.html', PROMOTED_SNIPPET),
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
    name='ckanext-##name##',
    version='0.1',
    description='',
    license='AGPL3',
    author='',
    author_email='',
    url='',
    namespace_packages=['ckanext'],
    packages=['ckanext.##name##'],
    zip_safe=False,
    entry_points = """
        [ckan.plugins]
        ##name##_skin = ckanext.##name##.plugins:CustomSkin
    """
)
'''

DOT_GITIGNORE = '''
*.pyc
ckanext_##name##.egg-info/*
build/*
dist/*
'''

PROMOTED_SNIPPET = '''{% set intro = g.site_intro_text %}

<div class="module-content box">
  <header>
    {% if intro %}
      {{ h.render_markdown(intro) }}
    {% else %}
      <h1 class="page-heading">{{ _("New Data Catalog") }}</h1>
      <p>
        {% trans %}
        Welcome to your new data catalog! To get started
        <a href="/user/login">log in</a> with the
        <code>admin</code> account password you created. Then create a
        <a href="/dataset/new">new dataset</a> or a
        <a href="/organization/new">new organization</a>.
        To reset your admin password run the command:
        {% endtrans %}
        <code>datacats admin</code>
      </p>
      <p>
        {% trans %}
        Your site configuration may be edited in the project
        directory you created: <code>conf/ckan.ini</code>.
        Edit this file then restart your site with
        the command: <code>datacats restart</code>
        {% endtrans %}
      </p>
      <p>
        {% trans %}
        This site has been customized by a new CKAN extension
        created for you: <code>ckanext-##name##custom</code>.
        This extension redefines some HTML templates and adds
        static image files. Edit these files and add your own
        to the directories:
        <code>src/ckanext-##name##custom/ckanext/##name##/templates</code>
        and <code>src/ckanext-##name##custom/ckanext/##name##/static</code>
        then reload your changes with: <code>datacats reload</code>
        {% endtrans %}
      </p>
    {% endif %}
  </header>

  {% block home_image %}
    <section class="featured media-overlay hidden-phone">
      <h2 class="media-heading">{% block home_image_caption %}{{ _("This is a featured section") }}{% endblock %}</h2>
      {% block home_image_content %}
        <a class="media-image" href="#">
          <img src="{{ h.url_for_static('/datacats/images/chart.png') }}" alt="Example chart" width="420" height="220" />
        </a>
      {% endblock %}
    </section>
  {% endblock %}
</div>
'''

