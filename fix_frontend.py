with open("c:/JobAgent/frontend.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("unsafe_allowed_html", "unsafe_allow_html")

with open("c:/JobAgent/frontend.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Frontend file fixed successfully.")
