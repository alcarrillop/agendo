import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const requestId = Math.random().toString(36).substring(7);
  console.log(`[${requestId}] Evolution webhook received`);

  try {
    // Get the request body
    const body = await request.json();
    console.log(`[${requestId}] Webhook data:`, JSON.stringify(body, null, 2));

    // Respond 200 immediately (required for webhook)
    const response = NextResponse.json({ 
      success: true, 
      requestId,
      message: 'Webhook processed successfully' 
    });

    // Process the webhook asynchronously (don't await)
    processWebhookAsync(body, requestId);

    return response;

  } catch (error) {
    console.error(`[${requestId}] Error processing webhook:`, error);
    return NextResponse.json(
      { error: 'Internal server error', requestId }, 
      { status: 500 }
    );
  }
}

// Async function to process the webhook without blocking the response
async function processWebhookAsync(data: any, requestId: string) {
  try {
    const { event, instance, data: eventData } = data;
    
    console.log(`[${requestId}] Processing event: ${event} for instance: ${instance}`);

    switch (event) {
      case 'connection.update':
        handleConnectionUpdate(eventData, instance, requestId);
        break;
      
      case 'messages.upsert':
        await handleIncomingMessage(eventData, instance, requestId);
        break;
      
      case 'qrcode.updated':
        handleQRCodeUpdate(eventData, instance, requestId);
        break;
      
      default:
        console.log(`[${requestId}] Unhandled event: ${event}`);
    }

  } catch (error) {
    console.error(`[${requestId}] Error in async webhook processing:`, error);
  }
}

function handleConnectionUpdate(data: any, instance: string, requestId: string) {
  console.log(`[${requestId}] Connection update for ${instance}:`, data);
  
  if (data.state === 'open') {
    console.log(`[${requestId}] 🎉 Instance ${instance} is now connected!`);
  } else if (data.state === 'close') {
    console.log(`[${requestId}] ❌ Instance ${instance} disconnected`);
  }
}

async function handleIncomingMessage(data: any, instance: string, requestId: string) {
  try {
    const messages = data.messages || [data];
    
    for (const message of messages) {
      if (message.messageType === 'conversation' || message.messageType === 'extendedTextMessage') {
        const from = message.key?.remoteJid;
        const text = message.message?.conversation || message.message?.extendedTextMessage?.text;
        
        console.log(`[${requestId}] 📱 Message from ${from}: "${text}"`);
        
        // Log incoming message (auto-reply disabled for now)
        if (text && from && !from.includes('@g.us')) { // Ignore group messages
          console.log(`[${requestId}] 💬 Incoming message logged, auto-reply disabled`);
          // TODO: Here we'll implement the intelligent agent response based on configuration
        }
      }
    }
  } catch (error) {
    console.error(`[${requestId}] Error handling incoming message:`, error);
  }
}

function handleQRCodeUpdate(data: any, instance: string, requestId: string) {
  console.log(`[${requestId}] QR Code updated for ${instance}`);
  // Here you could broadcast the QR code to connected clients via WebSocket, etc.
}

async function sendAutoReply(instance: string, to: string, originalMessage: string, requestId: string) {
  try {
    // Extract phone number from JID
    const phoneNumber = to.split('@')[0];
    
    // Auto-reply message
    const replyText = `¡Hola! Tu mensaje "${originalMessage}" fue recibido por Agendo ✅\n\nEn breve un agente se pondrá en contacto contigo.`;
    
    // Send reply using our own API
    const response = await fetch(`${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/api/evo/instances/${instance}/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        to: phoneNumber,
        text: replyText,
      }),
    });

    if (response.ok) {
      console.log(`[${requestId}] ✅ Auto-reply sent to ${phoneNumber}`);
    } else {
      console.error(`[${requestId}] ❌ Failed to send auto-reply to ${phoneNumber}`);
    }

  } catch (error) {
    console.error(`[${requestId}] Error sending auto-reply:`, error);
  }
}

// Handle GET requests (for webhook verification)
export async function GET() {
  return NextResponse.json({ 
    status: 'Evolution API webhook endpoint is ready',
    timestamp: new Date().toISOString(),
    events: ['connection.update', 'messages.upsert', 'qrcode.updated']
  });
}
