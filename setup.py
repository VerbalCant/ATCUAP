from setuptools import setup, find_packages

setup(
    name="ufo-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "python-dotenv",
        "tqdm",
    ],
    entry_points={
        'console_scripts': [
            'ufo-analyzer=ufo_analyzer:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to analyze audio files for UFO/UAP phenomena mentions",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    keywords="ufo, uap, audio analysis, transcription",
    url="https://github.com/yourusername/ufo-analyzer",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
) 