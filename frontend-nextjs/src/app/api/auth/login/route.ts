import { NextRequest, NextResponse } from 'next/server';
import { mockUsers, type User } from '@/lib/mockDatabase';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email and password are required.' },
        { status: 400 }
      );
    }

    // Find user by email or username
    const user = mockUsers.find(
      (u: User) => u.email.toLowerCase() === email.toLowerCase() || u.username === email
    );

    if (!user) {
      return NextResponse.json(
        { error: 'Invalid credentials. Please check your email/username and password.' },
        { status: 401 }
      );
    }

    // Verify password (in production, use bcrypt.compare)
    if (user.password !== password) {
      return NextResponse.json(
        { error: 'Invalid credentials. Please check your email/username and password.' },
        { status: 401 }
      );
    }

    // Successful login
    return NextResponse.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        fullName: user.fullName,
        role: user.role,
        allowedStates: user.allowedStates,
      },
      message: 'Login successful!',
    });

  } catch (error) {
    console.error('Error during login:', error);
    return NextResponse.json(
      { error: 'Login failed. Please try again.' },
      { status: 500 }
    );
  }
}

// NOTE: user creation helper moved to shared mockDatabase.ts
