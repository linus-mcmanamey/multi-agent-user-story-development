from pathlib import Path
from setuptools import setup, find_packages

readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        install_requires = [req.split(">=")[0] + ">=" + req.split(">=")[1] if ">=" in req else req for req in install_requires if not req.startswith("pytest") and not req.startswith("ruff") and not req.startswith("black") and not req.startswith("mypy")]
else:
    install_requires = [
        "anthropic>=0.7.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "loguru>=0.7.0",
        "azure-devops>=7.0.0",
        "azure-identity>=1.13.0",
        "azure-storage-blob>=12.17.0",
        "azure-keyvault-secrets>=4.7.0",
        "mcp>=0.1.0",
    ]

setup(
    name="multi-agent-user-story-development",
    version="1.0.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        "multi_agent_user_story_development": [
            "templates/*.md",
            "prompts/*.py",
            "py.typed",
        ]
    },
    include_package_data=True,
    python_requires=">=3.10",
    author="Program Unify",
    author_email="unify@emstas.com",
    description="Claude Code plugin for multi-agent ETL development from user stories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emstas/multi-agent-user-story-development",
    project_urls={
        "Bug Reports": "https://github.com/emstas/multi-agent-user-story-development/issues",
        "Source": "https://github.com/emstas/multi-agent-user-story-development",
        "Documentation": "https://github.com/emstas/multi-agent-user-story-development/blob/main/README.md",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    keywords="claude pyspark etl azure devops multi-agent orchestration user-stories",
)
