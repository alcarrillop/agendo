import { NextRequest, NextResponse } from 'next/server';
import { google } from 'googleapis';

// Simular función para obtener tokens guardados
async function getStoredTokens(instance: string) {
  // TODO: Obtener de base de datos real
  // Por ahora retornamos null para indicar que no hay tokens
  return null;
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const instance = searchParams.get('instance');
  const date = searchParams.get('date'); // YYYY-MM-DD
  
  if (!instance || !date) {
    return NextResponse.json(
      { error: 'Instance and date parameters required' },
      { status: 400 }
    );
  }

  try {
    // Obtener tokens almacenados
    const storedTokens = await getStoredTokens(instance);
    
    if (!storedTokens) {
      return NextResponse.json(
        { error: 'Google Calendar not connected for this instance' },
        { status: 401 }
      );
    }

    // Configurar cliente OAuth
    const oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/google/callback`
    );

    oauth2Client.setCredentials(storedTokens);

    // Crear cliente de Calendar
    const calendar = google.calendar({ version: 'v3', auth: oauth2Client });

    // Obtener eventos del día
    const startOfDay = new Date(`${date}T00:00:00.000Z`);
    const endOfDay = new Date(`${date}T23:59:59.999Z`);

    const events = await calendar.events.list({
      calendarId: 'primary',
      timeMin: startOfDay.toISOString(),
      timeMax: endOfDay.toISOString(),
      singleEvents: true,
      orderBy: 'startTime',
    });

    // Calcular disponibilidad
    const busySlots = events.data.items?.map(event => ({
      start: event.start?.dateTime || event.start?.date,
      end: event.end?.dateTime || event.end?.date,
      summary: event.summary
    })) || [];

    // Generar slots disponibles (ejemplo: cada hora de 9 AM a 6 PM)
    const availableSlots = [];
    for (let hour = 9; hour < 18; hour++) {
      const slotStart = new Date(`${date}T${hour.toString().padStart(2, '0')}:00:00`);
      const slotEnd = new Date(`${date}T${(hour + 1).toString().padStart(2, '0')}:00:00`);
      
      // Verificar si el slot está ocupado
      const isOccupied = busySlots.some(busy => {
        const busyStart = new Date(busy.start!);
        const busyEnd = new Date(busy.end!);
        return slotStart < busyEnd && slotEnd > busyStart;
      });

      if (!isOccupied) {
        availableSlots.push({
          start: slotStart.toISOString(),
          end: slotEnd.toISOString(),
          available: true
        });
      }
    }

    return NextResponse.json({
      success: true,
      date,
      busySlots,
      availableSlots,
      totalAvailable: availableSlots.length
    });

  } catch (error) {
    console.error('[Calendar] Error checking availability:', error);
    return NextResponse.json(
      { error: 'Failed to check calendar availability' },
      { status: 500 }
    );
  }
}
