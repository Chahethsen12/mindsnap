import api from './api'

export const createSnap = (data) => api.post('/snaps/', data)
export const getSnaps = () => api.get('/snaps/')
export const searchSnaps = (q) => api.get(`/snaps/search?q=${q}`)
export const deleteSnap = (id) => api.delete(`/snaps/${id}`)