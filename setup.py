#!/usr/bin/env python3
"""
Zhihu Publisher - 知乎文章自动发布工具
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="zhihu-publisher",
    version="2.0.0",
    author="delankesita",
    author_email="",
    description="知乎文章自动发布工具 - 一键发布文章到知乎专栏",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/delankesita/zhihu-publisher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "pillow>=9.0.0",
    ],
    extras_require={
        "yaml": ["pyyaml>=6.0"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "flake8>=6.0.0"],
    },
    entry_points={
        "console_scripts": [
            "zhihu-publisher=zhihu_publisher.cli:main",
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/delankesita/zhihu-publisher/issues",
        "Documentation": "https://github.com/delankesita/zhihu-publisher#readme",
        "Source Code": "https://github.com/delankesita/zhihu-publisher",
    },
)
