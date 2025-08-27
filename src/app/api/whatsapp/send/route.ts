import { NextRequest, NextResponse } from 'next/server';
import { Twilio } from 'twilio';

// Initialize Twilio client
const client = new Twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

export async function POST(request: NextRequest) {
  const requestId = Math.random().toString(36).substring(7);
  console.log(`[${requestId}] Send message request received`);

  try {
    // Parse JSON body
    const { to, body } = await request.json();
    
    console.log(`[${requestId}] Sending message to: ${to}, body: "${body}"`);

    // Validate required fields
    if (!to || !body) {
      console.log(`[${requestId}] Missing required fields: to=${to}, body=${body}`);
      return NextResponse.json(
        { error: 'Missing required fields: to and body are required' }, 
        { status: 400 }
      );
    }

    // Validate environment variables
    if (!process.env.TWILIO_WHATSAPP_FROM) {
      console.log(`[${requestId}] Missing TWILIO_WHATSAPP_FROM environment variable`);
      return NextResponse.json(
        { error: 'Server configuration error: missing WhatsApp sender number' }, 
        { status: 500 }
      );
    }

    // Format the 'to' number (ensure it has whatsapp: prefix)
    const formattedTo = to.startsWith('whatsapp:') ? to : `whatsapp:${to}`;

    // Send message via Twilio
    const message = await client.messages.create({
      from: process.env.TWILIO_WHATSAPP_FROM,
      to: formattedTo,
      body: body
    });

    console.log(`[${requestId}] Message sent successfully. SID: ${message.sid}`);

    return NextResponse.json({
      success: true,
      requestId,
      messageId: message.sid,
      to: formattedTo,
      body: body,
      status: message.status
    });

  } catch (error: unknown) {
    console.error(`[${requestId}] Error sending message:`, error);
    
    // Handle Twilio-specific errors
    if (error && typeof error === 'object' && 'code' in error && 'message' in error) {
      const twilioError = error as { code: string; message: string };
      return NextResponse.json(
        { 
          error: `Twilio error: ${twilioError.message}`, 
          code: twilioError.code,
          requestId 
        }, 
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to send message', requestId }, 
      { status: 500 }
    );
  }
}

// Handle GET requests (for testing)
export async function GET() {
  return NextResponse.json({ 
    status: 'Send message endpoint is ready',
    timestamp: new Date().toISOString(),
    usage: 'POST with JSON body: { "to": "+1234567890", "body": "Your message" }'
  });
}
