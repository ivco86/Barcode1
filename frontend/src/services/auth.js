import api from './api';

export const login = async (username, password) => {
  const response = await api.post('/auth/login', { username, password });
  const { access_token, tenant, user } = response.data;

  localStorage.setItem('token', access_token);
  localStorage.setItem('tenant', JSON.stringify(tenant));
  localStorage.setItem('user', JSON.stringify(user));

  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('tenant');
  localStorage.removeItem('user');
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};

export const getCurrentUser = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

export const getCurrentTenant = () => {
  const tenant = localStorage.getItem('tenant');
  return tenant ? JSON.parse(tenant) : null;
};
