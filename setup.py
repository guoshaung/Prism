"""Setup script for innersafe-mas.

A privacy & copyright governance middleware for LLM Multi-Agent Systems.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="innersafe-mas",
    version="0.1.0",
    author="InnerSafe Contributors",
    author_email="opensource@innersafe.ai",
    description=(
        "An endogenous security governance framework for LLM Multi-Agent "
        "Systems: client-side privacy protection + cloud-side copyright "
        "watermarking + open game-theoretic routing."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/innersafe-mas",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Intentionally minimal. Heavy deps (torch, networkx) are optional.
    ],
    extras_require={
        "dev": ["pytest>=7.0", "pytest-cov", "black", "mypy", "ruff"],
        "graph": ["networkx>=2.8"],
    },
    keywords=[
        "LLM", "multi-agent", "privacy", "watermark",
        "information-bottleneck", "AI-safety", "governance",
    ],
)
