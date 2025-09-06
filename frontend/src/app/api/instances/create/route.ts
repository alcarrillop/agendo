import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  const requestId = Math.random().toString(36).substring(7);
  
  try {
    const { instanceName, userId } = await request.json();
    
    console.log(`[${requestId}] Creating instance: ${instanceName}`);
    
    if (!instanceName) {
      return NextResponse.json(
        { error: 'Instance name is required' },
        { status: 400 }
      );
    }
    
    // Call backend to create instance with database persistence
    const response = await fetch(`${BACKEND_URL}/api/v1/instances/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        instance_name: instanceName,
        user_id: userId || null
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error(`[${requestId}] Backend error:`, errorData);
      return NextResponse.json(
        { error: errorData.detail || 'Failed to create instance' },
        { status: response.status }
      );
    }
    
    const result = await response.json();
    console.log(`[${requestId}] Instance created successfully:`, result.instance?.instance_name);
    
    return NextResponse.json({
      success: true,
      requestId,
      instance: result.instance,
      qrcode: result.qrcode,
      timestamp: new Date().toISOString(),
    });
    
  } catch (error) {
    console.error(`[${requestId}] Error creating instance:`, error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        requestId,
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

