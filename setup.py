import os
from setuptools import setup

from pkg_resources import parse_requirements

package_name = 'bloc'

dir_script = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(dir_script, package_name, 'version.py'), 'r') as f:
    exec(f.read(), about)


def load_requirements(file: str):
    requirements = []
    with open(file, 'r') as fb:
        for req in parse_requirements(fb.read()):
            requirements.append(str(req))
    return requirements


setup(
    name=about['title'],
    version=about['version'],
    description=about['description'],
    url=about['url'],
    packages=[package_name],
    author=about['author'],
    author_email=about['author_email'],
    include_package_data=True,
    python_requires='==3.8.*',
    install_requires=load_requirements('requirements.txt'),
    project_urls={
            'Documentation':  about['doc'],
            'Source': about['url'],
    }
)