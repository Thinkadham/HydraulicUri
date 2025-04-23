from setuptools import setup, find_packages

setup(
    name="HydraulicUri",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "supabase",
        "fpdf2",
        "num2words",
        "python-dotenv"
    ],
)
