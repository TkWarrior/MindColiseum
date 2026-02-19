import { useRef, useEffect, useMemo } from 'react';

// ─── Simplex Noise (compact 3D implementation) ───────────────────────────────
// Based on Stefan Gustavson's simplex noise — adapted to a minimal JS version.
const F3 = 1.0 / 3.0;
const G3 = 1.0 / 6.0;

const grad3 = [
    [1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0],
    [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],
    [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1],
];

function buildPermTable(seed = 0) {
    const p = new Uint8Array(256);
    for (let i = 0; i < 256; i++) p[i] = i;
    // Fisher-Yates shuffle with simple seed
    for (let i = 255; i > 0; i--) {
        seed = (seed * 16807 + 0) % 2147483647;
        const j = seed % (i + 1);
        [p[i], p[j]] = [p[j], p[i]];
    }
    const perm = new Uint8Array(512);
    const permMod12 = new Uint8Array(512);
    for (let i = 0; i < 512; i++) {
        perm[i] = p[i & 255];
        permMod12[i] = perm[i] % 12;
    }
    return { perm, permMod12 };
}

const { perm, permMod12 } = buildPermTable(42);

function simplex3D(x, y, z) {
    const s = (x + y + z) * F3;
    const i = Math.floor(x + s);
    const j = Math.floor(y + s);
    const k = Math.floor(z + s);
    const t = (i + j + k) * G3;
    const X0 = i - t, Y0 = j - t, Z0 = k - t;
    const x0 = x - X0, y0 = y - Y0, z0 = z - Z0;

    let i1, j1, k1, i2, j2, k2;
    if (x0 >= y0) {
        if (y0 >= z0) { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 1; k2 = 0; }
        else if (x0 >= z0) { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 0; k2 = 1; }
        else { i1 = 0; j1 = 0; k1 = 1; i2 = 1; j2 = 0; k2 = 1; }
    } else {
        if (y0 < z0) { i1 = 0; j1 = 0; k1 = 1; i2 = 0; j2 = 1; k2 = 1; }
        else if (x0 < z0) { i1 = 0; j1 = 1; k1 = 0; i2 = 0; j2 = 1; k2 = 1; }
        else { i1 = 0; j1 = 1; k1 = 0; i2 = 1; j2 = 1; k2 = 0; }
    }

    const x1 = x0 - i1 + G3, y1 = y0 - j1 + G3, z1 = z0 - k1 + G3;
    const x2 = x0 - i2 + 2 * G3, y2 = y0 - j2 + 2 * G3, z2 = z0 - k2 + 2 * G3;
    const x3 = x0 - 1 + 3 * G3, y3 = y0 - 1 + 3 * G3, z3 = z0 - 1 + 3 * G3;

    const ii = i & 255, jj = j & 255, kk = k & 255;

    const dot = (gi, dx, dy, dz) => grad3[gi][0] * dx + grad3[gi][1] * dy + grad3[gi][2] * dz;

    let n0 = 0, n1 = 0, n2 = 0, n3 = 0;
    let t0 = 0.6 - x0 * x0 - y0 * y0 - z0 * z0;
    if (t0 > 0) { t0 *= t0; n0 = t0 * t0 * dot(permMod12[ii + perm[jj + perm[kk]]], x0, y0, z0); }
    let t1 = 0.6 - x1 * x1 - y1 * y1 - z1 * z1;
    if (t1 > 0) { t1 *= t1; n1 = t1 * t1 * dot(permMod12[ii + i1 + perm[jj + j1 + perm[kk + k1]]], x1, y1, z1); }
    let t2 = 0.6 - x2 * x2 - y2 * y2 - z2 * z2;
    if (t2 > 0) { t2 *= t2; n2 = t2 * t2 * dot(permMod12[ii + i2 + perm[jj + j2 + perm[kk + k2]]], x2, y2, z2); }
    let t3 = 0.6 - x3 * x3 - y3 * y3 - z3 * z3;
    if (t3 > 0) { t3 *= t3; n3 = t3 * t3 * dot(permMod12[ii + 1 + perm[jj + 1 + perm[kk + 1]]], x3, y3, z3); }

    return 32.0 * (n0 + n1 + n2 + n3); // returns -1 to 1
}

// ─── Color Config Per Agent ──────────────────────────────────────────────────
const AGENT_COLORS = {
    pro: {
        color1: [50, 180, 255],   // bright blue
        color2: [0, 255, 255],    // vivid cyan
        rim: [30, 200, 255],      // glass rim tint
    },
    con: {
        color1: [255, 30, 80],    // vivid red
        color2: [255, 120, 50],   // bright orange-red
        rim: [255, 60, 100],      // glass rim tint
    },
    judge: {
        color1: [0, 255, 160],    // vivid green
        color2: [80, 255, 120],   // bright lime-green
        rim: [30, 255, 140],      // glass rim tint
    },
};

// ─── Glass Orb Component ─────────────────────────────────────────────────────
const GlassOrb = ({ agent = 'pro', isSpeaking = false, size = 128 }) => {
    const canvasRef = useRef(null);
    const animRef = useRef(null);
    const speakingRef = useRef(isSpeaking);

    // Keep speaking ref in sync without re-creating the animation loop
    useEffect(() => { speakingRef.current = isSpeaking; }, [isSpeaking]);

    const colors = useMemo(() => AGENT_COLORS[agent] || AGENT_COLORS.pro, [agent]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const w = size;
        const h = size;
        const cx = w / 2;
        const cy = h / 2;
        const radius = w * 0.42;

        // Pre-compute circle mask coordinates
        const circlePixels = [];
        for (let y = 0; y < h; y++) {
            for (let x = 0; x < w; x++) {
                const dx = x - cx;
                const dy = y - cy;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist <= radius) {
                    circlePixels.push({ x, y, dx, dy, dist, normDist: dist / radius });
                }
            }
        }

        let lastTime = 0;
        const idleFPS = 15;
        const activeFPS = 60;

        function render(time) {
            const speaking = speakingRef.current;
            const targetInterval = 1000 / (speaking ? activeFPS : idleFPS);

            if (time - lastTime < targetInterval) {
                animRef.current = requestAnimationFrame(render);
                return;
            }
            lastTime = time;

            const t = time * 0.001; // seconds
            const speed = speaking ? 1.5 : 0.35;
            const intensity = speaking ? 1.3 : 0.75;
            const noiseScale = speaking ? 2.5 : 2.0;
            const brightnessMult = speaking ? 1.6 : 1.4;

            const imageData = ctx.createImageData(w, h);
            const data = imageData.data;

            for (let i = 0; i < circlePixels.length; i++) {
                const { x, y, dx, dy, dist, normDist } = circlePixels[i];

                // Normalized position on sphere surface (-1 to 1)
                const nx = dx / radius;
                const ny = dy / radius;

                // Simulate Z depth on a sphere
                const nzSq = 1 - nx * nx - ny * ny;
                const nz = nzSq > 0 ? Math.sqrt(nzSq) : 0;

                // ── Internal Energy Flow ──
                // Sample 3D noise using sphere coordinates + time
                const noiseVal = simplex3D(
                    nx * noiseScale,
                    ny * noiseScale + t * speed,
                    nz * noiseScale + t * speed * 0.5
                );

                // Horizontal energy band — concentrated around equator (like reference)
                const bandWidth = speaking ? 0.6 : 0.45;
                const band = Math.max(0, 1 - Math.abs(ny) / bandWidth);
                const bandSmooth = band * band * (3 - 2 * band); // smoothstep

                // Noise-driven intensity within the band
                const energyRaw = (noiseVal * 0.5 + 0.5); // 0-1
                const energy = energyRaw * bandSmooth * intensity;

                // Color blend: mix color1 ↔ color2 based on noise
                const mixFactor = noiseVal * 0.5 + 0.5;
                const r = colors.color1[0] + (colors.color2[0] - colors.color1[0]) * mixFactor;
                const g = colors.color1[1] + (colors.color2[1] - colors.color1[1]) * mixFactor;
                const b = colors.color1[2] + (colors.color2[2] - colors.color1[2]) * mixFactor;

                // ── Glass Shell (Fresnel Rim) ──
                // Bright at edges, transparent at center (like real glass)
                const fresnel = Math.pow(1 - nz, 3);
                const rimStrength = 0.25 + (speaking ? 0.15 : 0);
                const rimR = colors.rim[0] * fresnel * rimStrength;
                const rimG = colors.rim[1] * fresnel * rimStrength;
                const rimB = colors.rim[2] * fresnel * rimStrength;

                // ── Specular Highlight (top-left) ──
                const specX = nx + 0.4;
                const specY = ny + 0.4;
                const specDist = Math.sqrt(specX * specX + specY * specY);
                const specular = Math.pow(Math.max(0, 1 - specDist * 1.5), 8) * 0.5;

                // ── Composite (with brightness boost) ──
                const finalR = Math.min(255, r * energy * brightnessMult + rimR + specular * 255);
                const finalG = Math.min(255, g * energy * brightnessMult + rimG + specular * 255);
                const finalB = Math.min(255, b * energy * brightnessMult + rimB + specular * 255);

                // Alpha: the sphere is visible, outer area stays transparent
                const edgeSoftness = Math.min(1, (1 - normDist) * 8);
                const alpha = Math.max(energy * 0.9, fresnel * rimStrength) * edgeSoftness * 255;

                const idx = (y * w + x) * 4;
                data[idx] = finalR;
                data[idx + 1] = finalG;
                data[idx + 2] = finalB;
                data[idx + 3] = Math.min(255, alpha);
            }

            ctx.putImageData(imageData, 0, 0);
            animRef.current = requestAnimationFrame(render);
        }

        animRef.current = requestAnimationFrame(render);

        return () => {
            if (animRef.current) cancelAnimationFrame(animRef.current);
        };
    }, [size, colors]);

    return (
        <canvas
            ref={canvasRef}
            width={size}
            height={size}
            style={{
                width: size,
                height: size,
                borderRadius: '50%',
                display: 'block',
            }}
        />
    );
};

export default GlassOrb;
