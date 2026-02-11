import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Adjust if backend runs on different port

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const debateService = {
  createDebate: async (topic) => {
    const response = await api.post('/debates', { topic, max_rounds: 3 });
    return response.data;
  },

  startDebate: async (debateId) => {
    const response = await api.post(`/debates/${debateId}/start`);
    return response.data;
  },

  getDebate: async (debateId) => {
    const response = await api.get(`/debates/${debateId}`);
    return response.data;
  },
};
