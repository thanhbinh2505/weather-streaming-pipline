import json
import base64
import urllib.request
import os

def fetch_base64_logo(url):
    if not url: return None
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = response.read()
            b64 = base64.b64encode(data).decode('utf-8')
            mime = "image/svg+xml" if url.endswith(".svg") else "image/png"
            return f"data:{mime};base64,{b64}"
    except Exception as e:
        print(f"Warning: Failed to fetch {url}: {e}")
        return None

def main():
    # Cấu trúc Nodes: Chia thành 3 Panel (Phân khu) nền hachure và các Node chức năng
    nodes_config = [
        # --- BACKGROUND PANELS (3 Phân khu chức năng) ---
        {"id": "bg1", "x": 40, "y": 40, "w": 580, "h": 460, "text": "STAGE 1: DATA ACQUISITION", "type": "panel", "color": "#1864ab", "bg": "#e7f5ff"},
        {"id": "bg2", "x": 640, "y": 40, "w": 280, "h": 460, "text": "STAGE 2: EVENT BUS", "type": "panel", "color": "#e67700", "bg": "#fff9db"},
        {"id": "bg3", "x": 940, "y": 40, "w": 880, "h": 460, "text": "STAGE 3: DOWNSTREAM CONSUMERS", "type": "panel", "color": "#5f3dc4", "bg": "#f3f0ff"},

        # --- FUNCTIONAL NODES ---
        {"id": "n1", "x": 80, "y": 230, "w": 220, "h": 80, "text": "Open-Meteo", "logo": "https://cdn-icons-png.flaticon.com/512/4005/4005817.png", "color": "#1971c2", "bg": "#d0ebff"},
        {"id": "n2", "x": 370, "y": 230, "w": 220, "h": 80, "text": "Python Producer", "logo": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg", "color": "#2b8a3e", "bg": "#d3f9d8"},
        
        {"id": "n3", "x": 670, "y": 230, "w": 220, "h": 80, "text": "Kafka Cluster", "logo": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/apachekafka/apachekafka-original.svg", "color": "#d9480f", "bg": "#ffe8cc"},
        
        {"id": "n4", "x": 980, "y": 120, "w": 230, "h": 80, "text": "Spark Streaming", "logo": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/apachespark/apachespark-original.svg", "color": "#6741d9", "bg": "#e5dbff"},
        {"id": "n5", "x": 980, "y": 340, "w": 230, "h": 80, "text": "Kafka Exporter", "logo": "https://raw.githubusercontent.com/prometheus/prometheus/main/docs/prometheus-logo.png", "color": "#c2255c", "bg": "#ffdeeb"},
        {"id": "n6", "x": 1280, "y": 340, "w": 230, "h": 80, "text": "Prometheus", "logo": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/prometheus/prometheus-original.svg", "color": "#d9480f", "bg": "#ffe8cc"},
        {"id": "n7", "x": 1560, "y": 340, "w": 220, "h": 80, "text": "Grafana", "logo": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/grafana/grafana-original.svg", "color": "#1864ab", "bg": "#d0ebff"},
    ]

    elements = []
    files = {}

    for node in nodes_config:
        nid, x, y, w, h = node["id"], node["x"], node["y"], node["w"], node["h"]
        is_panel = node.get("type") == "panel"

        # Vẽ hình chữ nhật
        elements.append({
            "type": "rectangle", "id": nid, "x": x, "y": y, "width": w, "height": h,
            "strokeColor": node["color"], "backgroundColor": node["bg"], 
            "fillStyle": "hachure" if is_panel else "solid", # Nền gạch chéo cho Panel tạo sự khác biệt
            "strokeWidth": 2, "strokeStyle": "solid",
            "roughness": 1 if is_panel else 0, 
            "roundness": {"type": 3}
        })

        if is_panel:
            # Tiêu đề của Panel
            elements.append({
                "type": "text", "x": x + 20, "y": y + 20, "text": node["text"], 
                "fontSize": 20, "fontFamily": 1, "strokeColor": node["color"], "opacity": 80
            })
        else:
            # Xử lý Logo và Text cho Node chức năng
            logo_url = node.get("logo")
            text_x_start = x + 25
            if logo_url:
                data_url = fetch_base64_logo(logo_url)
                if data_url:
                    fid = f"logo_{nid}"
                    files[fid] = {"id": fid, "dataURL": data_url, "mimeType": "image/png", "created": 1}
                    elements.append({
                        "type": "image", "x": x + 15, "y": y + 20, "width": 40, "height": 40,
                        "fileId": fid, "status": "saved"
                    })
                    text_x_start = x + 70

            elements.append({
                "type": "text", "x": text_x_start, "y": y + 28, "width": w - 80, "height": 30,
                "text": node["text"], "fontSize": 18, "fontFamily": 1, "textAlign": "left", 
                "strokeColor": "#000000"
            })

    # Hàm vẽ mũi tên động có nhãn
    def add_arrow(sx, sy, ex, ey, sid, eid, label=None):
        elements.append({
            "type": "arrow", "x": sx, "y": sy, "points": [[0,0], [ex-sx, ey-sy]],
            "strokeColor": "#343a40", "strokeWidth": 2, "endArrowhead": "arrow",
            "startBinding": {"elementId": sid}, "endBinding": {"elementId": eid}
        })
        if label:
            elements.append({
                "type": "text", "x": sx + (ex-sx)/2 - 30, "y": sy + (ey-sy)/2 - 25, 
                "text": label, "fontSize": 14, "fontFamily": 1, "strokeColor": "#495057",
                "backgroundColor": "#ffffff"
            })

    # Định tuyến mũi tên (Routing)
    add_arrow(300, 270, 370, 270, "n1", "n2", "HTTP GET")
    add_arrow(590, 270, 670, 270, "n2", "n3", "Produce")
    
    # Kafka chẻ nhánh ra 2 hướng (Lên Spark, Xuống Exporter)
    add_arrow(890, 250, 980, 160, "n3", "n4", "Consume")
    add_arrow(890, 290, 980, 380, "n3", "n5", "Metrics")
    
    # Luồng Monitoring
    add_arrow(1210, 380, 1280, 380, "n5", "n6", "Scrape")
    add_arrow(1510, 380, 1560, 380, "n6", "n7", "Query")

    # Xuất file Excalidraw
    doc = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com", "elements": elements, "files": files}
    os.makedirs("excalidraw", exist_ok=True)
    file_path = "excalidraw/weather_pipeline_horizontal_zones.excalidraw"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    print(f"Success: Diagram generated at {file_path}")

if __name__ == "__main__": main()