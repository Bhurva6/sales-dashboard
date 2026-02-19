import { NextRequest, NextResponse } from 'next/server';
import { rejectAccessRequest } from '@/lib/mockDatabase';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const requestId = params.id;
    await rejectAccessRequest(requestId);

    // In production, update database already performed by adapter
    console.log('Rejected access request:', requestId);

    return NextResponse.json({
      message: 'Access request rejected'
    });
  } catch (error) {
    console.error('Error rejecting access request:', error);
    return NextResponse.json(
      { message: 'Error rejecting access request', error: String(error) },
      { status: 500 }
    );
  }
}
