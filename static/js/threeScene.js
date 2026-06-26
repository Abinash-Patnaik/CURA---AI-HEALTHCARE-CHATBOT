// ==========================================================================
// CURA 3D Medical Scene - Procedural Three.js Models & Animation Core
// ==========================================================================

let scene, camera, renderer, controls;
let avatarGroup, headGroup, leftArm, rightArm;
let dnaGroup, heartMesh, particleSystem;

// Materials
let skinMaterial, metalMaterial, visorMaterial, eyeMaterial, glowMaterial;

// Animation State
let clock = new THREE.Clock();
let waveTimer = 0;
let isWaving = false;
let isNodding = false;
let nodTimer = 0;
let baseEyeColor = 0x00f0ff; // Cyan

function initThree() {
    const container = document.getElementById('three-container');
    if (!container) return;

    // 1. SCENE & CAMERA
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x070a13, 0.08);

    camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 1.2, 5.5);

    // 2. RENDERER
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    container.appendChild(renderer.domElement);

    // 3. LIGHTING
    const ambientLight = new THREE.AmbientLight(0x0e1c38, 1.5);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x00f0ff, 2.5);
    dirLight.position.set(5, 10, 7);
    scene.add(dirLight);

    const pointLight = new THREE.PointLight(0xc362ff, 3, 10);
    pointLight.position.set(-2, 1, 2);
    scene.add(pointLight);

    const curaLight = new THREE.PointLight(0x00f0ff, 2, 5);
    curaLight.position.set(0, 0, 0); // attached to avatar
    scene.add(curaLight);

    // 4. ORBIT CONTROLS
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 + 0.1; // don't go below ground
    controls.minDistance = 3;
    controls.maxDistance = 10;
    controls.target.set(0, 0.7, 0);

    // 5. INITIALIZE PROCEDURAL MATERIALS
    skinMaterial = new THREE.MeshStandardMaterial({
        color: 0xe2f1ff,
        roughness: 0.15,
        metalness: 0.8,
        bumpScale: 0.05
    });

    metalMaterial = new THREE.MeshStandardMaterial({
        color: 0x22324d,
        roughness: 0.3,
        metalness: 0.9
    });

    visorMaterial = new THREE.MeshStandardMaterial({
        color: 0x050811,
        roughness: 0.1,
        metalness: 0.9,
    });

    eyeMaterial = new THREE.MeshBasicMaterial({
        color: baseEyeColor
    });

    glowMaterial = new THREE.MeshBasicMaterial({
        color: 0x00f0ff,
        transparent: true,
        opacity: 0.4
    });

    // 6. BUILD AVATAR DOCTOR
    buildDoctorAvatar();

    // 7. BUILD BACKGROUND STRUCTURES
    buildDNAHelix();
    build3DHeart();
    buildParticleSystem();

    // 8. EVENT LISTENERS
    window.addEventListener('resize', onWindowResize);

    // 9. START LOOP
    animate();
    
    // Wave on load
    triggerWave();
}

function buildDoctorAvatar() {
    avatarGroup = new THREE.Group();
    avatarGroup.position.set(0, 0.2, 0);
    scene.add(avatarGroup);

    // Torso (White Doctor Coat Cone)
    const torsoGeom = new THREE.CylinderGeometry(0.2, 0.5, 1.2, 32);
    const coatMaterial = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        roughness: 0.4,
        metalness: 0.1
    });
    const torso = new THREE.Mesh(torsoGeom, coatMaterial);
    torso.position.y = 0.5;
    avatarGroup.add(torso);

    // Inside Chest Core (glowing medical cross)
    const coreGeom = new THREE.BoxGeometry(0.15, 0.35, 0.15);
    const coreMesh = new THREE.Mesh(coreGeom, metalMaterial);
    coreMesh.position.set(0, 0.6, 0.22);
    avatarGroup.add(coreMesh);

    const crossHoriz = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.04, 0.02), new THREE.MeshBasicMaterial({ color: 0x00f0ff }));
    crossHoriz.position.set(0, 0.6, 0.3);
    const crossVert = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.12, 0.02), new THREE.MeshBasicMaterial({ color: 0x00f0ff }));
    crossVert.position.set(0, 0.6, 0.3);
    avatarGroup.add(crossHoriz, crossVert);

    // Stethoscope Torus
    const stethGeom = new THREE.TorusGeometry(0.22, 0.02, 16, 32);
    const steth = new THREE.Mesh(stethGeom, metalMaterial);
    steth.rotation.x = Math.PI / 2;
    steth.position.set(0, 0.95, 0.05);
    avatarGroup.add(steth);

    // Neck
    const neckGeom = new THREE.CylinderGeometry(0.1, 0.1, 0.15, 16);
    const neck = new THREE.Mesh(neckGeom, metalMaterial);
    neck.position.y = 1.15;
    avatarGroup.add(neck);

    // HEAD GROUP (tiltable)
    headGroup = new THREE.Group();
    headGroup.position.set(0, 1.35, 0);
    avatarGroup.add(headGroup);

    // Head Sphere
    const headGeom = new THREE.SphereGeometry(0.28, 32, 32);
    const head = new THREE.Mesh(headGeom, skinMaterial);
    headGroup.add(head);

    // Visor Face Screen
    const visorGeom = new THREE.BoxGeometry(0.38, 0.18, 0.2, 16, 16);
    const visor = new THREE.Mesh(visorGeom, visorMaterial);
    visor.position.set(0, 0.05, 0.18);
    // Slight curve approximation
    visor.scale.set(1, 1, 0.7);
    headGroup.add(visor);

    // Digital Glowing Eyes
    const eyeGeom = new THREE.SphereGeometry(0.025, 16, 16);
    
    leftEye = new THREE.Mesh(eyeGeom, eyeMaterial);
    leftEye.position.set(-0.08, 0.05, 0.3);
    
    rightEye = new THREE.Mesh(eyeGeom, eyeMaterial);
    rightEye.position.set(0.08, 0.05, 0.3);
    
    headGroup.add(leftEye, rightEye);

    // Forehead Reflector Disk (Doctor Mirror)
    const mirrorBack = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.02, 16), metalMaterial);
    mirrorBack.rotation.x = Math.PI / 2;
    mirrorBack.position.set(0, 0.25, 0.2);
    const mirrorGem = new THREE.Mesh(new THREE.SphereGeometry(0.03, 16, 16), new THREE.MeshBasicMaterial({ color: 0x00f0ff }));
    mirrorGem.position.set(0, 0.25, 0.21);
    headGroup.add(mirrorBack, mirrorGem);

    // Ears / Antennas (Teal glowing capsules)
    const earGeom = new THREE.CylinderGeometry(0.03, 0.03, 0.1, 16);
    const leftEar = new THREE.Mesh(earGeom, metalMaterial);
    leftEar.position.set(-0.29, 0.05, 0);
    leftEar.rotation.z = Math.PI / 2;
    
    const rightEar = new THREE.Mesh(earGeom, metalMaterial);
    rightEar.position.set(0.29, 0.05, 0);
    rightEar.rotation.z = -Math.PI / 2;
    
    headGroup.add(leftEar, rightEar);

    // ARMS & HANDS
    // Left Arm (Idle hanging / floating)
    leftArm = new THREE.Group();
    leftArm.position.set(-0.35, 0.9, 0);
    avatarGroup.add(leftArm);
    
    const armGeom = new THREE.CylinderGeometry(0.06, 0.05, 0.5, 16);
    const upperArmLeft = new THREE.Mesh(armGeom, coatMaterial);
    upperArmLeft.position.y = -0.25;
    leftArm.add(upperArmLeft);
    
    const handLeft = new THREE.Mesh(new THREE.SphereGeometry(0.06, 16, 16), skinMaterial);
    handLeft.position.y = -0.55;
    leftArm.add(handLeft);

    // Right Arm (Interactive: waving, gesturing)
    rightArm = new THREE.Group();
    rightArm.position.set(0.35, 0.9, 0);
    avatarGroup.add(rightArm);

    const upperArmRight = new THREE.Mesh(armGeom, coatMaterial);
    upperArmRight.position.y = -0.25;
    rightArm.add(upperArmRight);

    const handRight = new THREE.Mesh(new THREE.SphereGeometry(0.06, 16, 16), skinMaterial);
    handRight.position.y = -0.55;
    rightArm.add(handRight);

    // Bottom Holographic Base Rings
    const ringGeom = new THREE.RingGeometry(0.4, 0.44, 32);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, side: THREE.DoubleSide, transparent: true, opacity: 0.5 });
    const hologramRing = new THREE.Mesh(ringGeom, ringMat);
    hologramRing.rotation.x = Math.PI / 2;
    hologramRing.position.y = -0.25;
    avatarGroup.add(hologramRing);

    const ringGeom2 = new THREE.RingGeometry(0.48, 0.5, 32);
    const ringMat2 = new THREE.MeshBasicMaterial({ color: 0xc362ff, side: THREE.DoubleSide, transparent: true, opacity: 0.3 });
    const hologramRing2 = new THREE.Mesh(ringGeom2, ringMat2);
    hologramRing2.rotation.x = Math.PI / 2;
    hologramRing2.position.y = -0.3;
    avatarGroup.add(hologramRing2);
}

function buildDNAHelix() {
    dnaGroup = new THREE.Group();
    dnaGroup.position.set(-2.2, 0.6, -1.8);
    scene.add(dnaGroup);

    const pointsCount = 30;
    const helixRadius = 0.5;
    const height = 4.0;
    const sphereGeom = new THREE.SphereGeometry(0.05, 16, 16);
    const strandMatA = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
    const strandMatB = new THREE.MeshBasicMaterial({ color: 0xc362ff });
    const rungMat = new THREE.MeshBasicMaterial({ color: 0x223c5e, transparent: true, opacity: 0.4 });

    for (let i = 0; i < pointsCount; i++) {
        const t = (i / pointsCount) * Math.PI * 5; // Twists
        const y = (i / pointsCount) * height - (height / 2);
        
        const x1 = Math.cos(t) * helixRadius;
        const z1 = Math.sin(t) * helixRadius;
        const x2 = Math.cos(t + Math.PI) * helixRadius;
        const z2 = Math.sin(t + Math.PI) * helixRadius;

        // Sphere A
        const sphereA = new THREE.Mesh(sphereGeom, strandMatA);
        sphereA.position.set(x1, y, z1);
        dnaGroup.add(sphereA);

        // Sphere B
        const sphereB = new THREE.Mesh(sphereGeom, strandMatB);
        sphereB.position.set(x2, y, z2);
        dnaGroup.add(sphereB);

        // Connecting Rung every other node
        if (i % 2 === 0) {
            const distance = helixRadius * 2;
            const rungGeom = new THREE.CylinderGeometry(0.012, 0.012, distance, 8);
            const rung = new THREE.Mesh(rungGeom, rungMat);
            rung.position.set((x1 + x2) / 2, y, (z1 + z2) / 2);
            
            // Point the cylinder from point 1 to point 2
            rung.rotation.z = -t;
            dnaGroup.add(rung);
        }
    }
}

function build3DHeart() {
    // Generate Heart Shape
    const x = 0, y = 0;
    const heartShape = new THREE.Shape();
    
    heartShape.moveTo( x + 5, y + 5 );
    heartShape.bezierCurveTo( x + 5, y + 5, x + 4, y, x, y );
    heartShape.bezierCurveTo( x - 6, y, x - 6, y + 7,x - 6, y + 7 );
    heartShape.bezierCurveTo( x - 6, y + 11, x - 3, y + 15.4, x + 5, y + 19 );
    heartShape.bezierCurveTo( x + 12, y + 15.4, x + 16, y + 11, x + 16, y + 7 );
    heartShape.bezierCurveTo( x + 16, y + 7, x + 16, y, x + 10, y );
    heartShape.bezierCurveTo( x + 7, y, x + 5, y + 5, x + 5, y + 5 );

    const extrudeSettings = { depth: 4, bevelEnabled: true, bevelSegments: 3, steps: 2, bevelSize: 1, bevelThickness: 1 };
    const heartGeom = new THREE.ExtrudeGeometry(heartShape, extrudeSettings);
    
    // Scale and center geometry
    heartGeom.scale(0.015, -0.015, 0.015);
    heartGeom.center();

    // Glowing pink physical material (semi-transparent glass)
    const heartMat = new THREE.MeshPhysicalMaterial({
        color: 0xff3366,
        roughness: 0.1,
        metalness: 0.1,
        transmission: 0.6,
        thickness: 0.5,
        ior: 1.5,
        transparent: true,
        opacity: 0.85,
        emissive: 0x4a0011,
        emissiveIntensity: 0.8
    });

    heartMesh = new THREE.Mesh(heartGeom, heartMat);
    heartMesh.position.set(2.2, 0.8, -1.8);
    scene.add(heartMesh);
}

function buildParticleSystem() {
    const particleCount = 200;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const scales = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
        // Distribute particles in a cube around avatar
        positions[i * 3] = (Math.random() - 0.5) * 8;
        positions[i * 3 + 1] = (Math.random() - 0.5) * 6 + 1;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 8;

        scales[i] = Math.random();
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    // Glowing medical crosses/circles texture replacement using point styling
    const material = new THREE.PointsMaterial({
        color: 0x00f0ff,
        size: 0.04,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending
    });

    particleSystem = new THREE.Points(geometry, material);
    scene.add(particleSystem);
}

// ==========================================================================
// Animation & Interaction APIs
// ==========================================================================

function triggerWave() {
    if (!avatarGroup) return;
    isWaving = true;
    waveTimer = 0;
    const el = document.getElementById('assistant-activity');
    if (el) el.innerText = "Waving Greeting";
}

function triggerNod() {
    if (!avatarGroup) return;
    isNodding = true;
    nodTimer = 0;
    const el = document.getElementById('assistant-activity');
    if (el) el.innerText = "Nodding Confirmed";
}

function setExpression(type) {
    if (!avatarGroup || !eyeMaterial) return;
    if (type === 'concern') {
        eyeMaterial.color.setHex(0xff3366); // Red/Orange for alerts
        const el = document.getElementById('assistant-activity');
        if (el) el.innerText = "Concerned Focus";
    } else if (type === 'wave' || type === 'nod') {
        eyeMaterial.color.setHex(0x00f0ff);
    } else {
        eyeMaterial.color.setHex(baseEyeColor);
        const el = document.getElementById('assistant-activity');
        if (el) el.innerText = "Monitoring Vitals";
    }
}

function resetAvatarState() {
    if (!avatarGroup) return;
    isWaving = false;
    isNodding = false;
    if (rightArm) rightArm.rotation.set(0, 0, 0);
    if (leftArm) leftArm.rotation.set(0, 0, 0);
    if (headGroup) headGroup.rotation.set(0, 0, 0);
    setExpression('idle');
}

function onWindowResize() {
    const container = document.getElementById('three-container');
    if (!container) return;
    
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);

    const time = clock.getElapsedTime();

    // 1. GENTLE AVATAR FLOATING (Idle Breathing)
    if (avatarGroup) {
        avatarGroup.position.y = 0.2 + Math.sin(time * 1.5) * 0.08;
        avatarGroup.rotation.y = Math.sin(time * 0.5) * 0.04;
    }

    // 2. EYE BLINKING
    if (leftEye && rightEye) {
        const blinkCycle = time % 4; // blink every 4 seconds
        if (blinkCycle > 3.85) {
            leftEye.scale.y = 0.1;
            rightEye.scale.y = 0.1;
        } else {
            leftEye.scale.y = 1;
            rightEye.scale.y = 1;
        }
    }

    // 3. NODDING INTERACTION
    if (isNodding && headGroup) {
        nodTimer += 0.05;
        headGroup.rotation.x = Math.sin(nodTimer * Math.PI * 4) * 0.12; // tilt head up and down
        if (nodTimer > 1.0) {
            isNodding = false;
            headGroup.rotation.x = 0;
            document.getElementById('assistant-activity').innerText = "Idle Monitoring";
        }
    }

    // 4. WAVING INTERACTION
    if (isWaving && rightArm) {
        waveTimer += 0.04;
        // Raise arm
        rightArm.rotation.z = -Math.PI / 1.5;
        // Wiggle hand
        rightArm.rotation.x = Math.sin(waveTimer * 12) * 0.25;
        
        if (waveTimer > 2.0) {
            isWaving = false;
            // Ease arm back down
            gsap.to(rightArm.rotation, { z: 0, x: 0, duration: 0.5 });
            document.getElementById('assistant-activity').innerText = "Idle Monitoring";
        }
    }

    // 5. DNA HELIX ROTATION
    if (dnaGroup) {
        dnaGroup.rotation.y = time * 0.3;
    }

    // 6. HEART FLOATING & ROTATION
    if (heartMesh) {
        heartMesh.rotation.y = time * 0.25;
        heartMesh.position.y = 0.8 + Math.sin(time * 1.2) * 0.05;
        
        // Emissive pulse matching heartbeat
        const heartbeatFreq = 1.2; // roughly 72 BPM
        const pulse = Math.pow(Math.sin(time * Math.PI * heartbeatFreq), 4);
        heartMesh.material.emissiveIntensity = 0.4 + pulse * 0.6;
    }

    // 7. DRIFT PARTICLES
    if (particleSystem) {
        particleSystem.rotation.y = time * 0.02;
        const positions = particleSystem.geometry.attributes.position.array;
        
        // slowly drift particles upward
        for (let i = 1; i < positions.length; i += 3) {
            positions[i] += 0.002;
            if (positions[i] > 4) {
                positions[i] = -2;
            }
        }
        particleSystem.geometry.attributes.position.needsUpdate = true;
    }

    // Update Controls
    if (controls) {
        controls.update();
    }

    // Render Scene
    if (renderer && scene && camera) {
        renderer.render(scene, camera);
    }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    // Delay slightly to ensure layout container has dimensions
    setTimeout(initThree, 100);
});

// Camera Reset Button
document.addEventListener('DOMContentLoaded', () => {
    const resetBtn = document.getElementById('reset-camera-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (camera && controls) {
                gsap.to(camera.position, { x: 0, y: 1.2, z: 5.5, duration: 1 });
                gsap.to(controls.target, { x: 0, y: 0.7, z: 0, duration: 1, onUpdate: () => controls.update() });
            }
        });
    }
});
