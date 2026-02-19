import { NextRequest, NextResponse } from 'next/server';
import { getUsers, createUser, type User } from '@/lib/mockDatabase';

export async function GET() {
  try {
    // Fetch users from adapter (Supabase or in-memory)
    const users = await getUsers();
    return NextResponse.json({ users });
  } catch (error) {
    return NextResponse.json(
      { message: 'Error fetching users', error: String(error) },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password, states, role = 'user', fullName } = body;

    if (!email || !password || !states || states.length === 0) {
      return NextResponse.json(
        { message: 'Missing required fields: email, password, and states' },
        { status: 400 }
      );
    }

    // Check if user already exists
    const users = await getUsers();
    if (users.find((u: User) => u.email === email)) {
      return NextResponse.json(
        { message: 'User already exists' },
        { status: 409 }
      );
    }

    const newUser = await createUser({
      email,
      password,
      states,
      role,
      fullName
    });

    console.log('Created user:', { email: newUser.email, allowedStates: newUser.allowedStates });

    return NextResponse.json(
      { message: 'User created successfully', user: newUser },
      { status: 201 }
    );
  } catch (error) {
    console.error('Error creating user:', error);
    return NextResponse.json(
      { message: 'Error creating user', error: String(error) },
      { status: 500 }
    );
  }
}
