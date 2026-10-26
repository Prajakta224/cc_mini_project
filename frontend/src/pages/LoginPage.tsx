import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Eye, EyeOff, Lock, Mail, ArrowRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { getErrorMessage } from '../api/client';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) { toast.error('Please enter email and password'); return; }
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-10">
          <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
            <Shield className="w-7 h-7 text-white" />
          </div>
          <div>
            <div className="text-white text-2xl font-bold">AFES</div>
            <div className="text-blue-400 text-xs">Authenticated File Encryption System</div>
          </div>
        </div>

        <div className="card">
          <h1 className="text-2xl font-bold text-white mb-1">Sign In</h1>
          <p className="text-slate-400 text-sm mb-8">Access your encrypted file vault</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                <input value={email} onChange={e => setEmail(e.target.value)}
                  type="email" placeholder="you@example.com" className="input-field pl-10" autoComplete="email" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
                <input value={password} onChange={e => setPassword(e.target.value)}
                  type={showPwd ? 'text' : 'password'} placeholder="Your password"
                  className="input-field pl-10 pr-10" autoComplete="current-password" />
                <button type="button" onClick={() => setShowPwd(p => !p)}
                  className="absolute right-3 top-3.5 text-slate-400 hover:text-slate-200">
                  {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3 text-base">
              {loading
                ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                : <><ArrowRight className="w-4 h-4" /> Sign In</>
              }
            </button>
          </form>

          {/* Demo credentials hint */}
          <div className="mt-6 p-4 bg-slate-800 rounded-lg text-xs text-slate-400">
            <p className="font-medium text-slate-300 mb-1">Demo Accounts (run seed script first)</p>
            <p>alice@afes.demo / Demo@Alice1</p>
            <p>bob@afes.demo / Demo@Bob1</p>
            <p>admin@afes.demo / Demo@Admin1</p>
          </div>
        </div>

        <p className="text-center text-slate-400 mt-6 text-sm">
          New to AFES?{' '}
          <Link to="/register" className="text-blue-400 hover:text-blue-300 font-medium">Create an account</Link>
        </p>
        <p className="text-center text-slate-500 mt-2 text-xs">
          <Link to="/" className="hover:text-slate-400">← Back to home</Link>
        </p>
      </div>
    </div>
  );
}
