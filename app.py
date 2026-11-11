"""Signal Eye simplified portfolio demo. Start with: python app.py"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

HTML = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Signal Eye | 표지판 후보 감지 데모</title>
<style>
:root{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:#1b3330;background:#f8f9f5}
*{box-sizing:border-box}body{margin:0}header{padding:54px 24px;background:linear-gradient(110deg,#073e36,#147b67);color:white}
.wrap{max-width:1000px;margin:auto}h1{font-size:clamp(40px,6vw,65px);margin:8px 0 12px}
header p{max-width:640px;line-height:1.8;color:#d2f1df}.eyebrow{font-size:12px;letter-spacing:.2em;font-weight:800;color:#8ddbc0}
main{max-width:1000px;margin:25px auto;padding:0 20px 50px}
.notice{padding:16px 20px;border-radius:14px;background:#fff6da;color:#5e4d22;border:1px solid #eed494;line-height:1.7;font-size:14px}
.card{margin-top:20px;padding:24px;border-radius:19px;background:white;border:1px solid #dce8dd;box-shadow:0 5px 22px #1a55400c}
h2{margin:0 0 8px}.muted{color:#637872;font-size:14px;line-height:1.7}
.inputRow{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:20px 0}
input[type=file]{max-width:100%;background:#edf7f1;padding:12px;border-radius:12px}
button{border:0;border-radius:10px;background:#0f6c58;color:white;padding:12px 18px;font-weight:800;cursor:pointer}
button:disabled{opacity:.55;cursor:default}
#image{width:100%;height:auto;display:block;border-radius:12px;border:1px solid #e0ece5;background:#f4f7f5}
#image[hidden]{display:none}.items{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-top:14px}
.item{border:1px solid #dce8dd;border-radius:12px;padding:15px;background:#fbfdfa}.item strong{color:#145847}
.status{font-weight:650;margin:16px 0;color:#245649}footer{padding:30px;text-align:center;color:#7a8981;font-size:13px}
code{background:#f0f6f2;border-radius:5px;padding:2px 5px}
</style>
</head>
<body>
<header><div class="wrap"><div class="eyebrow">MICROSOFT AI SCHOOL · PORTFOLIO RECONSTRUCTION</div>
<h1>Signal Eye</h1><p>이미지 속 교통표지판의 색상과 형태를 기반으로 <strong>후보 영역</strong>을 표시하고, 주의 안내를 음성으로 재생하는 데모입니다.</p>
</div></header>
<main>
<div class="notice"><strong>주의:</strong> 이 페이지는 학습용 예제입니다. 원본 Azure AI 모델이 아닌 OpenCV 규칙 기반 후보 검출이며, 표지판 종류를 정확하게 판별하지 않습니다. <strong>운전 중 사용하거나 안전 판단에 이용하지 마세요.</strong></div>
<section class="card">
<h2>교통표지판 후보 찾기</h2>
<p class="muted">빨간색·파란색 표지판이 비교적 선명하게 보이는 JPG, PNG 또는 WebP 이미지를 선택하세요. 파일은 데모 서버의 메모리에서 처리하며 저장하지 않습니다.</p>
<div class="inputRow">
<input type="file" id="file" accept="image/jpeg,image/png,image/webp">
<button id="analyze">이미지 분석하기</button>
<button id="speak" disabled>안내 음성 듣기</button>
</div>
<div id="status" class="status" role="status">이미지를 선택하세요.</div>
<canvas id="image" hidden></canvas>
<div id="results" class="items"></div>
</section>
<section class="card">
<h2>분석 흐름</h2>
<p class="muted">이미지 → OpenCV HSV 색상 마스크 → 외곽선/형태 분석 → 후보 영역 표시 → 브라우저 음성 합성</p>
<p class="muted">정밀한 분류가 필요한 원본 프로젝트에서는 Azure Computer Vision과 Custom Vision, OpenAI, Azure Speech를 연계했습니다. 이 데모에는 해당 유료 서비스가 필요하지 않습니다.</p>
</section>
</main>
<footer>Signal Eye · portfolio reconstruction · not for road use</footer>
<script>
const file=document.querySelector("#file");
const status=document.querySelector("#status");
const canvas=document.querySelector("#image");
const result=document.querySelector("#results");
const analyze=document.querySelector("#analyze");
const speak=document.querySelector("#speak");
let announcements=[];
const mk=(tag,cls,content)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(content!==undefined)n.textContent=content;return n;};

analyze.addEventListener("click",async()=>{
 const selected=file.files[0];
 if(!selected){status.textContent="이미지를 먼저 선택하세요.";return;}
 if(selected.size>5*1024*1024){status.textContent="5MB 이하 이미지를 선택하세요.";return;}
 analyze.disabled=true;speak.disabled=true;result.replaceChildren();announcements=[];
 status.textContent="표지판 후보를 분석하고 있습니다.";
 try{
  const response=await fetch("/api/analyze",{method:"POST",headers:{"Content-Type":"application/octet-stream"},body:selected});
  const data=await response.json();
  if(!response.ok)throw new Error(data.error||"요청에 실패했습니다.");
  const url=URL.createObjectURL(selected);
  const image=new Image();
  try{image.src=url;await image.decode();}finally{URL.revokeObjectURL(url);}
  const ratio=Math.min(1,1200/image.naturalWidth);
  canvas.width=Math.round(image.naturalWidth*ratio);
  canvas.height=Math.round(image.naturalHeight*ratio);
  const ctx=canvas.getContext("2d");
  ctx.drawImage(image,0,0,canvas.width,canvas.height);
  canvas.hidden=false;
  const sx=canvas.width/data.width,sy=canvas.height/data.height;
  data.detections.forEach((d,index)=>{
   const [x,y,w,h]=d.bbox;
   const px=x*sx,py=y*sy,pw=w*sx,ph=h*sy;
   const color=d.color==="red"?"#ff4e51":"#1d8fff";
   ctx.strokeStyle=color;ctx.lineWidth=4;ctx.strokeRect(px,py,pw,ph);
   ctx.fillStyle=color;ctx.fillRect(px,Math.max(0,py-27),Math.min(90,pw),25);
   ctx.fillStyle="#fff";ctx.font="bold 15px sans-serif";ctx.fillText("후보 "+(index+1),px+5,Math.max(19,py-8));
   const card=mk("article","item");card.append(mk("strong","",d.label),mk("p","muted",d.advice));result.append(card);
   announcements.push(d.advice);
  });
  status.textContent=data.detections.length?"후보 영역 "+data.detections.length+"개 감지":"뚜렷한 후보 영역을 찾지 못했습니다.";
  speak.disabled=announcements.length===0||!("speechSynthesis" in window);
 }catch(error){canvas.hidden=true;status.textContent="오류: "+error.message;}
 finally{analyze.disabled=false;}
});
speak.addEventListener("click",()=>{
 if(!announcements.length||!("speechSynthesis" in window))return;
 window.speechSynthesis.cancel();
 const utterance=new SpeechSynthesisUtterance(announcements.join(" "));
 utterance.lang="ko-KR";utterance.rate=.95;
 window.speechSynthesis.speak(utterance);
});
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _respond(self, status: int, body: bytes, mime: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            self._respond(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
        elif path == "/health":
            self._respond(200, b'{"status":"ok"}', "application/json")
        else:
            self._respond(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        if urlsplit(self.path).path != "/api/analyze":
            self._respond(404, b'{"error":"Not found"}', "application/json")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if not 0 < length <= 5 * 1024 * 1024:
            self._respond(
                413, json.dumps({"error": "5MB 이하 이미지를 업로드하세요."}, ensure_ascii=False).encode("utf-8"),
                "application/json; charset=utf-8",
            )
            return

        try:
            from detector import analyze
            output = analyze(self.rfile.read(length))
            status = 200
        except ImportError:
            output = {"error": "라이브러리가 없습니다. pip install -r requirements.txt 를 실행하세요."}
            status = 503
        except ValueError as error:
            output = {"error": str(error)}
            status = 400
        self._respond(status, json.dumps(output, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8001"))
    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as server:
        print(f"Signal Eye demo: http://127.0.0.1:{port}")
        server.serve_forever()
