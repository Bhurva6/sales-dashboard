import { NextRequest, NextResponse } from 'next/server';
import { mockAccessRequests, mockUsers, type User } from '@/lib/mockDatabase';

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
    accessRequest.status = 'approved';

    // Create a user from the approved request
    const newUser: User = {
      id: `user-${Date.now()}`,
      email: accessRequest.email,
      username: accessRequest.email.split('@')[0],
      password: accessRequest.password,
      fullName: accessRequest.fullName,
      role: 'user',
      allowedStates: accessRequest.requestedStates || [],
      status: 'active',
      createdAt: new Date().toISOString()
    };

    mockUsers.push(newUser);

    // In production, update database
    console.log('Approved access request:', requestId);
    console.log('Created user:', { email: newUser.email, allowedStates: newUser.allowedStates });

    return NextResponse.json({
      message: 'Access request approved',
      user: newUser
    });
  } catch (error) {
    console.error('Error approving access request:', error);
    return NextResponse.json(
      { message: 'Error approving access request', error: String(error) },
      { status: 500 }
    );
  }
}
