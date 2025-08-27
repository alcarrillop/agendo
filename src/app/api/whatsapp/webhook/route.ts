import { NextRequest, NextResponse } from 'next/server';
import { Twilio, validateRequest } from 'twilio';

// Initialize Twilio client
const client = new Twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

export async function POST(request: NextRequest) {
  const requestId = Math.random().toString(36).substring(7);
  console.log(`[${requestId}] Webhook received`);

  try {
    // Get the request body as text (URL-encoded)
    const body = await request.text();
    console.log(`[${requestId}] Body:`, body);

    // Parse URL-encoded body
    const params = new URLSearchParams(body);
    const messageData = Object.fromEntries(params.entries());
    
    console.log(`[${requestId}] Parsed data:`, messageData);

    // Validate Twilio signature
    const twilioSignature = request.headers.get('x-twilio-signature');
    const publicWebhookUrl = process.env.PUBLIC_WEBHOOK_URL;
    
    if (twilioSignature && publicWebhookUrl) {
      const isValid = validateRequest(
        process.env.TWILIO_AUTH_TOKEN!,
        twilioSignature,
        publicWebhookUrl,
        messageData
      );
      
      if (!isValid) {
        console.log(`[${requestId}] Invalid Twilio signature`);
        return NextResponse.json({ error: 'Invalid signature' }, { status: 401 });
      }
      console.log(`[${requestId}] Twilio signature validated`);
    } else {
      console.log(`[${requestId}] No signature validation (missing signature or webhook URL)`);
    }

    // Respond 200 immediately
    const response = NextResponse.json({ 
      success: true, 
      requestId,
      message: 'Webhook processed successfully' 
    });

    // Process the message asynchronously (don't await)
    processMessageAsync(messageData, requestId);

    return response;

  } catch (error) {
    console.error(`[${requestId}] Error processing webhook:`, error);
    return NextResponse.json(
      { error: 'Internal server error', requestId }, 
      { status: 500 }
    );
  }
}

// Async function to process the message without blocking the response
async function processMessageAsync(messageData: Record<string, string>, requestId: string) {
  try {
    const { From, Body } = messageData;
    
    if (!From) {
      console.log(`[${requestId}] No 'From' field in message data`);
      return;
    }

    console.log(`[${requestId}] Processing message from ${From}: "${Body}"`);

    // Send echo reply
    const message = await client.messages.create({
      from: process.env.TWILIO_WHATSAPP_FROM!,
      to: From,
      body: 'Recibido ✅'
    });

    console.log(`[${requestId}] Echo reply sent. Message SID: ${message.sid}`);

  } catch (error) {
    console.error(`[${requestId}] Error sending echo reply:`, error);
  }
}

// Handle GET requests (for webhook verification)
export async function GET() {
  return NextResponse.json({ 
    status: 'Webhook endpoint is ready',
    timestamp: new Date().toISOString()
  });
}
