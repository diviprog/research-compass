/**
 * Opportunities service for fetching research opportunities.
 */

import api from './auth';

export interface Opportunity {
  opportunity_id: number;
  source_url: string;
  scraped_at: string;
  last_updated: string;
  title: string;
  description: string;
  lab_name: string | null;
  pi_name: string | null;
  institution: string | null;
  research_topics: string[];
  methods: string[];
  datasets: string[];
  deadline: string | null;
  funding_status: string | null;
  experience_required: string | null;
  contact_email: string | null;
  application_link: string | null;
  is_active: boolean;
}

export interface OpportunityListParams {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  search?: string;
  institution?: string;
  funding_status?: string;
}

/**
 * Opportunities API service
 */
export const OpportunitiesService = {
  /**
   * Get list of opportunities with optional filters
   */
  async getOpportunities(params?: OpportunityListParams): Promise<Opportunity[]> {
    const queryParams = new URLSearchParams();
    
    if (params?.skip !== undefined) {
      queryParams.append('skip', params.skip.toString());
    }
    if (params?.limit !== undefined) {
      queryParams.append('limit', params.limit.toString());
    }
    if (params?.is_active !== undefined) {
      queryParams.append('is_active', params.is_active.toString());
    }
    if (params?.search) {
      queryParams.append('search', params.search);
    }
    if (params?.institution) {
      queryParams.append('institution', params.institution);
    }
    if (params?.funding_status) {
      queryParams.append('funding_status', params.funding_status);
    }

    const queryString = queryParams.toString();
    const url = `/opportunities${queryString ? `?${queryString}` : ''}`;
    
    const response = await api.get<Opportunity[]>(url);
    return response.data;
  },

  /**
   * Get a single opportunity by ID
   */
  async getOpportunity(id: number): Promise<Opportunity> {
    const response = await api.get<Opportunity>(`/opportunities/${id}`);
    return response.data;
  },

  /**
   * Create a new opportunity (for admin/scraper)
   */
  async createOpportunity(data: Partial<Opportunity>): Promise<Opportunity> {
    const response = await api.post<Opportunity>('/opportunities', data);
    return response.data;
  },

  /**
   * Update an opportunity
   */
  async updateOpportunity(id: number, data: Partial<Opportunity>): Promise<Opportunity> {
    const response = await api.put<Opportunity>(`/opportunities/${id}`, data);
    return response.data;
  },

  /**
   * Delete an opportunity (soft delete)
   */
  async deleteOpportunity(id: number): Promise<void> {
    await api.delete(`/opportunities/${id}`);
  }
};

export default OpportunitiesService;

