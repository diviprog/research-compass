/**
 * Outreach Email page — full-page view of a generated cold email draft.
 * Receives data via React Router location state (subject, body, opportunity details).
 */

import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Card, Button } from '../components/neo';

export interface OutreachEmailState {
  subject: string;
  body: string;
  opportunity_id: number;
  outreach_id: number;
  opportunity_title: string;
  pi_name: string | null;
  institution: string | null;
}

export const OutreachEmail: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as OutreachEmailState | null;

  const [copyFeedback, setCopyFeedback] = useState(false);

  if (!state?.subject && !state?.body) {
    navigate('/dashboard', { replace: true });
    return null;
  }

  const { subject, body, opportunity_title, pi_name, institution } = state;
  const toLine = [pi_name, institution].filter(Boolean).join(' — ') || 'Professor';

  const handleCopy = () => {
    const text = `Subject: ${subject}\n\n${body}`;
    navigator.clipboard.writeText(text).then(() => {
      setCopyFeedback(true);
      window.setTimeout(() => setCopyFeedback(false), 2000);
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 font-body">
      <nav className="bg-white border-b border-gray-100 sticky top-0 z-40 backdrop-blur-sm bg-white/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => navigate('/dashboard')}
                leftIcon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                }
              >
                Back
              </Button>
              <h1 className="text-xl font-bold font-display text-gray-900">Your Email Draft</h1>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/dashboard" className="text-sm font-medium text-gray-600 hover:text-gray-900">
                Dashboard
              </Link>
              <Link to="/profile" className="text-sm font-medium text-gray-600 hover:text-gray-900">
                Profile
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-2xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <Card variant="outlined" className="p-6">
          <p className="text-sm text-gray-600 mb-1">To: {toLine}</p>
          <p className="text-sm text-gray-600 mb-4">Re: {opportunity_title || 'Research opportunity'}</p>

          <p className="text-base font-bold text-gray-900 mb-2">Subject: {subject}</p>
          <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans bg-gray-50 border border-gray-100 rounded-lg p-4 overflow-x-auto mb-6">
            {body}
          </pre>

          <div className="flex flex-wrap gap-3">
            <Button type="button" onClick={handleCopy} variant="secondary" size="md">
              {copyFeedback ? 'Copied!' : 'Copy to Clipboard'}
            </Button>
            <span title="Coming soon">
              <Button type="button" disabled variant="ghost" size="md">
                Send via Gmail
              </Button>
            </span>
          </div>
        </Card>
      </main>
    </div>
  );
};

export default OutreachEmail;
