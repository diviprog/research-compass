/**
 * NeoCampus Dashboard - Research Opportunity Discovery
 * Award-winning production implementation with NeoCampus design system
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { OpportunitiesService } from '../services/opportunities';
import type { Opportunity } from '../services/opportunities';
import { ProfileService } from '../services/profile';
import { AxiosError } from 'axios';
import api from '../services/auth';
import { Card, Button, Badge, Input, Modal } from '../components/neo';
import { API_BASE_URL } from '../lib/apiBase';

/** Semantic search result item (no auth required). */
export interface SearchResultItem {
  opportunity_id: number;
  title: string;
  description: string;
  lab_name: string | null;
  pi_name: string | null;
  institution: string | null;
  location_city?: string | null;
  location_state?: string | null;
  is_remote?: boolean;
  degree_levels?: string[];
  paid_type?: string | null;
  min_hours?: number | null;
  max_hours?: number | null;
  research_topics: string[];
  deadline: string | null;
  application_link: string | null;
  contact_email: string | null;
  similarity_score: number;
  /** Present when from GET /opportunities, not from search */
  funding_status?: string | null;
  source_url?: string | null;
  methods?: string[];
  experience_required?: string | null;
}

/** Item we can display in the list (GET list or search results). */
type DisplayOpportunity = Opportunity | SearchResultItem;

function hasSimilarityScore(opp: DisplayOpportunity): opp is SearchResultItem {
  return 'similarity_score' in opp && typeof (opp as SearchResultItem).similarity_score === 'number';
}

export const DashboardNeo: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResultItem[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedOpportunity, setSelectedOpportunity] = useState<DisplayOpportunity | null>(null);
  const [emailGenerating, setEmailGenerating] = useState(false);
  const [isCuratedFromProfile, setIsCuratedFromProfile] = useState(false);
  const [showProfileBanner, setShowProfileBanner] = useState(false);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError(null);
        const profile = await ProfileService.getProfile();
        const interests = (profile.research_interests || '').trim();
        if (interests.length >= 10) {
          const res = await fetch(`${API_BASE_URL}/api/opportunities/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: interests, limit: 10 }),
          });
          if (res.ok) {
            const data = await res.json();
            setSearchResults(data.results || []);
            setOpportunities([]);
            setIsCuratedFromProfile(true);
            setShowProfileBanner(false);
          } else {
            const data = await res.json().catch(() => ({}));
            setError(data.detail || 'Search failed.');
            await fetchOpportunities();
            setShowProfileBanner(true);
          }
        } else {
          await fetchOpportunities();
          setSearchResults(null);
          setShowProfileBanner(true);
          setIsCuratedFromProfile(false);
        }
      } catch {
        await fetchOpportunities();
        setSearchResults(null);
        setShowProfileBanner(true);
        setIsCuratedFromProfile(false);
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
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
    const query = searchQuery.trim();
    if (!query) {
      setSearchResults(null);
      fetchOpportunities();
      setIsCuratedFromProfile(false);
      return;
    }
    if (query.length < 10) {
      setError('Enter at least 10 characters for semantic search.');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      setIsCuratedFromProfile(false);
      const res = await fetch(`${API_BASE_URL}/api/opportunities/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, limit: 10 }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        setError(errData.detail || 'Semantic search failed.');
        setSearchResults(null);
        return;
      }
      const data = await res.json();
      setSearchResults(data.results || []);
    } catch (err) {
      setError('Semantic search failed. Please try again.');
      setSearchResults(null);
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

  const handleGenerateEmail = async () => {
    if (!selectedOpportunity) return;
    try {
      setEmailGenerating(true);
      const { data } = await api.post<{ subject: string; body: string; opportunity_id: number; outreach_id: number }>(
        '/outreach/generate',
        { opportunity_id: selectedOpportunity.opportunity_id }
      );
      navigate('/outreach', {
        state: {
          subject: data.subject,
          body: data.body,
          opportunity_id: data.opportunity_id,
          outreach_id: data.outreach_id,
          opportunity_title: selectedOpportunity.title,
          pi_name: selectedOpportunity.pi_name ?? null,
          institution: selectedOpportunity.institution ?? null,
        },
      });
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>;
      setError(axiosError.response?.data?.detail || 'Failed to generate email.');
    } finally {
      setEmailGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 font-body">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-100 sticky top-0 z-40 backdrop-blur-sm bg-white/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-campus-500 to-campus-700 rounded-lg flex items-center justify-center shadow-elevation-1">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h1 className="text-xl font-bold font-display text-gray-900">Research Assistant</h1>
            </div>
            <div className="flex items-center gap-4">
              <Link
                to="/profile"
                className="text-sm font-medium text-gray-600 hover:text-gray-900"
              >
                Profile
              </Link>
              <span className="text-sm text-gray-600 hidden sm:inline">
                Welcome, <span className="font-semibold text-gray-900">{user?.name}</span>
              </span>
              <Button onClick={handleLogout} variant="ghost" size="sm">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header Section */}
        <div className="mb-8 animate-slide-down">
          <h2 className="text-4xl font-bold font-display text-gray-900 mb-2 tracking-tight">
            Research Opportunities
          </h2>
          <p className="text-lg text-gray-600">
            Discover positions that match your interests and expertise
          </p>
        </div>

        {/* Search Section — semantic search */}
        <div className="mb-8 animate-slide-up" style={{ animationDelay: '50ms' }}>
          <form onSubmit={handleSearch} className="flex gap-3">
            <Input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Describe your research interests... (e.g. 'machine learning for healthcare')"
              fullWidth
              leftIcon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              }
            />
            <Button type="submit" size="md">
              Search
            </Button>
            {searchQuery && (
              <Button
                type="button"
                onClick={() => {
                  setSearchQuery('');
                  setSearchResults(null);
                  fetchOpportunities();
                }}
                variant="ghost"
                size="md"
              >
                Clear
              </Button>
            )}
          </form>
        </div>

        {/* Banner: no research interests — prompt to upload resume */}
        {showProfileBanner && !loading && searchResults === null && opportunities.length > 0 && (
          <Card variant="outlined" className="mb-6 border-campus-200 bg-campus-50 animate-slide-up">
            <p className="text-sm text-campus-900">
              Upload your resume on the <Link to="/profile" className="font-semibold underline">Profile</Link> page to get personalized results.
            </p>
          </Card>
        )}

        {/* Error State */}
        {error && (
          <Card variant="outlined" className="mb-6 border-coral-200 bg-coral-50 animate-slide-up">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-coral-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div className="flex-1">
                <p className="text-sm font-semibold text-coral-900">{error}</p>
                <Button onClick={fetchOpportunities} variant="ghost" size="sm" className="mt-2">
                  Try again
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Loading State - Shimmer Effect */}
        {loading && (
          <div className="grid gap-6 lg:grid-cols-1">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="bg-white rounded-lg p-6 shadow-elevation-1 animate-pulse"
                style={{ animationDelay: `${i * 50}ms` }}
              >
                <div className="flex justify-between mb-4">
                  <div className="flex-1">
                    <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  </div>
                  <div className="h-6 w-24 bg-gray-200 rounded-full"></div>
                </div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                </div>
                <div className="flex gap-2 mt-4">
                  <div className="h-6 w-20 bg-gray-200 rounded"></div>
                  <div className="h-6 w-20 bg-gray-200 rounded"></div>
                  <div className="h-6 w-20 bg-gray-200 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && (searchResults ?? opportunities).length === 0 && (
          <Card className="text-center py-12 animate-scale-in">
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold font-display text-gray-900 mb-1">No opportunities found</h3>
              <p className="text-gray-600">
                {searchQuery ? 'Try adjusting your search terms' : 'Check back soon for new opportunities!'}
              </p>
            </div>
          </Card>
        )}

        {/* Opportunities Grid */}
        {!loading && (searchResults ?? opportunities).length > 0 && (() => {
          const listToShow: DisplayOpportunity[] = searchResults ?? opportunities;
          return (
          <>
            <div className="mb-4">
              {isCuratedFromProfile && (
                <p className="text-xs text-gray-500 font-medium mb-1">Curated for your profile</p>
              )}
              <p className="text-sm text-gray-600 font-medium">
                {listToShow.length} {listToShow.length === 1 ? 'opportunity' : 'opportunities'} found
                {searchResults !== null && !isCuratedFromProfile && ' (semantic search)'}
                {searchResults !== null && isCuratedFromProfile && ' (curated)'}
              </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-1">
              {listToShow.map((opp, index) => (
                <Card
                  key={opp.opportunity_id}
                  variant="interactive"
                  onClick={() => setSelectedOpportunity(opp)}
                  className="animate-slide-up"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  {/* Card Header */}
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-xl font-semibold font-display text-gray-900 mb-2 leading-tight">
                        {opp.title}
                      </h3>
                      <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600">
                        {opp.lab_name && (
                          <span className="font-medium text-campus-600">{opp.lab_name}</span>
                        )}
                        {opp.pi_name && (
                          <>
                            <span className="text-gray-300">•</span>
                            <span>{opp.pi_name}</span>
                          </>
                        )}
                        {opp.institution && (
                          <>
                            <span className="text-gray-300">•</span>
                            <span>{opp.institution}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-shrink-0 ml-4 items-center gap-2">
                      {hasSimilarityScore(opp) && (
                        <Badge variant="primary" size="md">
                          {Math.round(opp.similarity_score * 100)}% match
                        </Badge>
                      )}
                      {opp.deadline && isDeadlineSoon(opp.deadline) && (
                        <Badge variant="danger" size="md" className="animate-float">
                          Deadline Soon
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-gray-700 mb-4 line-clamp-3 leading-relaxed">
                    {opp.description}
                  </p>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {opp.research_topics?.slice(0, 4).map((topic, idx) => (
                      <Badge key={idx} variant="primary" size="sm">
                        {topic}
                      </Badge>
                    ))}
                    {opp.research_topics && opp.research_topics.length > 4 && (
                      <Badge variant="secondary" size="sm">
                        +{opp.research_topics.length - 4} more
                      </Badge>
                    )}
                  </div>

                  {/* Footer */}
                  <div className="flex justify-between items-center pt-4 border-t border-gray-100">
                    <div className="flex gap-6 text-sm text-gray-600">
                      {opp.funding_status && (
                        <div className="flex items-center gap-1.5">
                          <svg className="w-4 h-4 text-mint-500" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                          </svg>
                          <span className="font-medium capitalize">{opp.funding_status}</span>
                        </div>
                      )}
                      {opp.deadline && (
                        <div className="flex items-center gap-1.5">
                          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <span>{formatDate(opp.deadline)}</span>
                        </div>
                      )}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedOpportunity(opp);
                      }}
                      className="text-campus-600 hover:text-campus-700 font-semibold text-sm flex items-center gap-1 transition-colors duration-150"
                    >
                      View Details
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  </div>
                </Card>
              ))}
            </div>
          </>
          );
        })()}
      </main>

      {/* Opportunity Detail Modal */}
      <Modal
        isOpen={!!selectedOpportunity}
        onClose={() => setSelectedOpportunity(null)}
        title={selectedOpportunity?.title}
        size="lg"
      >
        {selectedOpportunity && (
          <div className="space-y-6">
            {/* Institution & Lab Info */}
            <div className="flex flex-wrap gap-3 text-sm text-gray-600 pb-6 border-b border-gray-100">
              {selectedOpportunity.lab_name && (
                <span className="font-semibold text-campus-600">{selectedOpportunity.lab_name}</span>
              )}
              {selectedOpportunity.pi_name && (
                <>
                  <span className="text-gray-300">•</span>
                  <span>{selectedOpportunity.pi_name}</span>
                </>
              )}
              {selectedOpportunity.institution && (
                <>
                  <span className="text-gray-300">•</span>
                  <span className="font-medium">{selectedOpportunity.institution}</span>
                </>
              )}
            </div>

            {/* Description */}
            <div>
              <h3 className="text-lg font-semibold font-display text-gray-900 mb-3">Description</h3>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{selectedOpportunity.description}</p>
            </div>

            {/* Research Topics */}
            {selectedOpportunity.research_topics && selectedOpportunity.research_topics.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold font-display text-gray-900 mb-3">Research Topics</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedOpportunity.research_topics.map((topic, idx) => (
                    <Badge key={idx} variant="primary" size="md">
                      {topic}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Methods & Techniques */}
            {selectedOpportunity.methods && selectedOpportunity.methods.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold font-display text-gray-900 mb-3">Methods & Techniques</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedOpportunity.methods.map((method, idx) => (
                    <Badge key={idx} variant="success" size="md">
                      {method}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Details Grid */}
            <div className="grid grid-cols-2 gap-6 py-6 border-t border-gray-100">
              {selectedOpportunity.deadline && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Deadline</h4>
                  <p className="text-gray-900 font-medium">{formatDate(selectedOpportunity.deadline)}</p>
                </div>
              )}
              {selectedOpportunity.funding_status && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Funding Status</h4>
                  <p className="text-gray-900 font-medium capitalize">{selectedOpportunity.funding_status}</p>
                </div>
              )}
              {selectedOpportunity.experience_required && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Experience Required</h4>
                  <p className="text-gray-900 font-medium capitalize">{selectedOpportunity.experience_required}</p>
                </div>
              )}
              {selectedOpportunity.contact_email && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Contact</h4>
                  <a
                    href={`mailto:${selectedOpportunity.contact_email}`}
                    className="text-campus-600 hover:text-campus-700 font-medium transition-colors duration-150"
                  >
                    {selectedOpportunity.contact_email}
                  </a>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-6 border-t border-gray-100">
              {selectedOpportunity.application_link && (
                <Button
                  as="a"
                  href={selectedOpportunity.application_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  variant="primary"
                  size="lg"
                  fullWidth
                  rightIcon={
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  }
                >
                  Apply Now
                </Button>
              )}
              <Button
                as="a"
                href={('source_url' in selectedOpportunity ? selectedOpportunity.source_url : null) ?? selectedOpportunity.application_link ?? '#'}
                target="_blank"
                rel="noopener noreferrer"
                variant="secondary"
                size="lg"
                fullWidth={!selectedOpportunity.application_link}
                rightIcon={
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                }
              >
                View Source
              </Button>
            </div>

            {/* Generate Email */}
            <div className="pt-6 border-t border-gray-100">
              <Button
                type="button"
                onClick={handleGenerateEmail}
                disabled={emailGenerating}
                variant="secondary"
                size="lg"
                fullWidth
              >
                {emailGenerating ? 'Generating...' : 'Generate Email'}
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default DashboardNeo;

