/**
 * Dashboard page - Protected route showing research opportunity listings.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { OpportunitiesService } from '../services/opportunities';
import type { Opportunity } from '../services/opportunities';
import { AxiosError } from 'axios';

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);

  useEffect(() => {
    fetchOpportunities();
  }, []);

  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await OpportunitiesService.getOpportunities({
        is_active: true,
        limit: 100
      });
      setOpportunities(data);
    } catch (err) {
      const axiosError = err as AxiosError<{ detail: string }>;
      setError(axiosError.response?.data?.detail || 'Failed to load opportunities');
      console.error('Error fetching opportunities:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/signin');
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      const data = await OpportunitiesService.getOpportunities({
        is_active: true,
        search: searchQuery,
        limit: 100
      });
      setOpportunities(data);
    } catch (err) {
      const axiosError = err as AxiosError<{ detail: string }>;
      setError(axiosError.response?.data?.detail || 'Failed to search opportunities');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'No deadline';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const isDeadlineSoon = (deadline: string | null) => {
    if (!deadline) return false;
    const deadlineDate = new Date(deadline);
    const now = new Date();
    const daysUntil = Math.floor((deadlineDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntil <= 7 && daysUntil >= 0;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Research Assistant</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, <span className="font-medium">{user?.name}</span>
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header with Search */}
          <div className="mb-6">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Research Opportunities</h2>
            <form onSubmit={handleSearch} className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search opportunities by title, description, lab, or PI..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Search
              </button>
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => {
                    setSearchQuery('');
                    fetchOpportunities();
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300"
                >
                  Clear
                </button>
              )}
            </form>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{error}</p>
              <button
                onClick={fetchOpportunities}
                className="mt-2 text-sm text-red-600 hover:text-red-800 font-medium"
              >
                Try again
              </button>
            </div>
          )}

          {/* Loading State */}
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : opportunities.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="mt-2 text-lg font-medium text-gray-900">No opportunities found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchQuery ? 'Try adjusting your search terms.' : 'Check back soon for new opportunities!'}
              </p>
            </div>
          ) : (
            <>
              {/* Results Count */}
              <div className="mb-4">
                <p className="text-sm text-gray-600">
                  Showing {opportunities.length} {opportunities.length === 1 ? 'opportunity' : 'opportunities'}
                </p>
              </div>

              {/* Opportunities Grid */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-1">
                {opportunities.map((opp) => (
                  <div
                    key={opp.opportunity_id}
                    className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => setSelectedOpportunity(opp)}
                  >
                    <div className="p-6">
                      {/* Header */}
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 mb-1">{opp.title}</h3>
                          <div className="flex flex-wrap gap-2 text-sm text-gray-600">
                            {opp.lab_name && <span className="font-medium">{opp.lab_name}</span>}
                            {opp.pi_name && <span>• {opp.pi_name}</span>}
                            {opp.institution && <span>• {opp.institution}</span>}
                          </div>
                        </div>
                        {opp.deadline && isDeadlineSoon(opp.deadline) && (
                          <span className="px-2 py-1 text-xs font-medium text-red-700 bg-red-100 rounded-full">
                            Deadline Soon
                          </span>
                        )}
                      </div>

                      {/* Description */}
                      <p className="text-sm text-gray-700 mb-3 line-clamp-3">{opp.description}</p>

                      {/* Tags */}
                      <div className="flex flex-wrap gap-2 mb-3">
                        {opp.research_topics?.slice(0, 3).map((topic, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded"
                          >
                            {topic}
                          </span>
                        ))}
                        {opp.research_topics && opp.research_topics.length > 3 && (
                          <span className="px-2 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded">
                            +{opp.research_topics.length - 3} more
                          </span>
                        )}
                      </div>

                      {/* Footer */}
                      <div className="flex justify-between items-center text-sm">
                        <div className="flex gap-4">
                          {opp.funding_status && (
                            <span className="text-gray-600">
                              <span className="font-medium">Funding:</span> {opp.funding_status}
                            </span>
                          )}
                          {opp.deadline && (
                            <span className="text-gray-600">
                              <span className="font-medium">Deadline:</span> {formatDate(opp.deadline)}
                            </span>
                          )}
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedOpportunity(opp);
                          }}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          View Details →
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </main>

      {/* Opportunity Detail Modal */}
      {selectedOpportunity && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedOpportunity(null)}
        >
          <div
            className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              {/* Modal Header */}
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-900">{selectedOpportunity.title}</h2>
                <button
                  onClick={() => setSelectedOpportunity(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Modal Content */}
              <div className="space-y-4">
                {/* Basic Info */}
                <div>
                  <div className="flex flex-wrap gap-2 text-sm text-gray-600 mb-4">
                    {selectedOpportunity.lab_name && (
                      <span className="font-medium">{selectedOpportunity.lab_name}</span>
                    )}
                    {selectedOpportunity.pi_name && <span>• {selectedOpportunity.pi_name}</span>}
                    {selectedOpportunity.institution && <span>• {selectedOpportunity.institution}</span>}
                  </div>
                </div>

                {/* Description */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedOpportunity.description}</p>
                </div>

                {/* Research Topics */}
                {selectedOpportunity.research_topics && selectedOpportunity.research_topics.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Research Topics</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedOpportunity.research_topics.map((topic, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 text-sm font-medium text-blue-700 bg-blue-100 rounded-full"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Methods */}
                {selectedOpportunity.methods && selectedOpportunity.methods.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Methods & Techniques</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedOpportunity.methods.map((method, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 text-sm font-medium text-green-700 bg-green-100 rounded-full"
                        >
                          {method}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Details Grid */}
                <div className="grid grid-cols-2 gap-4">
                  {selectedOpportunity.deadline && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-500">Deadline</h4>
                      <p className="text-gray-900">{formatDate(selectedOpportunity.deadline)}</p>
                    </div>
                  )}
                  {selectedOpportunity.funding_status && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-500">Funding Status</h4>
                      <p className="text-gray-900">{selectedOpportunity.funding_status}</p>
                    </div>
                  )}
                  {selectedOpportunity.experience_required && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-500">Experience Required</h4>
                      <p className="text-gray-900">{selectedOpportunity.experience_required}</p>
                    </div>
                  )}
                  {selectedOpportunity.contact_email && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-500">Contact</h4>
                      <a
                        href={`mailto:${selectedOpportunity.contact_email}`}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        {selectedOpportunity.contact_email}
                      </a>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  {selectedOpportunity.application_link && (
                    <a
                      href={selectedOpportunity.application_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 text-center"
                    >
                      Apply Now
                    </a>
                  )}
                  <a
                    href={selectedOpportunity.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 text-center"
                  >
                    View Source
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;

