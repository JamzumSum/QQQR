from setuptools import find_packages, setup

NAME = 'TencentLogin'
LOWERCASE = NAME.lower()

setup(
    name=NAME,
    version='2.3.0b4',
    description='A simulation of tencent login protocol',
    author='JamzumSum',
    author_email='zzzzss990315@gmail.com',
    url='https://github.com/JamzumSum/QQQR',
    license="AGPL-3.0",
    python_requires=">=3.8",  # for f-string and := op
    install_requires=['requests', 'apscheduler'],
    extras_require={
        'captcha': ['opencv-python'],  # Formal release will require opencv in all time.
    },
    packages=find_packages(where='src'),
    package_dir={"": 'src'},
    include_package_data=True,
)
