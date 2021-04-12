from setuptools import find_packages
from setuptools import setup

setup(
    name='deploy_service',
    version='0.0.1',
    description="Simple deploy application",
    author='vkutas',
    packages=['deploy_service'],
    install_requires=['Flask', 'docker'],
    include_package_data=True,
    keywords=[
        'cd', 'flask', 'docker'
    ],
    entry_points={
        'console_scripts': [
            'deploy-service = deploy_service.app:main']},
)