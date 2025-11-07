// === SCENE SETUP ===
const scene = new THREE.Scene();

// Create camera
const camera = new THREE.PerspectiveCamera(
    75, 
    window.innerWidth / window.innerHeight, 
    0.1, 
    1000
);
camera.position.z = 3;

// Create renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('canvas-container').appendChild(renderer.domElement);

// === STARRY BACKGROUND ===
const starGeometry = new THREE.BufferGeometry();
const starCount = 5000;
const starPositions = new Float32Array(starCount * 3);

for (let i = 0; i < starCount * 3; i += 3) {
    starPositions[i] = (Math.random() - 0.5) * 100;
    starPositions[i + 1] = (Math.random() - 0.5) * 100;
    starPositions[i + 2] = (Math.random() - 0.5) * 100;
}

starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));

const starMaterial = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 0.1,
    sizeAttenuation: true
});

const stars = new THREE.Points(starGeometry, starMaterial);
scene.add(stars);

// === GLOBE ===
const globeGeometry = new THREE.SphereGeometry(1, 32, 32);

const globeMaterial = new THREE.MeshPhongMaterial({
    color: 0x2233ff,
    emissive: 0x112244,
    shininess: 25,
    specular: 0x333333
});

const globe = new THREE.Mesh(globeGeometry, globeMaterial);
scene.add(globe);

// === LIGHTING ===
const ambientLight = new THREE.AmbientLight(0x404040, 1);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 3, 5);
scene.add(directionalLight);

// === MOUSE INTERACTION (FIXED) ===
let isDragging = false;
let previousMousePosition = { x: 0, y: 0 };

// Mouse down event
document.addEventListener('mousedown', (e) => {
    isDragging = true;
    previousMousePosition = { x: e.clientX, y: e.clientY };
});

// Mouse move event
document.addEventListener('mousemove', (e) => {
    if (isDragging) {
        // Calculate mouse movement delta
        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;
        
        // Rotate globe (inverted controls feel more natural)
        globe.rotation.y += deltaX * 0.005;
        globe.rotation.x += deltaY * 0.005;
        
        // Update previous position
        previousMousePosition = { x: e.clientX, y: e.clientY };
    }
});

// Mouse up event
document.addEventListener('mouseup', () => {
    isDragging = false;
});

// Mouse leave event
document.addEventListener('mouseleave', () => {
    isDragging = false;
});

// === ANIMATION LOOP ===
function animate() {
    requestAnimationFrame(animate);
    
    // Slowly rotate stars
    // stars.rotation.y += 0.0002;
    
    // Render scene
    renderer.render(scene, camera);
}

animate();

// === HANDLE WINDOW RESIZE ===
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});