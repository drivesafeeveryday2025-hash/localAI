"""
pallet_3d.py - Three.js WebGL Interactive 3D Pallet & Storage Room Box Stacking Visualizer.
Dynamically renders 3D product boxes inside a Pallet or Storage Room with full 360° drag-and-rotate.
"""
import json

def get_pallet_3d_html(
    target_type: str,
    item_l: float,
    item_w: float,
    item_h: float,
    container_l: float,
    container_w: float,
    container_h: float,
    quantity: int,
    max_quantity: int,
    utilization: float
) -> str:
    config = {
        "target_type": target_type,
        "item_l": max(0.05, float(item_l)),
        "item_w": max(0.05, float(item_w)),
        "item_h": max(0.05, float(item_h)),
        "container_l": max(0.1, float(container_l)),
        "container_w": max(0.1, float(container_w)),
        "container_h": max(0.1, float(container_h)),
        "quantity": int(quantity),
        "max_quantity": int(max_quantity),
        "utilization": round(float(utilization), 1)
    }
    config_json = json.dumps(config)

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      user-select: none;
    }}
    body, html {{
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: radial-gradient(circle at center, #0f172a 0%, #060913 75%, #020408 100%);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft JhengHei", sans-serif;
    }}
    #canvas-container {{
      width: 100%;
      height: 100%;
      position: relative;
      cursor: grab;
      overflow: hidden;
    }}
    #canvas-container:active {{
      cursor: grabbing;
    }}
    canvas {{
      display: block;
      width: 100%;
      height: 100%;
    }}
    /* Top HUD Header */
    .hud-top {{
      position: absolute;
      top: 14px;
      left: 16px;
      right: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      pointer-events: none;
      z-index: 100;
    }}
    .hud-badge {{
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(56, 189, 248, 0.5);
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.25);
      backdrop-filter: blur(10px);
      padding: 6px 16px;
      border-radius: 9999px;
      color: #38bdf8;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 1px;
      display: flex;
      align-items: center;
      gap: 7px;
    }}
    .hud-badge::before {{
      content: "";
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #38bdf8;
      box-shadow: 0 0 8px #38bdf8;
    }}
    .hud-stats {{
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(168, 85, 247, 0.5);
      box-shadow: 0 0 16px rgba(168, 85, 247, 0.2);
      backdrop-filter: blur(10px);
      padding: 6px 16px;
      border-radius: 9999px;
      color: #e2e8f0;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      gap: 12px;
    }}
    .hud-stats span b {{
      color: #38bdf8;
    }}
    /* Bottom Controls Hint */
    .hud-bottom {{
      position: absolute;
      bottom: 14px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(148, 163, 184, 0.25);
      backdrop-filter: blur(8px);
      padding: 6px 18px;
      border-radius: 20px;
      color: #94a3b8;
      font-size: 11.5px;
      pointer-events: none;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 8px;
      z-index: 100;
    }}
    .hud-bottom span {{
      color: #38bdf8;
      font-weight: 600;
    }}
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
  <div id="canvas-container">
    <div class="hud-top">
      <div class="hud-badge" id="hud-title">3D PACKING SIMULATION</div>
      <div class="hud-stats" id="hud-stats">
        <span>裝載: <b id="stat-count">0</b> 件</span>
        <span>最大容量: <b id="stat-max">0</b> 件</span>
        <span>容積率: <b id="stat-util">0%</b></span>
      </div>
    </div>
    <div class="hud-bottom">
      🖱️ <span>按住滑鼠左鍵拖曳</span> 360° 旋轉 | <span>滾輪</span> 縮放視野 (Scroll to Zoom)
    </div>
  </div>

  <script>
    const CFG = {config_json};

    document.getElementById('hud-title').innerText = (CFG.target_type === 'Pallet' ? '🪵 棧板 3D 裝載模擬 (Pallet)' : '🏢 倉庫 3D 空間模擬 (Storage Room)');
    document.getElementById('stat-count').innerText = CFG.quantity;
    document.getElementById('stat-max').innerText = CFG.max_quantity;
    document.getElementById('stat-util').innerText = CFG.utilization + '%';

    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();

    // Scene Center & World Group
    const worldGroup = new THREE.Group();
    scene.add(worldGroup);

    // Dimensions
    const cL = CFG.container_l;
    const cW = CFG.container_w;
    const cH = CFG.container_h;
    const iL = CFG.item_l;
    const iW = CFG.item_w;
    const iH = CFG.item_h;

    // Camera Calculation to Fit Container
    const maxDim = Math.max(cL, cW, cH);
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(maxDim * 1.5, maxDim * 1.3, maxDim * 1.8);
    camera.lookAt(0, cH * 0.4, 0);

    // Renderer
    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Lighting
    const ambLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambLight);

    const dirLight1 = new THREE.DirectionalLight(0x38bdf8, 1.2);
    dirLight1.position.set(maxDim * 2, maxDim * 3, maxDim * 2);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xa855f7, 0.8);
    dirLight2.position.set(-maxDim * 2, maxDim * 2, -maxDim * 2);
    scene.add(dirLight2);

    // Coordinate Grid Floor
    const gridDim = Math.max(12, Math.ceil(maxDim * 2.2));
    const grid = new THREE.GridHelper(gridDim, gridDim, 0x0ea5e9, 0x1e293b);
    grid.position.y = 0;
    worldGroup.add(grid);

    // =========================================================================
    // 1. RENDER CONTAINER (Pallet vs Storage Room)
    // =========================================================================
    if (CFG.target_type === 'Pallet') {{
      // --- PALLET BASE ---
      const palletGroup = new THREE.Group();
      const woodMat = new THREE.MeshStandardMaterial({{ color: 0xb45309, roughness: 0.85, metalness: 0.1 }});

      const palletH = 0.15; // standard wooden pallet base height
      // 3 Bottom stringer beams along length
      const beamGeo = new THREE.BoxGeometry(cL, palletH, 0.1);
      const b1 = new THREE.Mesh(beamGeo, woodMat); b1.position.set(0, palletH / 2, -cW / 2 + 0.08); palletGroup.add(b1);
      const b2 = new THREE.Mesh(beamGeo, woodMat); b2.position.set(0, palletH / 2, 0); palletGroup.add(b2);
      const b3 = new THREE.Mesh(beamGeo, woodMat); b3.position.set(0, palletH / 2, cW / 2 - 0.08); palletGroup.add(b3);

      // Top deck boards
      const boardCount = Math.max(5, Math.floor(cL / 0.15));
      const boardW = cL / (boardCount * 1.3);
      for (let i = 0; i < boardCount; i++) {{
        const xPos = -cL / 2 + (i + 0.5) * (cL / boardCount);
        const board = new THREE.Mesh(new THREE.BoxGeometry(boardW, 0.03, cW), woodMat);
        board.position.set(xPos, palletH + 0.015, 0);
        palletGroup.add(board);
      }}
      worldGroup.add(palletGroup);

      // Wireframe Limit Box (Stacking limit)
      const limitBoxGeo = new THREE.BoxGeometry(cL, cH, cW);
      const limitWire = new THREE.LineSegments(
        new THREE.EdgesGeometry(limitBoxGeo),
        new THREE.LineBasicMaterial({{ color: 0x38bdf8, transparent: true, opacity: 0.7 }})
      );
      limitWire.position.set(0, palletH + cH / 2, 0);
      worldGroup.add(limitWire);

    }} else {{
      // --- STORAGE ROOM ---
      const roomGroup = new THREE.Group();

      // Floor plane
      const floorMat = new THREE.MeshStandardMaterial({{ color: 0x0f172a, roughness: 0.6, metalness: 0.4 }});
      const floor = new THREE.Mesh(new THREE.PlaneGeometry(cL, cW), floorMat);
      floor.rotation.x = -Math.PI / 2;
      floor.position.set(0, 0.01, 0);
      roomGroup.add(floor);

      // Room Outer Edges Frame
      const roomBoxGeo = new THREE.BoxGeometry(cL, cH, cW);
      const roomEdges = new THREE.LineSegments(
        new THREE.EdgesGeometry(roomBoxGeo),
        new THREE.LineBasicMaterial({{ color: 0x0ea5e9, transparent: true, opacity: 0.85 }})
      );
      roomEdges.position.set(0, cH / 2, 0);
      roomGroup.add(roomEdges);

      // Semi-transparent walls
      const wallMat = new THREE.MeshBasicMaterial({{
        color: 0x0284c7,
        transparent: true,
        opacity: 0.08,
        side: THREE.DoubleSide
      }});
      const walls = new THREE.Mesh(roomBoxGeo, wallMat);
      walls.position.set(0, cH / 2, 0);
      roomGroup.add(walls);

      // Corner structural columns
      const colGeo = new THREE.BoxGeometry(0.12, cH, 0.12);
      const colMat = new THREE.MeshStandardMaterial({{ color: 0x38bdf8, metalness: 0.7, roughness: 0.3 }});
      const c1 = new THREE.Mesh(colGeo, colMat); c1.position.set(-cL/2, cH/2, -cW/2); roomGroup.add(c1);
      const c2 = new THREE.Mesh(colGeo, colMat); c2.position.set(cL/2, cH/2, -cW/2); roomGroup.add(c2);
      const c3 = new THREE.Mesh(colGeo, colMat); c3.position.set(-cL/2, cH/2, cW/2); roomGroup.add(c3);
      const c4 = new THREE.Mesh(colGeo, colMat); c4.position.set(cL/2, cH/2, cW/2); roomGroup.add(c4);

      worldGroup.add(roomGroup);
    }}

    // =========================================================================
    // 2. PACKING PRODUCT BOXES INTO 3D GRID
    // =========================================================================
    const baseY = (CFG.target_type === 'Pallet' ? 0.18 : 0.02);

    const nx = Math.max(1, Math.floor(cL / iL));
    const nz = Math.max(1, Math.floor(cW / iW));
    const ny = Math.max(1, Math.floor(cH / iH));

    const totalToPlace = Math.min(CFG.quantity, nx * nz * ny);

    // Box Geometry with slight gap so stacked boxes have defined edges
    const boxGeo = new THREE.BoxGeometry(iL * 0.96, iH * 0.96, iW * 0.96);
    const edgeGeo = new THREE.EdgesGeometry(boxGeo);

    // Materials: Cardboard warm orange/amber with bright outline
    const boxMat = new THREE.MeshStandardMaterial({{
      color: 0xf59e0b,
      roughness: 0.4,
      metalness: 0.2
    }});
    const boxEdgeMat = new THREE.LineBasicMaterial({{ color: 0xfef08a }});

    // Start coordinates (bottom-left corner)
    const startX = -cL / 2 + iL / 2;
    const startZ = -cW / 2 + iW / 2;

    const boxesGroup = new THREE.Group();
    worldGroup.add(boxesGroup);

    let placed = 0;
    for (let y = 0; y < ny && placed < totalToPlace; y++) {{
      for (let z = 0; z < nz && placed < totalToPlace; z++) {{
        for (let x = 0; x < nx && placed < totalToPlace; x++) {{
          const bx = startX + x * iL;
          const by = baseY + y * iH + (iH / 2);
          const bz = startZ + z * iW;

          const boxMesh = new THREE.Mesh(boxGeo, boxMat);
          boxMesh.position.set(bx, by, bz);

          const edges = new THREE.LineSegments(edgeGeo, boxEdgeMat);
          boxMesh.add(edges);

          boxesGroup.add(boxMesh);
          placed++;
        }}
      }}
    }}

    // =========================================================================
    // 3. MOUSE DRAG ROTATION & SCROLL ZOOM
    // =========================================================================
    let isDragging = false;
    let prevMouse = {{ x: 0, y: 0 }};
    let rotY = 0.4;
    let rotX = 0.25;
    let velX = 0;
    let velY = 0;

    container.addEventListener('mousedown', (e) => {{
      isDragging = true;
      prevMouse = {{ x: e.clientX, y: e.clientY }};
      velX = 0;
      velY = 0;
    }});

    window.addEventListener('mouseup', () => {{ isDragging = false; }});

    window.addEventListener('mousemove', (e) => {{
      if (!isDragging) return;
      const dx = e.clientX - prevMouse.x;
      const dy = e.clientY - prevMouse.y;

      rotY += dx * 0.006;
      rotX += dy * 0.006;
      rotX = Math.max(-0.15, Math.min(1.1, rotX)); // Keep above floor

      velX = dx * 0.003;
      velY = dy * 0.003;

      prevMouse = {{ x: e.clientX, y: e.clientY }};
    }});

    // Scroll Zoom
    container.addEventListener('wheel', (e) => {{
      e.preventDefault();
      const zoomFactor = e.deltaY * 0.002 * maxDim;
      camera.position.addScaledVector(camera.getWorldDirection(new THREE.Vector3()), -zoomFactor);
    }}, {{ passive: false }});

    // Touch Support
    container.addEventListener('touchstart', (e) => {{
      if (e.touches.length === 1) {{
        isDragging = true;
        prevMouse = {{ x: e.touches[0].clientX, y: e.touches[0].clientY }};
      }}
    }}, {{ passive: true }});

    window.addEventListener('touchend', () => {{ isDragging = false; }});

    window.addEventListener('touchmove', (e) => {{
      if (!isDragging || e.touches.length !== 1) return;
      const dx = e.touches[0].clientX - prevMouse.x;
      const dy = e.touches[0].clientY - prevMouse.y;
      rotY += dx * 0.006;
      rotX += dy * 0.006;
      rotX = Math.max(-0.15, Math.min(1.1, rotX));
      prevMouse = {{ x: e.touches[0].clientX, y: e.touches[0].clientY }};
    }}, {{ passive: true }});

    // Resize
    window.addEventListener('resize', () => {{
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    }});

    // Animation Loop
    function animate() {{
      requestAnimationFrame(animate);

      if (!isDragging) {{
        rotY += 0.0018 + velX;
        rotX += velY;
        velX *= 0.93;
        velY *= 0.93;
      }}

      worldGroup.rotation.y += (rotY - worldGroup.rotation.y) * 0.08;
      worldGroup.rotation.x += (rotX - worldGroup.rotation.x) * 0.08;

      renderer.render(scene, camera);
    }}

    animate();
  </script>
</body>
</html>
"""

