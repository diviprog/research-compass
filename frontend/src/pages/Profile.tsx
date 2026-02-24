/**
 * Profile page – edit your research profile (used for outreach email generation).
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ProfileService } from '../services/profile';
import type { ProfileResponse, ProfileUpdate } from '../services/profile';
import { AxiosError } from 'axios';
import { Card, Button, Input, Badge } from '../components/neo';
import { formatApiErrorDetail } from '../utils/apiError';

const EXPERIENCE_LEVELS = ['undergraduate', 'graduate', 'postdoc', 'independent'] as const;

export const Profile: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [resumeSuccess, setResumeSuccess] = useState<string | null>(null);
  const [resumeError, setResumeError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [form, setForm] = useState({
    name: '',
    research_interests: '',
    university: '',
    major: '',
    graduation_year: '',
    experience_level: 'undergraduate',
  });
  /** Read-only skills from profile (on load) or from latest resume parse (after upload). */
  const [displayedSkills, setDisplayedSkills] = useState<string[]>([]);

  useEffect(() => {
    let cancelled = false;
    ProfileService.getProfile()
      .then((data) => {
        if (!cancelled) {
          setProfile(data);
          setForm({
            name: data.name ?? '',
            research_interests: data.research_interests ?? '',
            university: data.university ?? '',
            major: data.major ?? '',
            graduation_year: data.graduation_year != null ? String(data.graduation_year) : '',
            experience_level: data.experience_level ?? 'undergraduate',
          });
          setDisplayedSkills(Array.isArray(data.skills) ? data.skills : []);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          const axiosError = err as AxiosError<{ detail?: unknown }>;
          setError(
            axiosError.response?.data != null
              ? formatApiErrorDetail(axiosError.response.data)
              : 'Failed to load profile.'
          );
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setError(null);
    setSuccess(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload: ProfileUpdate = {
      name: form.name.trim() || undefined,
      research_interests: form.research_interests.trim().length >= 10 ? form.research_interests.trim() : undefined,
      university: form.university.trim() || undefined,
      major: form.major.trim() || undefined,
      graduation_year: form.graduation_year ? parseInt(form.graduation_year, 10) : undefined,
      experience_level: form.experience_level,
    };
    if (payload.research_interests === undefined && !profile?.research_interests) {
      setError('Research interests are required (at least 10 characters) for generating outreach emails.');
      return;
    }
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const updated = await ProfileService.updateProfile(payload);
      setProfile(updated);
      setSuccess(true);
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: unknown }>;
      setError(
        axiosError.response?.data != null
          ? formatApiErrorDetail(axiosError.response.data)
          : 'Failed to save profile.'
      );
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/signin');
  };

  const handleResumeUpload = async () => {
    if (!selectedFile) return;
    setUploadingResume(true);
    setResumeError(null);
    setResumeSuccess(null);
    try {
      const response = await ProfileService.uploadResume(selectedFile);
      const parsed = response.parsed_data || {};
      const education = parsed.education || {};
      const researchSummary = typeof parsed.research_summary === 'string' ? parsed.research_summary.trim() : '';
      const university = education.university != null ? String(education.university).trim() : '';
      const major = education.major != null ? String(education.major).trim() : '';
      const graduationYear = education.graduation_year != null ? String(education.graduation_year) : '';
      setForm((prev) => ({
        ...prev,
        research_interests: researchSummary || prev.research_interests,
        university: university || prev.university,
        major: major || prev.major,
        graduation_year: graduationYear || prev.graduation_year,
      }));
      const skills = Array.isArray(parsed.skills) ? parsed.skills : [];
      setDisplayedSkills(skills);
      const updated = await ProfileService.getProfile();
      setProfile(updated);
      setResumeSuccess('Resume parsed — research summary and education auto-filled. Review and save.');
      setSelectedFile(null);
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: unknown }>;
      setResumeError(
        axiosError.response?.data != null
          ? formatApiErrorDetail(axiosError.response.data)
          : 'Upload failed. Please try again.'
      );
    } finally {
      setUploadingResume(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 font-body flex items-center justify-center">
        <p className="text-gray-600">Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 font-body">
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
                to="/dashboard"
                className="text-sm font-medium text-gray-600 hover:text-gray-900"
              >
                Dashboard
              </Link>
              <span className="text-sm text-gray-600 hidden sm:inline">
                <span className="font-semibold text-gray-900">{user?.name}</span>
              </span>
              <Button onClick={handleLogout} variant="ghost" size="sm">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-2xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h2 className="text-4xl font-bold font-display text-gray-900 mb-2 tracking-tight">
            My Profile
          </h2>
          <p className="text-lg text-gray-600">
            Customize your profile so we can personalize outreach emails when you use “Generate Email” on an opportunity.
          </p>
        </div>

        <Card variant="outlined" className="p-6">
          {/* Upload Resume section */}
          <div className="mb-8 pb-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold font-display text-gray-900 mb-3">Upload Resume</h3>
            <div className="flex flex-wrap items-end gap-3">
              <div>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    setSelectedFile(f || null);
                    setResumeError(null);
                    setResumeSuccess(null);
                  }}
                  className="block w-full text-sm text-gray-900 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border file:border-gray-200 file:bg-white file:text-gray-700"
                />
              </div>
              <Button
                type="button"
                onClick={handleResumeUpload}
                disabled={uploadingResume || !selectedFile}
                variant="secondary"
                size="md"
              >
                {uploadingResume ? 'Parsing...' : 'Upload & Parse'}
              </Button>
            </div>
            {resumeSuccess && (
              <div className="mt-3 rounded-md bg-green-50 p-3 text-sm text-green-800">
                {resumeSuccess}
              </div>
            )}
            {resumeError && (
              <div className="mt-3 rounded-md bg-red-50 p-3 text-sm text-red-800">
                {resumeError}
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="rounded-md bg-red-50 p-4 text-sm text-red-800">
                {error}
              </div>
            )}
            {success && (
              <div className="rounded-md bg-green-50 p-4 text-sm text-green-800">
                Profile saved.
              </div>
            )}

            <div>
              <label htmlFor="name" className="block text-sm font-semibold text-gray-700 mb-1.5">
                Display name
              </label>
              <Input
                id="name"
                name="name"
                type="text"
                value={form.name}
                onChange={handleChange}
                placeholder="Your name"
                fullWidth
              />
            </div>

            <div>
              <label htmlFor="research_interests" className="block text-sm font-semibold text-gray-700 mb-1.5">
                Research interests <span className="text-gray-500 font-normal">(required for Generate Email, min 10 characters)</span>
              </label>
              <textarea
                id="research_interests"
                name="research_interests"
                value={form.research_interests}
                onChange={handleChange}
                placeholder="e.g. I am interested in machine learning for healthcare and interpretable AI."
                rows={4}
                className="block w-full rounded-lg border border-gray-200 bg-white text-gray-900 placeholder-gray-500 px-3 py-2.5 text-base focus:outline-none focus:ring-2 focus:ring-campus-500 focus:border-campus-500"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                Skills <span className="text-gray-500 font-normal">(from resume, read-only)</span>
              </label>
              {displayedSkills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {displayedSkills.map((skill) => (
                    <Badge key={skill} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No skills extracted yet. Upload a resume to see skills.</p>
              )}
            </div>

            <div>
              <label htmlFor="university" className="block text-sm font-semibold text-gray-700 mb-1.5">
                University
              </label>
              <Input
                id="university"
                name="university"
                type="text"
                value={form.university}
                onChange={handleChange}
                placeholder="e.g. UCLA"
                fullWidth
              />
            </div>

            <div>
              <label htmlFor="major" className="block text-sm font-semibold text-gray-700 mb-1.5">
                Major / field
              </label>
              <Input
                id="major"
                name="major"
                type="text"
                value={form.major}
                onChange={handleChange}
                placeholder="e.g. Computer Science"
                fullWidth
              />
            </div>

            <div>
              <label htmlFor="graduation_year" className="block text-sm font-semibold text-gray-700 mb-1.5">
                Graduation year
              </label>
              <Input
                id="graduation_year"
                name="graduation_year"
                type="text"
                value={form.graduation_year}
                onChange={handleChange}
                placeholder="e.g. 2026"
                fullWidth
              />
            </div>

            <div>
              <label htmlFor="experience_level" className="block text-sm font-semibold text-gray-700 mb-1.5">
                Experience level
              </label>
              <select
                id="experience_level"
                name="experience_level"
                value={form.experience_level}
                onChange={handleChange}
                className="block w-full rounded-lg border border-gray-200 bg-white text-gray-900 px-3 py-2.5 text-base focus:outline-none focus:ring-2 focus:ring-campus-500 focus:border-campus-500"
              >
                {EXPERIENCE_LEVELS.map((level) => (
                  <option key={level} value={level}>
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex gap-3 pt-4">
              <Button type="submit" disabled={saving} size="lg">
                {saving ? 'Saving...' : 'Save profile'}
              </Button>
              <Button type="button" onClick={() => navigate('/dashboard')} variant="secondary" size="lg">
                Back to Dashboard
              </Button>
            </div>
          </form>
        </Card>
      </main>
    </div>
  );
};

export default Profile;
