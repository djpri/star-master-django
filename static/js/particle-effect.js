(() => {
  // --- Constants ---
  const PARTICLE_COUNT = 150;
  const MIN_SPEED = 0.2;
  const MAX_SPEED = 0.5;
  const MIN_RADIUS = 2;
  const MAX_RADIUS = 5;
  // --- You can fine-tune these! ---
  const MAX_TRAIL_LENGTH = 40; // How long the trail is
  const GRAVITY_STRENGTH = 50; // How strong the mouse pull is
  const ORBIT_STRENGTH = 0.1; // The "sideways" push to encourage orbits
  const FRICTION = 0.798; // A slight drag to stabilize orbits. 1 is no friction.
  const MAX_VELOCITY = 2; // The speed limit for particles
  const TRAIL_CAPACITY = MAX_TRAIL_LENGTH * 5; // Maximum stored trail points per particle
  const BUCKET_COUNT = 4; // Trail segments share stroke settings within these buckets

  // --- Internal Physics Constants ---
  const MIN_GRAVITY_DISTANCE = 100; // Prevents extreme force at close range

  /**
   * @typedef {object} Particle
   * @property {number} x
   * @property {number} y
   * @property {number} vx
   * @property {number} vy
   * @property {number} radius
   * @property {number} hue
   * @property {number} saturation
   * @property {number} lightness
   * @property {number} numPoints
   * @property {number} innerRadiusRatio
   * @property {number} orbitDirection
   * @property {{x: number, y: number}[]} trail
   * @property {number} trailIndex
   * @property {number} trailSize
   */

  // --- Canvas Setup ---
  const canvas = document.getElementById("particle-canvas");
  if (!canvas) {
    console.error('Canvas element with id "particle-canvas" not found.');
    return;
  }
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    console.error("Failed to get 2D rendering context for canvas.");
    return;
  }

  /** @type {(Particle | undefined)[]} */
  const particles = new Array(PARTICLE_COUNT);
  const { sqrt, max, min, floor } = Math;
  const fadeLookup = new Float32Array(TRAIL_CAPACITY + 1);
  for (let i = 0; i <= TRAIL_CAPACITY; i++) {
    const progress = i / TRAIL_CAPACITY;
    const fade = 1 - progress;
    fadeLookup[i] = fade * fade * sqrt(fade); // Approximates fade^(1.5) without per-frame pow.
  }
  const mouse = {
    x: null,
    y: null,
  };

  // --- Core Functions ---
  const resizeCanvas = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };

  const createParticles = () => {
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const radius = Math.random() * (MAX_RADIUS - MIN_RADIUS) + MIN_RADIUS;
      const speed = Math.random() * (MAX_SPEED - MIN_SPEED) + MIN_SPEED;
      const angle = Math.random() * Math.PI * 2;

      let particle = particles[i];
      if (!particle) {
        // Pre-create ring-buffer trail so we can reuse point objects every frame.
        particle = {
          x: 0,
          y: 0,
          vx: 0,
          vy: 0,
          radius,
          hue: 0,
          saturation: 80,
          lightness: 70,
          numPoints: 5,
          innerRadiusRatio: 0.5,
          orbitDirection: 1,
          trail: Array.from({ length: TRAIL_CAPACITY }, () => ({ x: 0, y: 0 })),
          trailIndex: 0,
          trailSize: 0,
        };
        particles[i] = particle;
      }

      particle.x = Math.random() * canvas.width;
      particle.y = Math.random() * canvas.height;
      particle.vx = Math.cos(angle) * speed;
      particle.vy = Math.sin(angle) * speed;
      particle.radius = radius;
      particle.hue = Math.random() * 360;
      particle.saturation = 80;
      particle.lightness = 70;
      particle.numPoints = Math.floor(Math.random() * 4) + 5; // 5 to 8 points
      particle.innerRadiusRatio = Math.random() * 0.2 + 0.4; // 0.4 to 0.6
      particle.orbitDirection = Math.random() < 0.5 ? 1 : -1; // 1 for CCW, -1 for CW
      particle.trailIndex = 0;
      particle.trailSize = 0;
    }
  };

  /** @param {Particle} p */
  const drawStar = (p) => {
    const innerRadius = p.radius * p.innerRadiusRatio;
    let rot = (Math.PI / 2) * 3;
    const step = Math.PI / p.numPoints;

    ctx.beginPath();
    ctx.moveTo(p.x, p.y - p.radius);
    for (let i = 0; i < p.numPoints; i++) {
      let x = p.x + Math.cos(rot) * p.radius;
      let y = p.y + Math.sin(rot) * p.radius;
      ctx.lineTo(x, y);
      rot += step;

      x = p.x + Math.cos(rot) * innerRadius;
      y = p.y + Math.sin(rot) * innerRadius;
      ctx.lineTo(x, y);
      rot += step;
    }
    ctx.lineTo(p.x, p.y - p.radius);
    ctx.closePath();
    ctx.fillStyle = `hsl(${p.hue}, ${p.saturation}%, ${p.lightness}%)`;
    ctx.fill();
  };

  const animate = () => {
    // Clear the entire canvas on each frame to draw fresh trails
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach((particle) => {
      if (!particle) {
        return;
      }
      const p = /** @type {Particle} */ (particle);
      // --- Gravitational Pull & Orbital Logic ---
      if (mouse.x !== null && mouse.y !== null) {
        const dx = mouse.x - p.x;
        const dy = mouse.y - p.y;
        const distSq = dx * dx + dy * dy;
        const dist = sqrt(distSq) || 1; // prevent division by zero

        // 1. Gravitational pull (inward force)
        const effectiveDistSq = max(
          distSq,
          MIN_GRAVITY_DISTANCE * MIN_GRAVITY_DISTANCE
        );
        const pullForce = GRAVITY_STRENGTH / effectiveDistSq;

        const ax_pull = (dx / dist) * pullForce;
        const ay_pull = (dy / dist) * pullForce;

        // 2. Orbital force (sideways/tangential force, 90 degrees to the pull)
        const orbitFactor = ORBIT_STRENGTH * p.orbitDirection;
        const ax_orbit = (-dy / dist) * orbitFactor;
        const ay_orbit = (dx / dist) * orbitFactor;

        // 3. Combine forces and apply to velocity
        p.vx += ax_pull + ax_orbit;
        p.vy += ay_pull + ay_orbit;
      }

      // --- Physics & Movement ---
      // Apply friction
      p.vx *= FRICTION;
      p.vy *= FRICTION;

      // Cap velocity
      const speedSq = p.vx * p.vx + p.vy * p.vy;
      if (speedSq > MAX_VELOCITY * MAX_VELOCITY) {
        const invMag = MAX_VELOCITY / sqrt(speedSq);
        p.vx *= invMag;
        p.vy *= invMag;
      }

      // Update position
      p.x += p.vx;
      p.y += p.vy;

      // --- Screen Wrapping & Glitch Fix ---
      let wrapped = false;
      if (p.x < -p.radius) {
        p.x = canvas.width + p.radius;
        wrapped = true;
      }
      if (p.x > canvas.width + p.radius) {
        p.x = -p.radius;
        wrapped = true;
      }
      if (p.y < -p.radius) {
        p.y = canvas.height + p.radius;
        wrapped = true;
      }
      if (p.y > canvas.height + p.radius) {
        p.y = -p.radius;
        wrapped = true;
      }

      if (wrapped) {
        p.trailIndex = 0;
        p.trailSize = 0;
      }

      // --- Enhanced Trail Logic ---
      // 1. Trail length is now dependent on particle speed
      const currentSpeedSq = p.vx * p.vx + p.vy * p.vy;
      const MIN_TRAIL_LENGTH = 5;
      const speedRatio = min(sqrt(currentSpeedSq) / MAX_VELOCITY, 1.0);
      const dynamicTrailLength = min(
        floor(
          MIN_TRAIL_LENGTH + (MAX_TRAIL_LENGTH - MIN_TRAIL_LENGTH) * speedRatio
        ) * 5,
        TRAIL_CAPACITY
      );

      // Circular buffer write keeps allocations constant.
      const writeIndex = p.trailIndex;
      const point = p.trail[writeIndex];
      point.x = p.x;
      point.y = p.y;
      p.trailIndex = (writeIndex + 1) % TRAIL_CAPACITY;
      if (p.trailSize < dynamicTrailLength) {
        p.trailSize++;
      } else if (p.trailSize > dynamicTrailLength) {
        p.trailSize = dynamicTrailLength;
      }

      const segments = p.trailSize - 1;
      if (segments > 0) {
        const baseLineWidth = p.radius * 0.6;
        for (let pass = 0; pass < 2; pass++) {
          const isGlowPass = pass === 0;
          if (!isGlowPass) {
            ctx.shadowBlur = 0;
            ctx.shadowColor = "transparent";
          }

          for (let bucket = 0; bucket < BUCKET_COUNT; bucket++) {
            const bucketStart = bucket / BUCKET_COUNT;
            const bucketEnd = (bucket + 1) / BUCKET_COUNT;
            const bucketMid = (bucketStart + bucketEnd) * 0.5;
            const lineWidth = (1 - bucketMid) * baseLineWidth;
            if (lineWidth < 0.1) {
              continue;
            }

            let hasSegment = false;
            ctx.beginPath();
            for (let i = 0; i < segments; i++) {
              const progress = i / p.trailSize;
              if (progress < bucketStart || progress >= bucketEnd) {
                continue;
              }

              const headIndex =
                (p.trailIndex - 1 - i + TRAIL_CAPACITY) % TRAIL_CAPACITY;
              const tailIndex =
                (headIndex - 1 + TRAIL_CAPACITY) % TRAIL_CAPACITY;
              const start = p.trail[headIndex];
              const end = p.trail[tailIndex];

              ctx.moveTo(start.x, start.y);
              ctx.lineTo(end.x, end.y);
              hasSegment = true;
            }

            if (!hasSegment) {
              continue;
            }

            const lookupIndex = floor(bucketMid * TRAIL_CAPACITY);
            const baseOpacity = fadeLookup[lookupIndex] * 0.4;
            if (baseOpacity <= 0) {
              continue;
            }

            const hueShift = (bucketMid - 0.5) * -25;
            const hue = (p.hue + hueShift + 360) % 360;
            const strokeOpacity = isGlowPass ? baseOpacity * 0.5 : baseOpacity;

            if (isGlowPass) {
              ctx.lineWidth = lineWidth * 2.5;
              ctx.shadowColor = `hsla(${hue}, ${p.saturation}%, ${
                p.lightness
              }%, ${strokeOpacity * 0.6})`;
              ctx.shadowBlur = ctx.lineWidth * 0.7; // soft halo without per-segment updates
            } else {
              ctx.lineWidth = lineWidth;
            }

            ctx.strokeStyle = `hsla(${hue}, ${p.saturation}%, ${p.lightness}%, ${strokeOpacity})`;
            ctx.stroke();
          }
        }
        ctx.shadowBlur = 0;
        ctx.shadowColor = "transparent";
      }

      // Draw the star itself on top of the trail
      drawStar(p);
    });

    requestAnimationFrame(animate);
  };

  // --- Event Listeners ---
  const handleResize = () => {
    resizeCanvas();
    createParticles();
  };

  const handleMouseMove = (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  };

  const handleMouseLeave = () => {
    mouse.x = null;
    mouse.y = null;
  };

  // --- Initialization ---
  const init = () => {
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    resizeCanvas();
    createParticles();
    animate();
    window.addEventListener("resize", handleResize);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseleave", handleMouseLeave);
  };

  init();
})();
