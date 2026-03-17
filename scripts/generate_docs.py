import json

with open("openapi.json", "r") as f:
    spec = f.read()

html = f"""<!DOCTYPE html>
<html>
<head>
    <title>UK Housing Affordability API - Documentation</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ margin: 0; padding: 0; }}
    </style>
</head>
<body>
    <div id="redoc-container"></div>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
    <script>
        const spec = {spec};
        Redoc.init(spec, {{
            scrollYOffset: 50
        }}, document.getElementById('redoc-container'));
    </script>
</body>
</html>
"""

with open("docs/api_docs.html", "w") as f:
    f.write(html)
