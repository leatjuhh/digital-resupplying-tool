'use client';

import { useEffect, useRef } from 'react';
import { useTheme } from 'next-themes';

const CONFIG_LIGHT = {
  nodes: {
    algorithm: { radius: 14, color: '#10b981' },
    store: { count: 10, radius: 8, color: '#3b82f6' }
  },
  edges: {
    commColor: '#64748b',
    commOpacity: 0.07,
    redisColor: '#f97316',
    redisOpacity: 0.2,
    flowColor: '#f97316',
    beamColor: '#f97316'
  },
  stock: {
    surplusColor: '#f97316',
    shortageColor: '#60a5fa',
    ringWidth: 2.5
  },
  ambient: {
    color: '#3b82f6',
    count: 45
  },
  physics: {
    friction: 0.95,
    springStrength: 0.008,
    mouseInfluence: 120
  },
  animation: {
    flowSpeed: 0.6,
    stateInterval: 4500
  },
  background: {
    gradient: 'linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%)',
    gridColor: 'rgba(100, 116, 139, 0.04)'
  }
};

const CONFIG_DARK = {
  nodes: {
    algorithm: { radius: 14, color: '#34d399' },
    store: { count: 10, radius: 8, color: '#60a5fa' }
  },
  edges: {
    commColor: '#94a3b8',
    commOpacity: 0.09,
    redisColor: '#fb923c',
    redisOpacity: 0.25,
    flowColor: '#fb923c',
    beamColor: '#fb923c'
  },
  stock: {
    surplusColor: '#fb923c',
    shortageColor: '#93c5fd',
    ringWidth: 2.5
  },
  ambient: {
    color: '#60a5fa',
    count: 45
  },
  physics: {
    friction: 0.95,
    springStrength: 0.008,
    mouseInfluence: 120
  },
  animation: {
    flowSpeed: 0.6,
    stateInterval: 4500
  },
  background: {
    gradient: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
    gridColor: 'rgba(148, 163, 184, 0.06)'
  }
};

interface Vector2D { x: number; y: number; }
type StockState = 'surplus' | 'shortage' | 'neutral';

class AmbientParticle {
  public pos: Vector2D;
  public vel: Vector2D;
  public opacity: number;
  public radius: number;

  constructor(w: number, h: number) {
    this.pos = { x: Math.random() * w, y: Math.random() * h };
    const angle = Math.random() * Math.PI * 2;
    const speed = 0.08 + Math.random() * 0.15;
    this.vel = { x: Math.cos(angle) * speed, y: Math.sin(angle) * speed };
    this.opacity = 0.06 + Math.random() * 0.14;
    this.radius = 0.8 + Math.random() * 1.4;
  }

  update(w: number, h: number) {
    this.pos.x += this.vel.x;
    this.pos.y += this.vel.y;
    if (this.pos.x < 0) this.pos.x = w;
    if (this.pos.x > w) this.pos.x = 0;
    if (this.pos.y < 0) this.pos.y = h;
    if (this.pos.y > h) this.pos.y = 0;
  }

  draw(ctx: CanvasRenderingContext2D, color: string) {
    ctx.beginPath();
    ctx.arc(this.pos.x, this.pos.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.globalAlpha = this.opacity;
    ctx.fill();
    ctx.globalAlpha = 1;
  }
}

class BurstParticle {
  public pos: Vector2D;
  public vel: Vector2D;
  public life: number = 1;
  public active: boolean = true;

  constructor(x: number, y: number) {
    this.pos = { x, y };
    const angle = Math.random() * Math.PI * 2;
    const speed = 0.8 + Math.random() * 1.8;
    this.vel = { x: Math.cos(angle) * speed, y: Math.sin(angle) * speed };
  }

  update(deltaTime: number) {
    const dt = deltaTime / 16;
    this.pos.x += this.vel.x * dt;
    this.pos.y += this.vel.y * dt;
    this.vel.x *= 0.93;
    this.vel.y *= 0.93;
    this.life -= deltaTime / 550;
    if (this.life <= 0) this.active = false;
  }

  draw(ctx: CanvasRenderingContext2D, color: string) {
    ctx.beginPath();
    ctx.arc(this.pos.x, this.pos.y, 2, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.globalAlpha = this.life * 0.7;
    ctx.fill();
    ctx.globalAlpha = 1;
  }
}

interface EdgeBeam {
  from: Vector2D;
  to: Vector2D;
  life: number; // 1 → 0
}

class StoreNode {
  public pos: Vector2D;
  public vel: Vector2D = { x: 0, y: 0 };
  public targetPos: Vector2D;
  public stockState: StockState = 'neutral';
  public stateTimer: number;
  public ringOpacity: number = 0;
  public depth: number; // 0.75–1.0, affects subtle size/opacity variation

  constructor(x: number, y: number, stateOffset: number, depth: number, private config: typeof CONFIG_LIGHT) {
    this.pos = { x, y };
    this.targetPos = { x, y };
    this.stateTimer = stateOffset;
    this.depth = depth;
  }

  updateState(deltaTime: number) {
    this.stateTimer += deltaTime;
    if (this.stateTimer >= this.config.animation.stateInterval) {
      this.stateTimer = 0;
      const roll = Math.random();
      if (this.stockState === 'neutral') {
        this.stockState = roll < 0.5 ? 'surplus' : 'shortage';
      } else {
        this.stockState = 'neutral';
      }
    }
    const target = this.stockState !== 'neutral' ? 1 : 0;
    this.ringOpacity += (target - this.ringOpacity) * 0.05;
  }

  update(mousePos: Vector2D | null, deltaTime: number) {
    const dx = this.targetPos.x - this.pos.x;
    const dy = this.targetPos.y - this.pos.y;
    this.vel.x += dx * this.config.physics.springStrength;
    this.vel.y += dy * this.config.physics.springStrength;

    if (mousePos) {
      const mdx = mousePos.x - this.pos.x;
      const mdy = mousePos.y - this.pos.y;
      const dist = Math.sqrt(mdx * mdx + mdy * mdy);
      if (dist < this.config.physics.mouseInfluence && dist > 0) {
        const force = (this.config.physics.mouseInfluence - dist) / this.config.physics.mouseInfluence;
        this.vel.x -= (mdx / dist) * force * 0.5;
        this.vel.y -= (mdy / dist) * force * 0.5;
      }
    }

    this.vel.x *= this.config.physics.friction;
    this.vel.y *= this.config.physics.friction;
    this.pos.x += this.vel.x;
    this.pos.y += this.vel.y;
    this.updateState(deltaTime);
  }

  draw(ctx: CanvasRenderingContext2D) {
    const baseRadius = this.config.nodes.store.radius * (0.85 + this.depth * 0.15);
    const baseOpacity = 0.7 + this.depth * 0.3;
    const { surplusColor, shortageColor, ringWidth } = this.config.stock;

    if (this.ringOpacity > 0.01) {
      const ringColor = this.stockState === 'surplus' ? surplusColor : shortageColor;
      // Outer glow ring
      ctx.beginPath();
      ctx.arc(this.pos.x, this.pos.y, baseRadius + 10, 0, Math.PI * 2);
      ctx.strokeStyle = ringColor;
      ctx.lineWidth = ringWidth;
      ctx.globalAlpha = this.ringOpacity * 0.25;
      ctx.stroke();
      // Inner ring
      ctx.beginPath();
      ctx.arc(this.pos.x, this.pos.y, baseRadius + 5, 0, Math.PI * 2);
      ctx.strokeStyle = ringColor;
      ctx.lineWidth = ringWidth;
      ctx.globalAlpha = this.ringOpacity * 0.65;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    ctx.beginPath();
    ctx.arc(this.pos.x, this.pos.y, baseRadius, 0, Math.PI * 2);
    ctx.fillStyle = this.config.nodes.store.color;
    ctx.globalAlpha = baseOpacity;
    ctx.shadowBlur = 10;
    ctx.shadowColor = this.config.nodes.store.color;
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.globalAlpha = 1;
  }
}

class AlgorithmNode {
  public pos: Vector2D;
  public vel: Vector2D = { x: 0, y: 0 };
  public targetPos: Vector2D;
  public pulsePhase: number = 0;

  constructor(x: number, y: number, private config: typeof CONFIG_LIGHT) {
    this.pos = { x, y };
    this.targetPos = { x, y };
  }

  update(mousePos: Vector2D | null, deltaTime: number) {
    const dx = this.targetPos.x - this.pos.x;
    const dy = this.targetPos.y - this.pos.y;
    this.vel.x += dx * this.config.physics.springStrength;
    this.vel.y += dy * this.config.physics.springStrength;

    if (mousePos) {
      const mdx = mousePos.x - this.pos.x;
      const mdy = mousePos.y - this.pos.y;
      const dist = Math.sqrt(mdx * mdx + mdy * mdy);
      if (dist < this.config.physics.mouseInfluence && dist > 0) {
        const force = (this.config.physics.mouseInfluence - dist) / this.config.physics.mouseInfluence;
        this.vel.x -= (mdx / dist) * force * 0.5;
        this.vel.y -= (mdy / dist) * force * 0.5;
      }
    }

    this.vel.x *= this.config.physics.friction;
    this.vel.y *= this.config.physics.friction;
    this.pos.x += this.vel.x;
    this.pos.y += this.vel.y;
    this.pulsePhase += deltaTime * 0.0022;
  }

  draw(ctx: CanvasRenderingContext2D) {
    const { radius, color } = this.config.nodes.algorithm;

    // Two concentric pulse rings
    for (let i = 0; i < 2; i++) {
      const phase = this.pulsePhase + i * Math.PI;
      const pulseR = radius + 9 + Math.sin(phase) * 5;
      const pulseOpacity = 0.18 + Math.sin(phase) * 0.1;
      ctx.beginPath();
      ctx.arc(this.pos.x, this.pos.y, pulseR, 0, Math.PI * 2);
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.5;
      ctx.globalAlpha = Math.max(0, pulseOpacity);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;

    ctx.beginPath();
    ctx.arc(this.pos.x, this.pos.y, radius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.shadowBlur = 18;
    ctx.shadowColor = color;
    ctx.fill();
    ctx.shadowBlur = 0;
  }
}

class FlowParticle {
  public progress: number;
  public trail: Vector2D[] = [];
  public active: boolean = true;

  constructor(
    public from: Vector2D,
    public to: Vector2D,
    startProgress: number = 0
  ) {
    this.progress = startProgress;
  }

  update(deltaTime: number, config: typeof CONFIG_LIGHT) {
    const x = this.from.x + (this.to.x - this.from.x) * this.progress;
    const y = this.from.y + (this.to.y - this.from.y) * this.progress;
    this.trail.push({ x, y });
    if (this.trail.length > 6) this.trail.shift();

    this.progress += config.animation.flowSpeed * deltaTime / 1000;
    if (this.progress >= 1) this.active = false;
  }

  draw(ctx: CanvasRenderingContext2D, config: typeof CONFIG_LIGHT) {
    const x = this.from.x + (this.to.x - this.from.x) * Math.min(this.progress, 1);
    const y = this.from.y + (this.to.y - this.from.y) * Math.min(this.progress, 1);

    for (let i = 0; i < this.trail.length; i++) {
      const t = this.trail[i];
      const trailOpacity = ((i + 1) / this.trail.length) * 0.3;
      ctx.beginPath();
      ctx.arc(t.x, t.y, 1.8, 0, Math.PI * 2);
      ctx.fillStyle = config.edges.flowColor;
      ctx.globalAlpha = trailOpacity;
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    ctx.beginPath();
    ctx.arc(x, y, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = config.edges.flowColor;
    ctx.shadowBlur = 12;
    ctx.shadowColor = config.edges.flowColor;
    ctx.fill();
    ctx.shadowBlur = 0;
  }
}

export function NetworkBackground() {
  const { theme, systemTheme } = useTheme();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const algorithmRef = useRef<AlgorithmNode | null>(null);
  const storesRef = useRef<StoreNode[]>([]);
  const particlesRef = useRef<FlowParticle[]>([]);
  const burstParticlesRef = useRef<BurstParticle[]>([]);
  const ambientParticlesRef = useRef<AmbientParticle[]>([]);
  const edgeBeamsRef = useRef<EdgeBeam[]>([]);
  const mouseRef = useRef<Vector2D | null>(null);
  const animationIdRef = useRef<number>();
  const lastTimeRef = useRef<number>(0);
  const spawnTimerRef = useRef<number>(0);

  const currentTheme = theme === 'system' ? systemTheme : theme;
  const isDark = currentTheme === 'dark';
  const CONFIG = isDark ? CONFIG_DARK : CONFIG_LIGHT;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const generateNetwork = () => {
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      algorithmRef.current = new AlgorithmNode(centerX, centerY, CONFIG);

      const stores: StoreNode[] = [];
      const storeRadius = Math.min(canvas.width, canvas.height) * 0.3;
      for (let i = 0; i < CONFIG.nodes.store.count; i++) {
        const angle = (i / CONFIG.nodes.store.count) * Math.PI * 2;
        const variance = 0.8 + Math.random() * 0.4;
        const depth = 0.75 + Math.random() * 0.25;
        const x = centerX + Math.cos(angle) * storeRadius * variance;
        const y = centerY + Math.sin(angle) * storeRadius * variance;
        stores.push(new StoreNode(x, y, i * (CONFIG.animation.stateInterval / CONFIG.nodes.store.count), depth, CONFIG));
      }
      stores[0].stockState = 'surplus';
      stores[3].stockState = 'shortage';
      stores[6].stockState = 'surplus';
      stores[8].stockState = 'shortage';

      storesRef.current = stores;
      particlesRef.current = [];
      burstParticlesRef.current = [];
      edgeBeamsRef.current = [];
      spawnTimerRef.current = 0;

      // Ambient particles
      ambientParticlesRef.current = Array.from(
        { length: CONFIG.ambient.count },
        () => new AmbientParticle(canvas.width, canvas.height)
      );
    };

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      generateNetwork();
    };

    const spawnParticles = () => {
      const stores = storesRef.current;
      const surpluses = stores.filter(s => s.stockState === 'surplus');
      const shortages = stores.filter(s => s.stockState === 'shortage');
      if (surpluses.length === 0 || shortages.length === 0) return;

      surpluses.forEach(src => {
        const dst = shortages[Math.floor(Math.random() * shortages.length)];
        const from = { ...src.pos };
        const to = { ...dst.pos };

        // Add edge beam flash
        edgeBeamsRef.current.push({ from, to, life: 1 });

        for (let i = 0; i < 3; i++) {
          particlesRef.current.push(new FlowParticle(from, to, i * 0.22));
        }
      });
    };

    const drawCommEdges = () => {
      const algo = algorithmRef.current;
      if (!algo) return;
      ctx.setLineDash([3, 9]);
      ctx.lineWidth = 1;
      storesRef.current.forEach(store => {
        ctx.beginPath();
        ctx.moveTo(algo.pos.x, algo.pos.y);
        ctx.lineTo(store.pos.x, store.pos.y);
        ctx.strokeStyle = CONFIG.edges.commColor;
        ctx.globalAlpha = CONFIG.edges.commOpacity;
        ctx.stroke();
      });
      ctx.setLineDash([]);
      ctx.globalAlpha = 1;
    };

    const drawRedisEdges = () => {
      const surpluses = storesRef.current.filter(s => s.stockState === 'surplus');
      const shortages = storesRef.current.filter(s => s.stockState === 'shortage');
      surpluses.forEach(src => {
        shortages.forEach(dst => {
          ctx.beginPath();
          ctx.moveTo(src.pos.x, src.pos.y);
          ctx.lineTo(dst.pos.x, dst.pos.y);
          ctx.strokeStyle = CONFIG.edges.redisColor;
          ctx.globalAlpha = CONFIG.edges.redisOpacity;
          ctx.lineWidth = 1.5;
          ctx.stroke();
          ctx.globalAlpha = 1;
        });
      });
    };

    const drawEdgeBeams = (deltaTime: number) => {
      edgeBeamsRef.current = edgeBeamsRef.current.filter(b => b.life > 0);
      edgeBeamsRef.current.forEach(beam => {
        ctx.beginPath();
        ctx.moveTo(beam.from.x, beam.from.y);
        ctx.lineTo(beam.to.x, beam.to.y);
        ctx.strokeStyle = CONFIG.edges.beamColor;
        ctx.lineWidth = 2;
        ctx.globalAlpha = beam.life * 0.5;
        ctx.shadowBlur = 12;
        ctx.shadowColor = CONFIG.edges.beamColor;
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1;
        beam.life -= deltaTime / 700;
      });
    };

    const animate = (currentTime: number) => {
      const deltaTime = Math.min(currentTime - lastTimeRef.current, 50);
      lastTimeRef.current = currentTime;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Parallax grid
      if (mouseRef.current) {
        const offsetX = (mouseRef.current.x - canvas.width / 2) * 0.02;
        const offsetY = (mouseRef.current.y - canvas.height / 2) * 0.02;
        ctx.strokeStyle = CONFIG.background.gridColor;
        ctx.lineWidth = 1;
        const gs = 50;
        for (let x = offsetX % gs; x < canvas.width; x += gs) {
          ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
        }
        for (let y = offsetY % gs; y < canvas.height; y += gs) {
          ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
        }
      }

      // Ambient particles (drawn first, behind everything)
      ambientParticlesRef.current.forEach(p => {
        p.update(canvas.width, canvas.height);
        p.draw(ctx, CONFIG.ambient.color);
      });

      drawCommEdges();
      drawEdgeBeams(deltaTime);
      drawRedisEdges();

      storesRef.current.forEach(store => {
        store.update(mouseRef.current, deltaTime);
        store.draw(ctx);
      });

      algorithmRef.current?.update(mouseRef.current, deltaTime);
      algorithmRef.current?.draw(ctx);

      // Spawn timer
      spawnTimerRef.current += deltaTime;
      if (spawnTimerRef.current >= 1200) {
        spawnTimerRef.current = 0;
        spawnParticles();
      }

      // Flow particles — collect finished ones for burst
      const surviving: FlowParticle[] = [];
      for (const p of particlesRef.current) {
        p.update(deltaTime, CONFIG);
        p.draw(ctx, CONFIG);
        if (!p.active) {
          for (let i = 0; i < 7; i++) {
            burstParticlesRef.current.push(new BurstParticle(p.to.x, p.to.y));
          }
        } else {
          surviving.push(p);
        }
      }
      particlesRef.current = surviving;

      // Burst particles
      burstParticlesRef.current = burstParticlesRef.current.filter(b => b.active);
      burstParticlesRef.current.forEach(b => {
        b.update(deltaTime);
        b.draw(ctx, CONFIG.edges.flowColor);
      });

      animationIdRef.current = requestAnimationFrame(animate);
    };

    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    };

    const handleClick = () => generateNetwork();

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('click', handleClick);
    lastTimeRef.current = performance.now();
    animationIdRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('click', handleClick);
      if (animationIdRef.current) cancelAnimationFrame(animationIdRef.current);
    };
  }, []);

  return (
    <>
      <canvas
        ref={canvasRef}
        className="fixed inset-0 w-full h-full"
        style={{ background: CONFIG.background.gradient, zIndex: 0 }}
      />

      {/* Legend */}
      <div className="fixed bottom-4 left-4 bg-white/70 dark:bg-gray-900/70 backdrop-blur-md rounded-lg p-3 text-xs text-muted-foreground shadow-sm border border-gray-200/50 dark:border-gray-700/50 z-10">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#10b981] dark:bg-[#34d399]"></div>
            <span>DRT Algoritme</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#3b82f6] dark:bg-[#60a5fa]"></div>
            <span>Filialen</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full ring-2 ring-[#f97316] bg-transparent"></div>
            <span>Overschot filiaal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full ring-2 ring-[#60a5fa] bg-transparent"></div>
            <span>Tekort filiaal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#f97316]"></div>
            <span>Artikel herverdeling</span>
          </div>
          <div className="text-[10px] mt-2 opacity-70">Klik om opnieuw te genereren</div>
        </div>
      </div>
    </>
  );
}
