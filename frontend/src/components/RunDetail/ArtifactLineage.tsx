import React, { useEffect, useState } from 'react';
import { artifactsApi } from '../../api/artifacts';
import type { Artifact } from '../../types/artifact';

const TYPE_COLORS: Record<string, string> = {
  model: '#7c3aed',
  dataset: '#059669',
  checkpoint: '#d97706',
  log: '#0284c7',
};

interface LineageNode {
  artifact: Artifact;
  children: LineageNode[];
}

function buildTree(lineage: unknown[]): LineageNode | null {
  const artifacts = lineage.filter((item): item is Artifact => !('children' in (item as object) && Object.keys(item as object).length === 1));
  if (artifacts.length === 0) return null;

  const root = artifacts[0];
  const chain: Artifact[] = artifacts;

  const buildNode = (idx: number): LineageNode => ({
    artifact: chain[idx],
    children: idx + 1 < chain.length ? [buildNode(idx + 1)] : [],
  });

  return buildNode(0);
}

const NODE_WIDTH = 200;
const NODE_HEIGHT = 64;
const VERTICAL_GAP = 80;

function renderTree(node: LineageNode, x: number, y: number, nodes: JSX.Element[], edges: JSX.Element[], depth = 0): number {
  const color = TYPE_COLORS[node.artifact.artifact_type] || '#94a3b8';

  nodes.push(
    <g key={node.artifact.id}>
      <rect x={x} y={y} width={NODE_WIDTH} height={NODE_HEIGHT} rx={8} fill="#1e293b" stroke={color} strokeWidth={2} />
      <text x={x + 10} y={y + 20} fill="#e2e8f0" fontSize={12} fontWeight={600}>
        {node.artifact.name.length > 22 ? node.artifact.name.slice(0, 22) + '…' : node.artifact.name}
      </text>
      <rect x={x + 10} y={y + 28} width={60} height={16} rx={4} fill={`${color}33`} />
      <text x={x + 40} y={y + 40} fill={color} fontSize={10} textAnchor="middle">{node.artifact.artifact_type}</text>
      <text x={x + 10} y={y + 56} fill="#64748b" fontSize={10}>
        {node.artifact.checksum ? node.artifact.checksum.slice(0, 20) + '…' : 'no checksum'}
      </text>
    </g>
  );

  node.children.forEach((child, i) => {
    const childY = y + NODE_HEIGHT + VERTICAL_GAP;
    const childX = x + i * (NODE_WIDTH + 20);

    const startX = x + NODE_WIDTH / 2;
    const startY = y + NODE_HEIGHT;
    const endX = childX + NODE_WIDTH / 2;
    const endY = childY;
    const midY = (startY + endY) / 2;

    edges.push(
      <path
        key={`edge-${node.artifact.id}-${child.artifact.id}`}
        d={`M${startX},${startY} C${startX},${midY} ${endX},${midY} ${endX},${endY}`}
        fill="none"
        stroke="#475569"
        strokeWidth={2}
      />
    );

    renderTree(child, childX, childY, nodes, edges, depth + 1);
  });

  return y + NODE_HEIGHT + VERTICAL_GAP;
}

interface ArtifactLineageProps {
  artifactId: string;
}

export const ArtifactLineage: React.FC<ArtifactLineageProps> = ({ artifactId }) => {
  const [lineage, setLineage] = useState<unknown[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    artifactsApi.getLineage(artifactId).then(setLineage).catch((e) => setError(String(e)));
  }, [artifactId]);

  if (error) return <div style={{ color: '#ef4444' }}>{error}</div>;

  const tree = buildTree(lineage);
  if (!tree) return <div style={{ color: '#64748b' }}>No lineage data</div>;

  const nodes: JSX.Element[] = [];
  const edges: JSX.Element[] = [];
  renderTree(tree, 20, 20, nodes, edges);

  const totalHeight = lineage.length * (NODE_HEIGHT + VERTICAL_GAP) + 40;

  return (
    <svg width={NODE_WIDTH + 40} height={totalHeight} style={{ display: 'block' }}>
      {edges}
      {nodes}
    </svg>
  );
};
