#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# SocialHub — ngrok local OAuth setup helper
#
# Meta's OAuth requires a publicly accessible HTTPS redirect URI.
# During local development, ngrok tunnels localhost:8000 to a public URL.
#
# Prerequisites:
#   brew install ngrok/ngrok/ngrok
#   ngrok config add-authtoken <YOUR_AUTHTOKEN>   # free at ngrok.com
#
# Usage:
#   chmod +x scripts/ngrok-setup.sh
#   ./scripts/ngrok-setup.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

BACKEND_PORT=8000
ENV_FILE="backend/.env"

if ! command -v ngrok &>/dev/null; then
  echo "ERROR: ngrok not found. Install: brew install ngrok/ngrok/ngrok"
  exit 1
fi

echo ""
echo "Starting ngrok tunnel on port $BACKEND_PORT..."
ngrok http $BACKEND_PORT --log=stdout &
NGROK_PID=$!
sleep 3

# Extract the public HTTPS URL from the ngrok API
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels \
  | python3 -c "import sys,json; tunnels=json.load(sys.stdin)['tunnels']; \
    https=[t['public_url'] for t in tunnels if t['public_url'].startswith('https')]; \
    print(https[0] if https else '')" 2>/dev/null)

if [[ -z "$NGROK_URL" ]]; then
  echo "ERROR: Could not get ngrok URL. Is ngrok running?"
  kill $NGROK_PID 2>/dev/null
  exit 1
fi

REDIRECT_URI="${NGROK_URL}/api/v1/auth/meta/callback"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ngrok tunnel active                                         ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Public URL:   %-47s ║\n" "$NGROK_URL"
printf "║  Redirect URI: %-47s ║\n" "$REDIRECT_URI"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "  1. Go to https://developers.facebook.com → your app → Facebook Login → Settings"
echo "     Add this URI to 'Valid OAuth Redirect URIs':"
echo "       $REDIRECT_URI"
echo ""
echo "  2. Update backend/.env:"
echo "       META_REDIRECT_URI=$REDIRECT_URI"
echo "       ALLOWED_ORIGINS=http://localhost:3000"
echo ""
echo "  3. Restart the backend:"
echo "       docker compose -f docker-compose.dev.yml restart backend"
echo "     or if running locally:"
echo "       (kill existing uvicorn and rerun)"
echo ""
echo "  Tunnel stays active until you press Ctrl+C"
echo ""

# Optionally patch the .env file automatically
read -rp "Auto-update $ENV_FILE with the new META_REDIRECT_URI? [y/N] " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
  if [[ -f "$ENV_FILE" ]]; then
    # Replace or append META_REDIRECT_URI
    if grep -q "^META_REDIRECT_URI=" "$ENV_FILE"; then
      sed -i.bak "s|^META_REDIRECT_URI=.*|META_REDIRECT_URI=$REDIRECT_URI|" "$ENV_FILE"
    else
      echo "META_REDIRECT_URI=$REDIRECT_URI" >> "$ENV_FILE"
    fi
    echo "  ✓ Updated $ENV_FILE"
    echo "  Restart the backend to pick up the change."
  else
    echo "  $ENV_FILE not found — copy backend/.env.example first."
  fi
fi

echo ""
echo "Keeping tunnel alive. Ctrl+C to stop."
wait $NGROK_PID
