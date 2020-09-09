from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

try:
    setup(
        #setup_requires=['setuptools-git-version'],
        name='sack',
        version='1.0',
        #version_format='{tag}.{commitcount}+{gitsha}',
        description='The only tool a Developer could ever Need',
        long_description=readme(),
        url='https://github.com/Willowlark/SwissArmyCodersKnife.git',
        author='William R Clark',
        author_email='clark.wrc@outlook.com',
        license='MIT',
        packages=['sack'],
        install_requires=[
            'pandas'
        ],
        package_data={
			'py_base': ['config/*.json']
		},
        #data_files = [
        #    ('config', ['config/credentials.json', 'config/variables.json'])
        #],
        zip_safe=False)
finally:
    print('complete')
