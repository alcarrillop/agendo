import { NextRequest, NextResponse } from 'next/server';
import { google } from 'googleapis';

const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/google/callback`
);

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');
  const state = searchParams.get('state'); // Esta es la instancia
  const error = searchParams.get('error');

  if (error) {
    console.error('[Google Auth] Authorization error:', error);
    return NextResponse.redirect(
      `${process.env.NEXT_PUBLIC_APP_URL}/setup?instance=${state}&google_error=${error}`
    );
  }

  if (!code || !state) {
    return NextResponse.json(
      { error: 'Missing authorization code or state' },
      { status: 400 }
    );
  }

  try {
    // Intercambiar código por tokens
    const { tokens } = await oauth2Client.getToken(code);
    oauth2Client.setCredentials(tokens);

    // Obtener información del usuario
    const oauth2 = google.oauth2({ version: 'v2', auth: oauth2Client });
    const userInfo = await oauth2.userinfo.get();

    // Probar acceso al calendario
    const calendar = google.calendar({ version: 'v3', auth: oauth2Client });
    const calendarList = await calendar.calendarList.list();

    console.log(`[Google Auth] Successfully authorized user: ${userInfo.data.email} for instance: ${state}`);
    console.log(`[Google Auth] Found ${calendarList.data.items?.length || 0} calendars`);

    // TODO: Aquí guardarías los tokens en la base de datos asociados a la instancia
    // Por ahora, simulamos que se guardó exitosamente
    
    // Simular guardado en "base de datos"
    const calendarConfig = {
      instance: state,
      userEmail: userInfo.data.email,
      userName: userInfo.data.name,
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      expiryDate: tokens.expiry_date,
      calendars: calendarList.data.items?.map(cal => ({
        id: cal.id,
        summary: cal.summary,
        primary: cal.primary
      })) || [],
      connectedAt: new Date().toISOString()
    };

    console.log('[Google Auth] Calendar configuration ready:', {
      instance: state,
      userEmail: userInfo.data.email,
      calendarsCount: calendarConfig.calendars.length
    });

    // Redireccionar de vuelta al setup con éxito
    return NextResponse.redirect(
      `${process.env.NEXT_PUBLIC_APP_URL}/setup?instance=${state}&google_success=true&email=${encodeURIComponent(userInfo.data.email || '')}`
    );

  } catch (error) {
    console.error('[Google Auth] Error during token exchange:', error);
    return NextResponse.redirect(
      `${process.env.NEXT_PUBLIC_APP_URL}/setup?instance=${state}&google_error=token_exchange_failed`
    );
  }
}
