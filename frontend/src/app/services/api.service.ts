import { Injectable, signal, computed } from '@angular/core';

export interface User {
  _id: string;
  email: string;
  username: string;
}

export interface Project {
  _id: string;
  user_id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  video_count?: number;
}

export interface Generator {
  id: string;
  display_name: string;
  description: string;
  supported_durations: string[];
  config_schema: Record<string, unknown>;
}

export interface VideoConfig {
  aspect_ratio: '9:16' | '1:1' | '16:9';
  duration: 'short' | 'long';
  output_format: 'mp4' | 'webm' | 'mov';
  quality: '720p' | '1080p' | '4k';
}

export interface Video {
  _id: string;
  project_id: string;
  user_id: string;
  topic: string;
  generator_id: string;
  video_config: VideoConfig | null;
  generator_config: Record<string, unknown> | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number | null;
  current_step: string | null;
  video_url: string | null;
  created_at: string;
  completed_at?: string;
  metadata?: Record<string, unknown>;
}

export interface GenerateVideoRequest {
  project_id: string;
  generator_id: string;
  topic: string;
  aspect_ratio: string;
  duration: string;
  output_format: string;
  quality: string;
  generator_config?: Record<string, unknown>;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly API_BASE = 'http://localhost:8001/api/v1';
  private readonly STORAGE_KEY_TOKEN = 'vidgen_token';
  private readonly STORAGE_KEY_USER = 'vidgen_user';

  currentUser = signal<User | null>(this.loadUser());
  isAuthenticated = computed(() => !!this.currentUser());
  
  // Cache for generators
  private generatorsCache = signal<Generator[]>([]);
  
  // Shared state for Sidebar
  projects = signal<Project[]>([]);

  constructor() {
    if (this.currentUser()) {
      this.refreshProjects();
      this.loadGenerators();
    }
  }

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem(this.STORAGE_KEY_TOKEN);
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
  }

  private loadUser(): User | null {
    const data = localStorage.getItem(this.STORAGE_KEY_USER);
    return data ? JSON.parse(data) : null;
  }

  // --- Auth Methods ---

  async login(email: string, password: string): Promise<{ access_token: string }> {
    const res = await fetch(`${this.API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    
    const data = await res.json();
    localStorage.setItem(this.STORAGE_KEY_TOKEN, data.access_token);
    
    // Fetch user info
    await this.fetchCurrentUser();
    this.refreshProjects();
    this.loadGenerators();
    
    return data;
  }

  async register(email: string, username: string, password: string): Promise<User> {
    const res = await fetch(`${this.API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, username, password })
    });
    
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    
    const user = await res.json();
    // Auto login after register
    await this.login(email, password);
    return user;
  }

  private async fetchCurrentUser(): Promise<void> {
    const res = await fetch(`${this.API_BASE}/auth/me`, {
      headers: this.getAuthHeaders()
    });
    
    if (res.ok) {
      const user = await res.json();
      localStorage.setItem(this.STORAGE_KEY_USER, JSON.stringify(user));
      this.currentUser.set(user);
    }
  }

  logout() {
    localStorage.removeItem(this.STORAGE_KEY_USER);
    localStorage.removeItem(this.STORAGE_KEY_TOKEN);
    this.currentUser.set(null);
    this.projects.set([]);
  }

  // --- Generator Methods ---

  async loadGenerators(): Promise<Generator[]> {
    try {
      const res = await fetch(`${this.API_BASE}/generators`, {
        headers: this.getAuthHeaders()
      });
      
      if (res.ok) {
        const generators = await res.json();
        this.generatorsCache.set(generators);
        return generators;
      }
    } catch (e) {
      console.error('Failed to load generators', e);
    }
    return [];
  }

  getGenerators(): Generator[] {
    return this.generatorsCache();
  }

  async getGenerator(id: string): Promise<Generator | null> {
    const res = await fetch(`${this.API_BASE}/generators/${id}`, {
      headers: this.getAuthHeaders()
    });
    
    if (res.ok) {
      return await res.json();
    }
    return null;
  }

  // --- Project Methods ---

  async refreshProjects(): Promise<Project[]> {
    try {
      const res = await fetch(`${this.API_BASE}/projects`, {
        headers: this.getAuthHeaders()
      });
      
      if (res.ok) {
        const projects = await res.json();
        this.projects.set(projects);
        return projects;
      }
    } catch (e) {
      console.error('Failed to load projects', e);
    }
    return [];
  }

  async getProjects(): Promise<Project[]> {
    return this.refreshProjects();
  }

  async getProject(id: string): Promise<Project> {
    const res = await fetch(`${this.API_BASE}/projects/${id}`, {
      headers: this.getAuthHeaders()
    });
    
    if (!res.ok) {
      throw new Error('Project not found');
    }
    
    return await res.json();
  }

  async createProject(data: { name: string; description?: string }): Promise<Project> {
    const res = await fetch(`${this.API_BASE}/projects`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
    
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create project');
    }
    
    const project = await res.json();
    this.refreshProjects();
    return project;
  }

  async deleteProject(id: string): Promise<void> {
    const res = await fetch(`${this.API_BASE}/projects/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
    
    if (!res.ok) {
      throw new Error('Failed to delete project');
    }
    
    this.refreshProjects();
  }

  // --- Video Methods ---

  async generateVideo(request: GenerateVideoRequest): Promise<Video> {
    const res = await fetch(`${this.API_BASE}/videos/generate`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(request)
    });
    
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to generate video');
    }
    
    return await res.json();
  }

  async getVideo(id: string): Promise<Video> {
    const res = await fetch(`${this.API_BASE}/videos/${id}`, {
      headers: this.getAuthHeaders()
    });
    
    if (!res.ok) {
      throw new Error('Video not found');
    }
    
    return await res.json();
  }

  async getProjectHistory(projectId: string): Promise<Video[]> {
    const res = await fetch(`${this.API_BASE}/projects/${projectId}/history`, {
      headers: this.getAuthHeaders()
    });
    
    if (res.ok) {
      return await res.json();
    }
    return [];
  }

  // Poll video status until complete or failed
  async pollVideoStatus(videoId: string, onProgress?: (video: Video) => void): Promise<Video> {
    const maxAttempts = 300; // 5 minutes max
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      const video = await this.getVideo(videoId);
      
      if (onProgress) {
        onProgress(video);
      }
      
      if (video.status === 'completed' || video.status === 'failed') {
        return video;
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      attempts++;
    }
    
    throw new Error('Video generation timed out');
  }
}