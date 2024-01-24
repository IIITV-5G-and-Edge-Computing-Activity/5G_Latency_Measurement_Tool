from setuptools import setup, find_packages

setup(
    name="experiments5G",
    version="1.0.0",
    author="Christoph Tittel, Justus Bracke (DFKI)",
    author_email="justus.bracke@dfki.de",
    description="Latency Experiments for 5G-Agrar.",
    packages=find_packages(),
    install_requires=['numpy>=1.22.2',
                      'tornado>=6.1',
                      'pydantic>=1.9.0',
                      'pandas>=1.4.1',
                      'grpcio==1.44.0',
                      'grpcio-tools==1.44.0',
                      'pyzmq>=22.3.0',
                      'protobuf==3.19.4',
                      'requests>=2.27.1',
                      'argparse>=1.4.0',
                      'humanfriendly>=10.0',
                      'streamlit>=1.6.0',
                      'streamlit_folium>=0.6.2',
                      'branca>=0.4.2',
                      'mqttools>=0.50.0',
                      'getkey>=0.6.5',
                      ],
    extras_require={
    },
    scripts=[
        'scripts/experiments5G_client',
        'scripts/experiments5G_server',
        'scripts/experiments5G_eval']
)
