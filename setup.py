# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='hollyrosa',
    version='0.1',
    description='',
    author='Martin Eliasson',
    author_email='asplunden@gmail.com',
    url='http://github.com/asplunden/hollyrosa',
    install_requires=[
        "TurboGears2 >= 2.3.11",
        # can be removed if use_toscawidgets = False
        "tw2.forms",
        "zope.sqlalchemy >= 0.4 ",
        "repoze.who",
        "tw2.dynforms >= 2.0.1",
        "couchdb >= 1.0.0",
        "webhelpers >= 1.3",
        "bleach >= 2.0",
        "kajiki >= 0.7.1",
        "webob >= 1.7.0",
        "Paste",
        "formencode"
    ],
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    package_data={'hollyrosa': ['i18n/*/LC_MESSAGES/*.mo',
                                'templates/*/*',
                                'public/*/*']},
    message_extractors={'hollyrosa': [
        ('**.py', 'python', None),
        ('templates/**.mako', 'mako', None),
        ('templates/**.html', 'genshi', None),
        ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = hollyrosa.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
