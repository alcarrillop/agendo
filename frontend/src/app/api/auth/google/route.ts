import { NextRequest, NextResponse } from 'next/server';

const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;
const REDIRECT_URI = process.env.NEXTAUTH_URL + '/api/auth/google/callback';

export async function GET(request: NextRequest) {
  const requestId = Math.random().toString(36).substring(7);
  const { searchParams } = new URL(request.url);
  const instanceName = searchParams.get('instance');

  console.log(`[${requestId}] Starting Google OAuth flow for instance: ${instanceName}`);

  if (!GOOGLE_CLIENT_ID || !GOOGLE_CLIENT_SECRET) {
    console.error(`[${requestId}] Google OAuth not configured`);
    return NextResponse.json(
      { error: 'Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.' },
      { status: 500 }
    );
  }

  if (!instanceName) {
    return NextResponse.json(
      { error: 'Instance name is required' },
      { status: 400 }
    );
  }

  try {
    // Google OAuth 2.0 authorization URL
    const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
    
    authUrl.searchParams.set('client_id', GOOGLE_CLIENT_ID);
    authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('scope', [
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/userinfo.email',
      'https://www.googleapis.com/auth/userinfo.profile'
    ].join(' '));
    authUrl.searchParams.set('access_type', 'offline');
    authUrl.searchParams.set('prompt', 'consent');
    
    // Store instance name in state parameter for callback
    authUrl.searchParams.set('state', JSON.stringify({ 
      instanceName,
      requestId 
    }));

    console.log(`[${requestId}] Generated OAuth URL for instance: ${instanceName}`);

    return NextResponse.json({
      success: true,
      authUrl: authUrl.toString(),
      requestId
    });

  } catch (error) {
    console.error(`[${requestId}] Error generating OAuth URL:`, error);
    return NextResponse.json(
      { error: 'Failed to generate authorization URL', requestId },
      { status: 500 }
    );
  }
}