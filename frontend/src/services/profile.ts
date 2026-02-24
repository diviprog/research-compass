/**
 * Profile API service for fetching and updating the current user's profile.
 */

import api from './auth';

export interface ProfileResponse {
  user_id: number;
  email: string;
  name: string;
  university: string | null;
  major: string | null;
  graduation_year: number | null;
  gpa: string | null;
  resume_file_path: string | null;
  resume_text: string | null;
  past_experiences: unknown[];
  skills: string[];
  publications: unknown[];
  research_interests: string;
  preferred_methods: string[];
  preferred_datasets: string[];
  experience_level: string;
  location_preferences: string[];
  availability: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileUpdate {
  name?: string;
  university?: string;
  major?: string;
  graduation_year?: number;
  gpa?: string;
  resume_text?: string;
  past_experiences?: unknown[];
  skills?: string[];
  publications?: unknown[];
  research_interests?: string;
  preferred_methods?: string[];
  preferred_datasets?: string[];
  experience_level?: string;
  location_preferences?: string[];
  availability?: string;
}

/** Response shape from POST /profile/upload-resume */
export interface UploadResumeResponse {
  message: string;
  file_path: string;
  parsed_data: {
    skills?: string[];
    education?: {
      university?: string | null;
      major?: string | null;
      graduation_year?: number | null;
    };
    research_summary?: string | null;
    raw_text?: string;
    [key: string]: unknown;
  };
  parsing_status?: string;
  note?: string;
}

export const ProfileService = {
  async getProfile(): Promise<ProfileResponse> {
    const response = await api.get<ProfileResponse>('/profile');
    return response.data;
  },

  async updateProfile(data: ProfileUpdate): Promise<ProfileResponse> {
    const response = await api.patch<ProfileResponse>('/profile', data);
    return response.data;
  },

  async uploadResume(file: File): Promise<UploadResumeResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<UploadResumeResponse>('/profile/upload-resume', formData);
    return response.data;
  },
};
