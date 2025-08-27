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

  console.log(`[${requestId}] Getting QR code for instance: ${name}`);

  try {
    const response = await fetch(`${EVOLUTION_API_URL}/instance/connect/${name}`, {
      method: 'GET',
      headers: {
        'apikey': EVOLUTION_API_KEY,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      console.error(`[${requestId}] Evolution API error:`, data);
      return NextResponse.json(
        { error: 'Failed to get QR code', details: data },
        { status: response.status }
      );
    }

    console.log(`[${requestId}] QR code retrieved successfully for ${name}`);

    // Normalize QR code to data URL if needed
    let qrCode = data.qr || data.base64 || data.code;
    
    if (qrCode && !qrCode.startsWith('data:image')) {
      qrCode = `data:image/png;base64,${qrCode}`;
    }

    return NextResponse.json({
      success: true,
      requestId,
      data: {
        type: data.type || 'qr',
        code: data.code,
        pairingCode: data.pairingCode,
        qr: qrCode,
      },
    });

  } catch (error) {
    console.error(`[${requestId}] Error getting QR code:`, error);
    return NextResponse.json(
      { error: 'Internal server error', requestId },
      { status: 500 }
    );
  }
}
