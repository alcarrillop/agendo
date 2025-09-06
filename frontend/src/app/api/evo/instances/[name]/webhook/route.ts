import { NextRequest, NextResponse } from 'next/server';

const EVOLUTION_API_URL = process.env.EVOLUTION_API_URL;
const EVOLUTION_API_KEY = process.env.EVOLUTION_API_KEY;

export async function POST(
  request: NextRequest,
  { params }: { params: { name: string } }
) {
  const requestId = Math.random().toString(36).substring(7);
  const instanceName = params.name;
  
  console.log(`[${requestId}] Setting webhook for instance: ${instanceName}`);

  try {
    if (!EVOLUTION_API_URL || !EVOLUTION_API_KEY) {
      console.error(`[${requestId}] Missing Evolution API configuration`);
      return NextResponse.json(
        { error: 'Evolution API not configured' },
        { status: 500 }
      );
    }

    const { webhookUrl } = await request.json();

    if (!webhookUrl) {
      return NextResponse.json(
        { error: 'Missing webhookUrl' },
        { status: 400 }
      );
    }

    console.log(`[${requestId}] Setting webhook: ${webhookUrl}`);

    const response = await fetch(
      `${EVOLUTION_API_URL}/instance/update/${instanceName}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'apikey': EVOLUTION_API_KEY,
        },
        body: JSON.stringify({
          webhook: webhookUrl,
          webhook_by_events: true,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.error(`[${requestId}] Evolution API error:`, data);
      return NextResponse.json(
        { error: 'Failed to set webhook', details: data },
        { status: response.status }
      );
    }

    console.log(`[${requestId}] Webhook set successfully:`, data);

    return NextResponse.json({
      success: true,
      requestId,
      data,
    });

  } catch (error) {
    console.error(`[${requestId}] Error setting webhook:`, error);
    return NextResponse.json(
      { error: 'Internal server error', requestId },
      { status: 500 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: { name: string } }
) {
  const requestId = Math.random().toString(36).substring(7);
  const instanceName = params.name;
  
  console.log(`[${requestId}] Getting webhook for instance: ${instanceName}`);

  try {
    if (!EVOLUTION_API_URL || !EVOLUTION_API_KEY) {
      return NextResponse.json(
        { error: 'Evolution API not configured' },
        { status: 500 }
      );
    }

    const response = await fetch(
      `${EVOLUTION_API_URL}/webhook/find/${instanceName}`,
      {
        headers: {
          'apikey': EVOLUTION_API_KEY,
        },
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.error(`[${requestId}] Evolution API error:`, data);
      return NextResponse.json(
        { error: 'Failed to get webhook', details: data },
        { status: response.status }
      );
    }

    console.log(`[${requestId}] Webhook retrieved:`, data);

    return NextResponse.json({
      success: true,
      requestId,
      data,
    });

  } catch (error) {
    console.error(`[${requestId}] Error getting webhook:`, error);
    return NextResponse.json(
      { error: 'Internal server error', requestId },
      { status: 500 }
    );
  }
}
