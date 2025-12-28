import { Component, inject, signal, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink, Router } from '@angular/router';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService, Project, Video } from '../services/api.service';
import { ThemeService } from '../services/theme.service';

@Component({
  selector: 'app-project-detail',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink, DatePipe],
  template: `
    <div class="flex h-screen bg-white dark:bg-slate-950 overflow-hidden transition-colors duration-300">
      <!-- Sidebar (Shared) -->
      <aside class="hidden md:flex w-64 flex-col bg-gray-50 dark:bg-slate-900 border-r border-gray-200 dark:border-slate-800 transition-colors duration-300">
        <div class="p-4 border-b border-gray-200 dark:border-slate-800 flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-amber-600 flex items-center justify-center text-white font-bold shadow-sm">V</div>
          <span class="font-bold text-gray-900 dark:text-white">VidGen AI</span>
        </div>
        
        <div class="p-3">
          <a routerLink="/dashboard" class="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-lg transition-colors border border-transparent hover:border-gray-200 dark:hover:border-slate-700/50">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            New Project
          </a>
        </div>

        <div class="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <h3 class="px-3 text-xs font-medium text-gray-500 dark:text-slate-500 uppercase tracking-wider mb-2">History</h3>
          @for (p of api.projects(); track p._id) {
            <a [routerLink]="['/projects', p._id]" 
               [class.bg-gray-200]="p._id === project()?._id"
               [class.dark:bg-slate-800]="p._id === project()?._id"
               [class.text-gray-900]="p._id === project()?._id"
               [class.dark:text-white]="p._id === project()?._id"
               class="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-slate-800 rounded-lg transition-colors truncate group">
              <svg class="w-4 h-4 text-gray-400 dark:text-slate-600 group-hover:text-gray-600 dark:group-hover:text-slate-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span class="truncate">{{ p.name }}</span>
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

      <!-- Main Chat Interface -->
      <main class="flex-1 flex flex-col h-full relative">
        <!-- Chat Header -->
        <header class="h-14 border-b border-gray-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/50 backdrop-blur flex items-center justify-between px-4 z-10 transition-colors">
          <div class="flex items-center gap-3">
             <div class="md:hidden">
               <a routerLink="/dashboard" class="text-gray-500 dark:text-slate-400"><svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg></a>
             </div>
             <h2 class="font-semibold text-gray-900 dark:text-white truncate max-w-[200px] sm:max-w-md">{{ project()?.name }}</h2>
          </div>
          <button (click)="deleteProject()" class="text-gray-400 hover:text-red-500 dark:text-slate-500 dark:hover:text-red-400 transition-colors">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </header>

        <!-- Chat Stream -->
        <div class="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth" #scrollContainer>
           @for (video of videos(); track video._id) {
             <!-- User Prompt Bubble -->
             <div class="flex justify-end">
               <div class="max-w-[85%] sm:max-w-[70%] bg-amber-100 dark:bg-slate-800 rounded-2xl rounded-tr-sm px-4 py-3 text-gray-900 dark:text-slate-200 shadow-sm dark:shadow-none">
                 <p>{{ video.topic }}</p>
                 <div class="mt-1 flex items-center justify-end gap-2 text-xs text-gray-500 dark:text-slate-500">
                    <span>{{ video.video_config?.aspect_ratio || "9:16" }}</span>
                    <span>•</span>
                    <span class="capitalize">{{ video.generator_id?.replace('_', ' ') || 'unknown' }}</span>
                    @if (video.video_config?.duration) {
                      <span>•</span>
                      <span class="capitalize">{{ video.video_config?.duration }}</span>
                    }
                 </div>
               </div>
             </div>

             <!-- AI Response Bubble -->
             <div class="flex justify-start">
                <div class="flex gap-3 max-w-[90%] sm:max-w-[80%]">
                   <div class="w-8 h-8 rounded-full bg-amber-600/10 dark:bg-amber-600/20 flex-shrink-0 flex items-center justify-center">
                     <span class="text-amber-600 dark:text-amber-500 text-xs font-bold">AI</span>
                   </div>
                   <div class="space-y-2 w-full">
                      <!-- Video Processing State -->
                      <div class="bg-transparent border border-gray-200 dark:border-slate-800 rounded-xl p-4 w-full">
                         @if (video.status === 'completed') {
                            <!-- Video Player -->
                            <video controls class="w-full rounded-lg bg-black aspect-video mb-3" [poster]="'https://picsum.photos/800/450?random=' + video._id">
                               <source [src]="video.video_url" type="video/mp4">
                               Your browser does not support the video tag.
                            </video>
                            <div class="flex items-center justify-between">
                               <span class="text-green-600 dark:text-green-400 text-xs font-medium flex items-center gap-1">
                                  <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                  Completed
                               </span>
                               <a [href]="video.video_url" target="_blank" class="text-xs text-amber-600 hover:text-amber-500 dark:text-amber-400 dark:hover:text-white transition-colors">Download MP4</a>
                            </div>
                         } @else if (video.status === 'failed') {
                            <div class="flex items-center gap-2 text-red-500 dark:text-red-400">
                               <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                               <span>Generation failed</span>
                            </div>
                         } @else {
                            <div class="flex items-center gap-3 py-2">
                               <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-amber-500 dark:border-amber-500"></div>
                               <div class="text-sm text-gray-600 dark:text-slate-300">
                                  {{ video.status === 'pending' ? 'Queued for generation...' : 'Rendering video...' }}
                               </div>
                            </div>
                         }

                         <!-- Script Preview -->
                         @if (video.current_step) {
                           <div class="mt-3 p-3 bg-gray-50 dark:bg-slate-900/50 rounded-lg text-sm text-gray-600 dark:text-slate-400 italic border-l-2 border-gray-300 dark:border-slate-700">
                             "{{ video.current_step }}"
                           </div>
                         }
                      </div>
                   </div>
                </div>
             </div>
           }
        </div>

        <!-- Input Area -->
        <div class="p-4 bg-white dark:bg-slate-950 border-t border-gray-200 dark:border-slate-800 transition-colors">
           <form [formGroup]="chatForm" (ngSubmit)="sendMessage()" class="max-w-4xl mx-auto relative">
              <div class="absolute left-3 bottom-3 flex gap-2">
                 <select formControlName="category" class="bg-gray-100 dark:bg-slate-900 border-none text-xs text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white rounded py-1 px-2 focus:ring-0 cursor-pointer transition-colors max-w-[120px]">
                     <option value="explainer_shorts">Explainer</option>
                     <option value="frequency_generator">Frequency</option>
                     <option value="subliminal">Subliminal</option>
                 </select>

                 @if (chatForm.get('category')?.value === 'explainer_shorts') {
                  <select formControlName="style" class="bg-gray-100 dark:bg-slate-900 border-none text-xs text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white rounded py-1 px-2 focus:ring-0 cursor-pointer transition-colors">
                      <option value="family_guy">Family Guy</option>
                      <option value="rick_morty">Rick & Morty</option>
                      <option value="south_park">South Park</option>
                      <option value="documentary">Documentary</option>
                      <option value="pixel_art">Pixel Art</option>
                   </select>
                 }

                 @if (chatForm.get('category')?.value === 'subliminal') {
                    <select formControlName="duration" class="bg-gray-100 dark:bg-slate-900 border-none text-xs text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white rounded py-1 px-2 focus:ring-0 cursor-pointer transition-colors">
                      <option value="short">Short</option>
                      <option value="long">Long</option>
                    </select>
                 }

                  <select formControlName="aspectRatio" class="bg-gray-100 dark:bg-slate-900 border-none text-xs text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white rounded py-1 px-2 focus:ring-0 cursor-pointer transition-colors">
                    <option value="16:9">16:9</option>
                    <option value="9:16">9:16</option>
                    <option value="1:1">1:1</option>
                 </select>
              </div>
              
              <textarea 
                 formControlName="prompt"
                 (keydown.enter)="$event.preventDefault(); sendMessage()"
                 placeholder="Message VidGen AI..." 
                 class="w-full bg-gray-50 dark:bg-slate-900 text-gray-900 dark:text-white rounded-xl border border-gray-300 dark:border-slate-800 pl-4 pr-12 pt-3 pb-10 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50 resize-none shadow-lg dark:shadow-none transition-colors"
                 rows="1"
                 style="min-height: 54px;"
              ></textarea>
              
              <button type="submit" [disabled]="chatForm.invalid || isProcessing()" class="absolute right-2 bottom-3 p-1.5 bg-amber-600 text-white rounded-lg hover:bg-amber-500 disabled:opacity-50 transition-colors">
                 @if (isProcessing()) {
                    <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                 } @else {
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/></svg>
                 }
              </button>
           </form>
           <p class="text-center text-xs text-gray-500 dark:text-slate-600 mt-2">VidGen AI can make mistakes. Consider checking important information.</p>
        </div>
      </main>
    </div>
  `
})
export class ProjectDetailComponent implements OnInit, OnDestroy, AfterViewChecked {
  public api: ApiService = inject(ApiService);
  public router: Router = inject(Router);
  public themeService: ThemeService = inject(ThemeService);
  private route: ActivatedRoute = inject(ActivatedRoute);
  private fb: FormBuilder = inject(FormBuilder);

  @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

  project = signal<Project | null>(null);
  videos = signal<Video[]>([]);
  isProcessing = signal(false);
  private pollInterval: any;
  private shouldScroll = false;

  chatForm = this.fb.group({
    prompt: ['', Validators.required],
    category: ['explainer_shorts'],
    style: ['family_guy'],
    aspectRatio: ['16:9'],
    duration: ['short']
  });

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.loadProject(id);
      }
    });
  }

  ngOnDestroy() {
    if (this.pollInterval) clearInterval(this.pollInterval);
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) {
        this.scrollToBottom();
        this.shouldScroll = false;
    }
  }

  scrollToBottom(): void {
    try {
        this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }

  async loadProject(id: string) {
    if (this.pollInterval) clearInterval(this.pollInterval);
    
    try {
      const p = await this.api.getProject(id);
      this.project.set(p);
      await this.refreshHistory();
      this.startPolling(id);
      this.shouldScroll = true;
    } catch (err) {
      console.error(err);
      this.router.navigate(['/dashboard']);
    }
  }

  async refreshHistory() {
    if (!this.project()) return;
    const v = await this.api.getProjectHistory(this.project()!._id);
    if (v.length > this.videos().length) this.shouldScroll = true;
    this.videos.set(v);
  }

  startPolling(id: string) {
    this.pollInterval = setInterval(() => this.refreshHistory(), 3000);
  }

  async sendMessage() {
    if (this.chatForm.invalid || this.isProcessing() || !this.project()) return;

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
      await this.api.generateVideo({
        project_id: this.project()!._id,
        generator_id: generatorId,
        topic: prompt!,
        aspect_ratio: aspectRatio!,
        duration: duration!,
        output_format: 'mp4',
        quality: '1080p'
      });
      this.chatForm.patchValue({ prompt: '' });
      await this.refreshHistory();
      this.shouldScroll = true;
    } catch (err) {
      console.error(err);
    } finally {
      this.isProcessing.set(false);
    }
  }

  async deleteProject() {
    if (!this.project() || !confirm('Are you sure you want to delete this chat?')) return;
    try {
      await this.api.deleteProject(this.project()!._id);
      this.router.navigate(['/dashboard']);
    } catch (err) {
      console.error(err);
    }
  }
}


