"""
hero_3d.py - Interactive 3D WebGL Hero Component with Logistics & AI compound:
Forklift, Logistics Truck, AI Computer Workstation, Central Knowledge Core, and Orbiting 2D Tags.
"""

def get_hero_3d_html() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      user-select: none;
    }
    body, html {
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: radial-gradient(circle at center, #0f172a 0%, #060913 70%, #020408 100%);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft JhengHei", sans-serif;
    }
    #canvas-container {
      width: 100%;
      height: 100%;
      position: relative;
      cursor: grab;
      overflow: hidden;
    }
    #canvas-container:active {
      cursor: grabbing;
    }
    canvas {
      display: block;
      width: 100%;
      height: 100%;
      pointer-events: none;
    }
    /* HUD Overlays */
    .hud-badge {
      position: absolute;
      top: 16px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(56, 189, 248, 0.4);
      box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
      backdrop-filter: blur(12px);
      padding: 6px 18px;
      border-radius: 9999px;
      color: #38bdf8;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 2px;
      text-transform: uppercase;
      pointer-events: none;
      display: flex;
      align-items: center;
      gap: 8px;
      z-index: 200;
    }
    .hud-badge::before {
      content: "";
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #38bdf8;
      box-shadow: 0 0 10px #38bdf8;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.8); }
    }
    .hud-hint {
      position: absolute;
      bottom: 16px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(148, 163, 184, 0.25);
      backdrop-filter: blur(8px);
      padding: 7px 18px;
      border-radius: 20px;
      color: #94a3b8;
      font-size: 12.5px;
      letter-spacing: 0.5px;
      pointer-events: none;
      display: flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
      z-index: 200;
    }
    .hud-hint span {
      color: #38bdf8;
      font-weight: 600;
    }

    /* 3D Floating Tags Layer */
    #tags-layer {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      overflow: hidden;
    }
    .floating-tag {
      position: absolute;
      display: flex;
      align-items: center;
      gap: 7px;
      padding: 6px 13px;
      border-radius: 20px;
      font-size: 11.5px;
      font-weight: 600;
      letter-spacing: 0.3px;
      white-space: nowrap;
      pointer-events: auto;
      cursor: pointer;
      backdrop-filter: blur(10px);
      transition: border-color 0.25s, box-shadow 0.25s, background 0.25s;
      will-change: transform, opacity;
      transform-origin: center center;
    }
    .floating-tag .tag-dot {
      width: 6.5px;
      height: 6.5px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .tag-cyan {
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(56, 189, 248, 0.5);
      color: #e0f2fe;
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5), inset 0 0 8px rgba(56, 189, 248, 0.15);
    }
    .tag-cyan .tag-dot {
      background: #38bdf8;
      box-shadow: 0 0 8px #38bdf8;
    }
    .tag-cyan:hover {
      border-color: #38bdf8;
      box-shadow: 0 0 22px rgba(56, 189, 248, 0.6);
      background: rgba(15, 23, 42, 0.95);
    }

    .tag-amber {
      background: rgba(36, 24, 6, 0.88);
      border: 1px solid rgba(251, 191, 36, 0.55);
      color: #fef3c7;
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5), inset 0 0 8px rgba(251, 191, 36, 0.15);
    }
    .tag-amber .tag-dot {
      background: #fbbf24;
      box-shadow: 0 0 8px #fbbf24;
    }
    .tag-amber:hover {
      border-color: #fbbf24;
      box-shadow: 0 0 22px rgba(251, 191, 36, 0.65);
    }

    .tag-purple {
      background: rgba(24, 16, 45, 0.88);
      border: 1px solid rgba(192, 132, 252, 0.5);
      color: #fae8ff;
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5), inset 0 0 8px rgba(192, 132, 252, 0.15);
    }
    .tag-purple .tag-dot {
      background: #c084fc;
      box-shadow: 0 0 8px #c084fc;
    }
    .tag-purple:hover {
      border-color: #c084fc;
      box-shadow: 0 0 22px rgba(192, 132, 252, 0.65);
    }

    .tag-emerald {
      background: rgba(6, 30, 24, 0.88);
      border: 1px solid rgba(52, 211, 153, 0.5);
      color: #ecfdf5;
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5), inset 0 0 8px rgba(52, 211, 153, 0.15);
    }
    .tag-emerald .tag-dot {
      background: #34d399;
      box-shadow: 0 0 8px #34d399;
    }
    .tag-emerald:hover {
      border-color: #34d399;
      box-shadow: 0 0 22px rgba(52, 211, 153, 0.65);
    }
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
  <div id="canvas-container">
    <div class="hud-badge">✦ STANLEY AI LOGISTICS & KNOWLEDGE ECOSYSTEM ✦</div>
    <div class="hud-hint">🖱️ <span>按住滑鼠拖曳 (Click & Drag)</span> 探索 3D 智慧物流與數據大腦</div>
    <div id="tags-layer"></div>
  </div>

  <script>
    const container = document.getElementById('canvas-container');
    const tagsLayer = document.getElementById('tags-layer');
    const scene = new THREE.Scene();

    // Camera
    const camera = new THREE.PerspectiveCamera(40, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 9, 27);
    camera.lookAt(0, 0, 0);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x38bdf8, 1.2);
    dirLight1.position.set(15, 20, 15);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xa855f7, 0.8);
    dirLight2.position.set(-15, 10, -10);
    scene.add(dirLight2);

    // Root Group for Drag & Rotate
    const worldGroup = new THREE.Group();
    scene.add(worldGroup);

    // =========================================================================
    // 1. HOLOGRAPHIC TECH PLATFORM BASE (Grid & Pedestal)
    // =========================================================================
    const gridHelper = new THREE.GridHelper(24, 24, 0x0ea5e9, 0x1e293b);
    gridHelper.position.y = -3.2;
    worldGroup.add(gridHelper);

    // Glowing base ring
    const baseRingGeo = new THREE.RingGeometry(9.8, 10.1, 64);
    const baseRingMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, side: THREE.DoubleSide, transparent: true, opacity: 0.65 });
    const baseRing = new THREE.Mesh(baseRingGeo, baseRingMat);
    baseRing.rotation.x = Math.PI / 2;
    baseRing.position.y = -3.18;
    worldGroup.add(baseRing);

    // Second concentric ring
    const baseRing2Geo = new THREE.RingGeometry(5.8, 5.95, 64);
    const baseRing2Mat = new THREE.MeshBasicMaterial({ color: 0xa855f7, side: THREE.DoubleSide, transparent: true, opacity: 0.45 });
    const baseRing2 = new THREE.Mesh(baseRing2Geo, baseRing2Mat);
    baseRing2.rotation.x = Math.PI / 2;
    baseRing2.position.y = -3.18;
    worldGroup.add(baseRing2);

    // =========================================================================
    // 2. MODEL A: HIGH-TECH FORKLIFT (堆高機)
    // =========================================================================
    function createForklift() {
      const g = new THREE.Group();
      
      const yellowMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.3, metalness: 0.4 });
      const darkMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.5, metalness: 0.5 });
      const chromeMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.2, metalness: 0.8 });
      const wheelMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.8 });

      // Chassis / Body
      const body = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.0, 2.4), yellowMat);
      body.position.y = 0.6;
      g.add(body);

      // Counterweight at rear
      const rear = new THREE.Mesh(new THREE.BoxGeometry(1.56, 0.95, 0.7), darkMat);
      rear.position.set(0, 0.62, 0.9);
      g.add(rear);

      // Overhead Guard (Cage)
      const postGeo = new THREE.CylinderGeometry(0.04, 0.04, 1.4);
      const p1 = new THREE.Mesh(postGeo, darkMat); p1.position.set(-0.65, 1.6, -0.4); g.add(p1);
      const p2 = new THREE.Mesh(postGeo, darkMat); p2.position.set(0.65, 1.6, -0.4); g.add(p2);
      const p3 = new THREE.Mesh(postGeo, darkMat); p3.position.set(-0.65, 1.6, 0.7); g.add(p3);
      const p4 = new THREE.Mesh(postGeo, darkMat); p4.position.set(0.65, 1.6, 0.7); g.add(p4);

      const roof = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.05, 1.3), darkMat);
      roof.position.set(0, 2.3, 0.15);
      g.add(roof);

      // Amber Strobe Light on roof
      const strobe = new THREE.Mesh(
        new THREE.CylinderGeometry(0.08, 0.08, 0.15),
        new THREE.MeshBasicMaterial({ color: 0xfbbf24 })
      );
      strobe.position.set(0, 2.4, 0.15);
      g.add(strobe);

      // Front Mast (Vertical rails)
      const mastL = new THREE.Mesh(new THREE.BoxGeometry(0.08, 2.6, 0.1), chromeMat);
      mastL.position.set(-0.55, 1.3, -1.25);
      g.add(mastL);
      const mastR = new THREE.Mesh(new THREE.BoxGeometry(0.08, 2.6, 0.1), chromeMat);
      mastR.position.set(0.55, 1.3, -1.25);
      g.add(mastR);

      // Fork Carriage & Horizontal Blades
      const carriage = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.35, 0.08), darkMat);
      carriage.position.set(0, 0.35, -1.32);
      g.add(carriage);

      const forkGeo = new THREE.BoxGeometry(0.12, 0.04, 1.3);
      const forkL = new THREE.Mesh(forkGeo, chromeMat);
      forkL.position.set(-0.35, 0.1, -1.95);
      g.add(forkL);
      const forkR = new THREE.Mesh(forkGeo, chromeMat);
      forkR.position.set(0.35, 0.1, -1.95);
      g.add(forkR);

      // Wooden Pallet on forks
      const pallet = new THREE.Mesh(
        new THREE.BoxGeometry(1.3, 0.12, 1.1),
        new THREE.MeshStandardMaterial({ color: 0x92400e, roughness: 0.9 })
      );
      pallet.position.set(0, 0.2, -1.95);
      g.add(pallet);

      // Glowing Cargo Crate
      const crate = new THREE.Mesh(
        new THREE.BoxGeometry(1.0, 0.9, 0.9),
        new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.3, metalness: 0.6 })
      );
      crate.position.set(0, 0.72, -1.95);
      g.add(crate);

      const crateEdges = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(1.0, 0.9, 0.9)),
        new THREE.LineBasicMaterial({ color: 0x38bdf8 })
      );
      crate.add(crateEdges);

      // 4 Wheels
      const wGeo = new THREE.CylinderGeometry(0.32, 0.32, 0.28, 16);
      wGeo.rotateZ(Math.PI / 2);
      const wFL = new THREE.Mesh(wGeo, wheelMat); wFL.position.set(-0.85, 0.32, -0.7); g.add(wFL);
      const wFR = new THREE.Mesh(wGeo, wheelMat); wFR.position.set(0.85, 0.32, -0.7); g.add(wFR);
      const wRL = new THREE.Mesh(wGeo, wheelMat); wRL.position.set(-0.85, 0.32, 0.8); g.add(wRL);
      const wRR = new THREE.Mesh(wGeo, wheelMat); wRR.position.set(0.85, 0.32, 0.8); g.add(wRR);

      return g;
    }

    const forklift = createForklift();
    forklift.position.set(-5.6, -3.2, 1.8);
    forklift.rotation.y = Math.PI / 4;
    worldGroup.add(forklift);

    // =========================================================================
    // 3. MODEL B: LOGISTICS TRUCK (物流貨車)
    // =========================================================================
    function createTruck() {
      const g = new THREE.Group();

      const cabMat = new THREE.MeshStandardMaterial({ color: 0x2563eb, roughness: 0.3, metalness: 0.4 });
      const containerMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.4, metalness: 0.2 });
      const darkMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.7 });
      const glassMat = new THREE.MeshBasicMaterial({ color: 0x0284c7, transparent: true, opacity: 0.8 });
      const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });

      // Cab (Cabin)
      const cab = new THREE.Mesh(new THREE.BoxGeometry(1.7, 1.5, 1.5), cabMat);
      cab.position.set(0, 1.1, -2.1);
      g.add(cab);

      // Windshield
      const glass = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.65, 0.05), glassMat);
      glass.position.set(0, 1.35, -2.86);
      g.add(glass);

      // Side Windows
      const sideGlassGeo = new THREE.BoxGeometry(0.05, 0.55, 0.7);
      const sGL = new THREE.Mesh(sideGlassGeo, glassMat); sGL.position.set(-0.86, 1.35, -2.2); g.add(sGL);
      const sGR = new THREE.Mesh(sideGlassGeo, glassMat); sGR.position.set(0.86, 1.35, -2.2); g.add(sGR);

      // Headlights
      const headL = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 12), new THREE.MeshBasicMaterial({ color: 0xfef08a }));
      headL.position.set(-0.6, 0.7, -2.86); g.add(headL);
      const headR = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 12), new THREE.MeshBasicMaterial({ color: 0xfef08a }));
      headR.position.set(0.6, 0.7, -2.86); g.add(headR);

      // Cargo Container Body
      const container = new THREE.Mesh(new THREE.BoxGeometry(1.85, 2.0, 3.8), containerMat);
      container.position.set(0, 1.5, 0.6);
      g.add(container);

      // Blue tech stripe along container
      const stripe = new THREE.Mesh(
        new THREE.BoxGeometry(1.87, 0.25, 3.78),
        new THREE.MeshBasicMaterial({ color: 0x38bdf8 })
      );
      stripe.position.set(0, 1.5, 0.6);
      g.add(stripe);

      // Chassis Underframe
      const chassis = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.25, 5.0), darkMat);
      chassis.position.set(0, 0.45, -0.4);
      g.add(chassis);

      // 6 Wheels
      const wGeo = new THREE.CylinderGeometry(0.36, 0.36, 0.3, 16);
      wGeo.rotateZ(Math.PI / 2);

      const wFrontL = new THREE.Mesh(wGeo, wheelMat); wFrontL.position.set(-0.95, 0.36, -2.1); g.add(wFrontL);
      const wFrontR = new THREE.Mesh(wGeo, wheelMat); wFrontR.position.set(0.95, 0.36, -2.1); g.add(wFrontR);

      const wMidL = new THREE.Mesh(wGeo, wheelMat); wMidL.position.set(-0.95, 0.36, 1.1); g.add(wMidL);
      const wMidR = new THREE.Mesh(wGeo, wheelMat); wMidR.position.set(0.95, 0.36, 1.1); g.add(wMidR);

      const wRearL = new THREE.Mesh(wGeo, wheelMat); wRearL.position.set(-0.95, 0.36, 1.95); g.add(wRearL);
      const wRearR = new THREE.Mesh(wGeo, wheelMat); wRearR.position.set(0.95, 0.36, 1.95); g.add(wRearR);

      return g;
    }

    const truck = createTruck();
    truck.position.set(5.8, -3.2, 1.0);
    truck.rotation.y = -Math.PI / 4.5;
    worldGroup.add(truck);

    // =========================================================================
    // 4. MODEL C: COMPUTER AI WORKSTATION (電腦終端 / 數據中樞)
    // =========================================================================
    function createComputerStation() {
      const g = new THREE.Group();

      const deskMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.4, metalness: 0.7 });
      const silverMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.3, metalness: 0.8 });
      const screenMat = new THREE.MeshBasicMaterial({ color: 0x06b6d4 });

      // Desk Table
      const deskTop = new THREE.Mesh(new THREE.BoxGeometry(3.0, 0.12, 1.5), deskMat);
      deskTop.position.set(0, 1.4, 0);
      g.add(deskTop);

      const legL = new THREE.Mesh(new THREE.BoxGeometry(0.1, 1.4, 1.3), silverMat);
      legL.position.set(-1.35, 0.7, 0); g.add(legL);
      const legR = new THREE.Mesh(new THREE.BoxGeometry(0.1, 1.4, 1.3), silverMat);
      legR.position.set(1.35, 0.7, 0); g.add(legR);

      // Ultrawide Curved Computer Display
      const monitorStand = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.6), silverMat);
      monitorStand.position.set(0, 1.7, -0.3);
      g.add(monitorStand);

      const monitorBase = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.04, 0.45), silverMat);
      monitorBase.position.set(0, 1.46, -0.3);
      g.add(monitorBase);

      const monitorBezel = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.1, 0.08), deskMat);
      monitorBezel.position.set(0, 2.3, -0.3);
      g.add(monitorBezel);

      // Glowing Cyan Display Panel
      const displayPanel = new THREE.Mesh(new THREE.PlaneGeometry(2.26, 0.96), screenMat);
      displayPanel.position.set(0, 2.3, -0.25);
      g.add(displayPanel);

      // Glowing Code/Data Wave on Screen
      const codeLinesGeo = new THREE.BufferGeometry();
      const codePoints = [];
      for (let i = 0; i < 60; i++) {
        codePoints.push(new THREE.Vector3(-1.0 + (i % 20) * 0.1, 2.6 - Math.floor(i / 20) * 0.25, -0.24));
      }
      codeLinesGeo.setFromPoints(codePoints);
      const codeParticles = new THREE.Points(codeLinesGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.035 }));
      g.add(codeParticles);

      // Slim Keyboard on desk
      const keyboard = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.03, 0.35), silverMat);
      keyboard.position.set(0, 1.48, 0.2);
      g.add(keyboard);

      // Mouse
      const mouse = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.03, 0.16), silverMat);
      mouse.position.set(0.65, 1.48, 0.2);
      g.add(mouse);

      // Server Tower beside desk
      const serverTower = new THREE.Mesh(
        new THREE.BoxGeometry(0.6, 1.6, 1.2),
        new THREE.MeshStandardMaterial({ color: 0x020617, roughness: 0.3, metalness: 0.8 })
      );
      serverTower.position.set(-1.95, 0.8, 0);
      g.add(serverTower);

      // Blinking LEDs on Server Tower
      const ledGeo = new THREE.SphereGeometry(0.04, 8, 8);
      const led1 = new THREE.Mesh(ledGeo, new THREE.MeshBasicMaterial({ color: 0x22c55e }));
      led1.position.set(-1.64, 1.35, 0.61); g.add(led1);
      const led2 = new THREE.Mesh(ledGeo, new THREE.MeshBasicMaterial({ color: 0x38bdf8 }));
      led2.position.set(-1.75, 1.35, 0.61); g.add(led2);
      const led3 = new THREE.Mesh(ledGeo, new THREE.MeshBasicMaterial({ color: 0xa855f7 }));
      led3.position.set(-1.86, 1.35, 0.61); g.add(led3);

      return g;
    }

    const computerStation = createComputerStation();
    computerStation.position.set(0, -3.2, -4.5);
    computerStation.rotation.y = 0;
    worldGroup.add(computerStation);

    // =========================================================================
    // 5. CENTRAL FLOATING NEURAL KNOWLEDGE CORE (Hovering above platform)
    // =========================================================================
    const coreGroup = new THREE.Group();
    coreGroup.position.set(0, 3.2, 0);
    worldGroup.add(coreGroup);

    // Inner Glowing Core
    const innerGeo = new THREE.SphereGeometry(1.6, 32, 32);
    const innerMat = new THREE.MeshBasicMaterial({ color: 0x0ea5e9, wireframe: true, transparent: true, opacity: 0.4 });
    const innerCore = new THREE.Mesh(innerGeo, innerMat);
    coreGroup.add(innerCore);

    // Geodesic Data Shell
    const icoGeo = new THREE.IcosahedronGeometry(2.8, 1);
    const icoMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true, transparent: true, opacity: 0.7 });
    const icoMesh = new THREE.Mesh(icoGeo, icoMat);
    coreGroup.add(icoMesh);

    // Vertices on shell
    const icoPoints = new THREE.Points(icoGeo, new THREE.PointsMaterial({ color: 0xa855f7, size: 0.25 }));
    coreGroup.add(icoPoints);

    // Rotating Orbital Rings
    const ring1 = new THREE.Mesh(
      new THREE.TorusGeometry(4.2, 0.035, 16, 100),
      new THREE.MeshBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.7 })
    );
    ring1.rotation.x = Math.PI / 3;
    coreGroup.add(ring1);

    const ring2 = new THREE.Mesh(
      new THREE.TorusGeometry(5.0, 0.035, 16, 100),
      new THREE.MeshBasicMaterial({ color: 0xa855f7, transparent: true, opacity: 0.6 })
    );
    ring2.rotation.x = -Math.PI / 4;
    coreGroup.add(ring2);

    // Floating Data Particle Cloud
    const particleCount = 500;
    const particlePositions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      const rad = 4.0 + Math.random() * 8.0;
      const th = Math.random() * Math.PI * 2;
      const ph = Math.acos((Math.random() * 2) - 1);
      particlePositions[i] = rad * Math.sin(ph) * Math.cos(th);
      particlePositions[i + 1] = rad * Math.sin(ph) * Math.sin(th);
      particlePositions[i + 2] = rad * Math.cos(ph);
    }
    const particleGeo = new THREE.BufferGeometry();
    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
    const particles = new THREE.Points(
      particleGeo,
      new THREE.PointsMaterial({ color: 0x67e8f9, size: 0.1, transparent: true, opacity: 0.6 })
    );
    coreGroup.add(particles);

    // =========================================================================
    // 6. 3D-ANCHORED FLOATING 2D TAGS
    // =========================================================================
    const tagsConfig = [
      { text: "🚜 幸冠智能堆高機 (Forklift)", color: "tag-amber", target: forklift, offset: [0, 3.2, 0] },
      { text: "🚚 物流配送貨車 (Truck)", color: "tag-cyan", target: truck, offset: [0, 3.8, 0] },
      { text: "💻 Stanley AI 智慧大腦終端", color: "tag-cyan", target: computerStation, offset: [0, 4.0, 0] },
      { text: "📦 倉庫驗收待清洗返回", color: "tag-emerald", target: forklift, offset: [0, 1.8, -1.9] },
      { text: "🚗 2026 Toyota Yaris D-CVT", color: "tag-purple", target: coreGroup, offset: [4.6, 2.2, 0.5] },
      { text: "🏆 Toyota Altis 銷冠", color: "tag-cyan", target: coreGroup, offset: [-4.8, 1.8, -1.0] },
      { text: "📋 新北拍賣租賃退回/報廢機制", color: "tag-emerald", target: coreGroup, offset: [0, 4.8, 0] }
    ];

    const tagObjects = [];

    tagsConfig.forEach(cfg => {
      const anchor = new THREE.Object3D();
      anchor.position.set(cfg.offset[0], cfg.offset[1], cfg.offset[2]);
      cfg.target.add(anchor);

      const el = document.createElement('div');
      el.className = `floating-tag ${cfg.color}`;
      el.innerHTML = `<span class="tag-dot"></span><span>${cfg.text}</span>`;
      tagsLayer.appendChild(el);

      tagObjects.push({ anchor, element: el });
    });

    // =========================================================================
    // 7. MOUSE & TOUCH DRAG ROTATION
    // =========================================================================
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let targetRotationY = 0.2;
    let targetRotationX = 0.15;
    let velocityX = 0;
    let velocityY = 0;

    container.addEventListener('mousedown', (e) => {
      isDragging = true;
      previousMousePosition = { x: e.clientX, y: e.clientY };
      velocityX = 0;
      velocityY = 0;
    });

    window.addEventListener('mouseup', () => {
      isDragging = false;
    });

    window.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const deltaX = e.clientX - previousMousePosition.x;
      const deltaY = e.clientY - previousMousePosition.y;

      targetRotationY += deltaX * 0.005;
      targetRotationX += deltaY * 0.005;

      // Restrict pitch so user doesn't flip below ground
      targetRotationX = Math.max(-0.25, Math.min(0.85, targetRotationX));

      velocityX = deltaX * 0.0025;
      velocityY = deltaY * 0.0025;

      previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    // Touch Support
    container.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        isDragging = true;
        previousMousePosition = { x: e.touches[0].clientX, y: e.touches[0].clientY };
        velocityX = 0;
        velocityY = 0;
      }
    }, { passive: true });

    window.addEventListener('touchend', () => {
      isDragging = false;
    });

    window.addEventListener('touchmove', (e) => {
      if (!isDragging || e.touches.length !== 1) return;
      const deltaX = e.touches[0].clientX - previousMousePosition.x;
      const deltaY = e.touches[0].clientY - previousMousePosition.y;

      targetRotationY += deltaX * 0.005;
      targetRotationX += deltaY * 0.005;
      targetRotationX = Math.max(-0.25, Math.min(0.85, targetRotationX));

      previousMousePosition = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    }, { passive: true });

    // Resize Handler
    window.addEventListener('resize', () => {
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    });

    const tempVec = new THREE.Vector3();
    let clock = new THREE.Clock();

    // =========================================================================
    // 8. ANIMATION LOOP
    // =========================================================================
    function animate() {
      requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Idle Rotation & Momentum
      if (!isDragging) {
        targetRotationY += 0.002 + velocityX;
        targetRotationX += velocityY;
        velocityX *= 0.93;
        velocityY *= 0.93;
      }

      // Smooth damping interpolation for the entire world
      worldGroup.rotation.y += (targetRotationY - worldGroup.rotation.y) * 0.07;
      worldGroup.rotation.x += (targetRotationX - worldGroup.rotation.x) * 0.07;

      // Internal Animations
      coreGroup.rotation.y -= 0.006;
      icoMesh.rotation.y += 0.004;
      ring1.rotation.z += 0.009;
      ring2.rotation.z -= 0.007;
      particles.rotation.y += 0.0006;

      // Floating core hovering bobbing motion
      coreGroup.position.y = 3.2 + Math.sin(elapsedTime * 1.5) * 0.25;

      // Pulse inner core
      const pulse = 1 + Math.sin(elapsedTime * 2.5) * 0.06;
      innerCore.scale.set(pulse, pulse, pulse);

      // Base concentric rings subtle rotation
      baseRing.rotation.z += 0.002;
      baseRing2.rotation.z -= 0.003;

      // Project 3D tags to 2D screen
      worldGroup.updateMatrixWorld(true);
      tagObjects.forEach(item => {
        item.anchor.getWorldPosition(tempVec);
        tempVec.project(camera);

        if (tempVec.z > 1) {
          item.element.style.display = 'none';
        } else {
          item.element.style.display = 'flex';
          const x = (tempVec.x * 0.5 + 0.5) * container.clientWidth;
          const y = (-(tempVec.y * 0.5) + 0.5) * container.clientHeight;

          const depth01 = (tempVec.z + 1) * 0.5;
          const scale = THREE.MathUtils.lerp(1.04, 0.72, depth01);
          const opacity = THREE.MathUtils.lerp(1.0, 0.35, depth01);
          const zIndex = Math.round((1 - depth01) * 100);

          item.element.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px) scale(${scale})`;
          item.element.style.opacity = opacity;
          item.element.style.zIndex = zIndex;
        }
      });

      renderer.render(scene, camera);
    }

    animate();
  </script>
</body>
</html>
"""
