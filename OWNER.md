# OWNER.md — How SocialHub Works (Plain English)

This is your personal guide. No tech jargon. Just what happens when you use this app.

---

## The Big Picture

Think of SocialHub as your **personal posting assistant**.

You hand it a video and a caption. It logs into your Instagram and Facebook accounts and posts it for you — while you go do something else.

---

## What Happens When You Post a Video

### Step 1 — You Upload
You go to the dashboard, pick a video file from your computer, write your caption, choose Instagram or Facebook (or both), and hit **Publish**.

### Step 2 — The App Stores Your Video
Your video gets saved on the server (inside a folder called `/media`). Think of it like a holding area.

### Step 3 — Instagram Posting (two-step process)

**Real-life analogy:** It's like submitting a YouTube video. First it uploads, then it processes, then it goes live.

1. **Upload the video** — The app sends your video URL to Instagram and says "hey, get ready to post this." Instagram calls this a "container." It's like a draft.
2. **Wait for Instagram to process** — Instagram takes 10–30 seconds to process the video (checking resolution, format, etc.). The app keeps checking every 3 seconds.
3. **Publish** — Once Instagram says it's ready, the app presses the final "Publish" button via the API. Your Reel goes live.
4. **Save the result** — The app saves the post ID (the link to your post) and marks the job as **published** ✅

If anything goes wrong, it marks it as **failed** ❌ and saves the error message so you know what happened.

### Step 4 — Facebook Posting (one-step process)

**Real-life analogy:** It's like emailing a video attachment directly. No draft step.

1. The app uploads the video file directly to your Facebook Page in one go.
2. Facebook publishes it immediately.
3. The app saves the post ID and marks it as **published** ✅

### Step 5 — You See the Result
Back in the dashboard, your post shows up with:
- Status: Published ✅ or Failed ❌
- The date/time it was posted
- A link to the post (the platform post ID)

---

## The Tokens (Why They Matter)

Your tokens are like **saved passwords** — but smarter and safer.

| Token | What it does | Expires |
|-------|-------------|---------|
| User Access Token | Proves you are you to Meta's servers | 60 days |
| Page Access Token | Lets the app post to your Facebook Page | Never (while user token is valid) |

**Real-life analogy:** The User Access Token is like a hotel key card. It works for 60 days. After that you need a new one. But the Page token is like a master key for your office — it stays valid as long as you have the hotel key.

When the token gets close to expiry (within 10 days), the app automatically renews it on startup.

---

## Your Accounts

| Platform | Account | ID |
|----------|---------|-----|
| Instagram | Kay Singh | `17841403379195979` |
| Facebook | Kay Singh (Page) | `114241926640777` |

---

## The Database (What Gets Saved)

Every action is recorded. Here's what lives in the database:

| Table | What's in it | Example |
|-------|-------------|---------|
| `devices` | A group for your accounts | "My Accounts" |
| `social_accounts` | Your IG and FB accounts + encrypted tokens | instagram: @kay_singh |
| `uploads` | Every video you've uploaded | "dance_video.mp4", status: ready |
| `posts` | One row per video × platform | Upload #5 → Instagram: published ✅ |
| `activity_logs` | Every event that ever happened | "2026-06-08: Reel published to @kay_singh" |

---

## What Could Go Wrong & What It Means

| Error | Plain English | What to do |
|-------|--------------|------------|
| `OAuthException code 190` | Your token expired | Go to secrets.md and regenerate a token |
| `Container status: ERROR` | Instagram rejected the video | Check video format (MP4, H.264, max 500MB) |
| `Container status: TIMEOUT` | Instagram took too long | Try again, usually a temporary glitch |
| `publish_video_to_page failed` | Facebook upload failed | Check your Page token is still valid |

---

## Token Renewal (Do This Every ~50 Days)

1. Go to `developers.facebook.com` → Tools → Graph API Explorer
2. Select the **Desi-HipHop** app
3. Get a new User Access Token with all 5 permissions
4. Paste the new token and I'll exchange it for a long-lived one automatically

Or run the auto-refresh endpoint:
```
POST http://localhost:8000/api/v1/accounts/{account_id}/refresh-token
```

---

## Quick Reference — API Endpoints

| What you want | Endpoint |
|--------------|----------|
| Check account status | `GET /api/v1/admin/status` |
| Re-seed accounts after token renewal | `POST /api/v1/admin/seed-accounts` |
| Upload a video | `POST /api/v1/uploads` |
| Publish to platforms | `POST /api/v1/posts/publish` |
| See all posts | `GET /api/v1/posts` |
| See activity log | `GET /api/v1/activity-logs` |
