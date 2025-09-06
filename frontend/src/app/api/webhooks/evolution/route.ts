import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const requestId = Math.random().toString(36).substring(7);
  
  try {
    const webhookData = await request.json();
    
    console.log(`[${requestId}] Evolution webhook received:`, JSON.stringify(webhookData, null, 2));
    
    // Por ahora solo loggeamos el webhook
    // Aquí es donde después enviaremos al backend para procesamiento con LangGraph
    
    // Verificar si es un mensaje
    if (webhookData.event === 'messages.upsert') {
      const messages = webhookData.data?.messages || [];
      
      for (const message of messages) {
        // Solo procesar mensajes entrantes (no enviados por nosotros)
        if (!message.key?.fromMe) {
          const from = message.key?.remoteJid;
          const messageContent = message.message?.conversation || 
                               message.message?.extendedTextMessage?.text;
          
          if (messageContent) {
            console.log(`[${requestId}] Message from ${from}: ${messageContent}`);
            
            // Enviar al backend para procesamiento con LangGraph
            try {
              const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
              const response = await fetch(`${backendUrl}/api/v1/webhooks/evolution`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  ...webhookData,
                  processed_by: 'frontend',
                  timestamp: new Date().toISOString(),
                  request_id: requestId
                })
              });
              
              if (response.ok) {
                const result = await response.json();
                console.log(`[${requestId}] Backend processed successfully:`, result);
              } else {
                console.error(`[${requestId}] Backend processing failed:`, response.status);
              }
            } catch (error) {
              console.error(`[${requestId}] Error sending to backend:`, error);
            }
          }
        }
      }
    }
    
    return NextResponse.json({ 
      success: true, 
      requestId,
      message: 'Webhook processed successfully' 
    });
    
  } catch (error) {
    console.error(`[${requestId}] Error processing webhook:`, error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        requestId 
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'Evolution webhook endpoint ready',
    timestamp: new Date().toISOString(),
    usage: 'POST webhook data from Evolution API'
  });
}
