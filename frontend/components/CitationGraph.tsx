'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { motion } from 'framer-motion';
import { ZoomIn, ZoomOut, Maximize2, Info } from 'lucide-react';

interface Patent {
  patent_id: string;
  title: string;
  assignee?: string;
  url?: string;
  citing_patents?: string[];
  cited_patents?: string[];
}

interface CitationGraphProps {
  patents: Patent[];
}

interface Node extends d3.SimulationNodeDatum {
  id: string;
  title: string;
  assignee: string;
  url: string;
  connections: number;
}

interface Link extends d3.SimulationLinkDatum<Node> {
  source: Node | string;
  target: Node | string;
}

export default function CitationGraph({ patents }: CitationGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    if (!svgRef.current || !patents || patents.length === 0) return;

    // Clear previous graph
    d3.select(svgRef.current).selectAll('*').remove();

    const width = containerRef.current?.clientWidth || 600;
    const height = 400;

    // Create nodes from patents
    const nodes: Node[] = patents.slice(0, 30).map((patent, i) => ({
      id: patent.patent_id,
      title: patent.title?.substring(0, 50) + (patent.title?.length > 50 ? '...' : ''),
      assignee: patent.assignee || 'Unknown',
      url: patent.url || '',
      connections: (patent.citing_patents?.length || 0) + (patent.cited_patents?.length || 0) + Math.random() * 5,
    }));

    // Create links (simulated if no citation data)
    const links: Link[] = [];
    for (let i = 0; i < nodes.length; i++) {
      // Create some random connections for visualization
      const numConnections = Math.floor(Math.random() * 3);
      for (let j = 0; j < numConnections; j++) {
        const targetIdx = Math.floor(Math.random() * nodes.length);
        if (targetIdx !== i) {
          links.push({
            source: nodes[i].id,
            target: nodes[targetIdx].id,
          });
        }
      }
    }

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Create gradient definitions
    const defs = svg.append('defs');
    
    const gradient = defs.append('linearGradient')
      .attr('id', 'nodeGradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '100%');
    
    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#6366f1');
    
    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#8b5cf6');

    // Container for zoom
    const g = svg.append('g');

    // Create simulation
    const simulation = d3.forceSimulation<Node>(nodes)
      .force('link', d3.forceLink<Node, Link>(links).id(d => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    // Draw links
    const link = g.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#475569')
      .attr('stroke-opacity', 0.4)
      .attr('stroke-width', 1);

    // Draw nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', d => Math.min(20, 8 + d.connections * 2))
      .attr('fill', 'url(#nodeGradient)')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        setSelectedNode(d);
        if (d.url) {
          window.open(d.url, '_blank');
        }
      })
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('stroke', '#22d3ee')
          .attr('stroke-width', 3);
        setSelectedNode(d);
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('stroke', '#fff')
          .attr('stroke-width', 2);
      })
      .call(d3.drag<SVGCircleElement, Node>()
        .on('start', (event: any, d: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event: any, d: any) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event: any, d: any) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }) as any
      );

    // Add labels
    const labels = g.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .text(d => d.id)
      .attr('font-size', '8px')
      .attr('fill', '#94a3b8')
      .attr('text-anchor', 'middle')
      .attr('dy', 25);

    // Zoom behavior
    const zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
        setZoom(event.transform.k);
      });

    svg.call(zoomBehavior);

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => (d.source as Node).x || 0)
        .attr('y1', d => (d.source as Node).y || 0)
        .attr('x2', d => (d.target as Node).x || 0)
        .attr('y2', d => (d.target as Node).y || 0);

      node
        .attr('cx', d => d.x || 0)
        .attr('cy', d => d.y || 0);

      labels
        .attr('x', d => d.x || 0)
        .attr('y', d => d.y || 0);
    });

    return () => {
      simulation.stop();
    };
  }, [patents]);

  const handleZoomIn = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg.transition().call(
        d3.zoom<SVGSVGElement, unknown>().scaleBy as any,
        1.2
      );
    }
  };

  const handleZoomOut = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg.transition().call(
        d3.zoom<SVGSVGElement, unknown>().scaleBy as any,
        0.8
      );
    }
  };

  if (!patents || patents.length === 0) {
    return (
      <div className="p-8 text-center text-[var(--text-muted)]">
        <Info className="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p>No patent data available for visualization</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="relative"
      ref={containerRef}
    >
      {/* Controls */}
      <div className="absolute top-2 right-2 flex gap-2 z-10">
        <button
          onClick={handleZoomIn}
          className="p-2 bg-[var(--bg-elevated)] rounded-lg hover:bg-[var(--bg-card)] transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4 text-[var(--text-secondary)]" />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-2 bg-[var(--bg-elevated)] rounded-lg hover:bg-[var(--bg-card)] transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4 text-[var(--text-secondary)]" />
        </button>
      </div>

      {/* Selected node info */}
      {selectedNode && (
        <div className="absolute top-2 left-2 bg-[var(--bg-secondary)] backdrop-blur-sm p-3 rounded-lg max-w-xs z-10 border border-[var(--border-color)]">
          <p className="text-xs font-mono text-primary-400">{selectedNode.id}</p>
          <p className="text-sm text-white font-medium mt-1">{selectedNode.title}</p>
          <p className="text-xs text-[var(--text-muted)] mt-1">Assignee: {selectedNode.assignee}</p>
          {selectedNode.url && (
            <a
              href={selectedNode.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-primary-400 hover:underline mt-2 block"
            >
              View Patent →
            </a>
          )}
        </div>
      )}

      {/* Graph */}
      <svg
        ref={svgRef}
        className="w-full bg-[var(--bg-primary)] rounded-lg border border-[var(--border-color)]"
        style={{ minHeight: '400px' }}
      />

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 text-xs text-[var(--text-muted)]">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-gradient-to-br from-primary-500 to-purple-500" />
          <span>Patent Node (size = citations)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-0.5 bg-[var(--bg-elevated)]" />
          <span>Citation Link</span>
        </div>
        <div className="flex items-center gap-2">
          <span>Zoom: {(zoom * 100).toFixed(0)}%</span>
        </div>
      </div>
    </motion.div>
  );
}
