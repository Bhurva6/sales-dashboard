import { NextRequest, NextResponse } from 'next/server';
import { approveAccessRequest } from '@/lib/mockDatabase';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const requestId = params.id;
    const result = await approveAccessRequest(requestId);

    return NextResponse.json({
      message: 'Access request approved',
      user: result.user
    });
  } catch (error) {
    console.error('Error approving access request:', error);
    return NextResponse.json(
      { message: 'Error approving access request', error: String(error) },
      { status: 500 }
    );
  }
}
