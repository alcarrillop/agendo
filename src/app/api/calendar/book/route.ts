import { NextRequest, NextResponse } from 'next/server';
import { google } from 'googleapis';

// Simular función para obtener tokens guardados
async function getStoredTokens(instance: string) {
  // TODO: Obtener de base de datos real
  return null;
}

export async function POST(request: NextRequest) {
  const requestId = Math.random().toString(36).substring(7);
  console.log(`[${requestId}] Calendar booking request received`);

  try {
    const body = await request.json();
    const { instance, title, description, startTime, endTime, customerEmail, customerName } = body;

    if (!instance || !title || !startTime || !endTime) {
      return NextResponse.json(
        { error: 'Missing required fields: instance, title, startTime, endTime' },
        { status: 400 }
      );
    }

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

    // Crear evento
    const event = {
      summary: title,
      description: description || `Cita agendada por Agendo\n\nCliente: ${customerName || 'No especificado'}\nEmail: ${customerEmail || 'No especificado'}`,
      start: {
        dateTime: startTime,
        timeZone: 'America/Bogota', // Ajustar según configuración
      },
      end: {
        dateTime: endTime,
        timeZone: 'America/Bogota',
      },
      attendees: customerEmail ? [{ email: customerEmail }] : [],
      reminders: {
        useDefault: false,
        overrides: [
          { method: 'email', minutes: 24 * 60 }, // 1 día antes
          { method: 'popup', minutes: 30 }, // 30 minutos antes
        ],
      },
    };

    const createdEvent = await calendar.events.insert({
      calendarId: 'primary',
      requestBody: event,
      sendUpdates: 'all', // Enviar invitaciones por email
    });

    console.log(`[${requestId}] Event created successfully:`, createdEvent.data.id);

    return NextResponse.json({
      success: true,
      requestId,
      eventId: createdEvent.data.id,
      eventUrl: createdEvent.data.htmlLink,
      event: {
        id: createdEvent.data.id,
        title: createdEvent.data.summary,
        start: createdEvent.data.start?.dateTime,
        end: createdEvent.data.end?.dateTime,
        description: createdEvent.data.description,
      }
    });

  } catch (error) {
    console.error(`[${requestId}] Error creating calendar event:`, error);
    
    // Manejar errores específicos de Google Calendar
    if (error && typeof error === 'object' && 'code' in error) {
      const googleError = error as any;
      return NextResponse.json(
        { 
          error: `Google Calendar error: ${googleError.message}`, 
          code: googleError.code,
          requestId 
        }, 
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to create calendar event', requestId },
      { status: 500 }
    );
  }
}
