import os
import requests

# We can query the active streamlit session or inspect the running server
s = requests.Session()
r = s.get("http://localhost:8501")
print("Streamlit index status:", r.status_code)
