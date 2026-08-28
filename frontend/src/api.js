import axios from 'axios';

const api = axios.create({
  baseURL: '/api'
});

export const analyzeUrl = (url) => api.post('/analyze/url', { url }).then(res => res.data);
export const analyzeText = (text, type) => api.post('/analyze/text', { text, type }).then(res => res.data);
export const analyzeQr = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/analyze/qr', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then(res => res.data);
};
export const getHistory = () => api.get('/history').then(res => res.data);
export const reportThreat = (scanId, comment) => api.post('/report', { scan_id: scanId, comment }).then(res => res.data);
