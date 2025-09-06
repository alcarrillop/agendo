import { NextRequest, NextResponse } from 'next/server';

const EVOLUTION_API_URL = process.env.EVOLUTION_API_URL;
const EVOLUTION_API_KEY = process.env.EVOLUTION_API_KEY;

export async function POST(request: NextRequest) {
  const requestId = Math.random().toString(36).substring(7);
  
  try {
    // Validate environment variables
    if (!EVOLUTION_API_URL || !EVOLUTION_API_KEY) {
      console.error(`[${requestId}] Missing Evolution API configuration`);
      return NextResponse.json(
        { 
          error: 'Evolution API not configured',
          code: 'MISSING_CONFIG'
        },
        { status: 500 }
      );
    }

    const { to, body } = await request.json();
    
    // Validate request body
    if (!to || !body) {
      return NextResponse.json(
        { 
          error: 'Missing required fields: to, body',
          code: 'INVALID_REQUEST'
        },
        { status: 400 }
      );
    }

    console.log(`[${requestId}] Sending test message to ${to}`);

    // Format phone number (remove + and any spaces)
    const phoneNumber = to.replace(/[\s+]/g, '');
    
    // Try to get an active instance from our own API
    let instanceName = null;
    try {
      // First try to get instances from our own frontend API
      const instancesResponse = await fetch(`${request.nextUrl.origin}/api/evo/instances`, {
        method: 'GET'
      });
      
      if (instancesResponse.ok) {
        const instancesData = await instancesResponse.json();
        console.log(`[${requestId}] Raw instances data:`, JSON.stringify(instancesData, null, 2));
        
        if (instancesData.instances && instancesData.instances.length > 0) {
          // Use the 'name' property from Evolution API response
          const firstInstance = instancesData.instances[0];
          instanceName = firstInstance.name;
          
          console.log(`[${requestId}] Using instance from our API: ${instanceName}`);
        }
      }
    } catch (error) {
      console.warn(`[${requestId}] Could not get instances from our API:`, error);
    }
    
    // If we still don't have an instance name, return an error
    if (!instanceName) {
      console.error(`[${requestId}] No WhatsApp instance available`);
      return NextResponse.json(
        { 
          error: 'No WhatsApp instance connected. Please connect WhatsApp first.',
          code: 'NO_INSTANCE'
        },
        { status: 400 }
      );
    }
    
    // Send message via Evolution API
    const evolutionResponse = await fetch(
      `${EVOLUTION_API_URL}/message/sendText/${instanceName}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': EVOLUTION_API_KEY,
        },
        body: JSON.stringify({
          number: phoneNumber,
          text: body,
        }),
      }
    );

    const evolutionData = await evolutionResponse.json();

    if (!evolutionResponse.ok) {
      console.error(`[${requestId}] Evolution API error:`, evolutionData);
      return NextResponse.json(
        { 
          error: 'Failed to send message via Evolution API',
          details: evolutionData,
          code: 'EVOLUTION_ERROR'
        },
        { status: evolutionResponse.status }
      );
    }

    console.log(`[${requestId}] Message sent successfully:`, evolutionData);

    return NextResponse.json({
      success: true,
      messageId: evolutionData.key?.id || 'unknown',
      status: 'sent',
      requestId,
      data: evolutionData
    });

  } catch (error) {
    console.error(`[${requestId}] Error sending message:`, error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        details: error instanceof Error ? error.message : 'Unknown error',
        code: 'INTERNAL_ERROR',
        requestId
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'WhatsApp send endpoint ready',
    timestamp: new Date().toISOString(),
    usage: 'POST { to: "+1234567890", body: "message" }'
  });
}
