# setup.py

from setuptools import find_packages, setup


setup(
    name="taskflow-manager",
    use_scm_version=True,

    setup_requires=["setuptools_scm"],

    description="CLI & servers for Taskflow (API, MCP & Web)",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "fastmcp",
        "click",
        # y cualquier otra dependencia que uses
    ],
    entry_points={
        "console_scripts": [
            "taskflow-manager=taskflow_manager.cli:cli",

    },
)
