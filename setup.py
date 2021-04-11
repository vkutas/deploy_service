from setuptools import find_packages
from setuptools import setup

setup(
    name='deploy_service',
    version='0.0.1',
    description="Training with GitHub Actions",
    author='dementevda',
    packages=['deploy_service'],
    install_requires=['Flask', 'docker'],
    include_package_data=True,
    keywords=[
        'ci', 'github actions', 'flask', 'docker'
    ],
    entry_points={
        'console_scripts': [
            'ci_example = deploy_service.app:main']},
)