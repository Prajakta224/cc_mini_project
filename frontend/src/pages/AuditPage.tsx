import React, { useEffect, useState } from 'react';
import { auditApi } from '../api/audit';
import type { AuditEvent } from '../types';
import { Activity, CheckCircle, XCircle, RefreshCw, Shield } from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';
import toast from 'react-hot-toast';

const EVENT_COLORS: Record<string, string> = {
  LOGIN_SUCCESS: 'text-emerald-400',
  LOGIN_FAILURE: 'text-red-400',
  REGISTER: 'text-blue-400',
  LOGOUT: 'text-slate-400',
  ENCRYPT_FILE: 'text-purple-400',
  DECRYPT_FILE: 'text-cyan-400',
  DELETE_FILE: 'text-orange-400',
  UNAUTHORIZED_ACCESS: 'text-red-500',
  TAMPER_TEST: 'text-amber-400',
  STORAGE_ERROR: 'text-red-400',
};

const EVENT_ICONS: Record<string, string> = {
  LOGIN_SUCCESS: '🔐',
  LOGIN_FAILURE: '🚫',
  REGISTER: '👤',
  LOGOUT: '🚪',
  ENCRYPT_FILE: '🔒',
  DECRYPT_FILE: '🔓',
  DELETE_FILE: '🗑️',
  UNAUTHORIZED_ACCESS: '⚠️',
  TAMPER_TEST: '🧪',
};

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  const load = async (type?: string) => {
    setLoading(true);
    try {
      const res = await auditApi.list({ limit: 100, event_type: type || undefined });
      setEvents(res.data.events);
      setTotal(res.data.total);
    } catch {
      toast.error('Failed to load audit events');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleFilter = (type: string) => {
    setFilter(type);
    load(type);
  };

  const EVENT_TYPES = ['', 'LOGIN_SUCCESS', 'LOGIN_FAILURE', 'ENCRYPT_FILE', 'DECRYPT_FILE', 'DELETE_FILE', 'UNAUTHORIZED_ACCESS'];

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Audit Log</h1>
          <p className="text-slate-400 mt-1">{total} security events recorded</p>
        </div>
        <button onClick={() => load(filter || undefined)} className="btn-secondary flex items-center gap-2">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {/* Filter chips */}
      <div className="flex flex-wrap gap-2 mb-6">
        {EVENT_TYPES.map(type => (
          <button key={type} onClick={() => handleFilter(type)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              filter === type
                ? 'bg-blue-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}>
            {type || 'All Events'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : events.length === 0 ? (
        <div className="card text-center py-16">
          <Activity className="w-12 h-12 mx-auto mb-3 text-slate-600" />
          <p className="text-slate-400">No audit events yet</p>
        </div>
      ) : (
        <div className="space-y-2">
          {events.map(event => {
            let details: Record<string, string> = {};
            try { details = event.details ? JSON.parse(event.details) : {}; } catch {}
            return (
              <div key={event.id} className="card p-4 flex items-start gap-4">
                <div className="text-2xl flex-shrink-0">{EVENT_ICONS[event.event_type] || '📋'}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`font-medium text-sm ${EVENT_COLORS[event.event_type] || 'text-white'}`}>
                      {event.event_type.replace(/_/g, ' ')}
                    </span>
                    {event.success
                      ? <CheckCircle className="w-4 h-4 text-emerald-400" />
                      : <XCircle className="w-4 h-4 text-red-400" />
                    }
                  </div>
                  {Object.entries(details).filter(([k]) => !['password', 'key', 'token'].includes(k)).length > 0 && (
                    <div className="text-xs text-slate-400 font-mono bg-slate-800 rounded px-2 py-1 mt-1 break-all">
                      {Object.entries(details)
                        .filter(([k]) => !['password', 'key', 'token'].includes(k))
                        .map(([k, v]) => `${k}: ${v}`).join(' | ')}
                    </div>
                  )}
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="text-xs text-slate-500">
                    {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                  </div>
                  <div className="text-xs text-slate-600 mt-0.5">
                    {format(new Date(event.timestamp), 'HH:mm:ss')}
                  </div>
                  {event.ip_address && (
                    <div className="text-xs text-slate-600 mt-0.5">{event.ip_address}</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
