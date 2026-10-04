import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
import streamlit as st
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py").run()
dl_buttons = at.download_button
print("Found download buttons:", len(dl_buttons))
for btn in dl_buttons:
    print("Label:", btn.proto.label.encode('ascii', 'replace').decode('ascii'))
    print("URL:", repr(btn.proto.url))
    print("Disabled:", btn.proto.disabled)
