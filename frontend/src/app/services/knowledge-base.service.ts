import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '@environments/environment';

export interface KBStats {
  document_count: number;
  chunk_count: number;
  relationship_count: number;
  version_count: number;
}

export interface QualityMetrics {
  overall_score: number;
  coverage_score: number;
  coverage_metrics: {
    document_coverage: number;
    chunk_density: number;
    category_coverage: number;
    total_documents: number;
    total_chunks: number;
    avg_chunks_per_doc: number;
    categories: string[];
    category_distribution: Record<string, number>;
  };
  consistency_score: number;
  consistency_metrics: {
    metadata_consistency: number;
    content_similarity: number;
    version_consistency: number;
    metadata_completeness: number;
    version_distribution: Record<string, number>;
  };
  relevance_score: number;
  relevance_metrics: {
    source_credibility: number;
    content_type_relevance: number;
    source_distribution: Record<string, number>;
    type_distribution: Record<string, number>;
  };
  diversity_score: number;
  diversity_metrics: {
    category_diversity: number;
    length_diversity: number;
    source_diversity: number;
    category_distribution: Record<string, number>;
    source_distribution: Record<string, number>;
    length_stats: {
      mean: number;
      std: number;
      min: number;
      max: number;
    };
  };
}

export interface Document {
  id: string;
  name: string;
  type: string;
  status: string;
  metadata: Record<string, any>;
}

@Injectable({
  providedIn: 'root'
})
export class KnowledgeBaseService {
  private apiUrl = `${environment.ragUrl}/api/v1/kb`;
  private kbStats = new BehaviorSubject<KBStats | null>(null);

  constructor(private http: HttpClient) {}

  getKBStats(): Observable<KBStats | null> {
    return this.kbStats.asObservable();
  }

  async refreshStats(): Promise<void> {
    try {
      const stats = await this.http.get<KBStats>(`${this.apiUrl}/stats`).toPromise();
      if (stats) {
        this.kbStats.next(stats);
      }
    } catch (error) {
      console.error('Error fetching KB stats:', error);
      throw error;
    }
  }

  async addDocument(file: File, progressCallback: (progress: number) => void): Promise<void> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Simulate progress for now since actual progress isn't available
      progressCallback(0);
      await this.http.post(`${this.apiUrl}/documents`, formData, {
        reportProgress: true,
        observe: 'events'
      }).toPromise();
      progressCallback(100);

      await this.refreshStats();
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  }

  async addDocumentFromUrl(url: string, progressCallback: (progress: number) => void): Promise<void> {
    try {
      // Simulate progress for now since actual progress isn't available
      progressCallback(0);
      await this.http.post(`${this.apiUrl}/documents/url`, { url }).toPromise();
      progressCallback(100);

      await this.refreshStats();
    } catch (error) {
      console.error('Error processing URL:', error);
      throw error;
    }
  }

  async assessQuality(): Promise<QualityMetrics> {
    try {
      const metrics = await this.http.get<QualityMetrics>(`${this.apiUrl}/quality`).toPromise();
      return metrics || this.getEmptyQualityMetrics();
    } catch (error) {
      console.error('Error assessing KB quality:', error);
      return this.getEmptyQualityMetrics();
    }
  }

  async getDocuments(): Promise<Document[]> {
    try {
      const docs = await this.http.get<Document[]>(`${this.apiUrl}/documents`).toPromise();
      return docs || [];
    } catch (error) {
      console.error('Error fetching documents:', error);
      return [];
    }
  }

  private getEmptyQualityMetrics(): QualityMetrics {
    return {
      overall_score: 0,
      coverage_score: 0,
      coverage_metrics: {
        document_coverage: 0,
        chunk_density: 0,
        category_coverage: 0,
        total_documents: 0,
        total_chunks: 0,
        avg_chunks_per_doc: 0,
        categories: [],
        category_distribution: {}
      },
      consistency_score: 0,
      consistency_metrics: {
        metadata_consistency: 0,
        content_similarity: 0,
        version_consistency: 0,
        metadata_completeness: 0,
        version_distribution: {}
      },
      relevance_score: 0,
      relevance_metrics: {
        source_credibility: 0,
        content_type_relevance: 0,
        source_distribution: {},
        type_distribution: {}
      },
      diversity_score: 0,
      diversity_metrics: {
        category_diversity: 0,
        length_diversity: 0,
        source_diversity: 0,
        category_distribution: {},
        source_distribution: {},
        length_stats: {
          mean: 0,
          std: 0,
          min: 0,
          max: 0
        }
      }
    };
  }
}