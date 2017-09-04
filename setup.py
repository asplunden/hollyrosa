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
        "TurboGears2 >= 2.3.8",
        #can be removed iif use_toscawidgets = False
        "toscawidgets >= 0.9.7.1",
        "zope.sqlalchemy >= 0.4 ",
        "repoze.who",
        #"repoze.what",
        "tw.dynforms >= 0.9.8",
        "tw2.tinymce",
        "couchdb >= 1.0.0",
        "webhelpers >= 1.3"
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
