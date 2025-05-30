export type User = {
  id: string;
  first_name: string;
  last_name: string | null;
  nickname: string;
  email: string;
  role: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
};

export type UserResponseLogin = {
  refresh: string;
  access: string;
  user: Pick<User, "id" | "email" | "nickname" | "is_active">;
};

export type AuthState = {
  currentUser?: User | null;
  isAuthenticated: boolean;
  loading: boolean;
};
