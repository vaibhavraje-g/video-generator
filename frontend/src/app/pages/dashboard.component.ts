import { Component, inject, signal } from '@angular/core';
import { RouterLink, Router } from '@angular/router';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService, Project } from '../services/api.service';
import { ThemeService } from '../services/theme.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterLink, ReactiveFormsModule, CommonModule],
  template: `
    <div class="flex h-screen bg-white dark:bg-slate-950 overflow-hidden transition-colors duration-300">
      <!-- Sidebar -->
      <aside class="hidden md:flex w-64 flex-col bg-gray-50 dark:bg-slate-900 border-r border-gray-200 dark:border-slate-800 transition-colors duration-300">
        <div class="p-4 border-b border-gray-200 dark:border-slate-800 flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-amber-600 flex items-center justify-center text-white font-bold shadow-sm">V</div>
          <span class="font-bold text-gray-900 dark:text-white">VidGen AI</span>
        </div>
        
        <div class="p-3">
          <a routerLink="/dashboard" class="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 dark:text-slate-300 bg-white dark:bg-slate-800 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors border border-gray-200 dark:border-slate-700 shadow-sm">
            <svg class="w-4 h-4 text-amber-600 dark:text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            New Project
          </a>
        </div>

        <div class="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <h3 class="px-3 text-xs font-medium text-gray-500 dark:text-slate-500 uppercase tracking-wider mb-2">History</h3>
          @for (project of api.projects(); track project._id) {
            <a [routerLink]="['/projects', project._id]" 
               class="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-slate-800 rounded-lg transition-colors truncate group">
              <svg class="w-4 h-4 text-gray-400 dark:text-slate-600 group-hover:text-gray-600 dark:group-hover:text-slate-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span class="truncate">{{ project.name }}</span>
            </a>
          }
        </div>

        <div class="p-4 border-t border-gray-200 dark:border-slate-800 space-y-2">
           <!-- Theme Toggle -->
           <button (click)="themeService.toggle()" class="flex items-center gap-2 text-sm text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white w-full transition-colors px-2 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800">
             @if (themeService.isDark()) {
               <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
               </svg>
               <span>Light Mode</span>
             } @else {
               <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
               </svg>
               <span>Dark Mode</span>
             }
           </button>

          <button (click)="api.logout(); router.navigate(['/login'])" class="flex items-center gap-2 text-sm text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white w-full transition-colors px-2 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign Out
          </button>
        </div>
      </aside>

      <!-- Main Content (New Chat State) -->
      <main class="flex-1 flex flex-col relative h-full">
        <!-- Mobile Header -->
        <div class="md:hidden flex items-center justify-between p-4 border-b border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <span class="font-bold text-gray-900 dark:text-white">VidGen AI</span>
          <button (click)="themeService.toggle()" class="text-gray-600 dark:text-slate-400">
            @if (themeService.isDark()) {
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
             } @else {
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
             }
          </button>
        </div>

        <div class="flex-1 flex flex-col items-center justify-center p-4 overflow-y-auto">
          <div class="w-full max-w-3xl space-y-8 text-center">
             <div class="space-y-4">
                <div class="w-16 h-16 bg-gray-100 dark:bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm">
                  <svg class="w-8 h-8 text-amber-600 dark:text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                </div>
                <h1 class="text-3xl font-bold text-gray-900 dark:text-white">What can I create for you?</h1>
             </div>

             <div class="bg-white dark:bg-slate-900/50 p-6 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-xl dark:shadow-none backdrop-blur-sm">
                <form [formGroup]="chatForm" (ngSubmit)="startChat()" class="space-y-4">
                  <textarea 
                    formControlName="prompt"
                    (keydown.enter)="$event.preventDefault(); startChat()"
                    placeholder="Describe the video you want to generate..." 
                    class="w-full bg-gray-50 dark:bg-slate-950 border border-gray-300 dark:border-slate-700 rounded-xl p-4 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-slate-500 focus:ring-2 focus:ring-amber-500 dark:focus:ring-amber-500 focus:border-transparent resize-none h-32 transition-colors"
                  ></textarea>

                  <div class="flex flex-col md:flex-row gap-4 items-center justify-between">
                     <div class="flex flex-wrap gap-2 w-full md:w-auto">
                        <!-- Category Select -->
                        <select formControlName="category" class="bg-gray-50 dark:bg-slate-950 border border-gray-300 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-gray-700 dark:text-slate-300 focus:ring-amber-500 dark:focus:ring-amber-500">
                           <option value="explainer_shorts">Explainer Shorts</option>
                           <option value="frequency_generator">Frequency Generator</option>
                           <option value="subliminal">Subliminal Videos</option>
                        </select>

                        <!-- Style Select (Only for Explainer Shorts) -->
                        @if (chatForm.get('category')?.value === 'explainer_shorts') {
                          <select formControlName="style" class="bg-gray-50 dark:bg-slate-950 border border-gray-300 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-gray-700 dark:text-slate-300 focus:ring-amber-500 dark:focus:ring-amber-500">
                            <option value="family_guy">Family Guy</option>
                            <option value="rick_morty">Rick & Morty</option>
                            <option value="south_park">South Park</option>
                            <option value="documentary">Documentary</option>
                            <option value="pixel_art">Pixel Art</option>
                          </select>
                        }

                        <!-- Duration Select (Only for Subliminal) -->
                        @if (chatForm.get('category')?.value === 'subliminal') {
                          <select formControlName="duration" class="bg-gray-50 dark:bg-slate-950 border border-gray-300 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-gray-700 dark:text-slate-300 focus:ring-amber-500 dark:focus:ring-amber-500">
                            <option value="short">Short (1 min)</option>
                            <option value="long">Long (10 mins)</option>
                          </select>
                        }
                        
                        <select formControlName="aspectRatio" class="bg-gray-50 dark:bg-slate-950 border border-gray-300 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-gray-700 dark:text-slate-300 focus:ring-amber-500 dark:focus:ring-amber-500">
                          <option value="16:9">16:9 Landscape</option>
                          <option value="9:16">9:16 Vertical</option>
                          <option value="1:1">1:1 Square</option>
                        </select>
                     </div>

                     <button type="submit" [disabled]="chatForm.invalid || isProcessing()" 
                       class="w-full md:w-auto bg-amber-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-amber-500 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-sm">
                       @if (isProcessing()) {
                         <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                       } @else {
                         <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                         </svg>
                       }
                       Generate
                     </button>
                  </div>
                </form>
             </div>
             
             <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-500 dark:text-slate-500">
                <button (click)="quickStart('Explain Quantum Physics')" class="p-3 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-800 hover:border-gray-300 dark:hover:border-slate-700 transition-all text-left shadow-sm dark:shadow-none">
                  "Explain Quantum Physics"
                </button>
                <button (click)="quickStart('Healing 528Hz Frequency')" class="p-3 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-800 hover:border-gray-300 dark:hover:border-slate-700 transition-all text-left shadow-sm dark:shadow-none">
                  "Healing 528Hz Frequency"
                </button>
                <button (click)="quickStart('Product launch trailer')" class="p-3 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-800 hover:border-gray-300 dark:hover:border-slate-700 transition-all text-left shadow-sm dark:shadow-none">
                  "Product launch trailer"
                </button>
                <button (click)="quickStart('Confidence Affirmations')" class="p-3 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-800 hover:border-gray-300 dark:hover:border-slate-700 transition-all text-left shadow-sm dark:shadow-none">
                  "Confidence Affirmations"
                </button>
             </div>
          </div>
        </div>
      </main>
    </div>
  `
})
export class DashboardComponent {
  public api: ApiService = inject(ApiService);
  public router: Router = inject(Router);
  public themeService: ThemeService = inject(ThemeService);
  private fb: FormBuilder = inject(FormBuilder);

  isProcessing = signal(false);

  chatForm = this.fb.group({
    prompt: ['', Validators.required],
    category: ['explainer_shorts'],
    style: ['family_guy'],
    aspectRatio: ['16:9'],
    duration: ['short']
  });

  quickStart(prompt: string) {
    this.chatForm.patchValue({ prompt });
    this.startChat();
  }

  async startChat() {
    if (this.chatForm.invalid || this.isProcessing()) return;

    this.isProcessing.set(true);
    const { prompt, category, style, aspectRatio, duration } = this.chatForm.value;
    
    // Map category to generator_id
    let generatorId = 'family_guy';
    if (category === 'explainer_shorts') {
      generatorId = style || 'family_guy';
    } else if (category === 'frequency_generator') {
      generatorId = 'frequency';
    } else if (category === 'subliminal') {
      generatorId = 'subliminal';
    }

    try {
      // Create project first
      const project = await this.api.createProject({ 
        name: (prompt || 'New Video').substring(0, 50),
        description: prompt || ''
      });
      
      // Then generate video
      await this.api.generateVideo({
        project_id: project._id,
        generator_id: generatorId,
        topic: prompt!,
        aspect_ratio: aspectRatio!,
        duration: duration!,
        output_format: 'mp4',
        quality: '1080p'
      });
      
      this.router.navigate(['/projects', project._id]);
    } catch (err) {
      console.error(err);
      alert('Failed to start project');
    } finally {
      this.isProcessing.set(false);
    }
  }
}