import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import bcrypt from 'bcryptjs';
import { SignJWT } from 'jose';
import { cookies } from 'next/headers';

const SECRET = new TextEncoder().encode(process.env.JWT_SECRET || 'secret');

export async function POST(request: Request) {
  const body = await request.json();
  
  // SIGN UP[cite: 1]
  if (body.action === 'SIGNUP') {
    const { employeeId, email, password, role, fullName } = body;
    if (password.length < 8 || !/[A-Z]/.test(password) || !/[0-9]/.test(password)) {
      return NextResponse.json({ error: 'Password does not meet security rules.' }, { status: 400 });
    }
    const hashedPassword = await bcrypt.hash(password, 10);
    await prisma.user.create({ data: { employeeId, email, passwordHash: hashedPassword, role, fullName } });
    return NextResponse.json({ success: true, message: 'Email verification is required.' }, { status: 201 });
  }
  
  // SIGN IN[cite: 1]
  if (body.action === 'LOGIN') {
    const { email, password } = body;
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
      return NextResponse.json({ error: 'Incorrect credentials' }, { status: 401 });
    }
    const token = await new SignJWT({ userId: user.id, role: user.role })
      .setProtectedHeader({ alg: 'HS256' }).setExpirationTime('24h').sign(SECRET);
    cookies().set('auth-token', token, { httpOnly: true, path: '/' });
    return NextResponse.json({ success: true, role: user.role });
  }

  // LOGOUT
  if (body.action === 'LOGOUT') {
    cookies().delete('auth-token');
    return NextResponse.json({ success: true });
  }
}