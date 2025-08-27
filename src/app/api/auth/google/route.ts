import { NextRequest, NextResponse } from 'next/server';
import { google } from 'googleapis';

const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/google/callback`
);

// Scopes necesarios para Google Calendar
const SCOPES = [
  'https://www.googleapis.com/auth/calendar.readonly',
  'https://www.googleapis.com/auth/calendar.events',
  'https://www.googleapis.com/auth/userinfo.email',
  'https://www.googleapis.com/auth/userinfo.profile'
];

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const instance = searchParams.get('instance');
  
  if (!instance) {
    return NextResponse.json(
      { error: 'Instance parameter required' },
      { status: 400 }
    );
  }

  try {
    // Generar URL de autorización
    const authUrl = oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: SCOPES,
      state: instance, // Pasamos la instancia como state
      prompt: 'consent' // Fuerza pantalla de consentimiento
    });

    console.log(`[Google Auth] Generated auth URL for instance: ${instance}`);

    return NextResponse.json({
      success: true,
      authUrl,
      message: 'Redirect user to this URL for authorization'
    });

  } catch (error) {
    console.error('[Google Auth] Error generating auth URL:', error);
    return NextResponse.json(
      { error: 'Failed to generate authorization URL' },
      { status: 500 }
    );
  }
}
