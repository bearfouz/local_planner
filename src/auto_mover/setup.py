from setuptools import find_packages, setup

package_name = 'auto_mover'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/auto_mover']),
        ('share/auto_mover', ['package.xml']),
        ('share/auto_mover/config', ['config/all.yaml'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bearfouz',
    maintainer_email='you@example.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        	'pre_auto = auto_mover.pre_auto:main',
        ],
    },
)
