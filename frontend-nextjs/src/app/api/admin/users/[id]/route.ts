import { NextRequest, NextResponse } from 'next/server';
import { deleteUser } from '@/lib/mockDatabase';

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const userId = params.id;

    // Delete via adapter (in-memory or Supabase)
    await deleteUser(userId);

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
