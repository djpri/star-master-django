(() => {
    // --- Constants ---
    const PARTICLE_COUNT = 150;
    const MIN_SPEED = 0.1;
    const MAX_SPEED = 0.5;
    const MIN_RADIUS = 2;
    const MAX_RADIUS = 5;
    // --- You can fine-tune these! ---
    const MAX_TRAIL_LENGTH = 40; // How long the trail is
    const GRAVITY_STRENGTH = 50; // How strong the mouse pull is
    const ORBIT_STRENGTH = 0.1;   // The "sideways" push to encourage orbits
    const FRICTION = 0.798;       // A slight drag to stabilize orbits. 1 is no friction.
    const MAX_VELOCITY = 2;       // The speed limit for particles
    
    // --- Internal Physics Constants ---
    const MIN_GRAVITY_DISTANCE = 100; // Prevents extreme force at close range
    
    // Regular expression for parsing HSL colors.
    const hslRegex = /hsl\((\d+\.?\d*),\s*(\d+)%,\s*(\d+)%\)/;


    /**
     * @typedef {object} Particle
     * @property {number} x
     * @property {number} y
     * @property {number} vx
     * @property {number} vy
     * @property {number} radius
     * @property {string} color
     * @property {number} numPoints
     * @property {number} innerRadiusRatio
     * @property {number} orbitDirection
     * @property {{x: number, y: number}[]} trail
     */

    // --- Canvas Setup ---
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) {
        console.error('Canvas element with id "particle-canvas" not found.');
        return;
    }
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('Failed to get 2D rendering context for canvas.');
        return;
    }

    /** @type {Particle[]} */
    let particles = [];
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
        particles = [];
        for (let i = 0; i < PARTICLE_COUNT; i++) {
            const radius = Math.random() * (MAX_RADIUS - MIN_RADIUS) + MIN_RADIUS;
            const speed = Math.random() * (MAX_SPEED - MIN_SPEED) + MIN_SPEED;
            const angle = Math.random() * Math.PI * 2;

            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                radius,
                color: `hsl(${Math.random() * 360}, 80%, 70%)`,
                numPoints: Math.floor(Math.random() * 4) + 5, // 5 to 8 points
                innerRadiusRatio: Math.random() * 0.2 + 0.4, // 0.4 to 0.6
                orbitDirection: Math.random() < 0.5 ? 1 : -1, // 1 for CCW, -1 for CW
                trail: [],
            });
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
        ctx.fillStyle = p.color;
        ctx.fill();
    };

    const animate = () => {
        // Clear the entire canvas on each frame to draw fresh trails
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(p => {
            // --- Gravitational Pull & Orbital Logic ---
            if (mouse.x !== null && mouse.y !== null) {
                const dx = mouse.x - p.x;
                const dy = mouse.y - p.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1; // prevent division by zero

                // 1. Gravitational pull (inward force)
                const distSq = dx * dx + dy * dy;
                const effectiveDistSq = Math.max(distSq, MIN_GRAVITY_DISTANCE * MIN_GRAVITY_DISTANCE);
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
            const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
            if (speed > MAX_VELOCITY) {
                p.vx = (p.vx / speed) * MAX_VELOCITY;
                p.vy = (p.vy / speed) * MAX_VELOCITY;
            }
            
            // Update position
            p.x += p.vx;
            p.y += p.vy;
            
            // --- Screen Wrapping & Glitch Fix ---
            let wrapped = false;
            if (p.x < -p.radius) { p.x = canvas.width + p.radius; wrapped = true; }
            if (p.x > canvas.width + p.radius) { p.x = -p.radius; wrapped = true; }
            if (p.y < -p.radius) { p.y = canvas.height + p.radius; wrapped = true; }
            if (p.y > canvas.height + p.radius) { p.y = -p.radius; wrapped = true; }
            
            if (wrapped) {
                p.trail = [];
            }
            
            // --- Enhanced Trail Logic ---
            // 1. Trail length is now dependent on particle speed
            const currentSpeed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
            const MIN_TRAIL_LENGTH = 5;
            const speedRatio = Math.min(currentSpeed / MAX_VELOCITY, 1.0);
            const dynamicTrailLength = Math.floor(MIN_TRAIL_LENGTH + (MAX_TRAIL_LENGTH - MIN_TRAIL_LENGTH) * speedRatio) * 5;

            p.trail.unshift({ x: p.x, y: p.y });
            if (p.trail.length > dynamicTrailLength) {
                p.trail.pop();
            }
            
            // 2. Parse HSL color for manipulation
            const colorMatch = p.color.match(hslRegex);
            if (!colorMatch) {
                drawStar(p);
                return; // Skips trail drawing for this particle if color format is unexpected
            }
            const [, baseHueStr, saturation, lightness] = colorMatch;
            const baseHue = parseFloat(baseHueStr);

            // 3. Draw the enhanced trail with glow, color shift, and better fading
            for (let i = 0; i < p.trail.length - 1; i++) {
                const start = p.trail[i];
                const end = p.trail[i + 1];

                const progress = i / p.trail.length;
                
                // Use a power curve for a more natural fade-out
                const opacity = Math.pow(1 - progress, 1.5) * 0.4;
                
                // Tapering width, slightly thicker base
                const lineWidth = (1 - progress) * (p.radius * 0.6);
                
                if (lineWidth < 0.1) continue;

                // Subtle color variation along the trail
                const hueShift = (progress - 0.5) * -25; // Shifts from -12.5 to +12.5
                const newHue = (baseHue + hueShift + 360) % 360;
                
                const trailColor = `hsla(${newHue}, ${saturation}%, ${lightness}%, ${opacity})`;

                // Draw a wider, more transparent "glow" line underneath
                ctx.beginPath();
                ctx.moveTo(start.x, start.y);
                ctx.lineTo(end.x, end.y);
                ctx.strokeStyle = `hsla(${newHue}, ${saturation}%, ${lightness}%, ${opacity * 0.5})`;
                ctx.lineWidth = lineWidth * 2.5;
                ctx.stroke();

                // Draw the main, sharper trail line on top
                ctx.beginPath();
                ctx.moveTo(start.x, start.y);
                ctx.lineTo(end.x, end.y);
                ctx.strokeStyle = trailColor;
                ctx.lineWidth = lineWidth;
                ctx.stroke();
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
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        resizeCanvas();
        createParticles();
        animate();
        window.addEventListener('resize', handleResize);
        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseleave', handleMouseLeave);
    };

    init();

})();