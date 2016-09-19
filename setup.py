import os
import versioneer

from setuptools import setup, find_packages



def readme():
    path = os.path.join(os.path.dirname(__file__), 'readme.rst')
    return open(path).read()


setup(name='deparse',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      packages=find_packages(exclude=["tests", ".tox"]),

      description=(
          'Declarative approach to parsing text documents using regular'
          ' expressions.'
      ),
      long_description=readme(),
      author='Aistis Jokubauskas',
      url='http://github.com/aisbaa/deparse',
      license='MIT',

      classifiers=(
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing'
      ),
)
