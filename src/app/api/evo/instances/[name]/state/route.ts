import { NextRequest, NextResponse } from 'next/server';

const EVOLUTION_API_URL = process.env.EVOLUTION_API_URL;
const EVOLUTION_API_KEY = process.env.EVOLUTION_API_KEY;

if (!EVOLUTION_API_URL || !EVOLUTION_API_KEY) {
  throw new Error('Missing Evolution API configuration');
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ name: string }> }
) {
  const requestId = Math.random().toString(36).substring(7);
  const { name } = await params;

  console.log(`[${requestId}] Getting connection state for instance: ${name}`);

  try {
    const response = await fetch(`${EVOLUTION_API_URL}/instance/connectionState/${name}`, {
      method: 'GET',
      headers: {
        'apikey': EVOLUTION_API_KEY,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      console.error(`[${requestId}] Evolution API error:`, data);
      return NextResponse.json(
        { error: 'Failed to get connection state', details: data },
        { status: response.status }
      );
    }

    console.log(`[${requestId}] Connection state for ${name}:`, data.state || data);

    return NextResponse.json({
      success: true,
      requestId,
      state: data.state || data.instance?.state || 'unknown',
      data,
    });

  } catch (error) {
    console.error(`[${requestId}] Error getting connection state:`, error);
    return NextResponse.json(
      { error: 'Internal server error', requestId },
      { status: 500 }
    );
  }
}
