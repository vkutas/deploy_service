import setuptools

setuptools.setup(
    name='deploy_service',
    version='0.0.1',
    description="Simple deploy application",
    author='vkutas',
    packages=setuptools.find_packages(),
    install_requires=['Flask', 'docker', 'flask-expects-json'],
    include_package_data=True,
    keywords=[
        'cd', 'flask', 'docker'
    ],
    entry_points={
        'console_scripts': [
            'deploy-service = deploy_service.app:main']},
)