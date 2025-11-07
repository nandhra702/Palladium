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
const globeGeometry = new THREE.SphereGeometry(1, 64, 64);

// ✅ ADD YOUR IMAGE AS TEXTURE HERE
const globeTexture = new THREE.TextureLoader().load('static/news/photoroom.png'); // replace with your JPEG filename
const globeMaterial = new THREE.MeshPhongMaterial({
    map: globeTexture,
    shininess: 25,
    specular: 0x333333
});

const globe = new THREE.Mesh(globeGeometry, globeMaterial);
scene.add(globe);

// === LIGHTING ===
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6); // brighter ambient light
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
scene.add(directionalLight);

// === DRAG CAMERA AROUND GLOBE ===
let isDragging = false;
let previousMousePosition = { x: 0, y: 0 };
let rotation = { x: 0, y: 0 }; // store rotation angles

renderer.domElement.addEventListener('mousedown', (e) => {
    isDragging = true;
    previousMousePosition = { x: e.clientX, y: e.clientY };
    e.preventDefault();
});

renderer.domElement.addEventListener('mousemove', (e) => {
    if (isDragging) {
        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;

        rotation.y += deltaX * 0.005;
        rotation.x += deltaY * 0.005;
        rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, rotation.x));

        previousMousePosition = { x: e.clientX, y: e.clientY };
    }
    e.preventDefault();
});

renderer.domElement.addEventListener('mouseup', () => { isDragging = false; });
renderer.domElement.addEventListener('mouseleave', () => { isDragging = false; });

// === ANIMATION LOOP ===
function animate() {
    requestAnimationFrame(animate);

    // Update camera position based on rotation
    const radius = 3;
    camera.position.x = radius * Math.sin(rotation.y) * Math.cos(rotation.x);
    camera.position.y = radius * Math.sin(rotation.x);
    camera.position.z = radius * Math.cos(rotation.y) * Math.cos(rotation.x);
    camera.lookAt(globe.position);

    renderer.render(scene, camera);
}
animate();

// === HANDLE WINDOW RESIZE ===
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    directionalLight.position.copy(camera.position);
    renderer.setSize(window.innerWidth, window.innerHeight);
});
