import { NextRequest, NextResponse } from 'next/server';

const EVOLUTION_API_URL = process.env.EVOLUTION_API_URL;
const EVOLUTION_API_KEY = process.env.EVOLUTION_API_KEY;

if (!EVOLUTION_API_URL) {
  throw new Error('Missing Evolution API URL');
}

// Log para debugging
console.log('Evolution API URL:', EVOLUTION_API_URL);
console.log('Evolution API KEY:', EVOLUTION_API_KEY ? '***configured***' : 'not-configured');

export async function POST(request: NextRequest) {
  const requestId = Math.random().toString(36).substring(7);
  console.log(`[${requestId}] Creating Evolution API instance`);

  try {
    const { name, webhookUrl } = await request.json();

    if (!name || !webhookUrl) {
      return NextResponse.json(
        { error: 'Missing required fields: name and webhookUrl' },
        { status: 400 }
      );
    }

    console.log(`[${requestId}] Creating instance: ${name} with webhook: ${webhookUrl}`);

    const headers: any = {
      'Content-Type': 'application/json',
    };
    
    // Solo agregar API key si está configurada
    if (EVOLUTION_API_KEY) {
      headers['apikey'] = EVOLUTION_API_KEY;
    }

    const response = await fetch(`${EVOLUTION_API_URL}/instance/create`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        instanceName: name,
        integration: 'WHATSAPP-BAILEYS',
        qrcode: true,
        // webhook: webhookUrl,
        // webhook_by_events: true,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      console.error(`[${requestId}] Evolution API error:`, data);
      return NextResponse.json(
        { error: 'Failed to create instance', details: data },
        { status: response.status }
      );
    }

    console.log(`[${requestId}] Instance created successfully:`, data);

    return NextResponse.json({
      success: true,
      requestId,
      data,
    });

  } catch (error) {
    console.error(`[${requestId}] Error creating instance:`, error);
    return NextResponse.json(
      { error: 'Internal server error', requestId },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'Evolution API instances endpoint ready',
    timestamp: new Date().toISOString(),
    usage: 'POST with JSON body: { "name": "TENANT_123", "webhookUrl": "https://your-domain.com/api/webhooks/evolution" }'
  });
}
