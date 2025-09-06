import { NextRequest, NextResponse } from 'next/server';

const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;
const REDIRECT_URI = process.env.NEXTAUTH_URL + '/api/auth/google/callback';

interface GoogleTokenResponse {
  access_token: string;
  refresh_token?: string;
  expires_in: number;
  token_type: string;
  scope: string;
}

interface GoogleUserInfo {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

export async function GET(request: NextRequest) {
  const requestId = Math.random().toString(36).substring(7);
  const { searchParams } = new URL(request.url);
  
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  const error = searchParams.get('error');

  console.log(`[${requestId}] Google OAuth callback received`);

  // Handle OAuth error
  if (error) {
    console.error(`[${requestId}] OAuth error: ${error}`);
    return NextResponse.redirect(
      new URL(`/setup?error=oauth_error&message=${encodeURIComponent(error)}`, request.url)
    );
  }

  // Validate required parameters
  if (!code || !state) {
    console.error(`[${requestId}] Missing code or state parameter`);
    return NextResponse.redirect(
      new URL('/setup?error=invalid_request', request.url)
    );
  }

  try {
    // Parse state parameter
    const stateData = JSON.parse(state);
    const { instanceName } = stateData;

    console.log(`[${requestId}] Processing OAuth for instance: ${instanceName}`);

    // Exchange code for tokens
    const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        client_id: GOOGLE_CLIENT_ID!,
        client_secret: GOOGLE_CLIENT_SECRET!,
        code: code,
        grant_type: 'authorization_code',
        redirect_uri: REDIRECT_URI,
      }),
    });

    if (!tokenResponse.ok) {
      const errorData = await tokenResponse.text();
      console.error(`[${requestId}] Token exchange failed:`, errorData);
      throw new Error('Failed to exchange code for tokens');
    }

    const tokens: GoogleTokenResponse = await tokenResponse.json();
    console.log(`[${requestId}] Tokens received successfully`);

    // Get user information
    const userResponse = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
      },
    });

    if (!userResponse.ok) {
      throw new Error('Failed to get user information');
    }

    const userInfo: GoogleUserInfo = await userResponse.json();
    console.log(`[${requestId}] User info retrieved for: ${userInfo.email}`);

    // Store tokens and user info (in a real app, you'd store this in a database)
    // For now, we'll store in memory or pass via URL params
    const userData = {
      instanceName,
      user: {
        id: userInfo.id,
        email: userInfo.email,
        name: userInfo.name,
        picture: userInfo.picture
      },
      tokens: {
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
        expires_in: tokens.expires_in,
        expires_at: Date.now() + (tokens.expires_in * 1000)
      },
      calendar_connected: true
    };

    // TODO: Store userData in database or session
    console.log(`[${requestId}] Calendar connected successfully for ${userInfo.email}`);

    // Redirect back to setup with success
    const redirectUrl = new URL('/setup', request.url);
    redirectUrl.searchParams.set('instance', instanceName);
    redirectUrl.searchParams.set('step', 'agent');
    redirectUrl.searchParams.set('calendar_success', 'true');
    redirectUrl.searchParams.set('user_email', userInfo.email);
    redirectUrl.searchParams.set('user_name', userInfo.name);

    return NextResponse.redirect(redirectUrl);

  } catch (error) {
    console.error(`[${requestId}] OAuth callback error:`, error);
    
    // Redirect with error
    const errorUrl = new URL('/setup', request.url);
    errorUrl.searchParams.set('error', 'oauth_failed');
    errorUrl.searchParams.set('message', error instanceof Error ? error.message : 'Unknown error');
    
    return NextResponse.redirect(errorUrl);
  }
}