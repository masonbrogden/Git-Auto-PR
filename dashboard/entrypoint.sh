#!/bin/sh
cat > /usr/share/nginx/html/env-config.js << EOF
window.API_URL = "${API_URL:-http://localhost:8000}";
EOF
exec nginx -g "daemon off;"
