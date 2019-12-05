import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cbdia", # Replace with your own username
    version="0.0.1",
    author="Anguelos Nicolaou",
    author_email="anguelos.nicolaou@gmail.com",
    description="Infrastructure for mass retrieval Document Image Analysis system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anguelos/czeck_bavaria",
    packages=setuptools.find_packages(),
    scripts=['bin/register_book'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy','scikit-learn','opencv-python', 'pytorch', 'tqdm'
    ],
)