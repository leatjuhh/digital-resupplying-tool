'use client';

/**
 * Network Background Animation
 * Visual representation of DRT's redistribution network
 * Shows warehouse (green) → stores (blue) → articles (yellow) with animated flows
 */

import { useEffect, useRef } from 'react';
import { useTheme } from 'next-themes';

// Configuration - Light Mode
const CONFIG_LIGHT = {
  nodes: {
    warehouse: { count: 1, radius: 12, color: '#10b981' },
    store: { count: 10, radius: 8, color: '#3b82f6' },
    article: { perStore: 8, radius: 4, color: '#fbbf24' }
  },
  edges: {
    color: '#64748b',
    opacity: 0.1,
    flowColor: '#84cc16'
  },
  physics: {
    friction: 0.95,
    springStrength: 0.008,
    mouseInfluence: 120
  },
  animation: {
    flowSpeed: 1.5,
    particleCount: 3,
    fps: 60
  },
  background: {
    gradient: 'linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%)',
    gridColor: 'rgba(100, 116, 139, 0.05)',
    clearColor: 'rgba(255, 255, 255, 0.05)'
  }
};

// Configuration - Dark Mode
const CONFIG_DARK = {
  nodes: {
    warehouse: { count: 1, radius: 12, color: '#34d399' },
    store: { count: 10, radius: 8, color: '#60a5fa' },
    article: { perStore: 8, radius: 4, color: '#fbbf24' }
  },
  edges: {
    color: '#94a3b8',
    opacity: 0.15,
    flowColor: '#a3e635'
  },
  physics: {
    friction: 0.95,
    springStrength: 0.008,
    mouseInfluence: 120
  },
  animation: {
    flowSpeed: 1.5,
    particleCount: 3,
    fps: 60
  },
  background: {
    gradient: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
    gridColor: 'rgba(148, 163, 184, 0.08)',
    clearColor: 'rgba(15, 23, 42, 0.05)'
  }
};

interface Vector2D {
  x: number;
  y: number;
}

type NodeType = 'warehouse' | 'store' | 'article';

class Node {
  public pos: Vector2D;
  public vel: Vector2D;
  public type: NodeType;
  public radius: number;
  public color: string;
  public targetPos: Vector2D;

  constructor(x: number, y: number, type: NodeType, config: typeof CONFIG_LIGHT) {
    this.pos = { x, y };
    this.vel = { x: 0, y: 0 };
    this.type = type;
    this.targetPos = { x, y };
    
    const nodeConfig = config.nodes[type];
    this.radius = nodeConfig.radius;
    this.color = nodeConfig.color;
  }

  update(mousePos: Vector2D | null, config: typeof CONFIG_LIGHT) {
    // Spring force towards target position
    const dx = this.targetPos.x - this.pos.x;
    const dy = this.targetPos.y - this.pos.y;
    
    this.vel.x += dx * config.physics.springStrength;
    this.vel.y += dy * config.physics.springStrength;

    // Mouse influence
    if (mousePos) {
      const mdx = mousePos.x - this.pos.x;
      const mdy = mousePos.y - this.pos.y;
      const dist = Math.sqrt(mdx * mdx + mdy * mdy);
      
      if (dist < config.physics.mouseInfluence && dist > 0) {
        const force = (config.physics.mouseInfluence - dist) / config.physics.mouseInfluence;
        this.vel.x -= (mdx / dist) * force * 0.5;
        this.vel.y -= (mdy / dist) * force * 0.5;
      }
    }

    // Apply friction
    this.vel.x *= config.physics.friction;
    this.vel.y *= config.physics.friction;

    // Update position
    this.pos.x += this.vel.x;
    this.pos.y += this.vel.y;
  }

  draw(ctx: CanvasRenderingContext2D) {
    ctx.beginPath();
    ctx.arc(this.pos.x, this.pos.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.color;
    ctx.fill();
    
    // Subtle glow
    ctx.shadowBlur = 10;
    ctx.shadowColor = this.color;
    ctx.fill();
    ctx.shadowBlur = 0;
  }
}

class Edge {
  constructor(
    public from: Node,
    public to: Node
  ) {}

  draw(ctx: CanvasRenderingContext2D, config: typeof CONFIG_LIGHT) {
    ctx.beginPath();
    ctx.moveTo(this.from.pos.x, this.from.pos.y);
    ctx.lineTo(this.to.pos.x, this.to.pos.y);
    ctx.strokeStyle = config.edges.color;
    ctx.globalAlpha = config.edges.opacity;
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }
}

class FlowParticle {
  public progress: number;
  
  constructor(
    public edge: Edge,
    startProgress: number = 0
  ) {
    this.progress = startProgress;
  }

  update(deltaTime: number, config: typeof CONFIG_LIGHT) {
    this.progress += config.animation.flowSpeed * deltaTime / 1000;
    if (this.progress > 1) {
      this.progress = 0;
    }
  }

  draw(ctx: CanvasRenderingContext2D, config: typeof CONFIG_LIGHT) {
    const x = this.edge.from.pos.x + (this.edge.to.pos.x - this.edge.from.pos.x) * this.progress;
    const y = this.edge.from.pos.y + (this.edge.to.pos.y - this.edge.from.pos.y) * this.progress;

    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    ctx.fillStyle = config.edges.flowColor;
    ctx.fill();
    
    // Glow effect
    ctx.shadowBlur = 8;
    ctx.shadowColor = config.edges.flowColor;
    ctx.fill();
    ctx.shadowBlur = 0;
  }
}

export function NetworkBackground() {
  const { theme, systemTheme } = useTheme();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<Node[]>([]);
  const edgesRef = useRef<Edge[]>([]);
  const particlesRef = useRef<FlowParticle[]>([]);
  const mouseRef = useRef<Vector2D | null>(null);
  const animationIdRef = useRef<number>();
  const lastTimeRef = useRef<number>(0);

  // Determine current theme and get appropriate config
  const currentTheme = theme === 'system' ? systemTheme : theme;
  const isDark = currentTheme === 'dark';
  const CONFIG = isDark ? CONFIG_DARK : CONFIG_LIGHT;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      
      // Regenerate network on resize
      if (nodesRef.current.length === 0) {
        generateNetwork();
      }
    };

    // Generate network topology
    const generateNetwork = () => {
      const nodes: Node[] = [];
      const edges: Edge[] = [];
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      // Create warehouse (center)
      const warehouse = new Node(centerX, centerY, 'warehouse', CONFIG);
      nodes.push(warehouse);

      // Create stores in circle around warehouse
      const stores: Node[] = [];
      const storeRadius = Math.min(canvas.width, canvas.height) * 0.3;
      
      for (let i = 0; i < CONFIG.nodes.store.count; i++) {
        const angle = (i / CONFIG.nodes.store.count) * Math.PI * 2;
        const variance = 0.8 + Math.random() * 0.4; // Random radius variance
        const x = centerX + Math.cos(angle) * storeRadius * variance;
        const y = centerY + Math.sin(angle) * storeRadius * variance;
        
        const store = new Node(x, y, 'store', CONFIG);
        nodes.push(store);
        stores.push(store);
        
        // Connect warehouse to store
        edges.push(new Edge(warehouse, store));
      }

      // Create articles around each store
      const articleRadius = 50;
      stores.forEach(store => {
        for (let i = 0; i < CONFIG.nodes.article.perStore; i++) {
          const angle = (i / CONFIG.nodes.article.perStore) * Math.PI * 2;
          const variance = 0.7 + Math.random() * 0.6;
          const x = store.pos.x + Math.cos(angle) * articleRadius * variance;
          const y = store.pos.y + Math.sin(angle) * articleRadius * variance;
          
          const article = new Node(x, y, 'article', CONFIG);
          nodes.push(article);
          
          // Connect store to article
          edges.push(new Edge(store, article));
        }
      });

      // Add some store-to-store connections (redistribution routes)
      for (let i = 0; i < stores.length; i++) {
        const nextStore = stores[(i + 1) % stores.length];
        if (Math.random() > 0.6) { // Only connect some stores
          edges.push(new Edge(stores[i], nextStore));
        }
      }

      nodesRef.current = nodes;
      edgesRef.current = edges;

      // Create flow particles on random edges
      const particles: FlowParticle[] = [];
      const flowEdges = edges.filter(() => Math.random() > 0.7); // Only some edges have flows
      
      flowEdges.slice(0, CONFIG.animation.particleCount).forEach((edge, i) => {
        particles.push(new FlowParticle(edge, i / CONFIG.animation.particleCount));
      });
      
      particlesRef.current = particles;
    };

    // Animation loop
    const animate = (currentTime: number) => {
      const deltaTime = currentTime - lastTimeRef.current;
      lastTimeRef.current = currentTime;

      // Clear canvas completely to prevent smearing
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw subtle grid (parallax effect)
      if (mouseRef.current) {
        const offsetX = (mouseRef.current.x - canvas.width / 2) * 0.02;
        const offsetY = (mouseRef.current.y - canvas.height / 2) * 0.02;
        
        ctx.strokeStyle = CONFIG.background.gridColor;
        ctx.lineWidth = 1;
        
        const gridSize = 50;
        for (let x = offsetX % gridSize; x < canvas.width; x += gridSize) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, canvas.height);
          ctx.stroke();
        }
        
        for (let y = offsetY % gridSize; y < canvas.height; y += gridSize) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(canvas.width, y);
          ctx.stroke();
        }
      }

      // Update and draw edges
      edgesRef.current.forEach(edge => edge.draw(ctx, CONFIG));

      // Update and draw nodes
      nodesRef.current.forEach(node => {
        node.update(mouseRef.current, CONFIG);
        node.draw(ctx);
      });

      // Update and draw flow particles
      particlesRef.current.forEach(particle => {
        particle.update(deltaTime, CONFIG);
        particle.draw(ctx, CONFIG);
      });

      animationIdRef.current = requestAnimationFrame(animate);
    };

    // Mouse move handler
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
    };

    // Click handler - regenerate network
    const handleClick = () => {
      generateNetwork();
    };

    // Initialize
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('click', handleClick);
    
    lastTimeRef.current = performance.now();
    animationIdRef.current = requestAnimationFrame(animate);

    // Cleanup
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('click', handleClick);
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
    };
  }, []);

  return (
    <>
      <canvas
        ref={canvasRef}
        className="fixed inset-0 w-full h-full"
        style={{ 
          background: CONFIG.background.gradient,
          zIndex: 0
        }}
      />
      
      {/* Legend */}
      <div className="fixed bottom-4 left-4 bg-white/70 dark:bg-gray-900/70 backdrop-blur-md rounded-lg p-3 text-xs text-muted-foreground shadow-sm border border-gray-200/50 dark:border-gray-700/50">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#10b981]"></div>
            <span>Magazijn (centraal)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#3b82f6]"></div>
            <span>Winkels (locaties)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#fbbf24]"></div>
            <span>Artikelen (voorraad)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#84cc16]"></div>
            <span>Flow (herverdeling)</span>
          </div>
          <div className="text-[10px] mt-2 opacity-70">
            Klik om opnieuw te genereren
          </div>
        </div>
      </div>
    </>
  );
}
