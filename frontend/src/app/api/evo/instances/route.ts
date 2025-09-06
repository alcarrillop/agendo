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

    // Configurar webhook después de crear la instancia
    try {
      console.log(`[${requestId}] Configuring webhook for ${name}...`);
      const webhookResponse = await fetch(`${EVOLUTION_API_URL}/webhook/set/${name}`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          webhook: {
            url: webhookUrl,
            enabled: true,
            events: ['MESSAGES_UPSERT'],
          },
        }),
      });

      if (webhookResponse.ok) {
        const webhookData = await webhookResponse.json();
        console.log(`[${requestId}] Webhook configured successfully:`, webhookData);
      } else {
        const webhookError = await webhookResponse.json();
        console.warn(`[${requestId}] Webhook configuration failed:`, webhookError);
        // Continuar aunque falle el webhook - se puede configurar después
      }
    } catch (webhookError) {
      console.warn(`[${requestId}] Webhook configuration error:`, webhookError);
    }

    // Sincronizar con la base de datos del backend
    try {
      const backendResponse = await fetch('http://localhost:8000/api/v1/instances/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          instance_name: name,
          evolution_instance_id: data.instance?.instanceId || data.instance?.instanceName,
          status: 'connecting',
          webhook_url: webhookUrl,
          token: data.instance?.token || '',
          client_name: data.instance?.clientName || 'evolution_exchange',
        }),
      });

      if (backendResponse.ok) {
        console.log(`[${requestId}] Instance synced to backend database`);
      } else {
        console.error(`[${requestId}] Failed to sync instance to backend:`, await backendResponse.text());
      }
    } catch (syncError) {
      console.error(`[${requestId}] Error syncing instance to backend:`, syncError);
    }

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
  const requestId = Math.random().toString(36).substring(7);
  console.log(`[${requestId}] Fetching Evolution API instances`);

  try {
    if (!EVOLUTION_API_KEY) {
      console.error(`[${requestId}] Missing Evolution API key`);
      return NextResponse.json(
        { error: 'Evolution API not configured' },
        { status: 500 }
      );
    }

    const response = await fetch(`${EVOLUTION_API_URL}/instance/fetchInstances`, {
      headers: {
        'apikey': EVOLUTION_API_KEY,
      },
    });

    if (!response.ok) {
      console.error(`[${requestId}] Evolution API error:`, response.status);
      return NextResponse.json(
        { error: 'Failed to fetch instances from Evolution API' },
        { status: response.status }
      );
    }

    const instances = await response.json();
    console.log(`[${requestId}] Found ${instances.length} instances`);

    return NextResponse.json({
      success: true,
      requestId,
      instances: instances || [],
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error(`[${requestId}] Error fetching instances:`, error);
    return NextResponse.json(
      { error: 'Internal server error', requestId },
      { status: 500 }
    );
  }
}
