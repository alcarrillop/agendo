import { NextRequest, NextResponse } from 'next/server';

const EVOLUTION_API_URL = process.env.EVOLUTION_API_URL;
const EVOLUTION_API_KEY = process.env.EVOLUTION_API_KEY;

if (!EVOLUTION_API_URL || !EVOLUTION_API_KEY) {
  throw new Error('Missing Evolution API configuration');
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ name: string }> }
) {
  const requestId = Math.random().toString(36).substring(7);
  const { name } = await params;

  console.log(`[${requestId}] Sending message via instance: ${name}`);

  try {
    const { to, text } = await request.json();

    if (!to || !text) {
      return NextResponse.json(
        { error: 'Missing required fields: to and text' },
        { status: 400 }
      );
    }

    // Clean phone number (remove spaces, dashes, etc.)
    const cleanNumber = to.replace(/\D/g, '');
    
    console.log(`[${requestId}] Sending to: ${cleanNumber}, text: "${text}"`);

    const response = await fetch(`${EVOLUTION_API_URL}/message/sendText/${name}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': EVOLUTION_API_KEY,
      },
      body: JSON.stringify({
        number: cleanNumber,
        text: text,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      console.error(`[${requestId}] Evolution API error:`, data);
      return NextResponse.json(
        { error: 'Failed to send message', details: data },
        { status: response.status }
      );
    }

    console.log(`[${requestId}] Message sent successfully:`, data);

    return NextResponse.json({
      success: true,
      requestId,
      messageId: data.messageId || data.id,
      data,
    });

  } catch (error) {
    console.error(`[${requestId}] Error sending message:`, error);
    return NextResponse.json(
      { error: 'Internal server error', requestId },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'Evolution API send message endpoint ready',
    timestamp: new Date().toISOString(),
    usage: 'POST with JSON body: { "to": "5511999999999", "text": "Hello from Agendo!" }'
  });
}
