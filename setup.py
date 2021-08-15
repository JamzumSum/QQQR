from setuptools import find_packages, setup

NAME = 'TencentLogin'
LOWERCASE = NAME.lower()

setup(
    name=NAME,
    version='2.3.0.beta0',
    description='A simulation of tencent login protocol',
    author='JamzumSum',
    url='https://github.com/JamzumSum/QQQR',
    license="AGPL-3.0",
    python_requires=">=3.8",  # for f-string and := op
    install_requires=['requests'],
    extras_require={
        'captcha': ['opencv-python'],
    },
    packages=find_packages(where='src'),
    package_dir={"": 'src'},
)
