import { NextRequest, NextResponse } from 'next/server';
import { mockAccessRequests } from '@/lib/mockDatabase';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const requestId = params.id;
    const requestIndex = mockAccessRequests.findIndex(r => r.id === requestId);

    if (requestIndex === -1) {
      return NextResponse.json(
        { message: 'Access request not found' },
        { status: 404 }
      );
    }

    const accessRequest = mockAccessRequests[requestIndex];
    accessRequest.status = 'rejected';

    // In production, update database
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
