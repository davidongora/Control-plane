import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Api, Project } from '../../services/api';

@Component({
  selector: 'app-projects',
  imports: [CommonModule],
  templateUrl: './projects.html',
  styleUrl: './projects.css',
})
export class Projects implements OnInit {
  projects: Project[] = [];
  loading = true;

  constructor(private api: Api) {}

  ngOnInit() {
    this.loadProjects();
  }

  loadProjects() {
    this.loading = true;
    this.api.getProjects().subscribe({
      next: (response) => {
        this.projects = response.results || response;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading projects:', err);
        this.loading = false;
      }
    });
  }
}
