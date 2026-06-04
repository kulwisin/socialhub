# Local OAuth Setup — Instagram & Facebook

Meta's OAuth requires a publicly accessible HTTPS redirect URI. When developing locally, you need ngrok to expose your backend.

---

## One-time setup

### 1. Install ngrok
```bash
brew install ngrok/ngrok/ngrok
```
Sign up free at [ngrok.com](https://ngrok.com) and run:
```bash
ngrok config add-authtoken <YOUR_AUTHTOKEN>
```

### 2. Create a Meta App
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. **My Apps → Create App → Business**
3. Add products: **Facebook Login** + **Instagram Graph API**
4. Under **Facebook Login → Settings**, add to *Valid OAuth Redirect URIs*:
   ```
   https://<your-ngrok-id>.ngrok.io/api/v1/auth/meta/callback
   ```
   *(You'll get this URL in step 3 below)*

### 3. Start the tunnel
```bash
./scripts/ngrok-setup.sh
```
The script starts ngrok, prints the public URL, and can auto-update `backend/.env`.

---

## Required Meta App Permissions

Request these in **App Review → Permissions and Features**:

| Permission | Why |
|---|---|
| `instagram_basic` | Read profile, follower count, media count |
| `instagram_content_publish` | Post reels and images |
| `pages_show_list` | List the user's Facebook Pages |
| `pages_read_engagement` | Read Page-level insights |
| `business_management` | Required for Instagram Business accounts |
| `public_profile` | Basic user info |

> **Note:** For development, you can test with your own accounts without going through App Review. App Review is only needed to go live with other users.

---

## Environment variables

`backend/.env`:
```env
META_APP_ID=<your-app-id>
META_APP_SECRET=<your-app-secret>
META_REDIRECT_URI=https://<ngrok-id>.ngrok.io/api/v1/auth/meta/callback
META_GRAPH_API_VERSION=v21.0
```

`frontend/.env.local`:
```env
NEXT_PUBLIC_META_APP_ID=<your-app-id>   # same as META_APP_ID
```

---

## Publishing videos locally

Instagram downloads your video from a public URL. When running locally, the backend serves media at:
```
https://<ngrok-id>.ngrok.io/media/<your-file-path>
```

The backend constructs this URL automatically from `META_REDIRECT_URI`. Make sure the ngrok tunnel is running when you click **Publish**.

---

## Full local development flow

```
Terminal 1: ./scripts/ngrok-setup.sh    ← keeps tunnel alive
Terminal 2: make dev                    ← starts postgres + backend + frontend
Terminal 3: make migrate                ← first time only
```

Then open [http://localhost:3000](http://localhost:3000).

---

## Instagram account requirements

Your Instagram account **must** be a **Business** or **Creator** account and must be **connected to a Facebook Page**.

To convert:
1. Instagram app → Profile → Settings → Account → Switch to Professional Account
2. Choose **Business**
3. Connect to a Facebook Page (create one if you don't have one)

After connecting via SocialHub OAuth, the platform will automatically detect the Instagram Business Account linked to your Page.

---

## Token lifetimes

| Token type | Lifetime | Auto-refresh |
|---|---|---|
| Short-lived user token | 1 hour | Exchanged immediately after OAuth |
| Long-lived user token | 60 days | Manual via **Refresh token** button, or auto on startup |
| Page access token | Never expires* | Extended during OAuth |

*After the `fb_exchange_token` grant.

SocialHub refreshes expiring Instagram tokens automatically on startup. You can also trigger a manual refresh from the device detail page using the **Refresh token** button on any Instagram account card.
