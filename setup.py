import os

from setuptools import setup, find_packages

version = '1.0'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = (
    read('README.md')
    + '\n' +
    read('CHANGES.md')
    + '\n')

setup(name='ims.fieldupdater',
      version=version,
      long_description=long_description,
      description="Update all objects in Plone based on a schema/field strategy",
      classifiers=[
          "Framework :: Plone :: 5.0",
          "Framework :: Plone :: 5.1",
          "Programming Language :: Python",
      ],
      keywords='',
      author='Eric Wohnlich',
      author_email='wohnlice@imsweb.com',
      url='https://github.com/imsweb/ims.fieldupdater',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ims'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.api',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      extras_require={
          'test': ['plone.app.testing', 'plone.mocktestcase', 'formencode'],
      },
      )
