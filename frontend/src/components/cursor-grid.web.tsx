/**
 * CursorGrid – web-only canvas implementation.
 * Adapted from the React Bits open-source component (reactbits.dev).
 *
 * Uses window-level pointer listeners so the grid reacts to the cursor
 * even when the user hovers over content elements rendered on top of
 * the canvas (e.g. buttons, text).
 *
 * Platform-specific resolution:
 *   cursor-grid.web.tsx  → web build  (this file)
 *   cursor-grid.tsx      → native build (iOS / Android)
 */
import { useEffect, useRef } from 'react';

type Falloff = 'linear' | 'smooth' | 'sharp';

export interface CursorGridProps {
  cellSize?: number;
  color?: string;
  radius?: number;
  falloff?: Falloff;
  holdTime?: number;
  fadeDuration?: number;
  lineWidth?: number;
  maxOpacity?: number;
  fillOpacity?: number;
  gridOpacity?: number;
  cellRadius?: number;
  clickPulse?: boolean;
  pulseSpeed?: number;
}

const FALLOFF: Record<Falloff, (t: number) => number> = {
  linear: (t) => t,
  smooth: (t) => t * t * (3 - 2 * t),
  sharp:  (t) => t * t * t,
};

function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  const v = h.length === 3 ? h.split('').map((c) => c + c).join('') : h;
  const n = parseInt(v.slice(0, 6), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

export function CursorGrid({
  cellSize    = 58,
  color       = '#FF5722',
  radius      = 190,
  falloff     = 'smooth',
  holdTime    = 500,
  fadeDuration = 900,
  lineWidth   = 1.0,
  maxOpacity  = 0.65,
  fillOpacity = 0.05,
  gridOpacity = 0.05,
  cellRadius  = 3,
  clickPulse  = true,
  pulseSpeed  = 550,
}: CursorGridProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef    = useRef<HTMLCanvasElement>(null);
  const propsRef     = useRef({
    cellSize, color, radius, falloff, holdTime, fadeDuration,
    lineWidth, maxOpacity, fillOpacity, gridOpacity, cellRadius,
    clickPulse, pulseSpeed,
  });
  const wakeRef = useRef<(() => void) | null>(null);

  // Keep latest props available inside the animation loop without restarting the effect.
  propsRef.current = {
    cellSize, color, radius, falloff, holdTime, fadeDuration,
    lineWidth, maxOpacity, fillOpacity, gridOpacity, cellRadius,
    clickPulse, pulseSpeed,
  };

  // ── Main animation effect ────────────────────────────────────────────────
  useEffect(() => {
    const container = containerRef.current;
    const canvas    = canvasRef.current;
    if (!container || !canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    let cols = 0, rows = 0, offX = 0, offY = 0;
    let alphas  = new Float32Array(0);
    let touched = new Float64Array(0);
    let w = 0, h = 0;

    type Pulse = { x: number; y: number; t0: number };
    const pulses: Pulse[] = [];
    let raf = 0, running = false, lastFrame = 0;

    // ── Resize / rebuild grid ──────────────────────────────────────────────
    const rebuild = () => {
      const p = propsRef.current;
      w = container.offsetWidth;
      h = container.offsetHeight;
      canvas.width  = Math.max(1, Math.round(w * dpr));
      canvas.height = Math.max(1, Math.round(h * dpr));
      canvas.style.width  = `${w}px`;
      canvas.style.height = `${h}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      cols = Math.ceil(w / p.cellSize) + 1;
      rows = Math.ceil(h / p.cellSize) + 1;
      offX = (w - cols * p.cellSize) / 2;
      offY = (h - rows * p.cellSize) / 2;
      alphas  = new Float32Array(cols * rows);
      touched = new Float64Array(cols * rows);
    };

    // ── Helpers ────────────────────────────────────────────────────────────
    const cellCenter = (i: number): [number, number] => {
      const p = propsRef.current;
      return [
        offX + (i % cols) * p.cellSize + p.cellSize / 2,
        offY + Math.floor(i / cols) * p.cellSize + p.cellSize / 2,
      ];
    };

    const energize = (x: number, y: number) => {
      const p   = propsRef.current;
      const r   = Math.max(p.radius, 1);
      const ease = FALLOFF[p.falloff as Falloff] ?? FALLOFF.smooth;
      const now = performance.now();
      const minCol = Math.max(0, Math.floor((x - r - offX) / p.cellSize));
      const maxCol = Math.min(cols - 1, Math.ceil((x + r - offX) / p.cellSize));
      const minRow = Math.max(0, Math.floor((y - r - offY) / p.cellSize));
      const maxRow = Math.min(rows - 1, Math.ceil((y + r - offY) / p.cellSize));
      for (let cRow = minRow; cRow <= maxRow; cRow++) {
        for (let cCol = minCol; cCol <= maxCol; cCol++) {
          const i = cRow * cols + cCol;
          const [cx, cy] = cellCenter(i);
          const dist = Math.hypot(cx - x, cy - y);
          if (dist > r) continue;
          const level = ease(1 - dist / r) * p.maxOpacity;
          if (level > alphas[i]) { alphas[i] = level; touched[i] = now; }
          else if (level > 0)    { touched[i] = now; }
        }
      }
    };

    // ── Draw static lattice ────────────────────────────────────────────────
    const drawLattice = (cr: number, cg: number, cb: number, opacity: number) => {
      ctx.strokeStyle = `rgba(${cr},${cg},${cb},${opacity})`;
      ctx.lineWidth   = 0.7;
      ctx.beginPath();
      for (let c = 0; c <= cols; c++) {
        const x = Math.round(offX + c * propsRef.current.cellSize) + 0.5;
        ctx.moveTo(x, 0); ctx.lineTo(x, h);
      }
      for (let r = 0; r <= rows; r++) {
        const y = Math.round(offY + r * propsRef.current.cellSize) + 0.5;
        ctx.moveTo(0, y); ctx.lineTo(w, y);
      }
      ctx.stroke();
    };

    // ── Main render loop ───────────────────────────────────────────────────
    const draw = (now: number) => {
      const p  = propsRef.current;
      const dt = Math.min(now - lastFrame, 50);
      lastFrame = now;
      ctx.clearRect(0, 0, w, h);

      const [cr, cg, cb] = hexToRgb(p.color);

      if (p.gridOpacity > 0) drawLattice(cr, cg, cb, p.gridOpacity);

      // ── Expand click pulses ──────────────────────────────────────────────
      for (let pi = pulses.length - 1; pi >= 0; pi--) {
        const pulse = pulses[pi];
        const age   = (now - pulse.t0) / 1000;
        const ringR = age * p.pulseSpeed;
        if (ringR > Math.hypot(w, h)) { pulses.splice(pi, 1); continue; }
        const band   = p.cellSize;
        const mnC = Math.max(0, Math.floor((pulse.x - ringR - band - offX) / p.cellSize));
        const mxC = Math.min(cols - 1, Math.ceil((pulse.x + ringR + band - offX) / p.cellSize));
        const mnR = Math.max(0, Math.floor((pulse.y - ringR - band - offY) / p.cellSize));
        const mxR = Math.min(rows - 1, Math.ceil((pulse.y + ringR + band - offY) / p.cellSize));
        for (let cRow = mnR; cRow <= mxR; cRow++) {
          for (let cCol = mnC; cCol <= mxC; cCol++) {
            const i = cRow * cols + cCol;
            const [cx, cy] = cellCenter(i);
            const dist = Math.hypot(cx - pulse.x, cy - pulse.y);
            if (Math.abs(dist - ringR) < band / 2 && p.maxOpacity > alphas[i]) {
              alphas[i] = p.maxOpacity;
              touched[i] = now;
            }
          }
        }
      }

      // ── Draw lit cells ───────────────────────────────────────────────────
      let anyVisible  = pulses.length > 0;
      const fadeStep  = dt / Math.max(p.fadeDuration, 16);
      const half      = p.cellSize / 2;

      for (let i = 0; i < alphas.length; i++) {
        let a = alphas[i];
        if (a <= 0) continue;
        if (now - touched[i] > p.holdTime) {
          a = Math.max(0, a - fadeStep);
          alphas[i] = a;
          if (a <= 0) continue;
        }
        anyVisible = true;
        const [cx, cy] = cellCenter(i);
        const grad = ctx.createRadialGradient(cx, cy, half * 0.1, cx, cy, p.cellSize);
        grad.addColorStop(0, `rgba(${cr},${cg},${cb},${a})`);
        grad.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
        const x = cx - half + 0.5;
        const y = cy - half + 0.5;
        const s = p.cellSize - 1;
        ctx.beginPath();
        if (p.cellRadius > 0) {
          // ctx.roundRect is available in modern browsers
          (ctx as any).roundRect(x, y, s, s, p.cellRadius);
        } else {
          ctx.rect(x, y, s, s);
        }
        if (p.fillOpacity > 0) {
          ctx.fillStyle = `rgba(${cr},${cg},${cb},${a * p.fillOpacity})`;
          ctx.fill();
        }
        ctx.strokeStyle = grad;
        ctx.lineWidth   = p.lineWidth;
        ctx.stroke();
      }

      if (anyVisible) {
        raf = requestAnimationFrame(draw);
      } else {
        running = false;
        // Persist the static lattice after the last animated frame.
        if (p.gridOpacity > 0) {
          ctx.clearRect(0, 0, w, h);
          drawLattice(cr, cg, cb, p.gridOpacity);
        } else {
          ctx.clearRect(0, 0, w, h);
        }
      }
    };

    const wake = () => {
      if (running) return;
      running  = true;
      lastFrame = performance.now();
      raf = requestAnimationFrame(draw);
    };
    wakeRef.current = wake;

    // ── Window-level pointer listeners ─────────────────────────────────────
    // Listening at window level means the grid responds to cursor movement
    // even when the pointer is over UI elements painted on top of the canvas.
    const onMove = (e: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      // Allow a one-cell margin so edge cells light up when the cursor is
      // slightly outside the canvas bounding rect.
      if (x >= -cellSize && y >= -cellSize && x <= w + cellSize && y <= h + cellSize) {
        energize(x, y);
        wake();
      }
    };

    const onDown = (e: PointerEvent) => {
      if (!propsRef.current.clickPulse) return;
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      if (x >= 0 && y >= 0 && x <= w && y <= h) {
        pulses.push({ x, y, t0: performance.now() });
        wake();
      }
    };

    const ro = new ResizeObserver(() => { rebuild(); wake(); });
    ro.observe(container);

    rebuild();
    wake();

    window.addEventListener('pointermove', onMove, { passive: true });
    window.addEventListener('pointerdown', onDown, { passive: true });

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerdown', onDown);
    };
    // cellSize triggers a full rebuild; other props are read live via propsRef.
  }, [cellSize]);

  // Re-wake the loop whenever purely visual props change while idle.
  useEffect(() => { wakeRef.current?.(); }, [gridOpacity, color, lineWidth, maxOpacity, fillOpacity, cellRadius]);

  return (
    <div
      ref={containerRef}
      style={{
        position:      'absolute',
        top:           0,
        left:          0,
        right:         0,
        bottom:        0,
        overflow:      'hidden',
        // Canvas sits behind all content — pointer events remain on content elements.
        pointerEvents: 'none',
        zIndex:        0,
      }}
    >
      <canvas
        ref={canvasRef}
        style={{ display: 'block', width: '100%', height: '100%' }}
      />
    </div>
  );
}
