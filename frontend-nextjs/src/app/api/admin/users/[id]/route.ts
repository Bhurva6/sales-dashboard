import { NextRequest, NextResponse } from 'next/server';
import { mockUsers } from '@/lib/mockDatabase';

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const userId = params.id;
    const userIndex = mockUsers.findIndex(u => u.id === userId);

    if (userIndex === -1) {
      return NextResponse.json(
        { message: 'User not found' },
        { status: 404 }
      );
    }

    mockUsers.splice(userIndex, 1);

    // In production, delete from database
    console.log('Deleted user:', userId);

    return NextResponse.json({ message: 'User deleted successfully' });
  } catch (error) {
    console.error('Error deleting user:', error);
    return NextResponse.json(
      { message: 'Error deleting user', error: String(error) },
      { status: 500 }
    );
  }
}
