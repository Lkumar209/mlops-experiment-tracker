export type ArtifactType = 'model' | 'dataset' | 'checkpoint' | 'log';

export interface Artifact {
  id: string;
  run_id: string;
  name: string;
  artifact_type: ArtifactType;
  uri: string;
  size_bytes: number | null;
  checksum: string | null;
  parent_artifact_id: string | null;
  created_at: string;
}
