// === SCENE SETUP ===
const scene = new THREE.Scene();

// Create camera
const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);
camera.position.z = 30;

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
const stars = new THREE.Points(
    starGeometry,
    new THREE.PointsMaterial({ color: 0xffffff, size: 0.1 })
);
scene.add(stars);

// === GLOBE ===
const globeTexture = new THREE.TextureLoader().load("static/news/equitangular_daymap.jpg");
const globe = new THREE.Mesh(
    new THREE.SphereGeometry(1, 64, 64),
    new THREE.MeshPhongMaterial({
        map: globeTexture,
        shininess: 25,
        specular: 0x333333
    })
);
scene.add(globe);

// === LAT/LON → 3D VECTOR ===
function latLonToVector3(lat, lon, radius = 1.05) {
    const phi = (90 - lat) * Math.PI / 180;
    const theta = (lon + 180) * Math.PI / 180;

    return new THREE.Vector3(
        -(radius * Math.sin(phi) * Math.cos(theta)),
        radius * Math.cos(phi),
        radius * Math.sin(phi) * Math.sin(theta)
    );
}

// === MARKERS (BIGGER FOR EASIER CLICKING) ===
const markerMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
const markerHoverMaterial = new THREE.MeshBasicMaterial({ color: 0xff6600 });
const markerGeometry = new THREE.SphereGeometry(0.08, 16, 16); // Increased from 0.05

const countries = [
    { name: "India", lat: 20.6, lon: 78.96 },
    { name: "Russia", lat: 61.524, lon: 105.3188 },
    { name: "China", lat: 35.86, lon: 104.19 },
    { name: "USA", lat: 38.895, lon: -77.036 },
    { name: "Australia", lat: -25.2744, lon: 133.775 }
];

const markers = [];
countries.forEach(c => {
    const marker = new THREE.Mesh(markerGeometry, markerMaterial.clone());
    marker.position.copy(latLonToVector3(c.lat, c.lon));
    marker.userData = { country: c.name };
    scene.add(marker);
    markers.push(marker);
});

// === LIGHTING ===
scene.add(new THREE.AmbientLight(0xffffff, 0.9));
scene.add(new THREE.DirectionalLight(0xffffff, 1));

// === DRAG CONTROL ===
let isDragging = false;
let previousMousePosition = { x: 0, y: 0 };
let rotation = { x: 0, y: 0 };

renderer.domElement.addEventListener("mousedown", (e) => {
    isDragging = true;
    previousMousePosition.x = e.clientX;
    previousMousePosition.y = e.clientY;
});

renderer.domElement.addEventListener("mousemove", (e) => {
    if (!isDragging) {
        // Check for hover on markers
        mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
        
        raycaster.setFromCamera(mouse, camera);
        const hits = raycaster.intersectObjects(markers);
        
        // Reset all markers to default color
        markers.forEach(m => m.material.color.set(0xff0000));
        
        // Highlight hovered marker
        if (hits.length > 0) {
            hits[0].object.material.color.set(0xff6600);
            renderer.domElement.style.cursor = 'pointer';
        } else {
            renderer.domElement.style.cursor = 'grab';
        }
    } else {
        rotation.y += (e.clientX - previousMousePosition.x) * 0.004;
        rotation.x += (e.clientY - previousMousePosition.y) * 0.004;

        rotation.x = Math.max(-1.2, Math.min(1.2, rotation.x));
        
        previousMousePosition.x = e.clientX;
        previousMousePosition.y = e.clientY;
    }
});

renderer.domElement.addEventListener("mouseup", () => isDragging = false);
renderer.domElement.addEventListener("mouseleave", () => {
    isDragging = false;
    renderer.domElement.style.cursor = 'grab';
    markers.forEach(m => m.material.color.set(0xff0000));
});

// === RAYCASTER FOR CLICKS ===
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

let targetRotation = null;
let targetZoom = null;
let cameraOffset = { x: 0, y: 0 }; // For shifting globe left
let targetOffset = { x: 0, y: 0 };

window.addEventListener("click", (event) => {
    if (isDragging) return; // Don't trigger on drag
    
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(markers);

    if (hits.length > 0) {
        const marker = hits[0].object;
        focusOnMarker(marker);
        openSidePanel(marker.userData.country);
    }
});

// === CAMERA FOCUS ===
function focusOnMarker(marker) {
    const v = marker.position.clone().normalize();

    targetRotation = {
        x: Math.asin(v.y),
        y: Math.atan2(v.x, v.z)
    };

    targetZoom = 2.5;
    targetOffset = { x: -1.5, y: 0 }; // Shift globe left
}

// === SUPABASE SETUP ===
const SUPABASE_URL = "https://mydfflfgggqoliryamtn.supabase.co"
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im15ZGZmbGZnZ2dxb2xpcnlhbXRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2Nzg5NTksImV4cCI6MjA3NzI1NDk1OX0.mVM685NQKkxUV0ja5TZC3jf3uio9HhW6_ugVLHmgb5U"
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// Map country names to table names
const countryTableMap = {
    'USA': 'USA_news',
    'Russia': 'Russia_news',
    'India': 'India_news',
    'Australia': 'Australia_news',
    'China': 'China_news'
};

// === SLIDE-IN PANEL ===
async function openSidePanel(countryName) {
    const panel = document.getElementById("infoPanel");
    const title = document.getElementById("countryTitle");
    const content = document.getElementById("panelContent");

    title.textContent = countryName;
    panel.style.width = "700px";
    
    // Show loading state
    content.innerHTML = '<div style="text-align: center; padding: 20px;"><div class="loader"></div><p>Loading news...</p></div>';
    
    try {
        // Get the correct table name
        const tableName = countryTableMap[countryName];
        
        if (!tableName) {
            throw new Error('No news table found for this country');
        }
        
        // Fetch data from Supabase
        const { data, error } = await supabase
            .from(tableName)
            .select('*')
            .order('created_at', { ascending: false })
            .limit(10);
        
        if (error) throw error;
        
        // Display the data
        displayNewsData(data);
        
    } catch (error) {
        console.error('Error fetching data:', error);
        content.innerHTML = '<p style="color: #ffcccc;">Error loading news. Please try again.</p>';
    }
}

// Store news items globally for access
let currentNewsItems = [];

// === DISPLAY NEWS DATA ===
function displayNewsData(newsItems) {
    const content = document.getElementById("panelContent");
    
    if (!newsItems || newsItems.length === 0) {
        content.innerHTML = '<p style="opacity: 0.7;">No news available for this country.</p>';
        return;
    }
    
    // Store items for later access
    currentNewsItems = newsItems;
    
    // Create HTML for news items
    let html = '';
    newsItems.forEach((item, index) => {
        // Parse JSON fields if they're strings
        const headline = typeof item.headline === 'string' ? JSON.parse(item.headline) : item.headline;
        const link = typeof item.link === 'string' ? JSON.parse(item.link) : item.link;
        
        // Extract the actual text from headline and link (they might be objects or direct values)
        const headlineText = typeof headline === 'object' ? (headline.text || headline.title || Object.values(headline)[0]) : headline;
        const linkUrl = typeof link === 'object' ? (link.url || link.href || Object.values(link)[0]) : link;
        
        // Format tags
        const tagsHtml = item.tags && item.tags.length > 0 
            ? item.tags.map(tag => `<span style="
                background: rgba(255, 255, 255, 0.2);
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.75rem;
                margin-right: 5px;
                display: inline-block;
                margin-top: 5px;
            ">${tag}</span>`).join('')
            : '';
        
        html += `
            <div class="news-item" data-index="${index}" style="
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                border-left: 3px solid white;
                cursor: pointer;
                transition: all 0.3s ease;
            " 
            onmouseover="this.style.background='rgba(255, 255, 255, 0.15)'; this.style.transform='translateX(-5px)'"
            onmouseout="this.style.background='rgba(255, 255, 255, 0.1)'; this.style.transform='translateX(0)'">
                <h3 style="margin: 0 0 10px 0; font-size: 1.05rem; line-height: 1.4;">${headlineText || 'Untitled'}</h3>
                
                ${tagsHtml ? `<div style="margin-bottom: 10px;">${tagsHtml}</div>` : ''}
                
                ${linkUrl ? `<a href="${linkUrl}" target="_blank" onclick="event.stopPropagation()" style="
                    color: #fff;
                    font-size: 0.85rem;
                    text-decoration: none;
                    opacity: 0.8;
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                ">🔗 Read original source</a>` : ''}
            </div>
        `;
    });
    
    content.innerHTML = html;
    
    // Add click listeners to news items
    document.querySelectorAll('.news-item').forEach(item => {
        item.addEventListener('click', () => {
            const index = parseInt(item.getAttribute('data-index'));
            const newsItem = currentNewsItems[index];
            
            // Parse fields
            const headline = typeof newsItem.headline === 'string' ? JSON.parse(newsItem.headline) : newsItem.headline;
            const link = typeof newsItem.link === 'string' ? JSON.parse(newsItem.link) : newsItem.link;
            
            const headlineText = typeof headline === 'object' ? (headline.text || headline.title || Object.values(headline)[0]) : headline;
            const linkUrl = typeof link === 'object' ? (link.url || link.href || Object.values(link)[0]) : link;
            
            openArticleModal(headlineText, newsItem.content || '', linkUrl);
        });
    });
}
// === OPEN ARTICLE MODAL ===
async function openArticleModal(headline, content, link) {
    const modal = document.getElementById('articleModal');
    const modalHeadline = document.getElementById('modalHeadline');
    const modalContent = document.getElementById('modalContent');
    const modalLink = document.getElementById('modalLink');
    
    modalHeadline.textContent = headline;
    
    // Show loading state
    modalContent.innerHTML = '<div style="text-align: center; padding: 40px;"><div class="loader"></div><p>Loading article...</p></div>';
    
    // Show modal immediately
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    // Display content (it's already fetched from the initial load)
    modalContent.innerHTML = content ? `<p style="white-space: pre-wrap; line-height: 1.6;">${content}</p>` : '<p style="opacity: 0.7;">No content available.</p>';
    
    if (link) {
        modalLink.href = link;
        modalLink.style.display = 'inline-block';
    } else {
        modalLink.style.display = 'none';
    }
}
// === CLOSE ARTICLE MODAL ===
function closeArticleModal() {
    const modal = document.getElementById('articleModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    const modal = document.getElementById('articleModal');
    if (e.target === modal) {
        closeArticleModal();
    }
});

// Close panel when clicking close button
document.getElementById("closePanel").addEventListener("click", () => {
    const panel = document.getElementById("infoPanel");
    panel.style.width = "0";
    
    // Reset camera position
    targetZoom = null;
    targetOffset = { x: 0, y: 0 };
    targetRotation = null;
});

// === ANIMATION LOOP ===
function animate() {
    requestAnimationFrame(animate);

    // Smooth camera easing
    if (targetRotation) {
        rotation.x += (targetRotation.x - rotation.x) * 0.05;
        rotation.y += (targetRotation.y - rotation.y) * 0.05;
    }

    // Smooth offset transition
    cameraOffset.x += (targetOffset.x - cameraOffset.x) * 0.05;
    cameraOffset.y += (targetOffset.y - cameraOffset.y) * 0.05;

    const radius = targetZoom || 3;

    camera.position.x = radius * Math.sin(rotation.y) * Math.cos(rotation.x) + cameraOffset.x;
    camera.position.y = radius * Math.sin(rotation.x) + cameraOffset.y;
    camera.position.z = radius * Math.cos(rotation.y) * Math.cos(rotation.x);

    camera.lookAt(cameraOffset.x, cameraOffset.y, 0);

    renderer.render(scene, camera);
}

animate();

// === RESIZE ===
window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});