from setuptools import setup, find_packages

setup(
    name="multi-agent-user-story-development",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.7.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "azure-devops>=7.0.0",
        "azure-identity>=1.13.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "ruff>=0.1.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
        "mcp": [
            "mcp>=0.1.0",
        ],
    },
    python_requires=">=3.10",
    author="Program Unify",
    author_email="unify@emstas.com",
    description="Claude Code plugin for multi-agent ETL development from user stories",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/emstas/multi-agent-user-story-development",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
