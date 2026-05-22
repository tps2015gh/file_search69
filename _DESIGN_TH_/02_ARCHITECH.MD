# สถาปัตยกรรมระบบ (System Architecture)

## สถาปัตยกรรมระดับสูง (High-Level Architecture)
แอปพลิเคชันปฏิบัติตามสถาปัตยกรรมแบบโมดูลที่แยกส่วน (decoupled) ซึ่งประกอบด้วยส่วนจัดการดัชนี/เวกเตอร์ (indexing/vector backend) และส่วนต่อประสานกราฟิก (graphical frontend) ที่สมบูรณ์

```mermaid
graph TD
    A[PySide6 GUI] -->|ค้นหา / กรอง / มุมมอง| B[Query Engine]
    A -->|เพิ่ม/ลบ ไดเรกทอรี| C[Crawler Controller]
    C -->|งานสแกน| D[Background Crawler Thread]
    D -->|ไฟล์/ไดเรกทอรี| E[Vector Extractor]
    E -->|เมทาดาตา & เวกเตอร์| F[SQLite Database]
    F -->|สืบค้นข้อมูล| B
    B -->|โหนดกราฟ & เส้นเชื่อม| G[Graph Visualizer]
    H[FS Watcher] -->|เหตุการณ์การเปลี่ยนแปลง| C
    I[Responsiveness Monitor] -->|ควบคุมการชะลอ (Throttle Control)| D
    D -->|เหตุการณ์ในไปป์ไลน์แบบเรียลไทม์| K[GUI Kanban Widget]
    L[Resource Monitor] -->|สถิติระบบ| A
    D -->|บันทึกเหตุการณ์สำคัญ (Log Milestones)| M[Import Logger]
```

### ส่วนประกอบ (Components)
1. **เอนจินรวบรวมข้อมูลแบบชะลอการทำงาน (Throttled Crawler Engine)**
   - ท่องไปยังไดเรกทอรีของผู้ใช้โดยใช้ API ระบบไฟล์มาตรฐานในเธรดเบื้องหลัง
   - การปรับใช้แบบชะลอการทำงาน: นำเสนอ micro-sleeps เพื่อป้องกันการใช้งาน CPU มากเกินไป
   - วิเคราะห์ไฟล์ `.ignore` เพื่อตัดการท่องไปยังไดเรกทอรีแต่เนิ่นๆ

2. **ไปป์ไลน์การแยกเวกเตอร์ (Vector Extraction Pipeline)**
   - แปลงข้อมูลเมทาดาตาของไฟล์ โครงสร้างเส้นทาง และการตรวจสอบเนื้อหาให้เป็นเวกเตอร์ 42 มิติแบบมาตรฐาน

3. **ระบบย่อยการจัดเก็บ (Storage Subsystem)**
   - ฐานข้อมูลเชิงสัมพันธ์ SQLite สำหรับจัดเก็บเส้นทางของไฟล์ คุณสมบัติของเมทาดาตา และข้อมูลเวกเตอร์แบบ blob ที่แปลงให้เป็นแบบอันดับ

4. **เอนจินค้นหาความคล้ายคลึงกัน (Similarity Search Engine)**
   - ใช้ NumPy/SciPy สำหรับการคำนวณทางคณิตศาสตร์ระยะทางของเวกเตอร์

5. **ส่วนต่อประสานกราฟิกกับผู้ใช้ (GUI) & การทำงานพร้อมกัน (Concurrency)**
   - **กรอบการทำงาน (Framework)**: PySide6.
   - **ส่วนประกอบกราฟ (Graph Component)**: แคนวาส HTML5 ที่ฝังอยู่ผ่าน `QWebEngineView` โดยใช้ `vis.js` หรือ `d3.js` สำหรับการเรนเดอร์แบบ force-directed.
   - **แดชบอร์ดความคืบหน้า & ตัวชี้วัด (Progress & Metrics Dashboard)**: รวมถึง **Run-time Kanban Process Board** ที่กำหนดเองและวิดเจ็ตแถบสถานะสำหรับ **โหนด (Nodes), หน่วยความจำ (Memory), และ ดิสก์ (Disk)**.

---

## ส่วนประกอบกราฟ HTML5 & การปรับแรง (HTML5 Graph Component & Force Adjustment - vis.js/D3.js Template)

เพื่อป้องกันการซ้อนทับกันของโหนดและปรับใช้คุณสมบัติ "สั่น (Shake)" ใน HTML ที่ฝังไว้ ให้ใช้โครงสร้างลอจิก Javascript นี้ตรงๆ ภายในรหัสแคนวาส `QWebEngineView`:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body, html, #graph { width: 100%; height: 100%; margin: 0; background-color: #11111b; overflow: hidden; }
    </style>
    <!-- นำเข้าไลบรารี vis.js จากโฟลเดอร์ asset ในพื้นที่ -->
    <script src="vis-network.min.js"></script>
</head>
<body>
    <div id="graph"></div>
    <script>
        let nodes = new vis.DataSet([]);
        let edges = new vis.DataSet([]);
        let container = document.getElementById('graph');
        let data = { nodes: nodes, edges: edges };
        
        // การกำหนดค่าฟิสิกส์อนุญาตให้มีแรงผลักสูงเพื่อป้องกันการซ้อนทับกัน
        let options = {
            interaction: {
                dragView: true,  // เปิดใช้งานการเลื่อนหน้าต่างด้วยเมาส์
                hover: true
            },
            physics: {
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {
                    gravitationalConstant: -50,
                    centralGravity: 0.01,
                    springLength: 100, // ระยะห่างที่ปรับได้
                    springConstant: 0.08,
                    damping: 0.4,
                    avoidOverlap: 1.0  // นโยบาย: บังคับหลีกเลี่ยงการซ้อนทับ
                }
            }
        };
        let network = new vis.Network(container, data, options);

        // การแช่แข็งฟิสิกส์แบบไดนามิกสำหรับโหนดความหนาแน่นสูง
        network.on("stabilizationIterationsDone", function () {
            if (nodes.length > 1500) {
                network.setOptions({ physics: false });
            }
        });

        // ระดับรายละเอียด (LoD) Zoom Handler
        network.on("zoom", function (params) {
            let scale = network.getScale();
            let allNodes = nodes.get();
            let updates = [];
            
            allNodes.forEach(node => {
                let updated = false;
                if (scale < 0.4) {
                    // ซูมออกไกล: ซ่อนฉลาก, ย่อขนาดโหนด
                    if (node.label !== "") {
                        node.oldLabel = node.label || node.oldLabel;
                        node.label = ""; 
                        node.size = 4;   
                        updated = true;
                    }
                } else {
                    // ซูมเข้า: กู้คืนฉลากเดิม
                    if (node.label === "" && node.oldLabel) {
                        node.label = node.oldLabel;
                        node.size = undefined; 
                        updated = true;
                    }
                }
                if (updated) {
                    updates.push(node);
                }
            });
            if (updates.length > 0) {
                nodes.update(updates);
            }
        });

        // แป้นพิมพ์เลื่อนหน้าจอ (WASD & แป้นลูกศร) พร้อมชดเชยการซูม
        window.addEventListener('keydown', function (event) {
            let baseStep = 40; // พิกเซลต่อหนึ่งขั้นตอนการกดแป้นพิมพ์
            let scale = network.getScale();
            let stepScaled = baseStep / scale; // ปรับความเร็วตามระดับความลึกในการซูม
            
            let pos = network.getViewPosition();
            let key = event.key.toLowerCase();
            
            if (key === 'w' || key === 'arrowup') {
                network.moveTo({ position: { x: pos.x, y: pos.y - stepScaled } });
                event.preventDefault(); // ป้องกันไม่ให้หน้าเลื่อนโดยเริ่มต้น
            } else if (key === 's' || key === 'arrowdown') {
                network.moveTo({ position: { x: pos.x, y: pos.y + stepScaled } });
                event.preventDefault();
            } else if (key === 'a' || key === 'arrowleft') {
                network.moveTo({ position: { x: pos.x - stepScaled, y: pos.y } });
                event.preventDefault();
            } else if (key === 'd' || key === 'arrowright') {
                network.moveTo({ position: { x: pos.x + stepScaled, y: pos.y } });
                event.preventDefault();
            }
        });

        // GUI Communication API: Python QWebEngineView เรียกใช้งานฟังก์ชันเหล่านี้

        // 1. แยกมากขึ้น (ตัวคูณระยะห่างทั่วโลก)
        function setSeparateMore(multiplier) {
            // ค่าพื้นฐาน: gravitationalConstant = -50, springLength = 100
            let repulsion = -50 * multiplier;
            let springLength = 100 * multiplier;
            network.setOptions({
                physics: {
                    forceAtlas2Based: {
                        gravitationalConstant: repulsion,
                        springLength: springLength
                    }
                }
            });
        }

        // 2. แยกใกล้ (ตัวคูณป้องกันการทับซ้อนระยะใกล้เฉพาะที่)
        function setSeparateNear(multiplier) {
            // ปรับระยะขอบของฉลากแบบไดนามิกเพื่อเพิ่มขอบเขตบริเวณความใกล้เคียง
            let allNodes = nodes.get();
            allNodes.forEach(node => {
                node.margin = {
                    top: 10 * multiplier,
                    bottom: 10 * multiplier,
                    left: 15 * multiplier,
                    right: 15 * multiplier
                };
            });
            nodes.update(allNodes);
            
            // ปรับแต่งการตั้งค่าหลีกเลี่ยงการทับซ้อนแบบไดนามิก
            let avoidVal = multiplier > 1.2 ? 1.0 : 0.5;
            network.setOptions({
                physics: {
                    forceAtlas2Based: {
                        avoidOverlap: avoidVal
                    }
                }
            });
        }

        // 3. สั่นทุกโหนด (Global Jitter)
        function shakeAllNodes() {
            let allNodes = nodes.get();
            allNodes.forEach(node => {
                // ปรับใช้ค่าเบี่ยงเบนสุ่ม (-100px ถึง 100px)
                node.x = (node.x || 0) + (Math.random() - 0.5) * 200;
                node.y = (node.y || 0) + (Math.random() - 0.5) * 200;
            });
            nodes.update(allNodes);
            network.stabilize(50); // จัดการพื้นที่ทับซ้อน
        }

        // 4. สั่นคลัสเตอร์ที่เลือก (Neighborhood Jitter)
        function shakeCluster(selectedNodeId) {
            if (!selectedNodeId) return;
            // ดึงข้อมูลเพื่อนบ้านเชิงโทโพโลยีไม่เกิน 2 ครั้ง (hops)
            let firstHop = network.getConnectedNodes(selectedNodeId);
            let neighbors = new Set([selectedNodeId, ...firstHop]);
            firstHop.forEach(nId => {
                network.getConnectedNodes(nId).forEach(nnId => neighbors.add(nnId));
            });

            let updates = [];
            neighbors.forEach(id => {
                let node = nodes.get(id);
                if (node) {
                    node.x = (node.x || 0) + (Math.random() - 0.5) * 100;
                    node.y = (node.y || 0) + (Math.random() - 0.5) * 100;
                    updates.push(node);
                }
            });
            nodes.update(updates);
            network.stabilize(30);
        }

        // 5. สั่นโหนดที่ทับซ้อนกัน (Proximity Jitter)
        function shakeOverlappingNodes() {
            let positions = network.getPositions();
            let allNodes = nodes.get();
            let updates = [];
            let overlapLimit = 120; // ค่าขีดจำกัดพิกเซลสำหรับการตรวจสอบความใกล้เคียง

            for (let i = 0; i < allNodes.length; i++) {
                let nodeA = allNodes[i];
                let posA = positions[nodeA.id];
                if (!posA) continue;

                for (let j = i + 1; j < allNodes.length; j++) {
                    let nodeB = allNodes[j];
                    let posB = positions[nodeB.id];
                    if (!posB) continue;

                    let dx = posA.x - posB.x;
                    let dy = posA.y - posB.y;
                    let distance = Math.sqrt(dx * dx + dy * dy);

                    // หากโหนดอยู่ใกล้กันเกินไป (อ่านไม่ได้), ปรับใช้ค่าสั่นสะเทือน (jitter)
                    if (distance < overlapLimit) {
                        nodeA.x = posA.x + (Math.random() - 0.5) * 60;
                        nodeA.y = posA.y + (Math.random() - 0.5) * 60;
                        nodeB.x = posB.x + (Math.random() - 0.5) * 60;
                        nodeB.y = posB.y + (Math.random() - 0.5) * 60;

                        if (!updates.some(n => n.id === nodeA.id)) updates.push(nodeA);
                        if (!updates.some(n => n.id === nodeB.id)) updates.push(nodeB);
                    }
                }
            }
            if (updates.length > 0) {
                nodes.update(updates);
                network.stabilize(40);
            }
        }
    </script>
</body>
</html>
```

---

## ระบบบันทึกนำเข้าและตรวจจับความผิดปกติ (Import Logger & Crash Detector - Concrete Code Skeleton)
- เขียนรายละเอียดการดำเนินการความคืบหน้าไปที่ `import_progress.log`
- ล้างไฟล์บันทึกเมื่อเริ่มต้นโปรแกรม, เขียนส่วนหัวที่มีวันที่และเวลาเมื่อมีการทำงานนำเข้าใหม่เสมอ

---

## ส่วนประกอบดูแลทรัพยากรระบบ (System Resource Monitor Component - Concrete Code Skeleton)
- ตรวจสอบ RAM (MB) และเปอร์เซ็นต์การใช้งาน Disk เป็นระยะ โดยส่งข้อมูลสถิติไปยัง PySide6
