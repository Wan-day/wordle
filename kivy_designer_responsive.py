"""
Kivy UI Designer - Layout Parenting Edition v3.1
Run:  pip install bottle
      python main.py
Open: http://localhost:8080

Features:
- Drag-to-layout: Click inside a layout to place widgets as children
- BoxLayout: Vertical/horizontal stacking with equal sizing
- GridLayout: Grid arrangement with configurable columns
- ScrollView: Contains one child that fills the view
- Children move with parent when dragged
- Layouts auto-rearrange children on resize
- Code generation skips pos_hint/size_hint for layout children
- Properties panel shows parent/child relationships
- "Add to Layout" / "Detach from Layout" buttons in properties
"""
from bottle import Bottle, run, response, request
import json

app = Bottle()

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Kivy UI Designer - Layout Parenting v3.1</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0d0f14;--panel:#13161f;--panel2:#1a1e2a;--border:#252a38;--accent:#00e5ff;--accent2:#7c3aed;--accent3:#10b981;--text:#e2e8f0;--text2:#8892a4;--danger:#ef4444;--warn:#f59e0b;--topbar-h:44px;--panel-min:180px;--panel-max:380px;--code-h:220px;--code-collapsed:36px}
html,body{height:100%;height:100dvh}
body{font-family:Segoe UI,sans-serif;background:var(--bg);color:var(--text);display:flex;flex-direction:column;overflow:hidden;user-select:none;touch-action:none}
.topbar{height:var(--topbar-h);background:var(--panel);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 8px;gap:4px;flex-shrink:0;overflow-x:auto;overflow-y:hidden;scrollbar-width:none}
.topbar::-webkit-scrollbar{display:none}
.logo{font-size:13px;font-weight:800;color:var(--accent);display:flex;align-items:center;gap:6px;white-space:nowrap;flex-shrink:0}
.tbtn{padding:5px 10px;border-radius:6px;border:none;cursor:pointer;font-size:11px;font-weight:600;transition:all .15s;display:flex;align-items:center;gap:4px;white-space:nowrap;flex-shrink:0;background:transparent;color:var(--text2);border:1px solid var(--border)}
.tbtn:hover{color:var(--text);background:var(--panel2)}
.tbtn.active{background:var(--accent);color:#000;border-color:var(--accent)}
.tsep{width:1px;height:20px;background:var(--border);margin:0 2px;flex-shrink:0}
.btn-export{background:var(--accent);color:#000;border-color:var(--accent)}
.btn-export:hover{filter:brightness(1.15)}
.btn-code{background:var(--accent2);color:#fff;border-color:var(--accent2)}
.btn-warn{background:var(--warn);color:#000;border-color:var(--warn)}
.main{display:flex;flex:1;overflow:hidden;position:relative}
.palette{position:relative;background:var(--panel);border-right:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden;flex-shrink:0;transition:width .25s cubic-bezier(.4,0,.2,1),margin .25s}
.palette.collapsed{width:0!important;margin-left:0!important;border-right:none;overflow:hidden}
.palette.collapsed *{opacity:0;pointer-events:none}
.p-resize{position:absolute;right:-3px;top:0;width:6px;height:100%;cursor:col-resize;z-index:100;opacity:0;transition:opacity .2s}
.p-resize:hover,.p-resize.dragging{opacity:1;background:var(--accent)}
.p-resize::after{content:"";position:absolute;left:2px;top:50%;transform:translateY(-50%);width:2px;height:40px;background:var(--border);border-radius:1px}
.props-panel{position:relative;background:var(--panel);border-left:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden;flex-shrink:0;transition:width .25s cubic-bezier(.4,0,.2,1),margin .25s}
.props-panel.collapsed{width:0!important;margin-right:0!important;border-left:none;overflow:hidden}
.props-panel.collapsed *{opacity:0;pointer-events:none}
.r-resize{position:absolute;left:-3px;top:0;width:6px;height:100%;cursor:col-resize;z-index:100;opacity:0;transition:opacity .2s}
.r-resize:hover,.r-resize.dragging{opacity:1;background:var(--accent)}
.r-resize::after{content:"";position:absolute;right:2px;top:50%;transform:translateY(-50%);width:2px;height:40px;background:var(--border);border-radius:1px}
.panel-title{padding:8px 12px 6px;font-size:10px;font-weight:700;letter-spacing:.12em;color:var(--text2);text-transform:uppercase;border-bottom:1px solid var(--border);flex-shrink:0}
.pbody{padding:8px;overflow-y:auto;flex:1;min-width:0}
.wgroup{padding:4px 6px}
.wgroup-lbl{font-size:9px;font-weight:700;letter-spacing:.1em;color:var(--accent2);text-transform:uppercase;padding:3px 5px}
.witem{display:flex;align-items:center;gap:8px;padding:6px 8px;border-radius:6px;cursor:pointer;font-size:12px;font-weight:600;color:var(--text);border:2px solid transparent;margin-bottom:2px;transition:all .12s}
.witem:hover{background:var(--panel2);border-color:var(--border);color:var(--accent)}
.witem.active{border-color:var(--accent);background:rgba(0,229,255,.1);color:var(--accent)}
.wicon{width:22px;height:22px;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:10px;flex-shrink:0}
.canvas-wrap{flex:1;background:#0a0c12;display:flex;flex-direction:column;overflow:hidden;position:relative;min-width:0}
.ctoolbar{height:32px;background:var(--panel);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 10px;gap:8px;font-size:11px;color:var(--text2);flex-shrink:0;overflow-x:auto;overflow-y:hidden;scrollbar-width:none}
.ctoolbar::-webkit-scrollbar{display:none}
.ctoolbar span{font-family:monospace}
#hintbar{font-size:11px;color:var(--accent);background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.2);padding:2px 8px;border-radius:4px;display:none;white-space:nowrap}
.cscroll{flex:1;display:flex;align-items:center;justify-content:center;padding:10px;overflow:auto;position:relative}
#canvas{position:relative;background:#1a1e2a;border:2px solid var(--border);border-radius:6px;flex-shrink:0;overflow:hidden;transform-origin:center center;transition:transform .15s;min-width:200px;min-height:200px}
#canvas.placing{cursor:crosshair!important;border-color:var(--accent);border-style:dashed}
#canvas.placing-inside{cursor:copy!important;border-color:var(--accent3);border-style:dashed}
.cgrid{position:absolute;inset:0;pointer-events:none;background-image:linear-gradient(rgba(255,255,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.06) 1px,transparent 1px);background-size:10% 10%}
.cgrid.off{background-image:none}
.drophint{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;pointer-events:none;gap:10px;transition:opacity .3s}
.drophint.hidden{opacity:0}
.dh-icon{font-size:38px;opacity:.12}
.dh-text{font-size:12px;color:var(--text2);opacity:.5;text-align:center;line-height:1.8}
.zoom-badge{position:absolute;bottom:8px;right:8px;background:var(--panel);border:1px solid var(--border);padding:3px 8px;border-radius:4px;font-size:10px;color:var(--text2);z-index:50;pointer-events:none}
.cv-widget{position:absolute;cursor:move;border:2px solid transparent;border-radius:4px;z-index:1}
.cv-widget:hover{border-color:rgba(0,229,255,.45)}
.cv-widget.selected{border-color:#00e5ff!important;box-shadow:0 0 0 1px #00e5ff,0 0 14px rgba(0,229,255,.25);z-index:100}
.cv-widget.layout-widget{border:2px dashed rgba(124,58,237,.6)}
.cv-widget.layout-widget:hover{border-color:rgba(124,58,237,.9)}
.cv-widget.layout-widget.drop-target{border-color:var(--accent3)!important;box-shadow:0 0 0 2px var(--accent3),0 0 20px rgba(16,185,129,.3)!important;z-index:100}
.cv-widget.selected .wtag,.cv-widget.selected .wdel,.cv-widget.selected .rh,.cv-widget.selected .zup,.cv-widget.selected .zdn{display:block}
.wtag{display:none;position:absolute;top:-19px;left:0;background:#00e5ff;color:#000;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px 3px 0 0;white-space:nowrap;z-index:30}
.wdel{display:none;position:absolute;top:-19px;right:0;background:var(--danger);color:#fff;border:none;font-size:10px;font-weight:700;padding:1px 6px;border-radius:3px 3px 0 0;cursor:pointer;z-index:30}
.zup,.zdn{display:none;position:absolute;top:-19px;height:17px;background:var(--accent2);color:#fff;border:none;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px 3px 0 0;cursor:pointer;z-index:30}
.zup{right:22px}
.zdn{right:44px}
.rh{display:none;position:absolute;bottom:-5px;right:-5px;width:12px;height:12px;background:#00e5ff;border-radius:3px;cursor:se-resize;z-index:20}
.child-badge{position:absolute;top:2px;left:2px;background:rgba(124,58,237,.7);color:#fff;font-size:8px;font-weight:700;padding:1px 4px;border-radius:2px;pointer-events:none;z-index:5}
.pgroup{display:flex;flex-direction:column;gap:4px;margin-bottom:8px}
.pgt{font-size:9px;font-weight:700;letter-spacing:.12em;color:var(--accent2);text-transform:uppercase;padding-bottom:3px;border-bottom:1px solid var(--border)}
.prow{display:flex;align-items:center;gap:5px}
.plbl{font-size:10px;color:var(--text2);width:80px;flex-shrink:0;font-family:monospace}
.pinput{flex:1;background:var(--panel2);border:1px solid var(--border);color:var(--text);border-radius:4px;padding:4px 6px;font-size:11px;font-family:monospace;outline:none;transition:border-color .15s;min-width:0}
.pinput:focus{border-color:var(--accent)}
.pinput[type=color]{padding:2px 4px;height:26px;cursor:pointer;width:36px;flex-shrink:0}
.no-sel{padding:20px 12px;text-align:center;color:var(--text2);font-size:12px;line-height:1.7}
.no-sel .ico{font-size:26px;margin-bottom:8px}
.pbtn{background:var(--panel2);border:1px solid var(--border);color:var(--text);border-radius:4px;padding:4px 6px;font-size:10px;cursor:pointer;transition:all .15s;flex:1}
.pbtn:hover{background:var(--border);color:var(--accent)}
.pbtn-row{display:flex;gap:4px;flex-wrap:wrap;margin-top:3px}
.pct-label{font-family:monospace;font-size:10px;color:var(--accent);min-width:30px;text-align:right}
.code-panel{height:var(--code-h);background:var(--panel);border-top:1px solid var(--border);display:flex;flex-direction:column;flex-shrink:0;transition:height .25s cubic-bezier(.4,0,.2,1)}
.code-panel.collapsed{height:var(--code-collapsed)}
.code-panel.collapsed .code-body{display:none}
.code-hdr{height:var(--code-collapsed);display:flex;align-items:center;padding:0 12px;cursor:pointer;flex-shrink:0;border-bottom:1px solid var(--border);gap:8px}
.code-title{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--accent3);white-space:nowrap}
.code-toggle{font-size:11px;color:var(--text2);margin-left:auto;white-space:nowrap}
.code-tabs{display:flex;gap:6px;margin-left:10px}
.code-tab{font-size:10px;padding:2px 8px;border-radius:4px;background:var(--panel2);border:1px solid var(--border);color:var(--text2);cursor:pointer;transition:all .15s;white-space:nowrap}
.code-tab.active{background:var(--accent);color:#000;border-color:var(--accent)}
.code-tab:hover:not(.active){color:var(--text)}
.code-body{flex:1;overflow:auto;display:none}
.code-body.active{display:block}
pre{padding:8px 12px;font-family:Courier New,monospace;font-size:11px;line-height:1.75;color:#a8b2c7;white-space:pre}
.kw{color:#c084fc}.cls{color:#fb923c}.str{color:#34d399}.cm{color:#4b5563}.num{color:#fbbf24}
#toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(80px);background:var(--panel);border:1px solid var(--border);padding:8px 18px;border-radius:6px;font-size:12px;color:var(--accent);z-index:999;transition:transform .3s,opacity .3s;opacity:0;pointer-events:none}
#toast.show{transform:translateX(-50%) translateY(0);opacity:1}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
.kv-inner{width:100%;height:100%;border-radius:3px;overflow:hidden;display:flex;align-items:center;justify-content:center;font-size:12px}
.kv-Button{background:linear-gradient(135deg,#3b82f6,#1d4ed8);color:#fff;font-weight:600;border-radius:5px;box-shadow:0 2px 8px rgba(0,0,0,.4)}
.kv-Label{color:#e2e8f0}
.kv-TextInput{background:#111827;border:1.5px solid #374151;border-radius:4px;color:#6b7280;justify-content:flex-start;padding:0 10px}
.kv-CheckBox{justify-content:flex-start;padding:0 10px;gap:8px;color:#e2e8f0}
.kv-Slider{padding:0 12px}
.kv-slider-wrap{width:100%;height:6px;background:#374151;border-radius:3px;position:relative}
.kv-slider-wrap::before{content:"";position:absolute;left:0;top:0;width:50%;height:100%;background:#3b82f6;border-radius:3px}
.kv-slider-wrap::after{content:"";position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:16px;height:16px;background:#60a5fa;border-radius:50%}
.kv-Switch{justify-content:flex-start;padding:0 10px;gap:10px;color:#e2e8f0}
.sw-track{width:40px;height:22px;background:#10b981;border-radius:11px;position:relative;flex-shrink:0}
.sw-track::after{content:"";position:absolute;right:3px;top:3px;width:16px;height:16px;background:#fff;border-radius:50%}
.kv-Spinner{background:#111827;border:1.5px solid #374151;border-radius:4px;justify-content:space-between;padding:0 10px;color:#e2e8f0}
.kv-ProgressBar{padding:0 12px}
.kv-pb-wrap{width:100%;height:10px;background:#374151;border-radius:5px;overflow:hidden}
.kv-pb-fill{height:100%;background:linear-gradient(90deg,#3b82f6,#06b6d4);border-radius:5px}
.kv-Image{background:#111827;border:1.5px dashed #374151;border-radius:4px;flex-direction:column;gap:6px;font-size:10px;color:#6b7280}
.kv-BoxLayout{background:rgba(124,58,237,.07);font-size:10px;color:#9f7aea;font-weight:700;flex-direction:column;gap:4px;padding:6px}
.kv-GridLayout{background:rgba(245,158,11,.07);font-size:10px;color:#f59e0b;font-weight:700;padding:4px}
.kv-ScrollView{background:rgba(99,102,241,.07);font-size:10px;color:#818cf8;font-weight:700;position:relative}
.kv-ScrollView::after{content:"";position:absolute;right:4px;top:6px;bottom:6px;width:5px;background:rgba(99,102,241,.3);border-radius:3px}
.layout-children-preview{position:absolute;inset:20px 4px 4px 4px;display:flex;flex-direction:column;gap:3px;overflow:hidden;pointer-events:none}
.layout-child-preview{background:rgba(255,255,255,.08);border-radius:3px;flex:1;min-height:12px}
.layout-drop-hint{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;opacity:0;transition:opacity .2s;font-size:10px;font-weight:700;color:var(--accent3);background:rgba(16,185,129,.1);border-radius:4px;z-index:10}
.layout-drop-hint.show{opacity:1}
@media (max-width: 768px) {:root{--topbar-h:40px}
.tbtn{padding:4px 8px;font-size:10px}
.tbtn .lbl{display:none}
.logo span{display:none}
.palette{position:absolute;z-index:200;box-shadow:4px 0 20px rgba(0,0,0,.5)}
.palette.collapsed{position:relative;box-shadow:none}
.props-panel{position:absolute;right:0;z-index:200;box-shadow:-4px 0 20px rgba(0,0,0,.5)}
.props-panel.collapsed{position:relative;box-shadow:none}
.p-resize,.r-resize{display:none}
.code-panel{height:180px}}
@media (max-width: 480px) {.ctoolbar{font-size:10px;padding:0 6px}
#canvas{min-width:150px;min-height:150px}
.dh-text{font-size:11px}}

/* Developer Credit Footer */
.dev-footer{
  position:fixed;
  bottom:0;
  left:0;
  right:0;
  height:28px;
  background:var(--panel);
  border-top:1px solid var(--border);
  display:flex;
  align-items:center;
  justify-content:center;
  gap:16px;
  padding:0 12px;
  font-size:11px;
  color:var(--text2);
  z-index:1000;
  flex-shrink:0;
}
.dev-footer a{
  color:var(--accent);
  text-decoration:none;
  display:flex;
  align-items:center;
  gap:4px;
  transition:color .15s;
  font-weight:600;
}
.dev-footer a:hover{
  color:var(--accent3);
  text-decoration:underline;
}
.dev-footer .dev-name{
  color:var(--text);
  font-weight:700;
  margin-right:4px;
}
.dev-footer .sep{
  color:var(--border);
}
/* Adjust body padding to account for footer */
body{padding-bottom:28px}
/* Adjust code panel when footer is present */
.code-panel{bottom:28px}

</style>
</head>
<body>
<div class="topbar">
  <button class="tbtn" onclick="togglePalette()" title="Toggle Palette">☰</button>
  <div class="logo">▢ <span>Kivy Designer</span> <span style="font-size:10px;color:var(--text2);font-weight:500">v3.1</span></div>
  <div style="flex:1"></div>
  <button class="tbtn" onclick="undo()" title="Ctrl+Z"><span class="lbl">↩ </span>Undo</button>
  <button class="tbtn" onclick="redo()" title="Ctrl+Y"><span class="lbl">↪ </span>Redo</button>
  <div class="tsep"></div>
  <button class="tbtn" onclick="saveProject()"><span class="lbl">💾 </span>Save</button>
  <button class="tbtn" onclick="loadProject()"><span class="lbl">📂 </span>Load</button>
  <div class="tsep"></div>
  <button class="tbtn" onclick="toggleSnap()" id="snapBtn">▦ <span class="lbl">Snap</span></button>
  <button class="tbtn" onclick="zoomOut()">−</button>
  <span id="zoomLabel" style="font-family:monospace;min-width:36px;text-align:center;font-size:11px">100%</span>
  <button class="tbtn" onclick="zoomIn()">+</button>
  <div class="tsep"></div>
  <button class="tbtn" onclick="clearCanvas()">🗑 <span class="lbl">Clear</span></button>
  <button class="tbtn btn-code" onclick="toggleCode()">⌀ <span class="lbl">Code</span></button>
  <button class="tbtn btn-export" onclick="exportPy()">⇓ <span class="lbl">.py</span></button>
  <button class="tbtn btn-warn" onclick="exportKv()">⇓ <span class="lbl">.kv</span></button>
  <button class="tbtn" onclick="copyCode()" title="Copy">📋</button>
  <button class="tbtn" onclick="toggleProps()" title="Toggle Properties">⚙</button>
</div>

<div class="main">
  <div class="palette" id="palette" style="width:220px">
    <div class="p-resize" id="pResize"></div>
    <div class="panel-title">Widgets</div>
    <div class="pbody">
      <div class="wgroup">
        <div class="wgroup-lbl">Basic</div>
        <div class="witem" data-type="Button"><div class="wicon" style="background:#1d4ed820;color:#3b82f6">Btn</div>Button</div>
        <div class="witem" data-type="Label"><div class="wicon" style="background:#6b728020;color:#9ca3af">Lbl</div>Label</div>
        <div class="witem" data-type="TextInput"><div class="wicon" style="background:#10b98120;color:#10b981">Txt</div>TextInput</div>
        <div class="witem" data-type="Image"><div class="wicon" style="background:#f5940020;color:#f59400">🖼</div>Image</div>
      </div>
      <div class="wgroup">
        <div class="wgroup-lbl">Controls</div>
        <div class="witem" data-type="CheckBox"><div class="wicon" style="background:#3b82f620;color:#3b82f6">☑</div>CheckBox</div>
        <div class="witem" data-type="Slider"><div class="wicon" style="background:#60a5fa20;color:#60a5fa">━</div>Slider</div>
        <div class="witem" data-type="Switch"><div class="wicon" style="background:#10b98120;color:#10b981">⏻</div>Switch</div>
        <div class="witem" data-type="Spinner"><div class="wicon" style="background:#8b5cf620;color:#8b5cf6">▽</div>Spinner</div>
        <div class="witem" data-type="ProgressBar"><div class="wicon" style="background:#06b6d420;color:#06b6d4">▬</div>ProgressBar</div>
      </div>
      <div class="wgroup">
        <div class="wgroup-lbl">Layouts</div>
        <div class="witem" data-type="BoxLayout"><div class="wicon" style="background:#7c3aed20;color:#7c3aed">□</div>BoxLayout</div>
        <div class="witem" data-type="GridLayout"><div class="wicon" style="background:#f59e0b20;color:#f59e0b">⊞</div>GridLayout</div>
        <div class="witem" data-type="ScrollView"><div class="wicon" style="background:#6366f120;color:#6366f1">↕</div>ScrollView</div>
      </div>
      <div style="padding:8px;font-size:10px;color:var(--text2);line-height:1.6;border-top:1px solid var(--border);margin-top:4px">
        <b style="color:var(--accent)">Tip:</b> Drag panel edges to resize. Click ☰/⚙ to collapse.
        <br><b style="color:var(--accent3)">Shortcuts:</b> Ctrl+D=Dup, Del=Delete, Arrows=Nudge, Ctrl+Z/Y=Undo/Redo
        <br><b style="color:var(--accent2)">Layouts:</b> Click inside a layout to place child widgets. Layouts auto-arrange children.
      </div>
    </div>
  </div>

  <div class="canvas-wrap">
    <div class="ctoolbar">
      <span id="wcount">0 widgets</span>
      <span style="color:var(--border)">|</span>
      <div id="hintbar">▶ Click canvas to place &nbsp;|&nbsp; Esc=cancel</div>
      <span id="selinfo" style="color:var(--accent);margin-left:auto">Click a palette item to start</span>
    </div>
    <div class="cscroll">
      <div id="canvas" style="width:600px;height:600px">
        <div class="cgrid" id="cgrid"></div>
        <div class="drophint" id="drophint">
          <div class="dh-icon">▢</div>
          <div class="dh-text">1→ Click widget in left panel<br>2→ Click on canvas to place (top-level)<br>3→ Click INSIDE a layout to place as child</div>
        </div>
      </div>
    </div>
    <div class="zoom-badge" id="zoomBadge">100%</div>
  </div>

  <div class="props-panel" id="propsPanel" style="width:260px">
    <div class="r-resize" id="rResize"></div>
    <div class="panel-title">Properties</div>
    <div class="pbody" id="propsContent"><div class="no-sel"><div class="ico">◉</div>Select a widget to edit<br><span style="font-size:10px">Ctrl+D to duplicate</span></div></div>
  </div>
</div>

<div class="code-panel" id="codePanel">
  <div class="code-hdr" onclick="toggleCode()">
    <div class="code-title"><span style="color:var(--accent3)">●</span> Generated Code</div>
    <div class="code-tabs">
      <div class="code-tab active" onclick="switchCodeTab(event,&#39;py&#39;)" id="tab-py">Python</div>
      <div class="code-tab" onclick="switchCodeTab(event,&#39;kv&#39;)" id="tab-kv">KV Lang</div>
    </div>
    <span class="code-toggle" id="codeToggle">▲ Collapse</span>
  </div>
  <div class="code-body active" id="body-py"><pre id="codePre"></pre></div>
  <div class="code-body" id="body-kv"><pre id="kvPre"></pre></div>
</div>

<div id="toast"></div>
<input type="file" id="fileInput" style="display:none" accept=".json" onchange="handleFileLoad(event)">

<script>
// =====================================================
// GLOBAL STATE
// =====================================================
let widgets = [];
let selectedId = null;
let idCounter = 1;
let pendingType = null;
let zoomLevel = 1;
const CANVAS_PX = 600;
let snapEnabled = true;
let currentCodeTab = "py";
let history = [];
let historyIdx = -1;
let hoveredLayoutId = null;

const BOOLPROPS = new Set(["active","disabled","readonly","multiline","password","allow_stretch","keep_ratio"]);
const NUMPROPS = new Set(["font_size","value","max","min","cols","rows","spacing","padding","border_width"]);
const RAWPROPS = new Set(["pos_hint","size_hint"]);
const COLORPROPS = new Set(["background_color","color","foreground_color","border_color"]);
const LAYOUTS = ["BoxLayout","GridLayout","ScrollView"];
const isLayout = t => LAYOUTS.includes(t);

// =====================================================
// LAYOUT HELPERS
// =====================================================
function getParentLayout(w){
  if(!w.parentId) return null;
  return widgets.find(x => x.id === w.parentId);
}
function isChildOfLayout(w){
  return w.parentId && isLayout(getParentLayout(w)?.type);
}

// =====================================================
// ARRANGE LAYOUT CHILDREN
// =====================================================
function arrangeLayoutChildren(layoutId){
  const layout = widgets.find(x => x.id === layoutId);
  if(!layout || !isLayout(layout.type)) return;
  const children = widgets.filter(w => w.parentId === layoutId);
  if(!children.length) return;

  const size = document.getElementById("canvas").offsetWidth;
  const lx = layout.x * size, ly = layout.y * size;
  const lw = layout.width * size, lh = layout.height * size;

  if(layout.type === 'BoxLayout'){
    const isHoriz = layout.props.orientation && (layout.props.orientation.includes('horiz') || layout.props.orientation === 'horizontal');
    const spacing = parseFloat(layout.props.spacing || 10);
    const padding = parseFloat(layout.props.padding || 10);

    if(isHoriz){
      const availW = Math.max(1, lw - padding * 2 - spacing * (children.length - 1));
      const childW = availW / children.length;
      children.forEach((cw, i) => {
        cw.x = (lx + padding + i * (childW + spacing)) / size;
        cw.y = (ly + padding) / size;
        cw.width = childW / size;
        cw.height = (lh - padding * 2) / size;
        updateWidgetVisual(cw);
      });
    } else {
      const availH = Math.max(1, lh - padding * 2 - spacing * (children.length - 1));
      const childH = availH / children.length;
      children.forEach((cw, i) => {
        cw.x = (lx + padding) / size;
        cw.y = (ly + padding + i * (childH + spacing)) / size;
        cw.width = (lw - padding * 2) / size;
        cw.height = childH / size;
        updateWidgetVisual(cw);
      });
    }
  } else if(layout.type === 'GridLayout'){
    const cols = parseInt(layout.props.cols || 2);
    const spacing = parseFloat(layout.props.spacing || 10);
    const padding = parseFloat(layout.props.padding || 10);
    const rows = Math.ceil(children.length / cols);
    const cellW = Math.max(1, (lw - padding * 2 - spacing * (cols - 1)) / cols);
    const cellH = Math.max(1, (lh - padding * 2 - spacing * (rows - 1)) / rows);

    children.forEach((cw, i) => {
      const col = i % cols;
      const row = Math.floor(i / cols);
      cw.x = (lx + padding + col * (cellW + spacing)) / size;
      cw.y = (ly + padding + row * (cellH + spacing)) / size;
      cw.width = cellW / size;
      cw.height = cellH / size;
      updateWidgetVisual(cw);
    });
  } else if(layout.type === 'ScrollView'){
    if(children.length > 0){
      const cw = children[0];
      cw.x = layout.x;
      cw.y = layout.y;
      cw.width = layout.width;
      cw.height = layout.height;
      updateWidgetVisual(cw);
    }
  }
}

function updateWidgetVisual(w){
  const el = document.getElementById('cw_' + w.id);
  const size = document.getElementById("canvas").offsetWidth;
  if(el){
    el.style.left = (w.x * size) + 'px';
    el.style.top = (w.y * size) + 'px';
    el.style.width = (w.width * size) + 'px';
    el.style.height = (w.height * size) + 'px';
  }
}

function addToLayout(childId, layoutId){
  const child = widgets.find(x => x.id === childId);
  const layout = widgets.find(x => x.id === layoutId);
  if(!child || !layout || !isLayout(layout.type)) return;
  if(childId === layoutId) return;
  let p = layout;
  while(p){
    if(p.parentId === childId) return;
    p = widgets.find(x => x.id === p.parentId);
  }

  if(child.parentId){
    const oldParent = widgets.find(x => x.id === child.parentId);
    if(oldParent) oldParent.childIds = oldParent.childIds.filter(c => c !== childId);
  }

  child.parentId = layoutId;
  if(!layout.childIds.includes(childId)) layout.childIds.push(childId);
  arrangeLayoutChildren(layoutId);
  refreshLayoutPreview(layout);
  updateHint();
  generateCode();
  toast(child.type + " added to " + layout.type + " #" + layoutId);
}

function removeFromLayout(childId){
  const child = widgets.find(x => x.id === childId);
  if(!child || !child.parentId) return;
  const layout = widgets.find(x => x.id === child.parentId);
  if(layout) layout.childIds = layout.childIds.filter(c => c !== childId);
  child.parentId = null;
  if(layout) refreshLayoutPreview(layout);
  updateHint();
  generateCode();
  toast(child.type + " #" + childId + " removed from layout");
}

// =====================================================
// DROP TARGET DETECTION
// =====================================================
function findLayoutAtPoint(x, y){
  const layouts = widgets.filter(w => isLayout(w.type) && !w.parentId).sort((a,b) => (b.zIndex||1) - (a.zIndex||1));
  for(const lw of layouts){
    if(x >= lw.x && x <= lw.x + lw.width && y >= lw.y && y <= lw.y + lw.height){
      return lw.id;
    }
  }
  return null;
}

function highlightLayout(layoutId){
  document.querySelectorAll('.cv-widget').forEach(el => el.classList.remove('drop-target'));
  if(layoutId){
    const el = document.getElementById('cw_' + layoutId);
    if(el) el.classList.add('drop-target');
  }
}

// =====================================================
// RESPONSIVE PANEL MANAGEMENT
// =====================================================
function togglePalette(){
  const p = document.getElementById("palette");
  p.classList.toggle("collapsed");
  savePanelState();
}
function toggleProps(){
  const p = document.getElementById("propsPanel");
  p.classList.toggle("collapsed");
  savePanelState();
}
function savePanelState(){
  const state = {
    palette: !document.getElementById("palette").classList.contains("collapsed"),
    props: !document.getElementById("propsPanel").classList.contains("collapsed"),
    code: !document.getElementById("codePanel").classList.contains("collapsed")
  };
  localStorage.setItem("kivyDesignerPanels", JSON.stringify(state));
}
function loadPanelState(){
  try{
    const state = JSON.parse(localStorage.getItem("kivyDesignerPanels") || "{}");
    if(state.palette === false) document.getElementById("palette").classList.add("collapsed");
    if(state.props === false) document.getElementById("propsPanel").classList.add("collapsed");
    if(state.code === false) document.getElementById("codePanel").classList.add("collapsed");
  }catch(e){}
}

// =====================================================
// RESIZABLE PANELS
// =====================================================
function setupResize(handle, panel, minW, maxW, side){
  let startX, startW;
  handle.addEventListener("mousedown", e => {
    e.preventDefault();
    startX = e.clientX;
    startW = panel.offsetWidth;
    handle.classList.add("dragging");
    document.body.style.cursor = side === "left" ? "e-resize" : "w-resize";
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
  });
  function onMove(e){
    const dx = e.clientX - startX;
    const newW = side === "left" ? startW + dx : startW - dx;
    const clamped = Math.max(minW, Math.min(maxW, newW));
    panel.style.width = clamped + "px";
    panel.classList.remove("collapsed");
  }
  function onUp(){
    handle.classList.remove("dragging");
    document.body.style.cursor = "";
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onUp);
  }
}

// =====================================================
// CANVAS AUTO-RESIZE
// =====================================================
function fitCanvas(){
  const wrap = document.querySelector(".canvas-wrap");
  const canvas = document.getElementById("canvas");
  const availW = wrap.clientWidth - 40;
  const availH = wrap.clientHeight - 60;
  const size = Math.min(availW, availH, 800);
  canvas.style.width = size + "px";
  canvas.style.height = size + "px";
  widgets.forEach(w => {
    const el = document.getElementById("cw_" + w.id);
    if(el){
      el.style.left = (w.x * size) + "px";
      el.style.top = (w.y * size) + "px";
      el.style.width = (w.width * size) + "px";
      el.style.height = (w.height * size) + "px";
    }
  });
}

// =====================================================
// HELPERS
// =====================================================
function snap(v){
  if(!snapEnabled) return v;
  const step = 0.05;
  return Math.round(v / step) * step;
}
function toast(msg){
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2000);
}
function pushState(){
  if(historyIdx < history.length - 1) history = history.slice(0, historyIdx + 1);
  history.push(JSON.stringify(widgets));
  if(history.length > 50) history.shift();
  else historyIdx++;
}
function undo(){
  if(historyIdx > 0){
    historyIdx--;
    widgets = JSON.parse(history[historyIdx]);
    rebuildAll();
  }
}
function redo(){
  if(historyIdx < history.length - 1){
    historyIdx++;
    widgets = JSON.parse(history[historyIdx]);
    rebuildAll();
  }
}
function rebuildAll(){
  document.querySelectorAll(".cv-widget").forEach(e => e.remove());
  widgets.forEach(w => renderWidget(w));
  updateHint();
  generateCode();
  deselectAll();
}
function bringToFront(id){
  const w = widgets.find(x => x.id === id);
  if(!w) return;
  const maxZ = Math.max(...widgets.map(x => x.zIndex || 1), 1);
  w.zIndex = maxZ + 1;
  const el = document.getElementById("cw_" + id);
  if(el) el.style.zIndex = w.zIndex;
}
function sendToBack(id){
  const w = widgets.find(x => x.id === id);
  if(!w) return;
  w.zIndex = 1;
  const el = document.getElementById("cw_" + id);
  if(el) el.style.zIndex = 1;
}
function duplicateSelected(){
  if(!selectedId) return;
  const w = widgets.find(x => x.id === selectedId);
  if(!w) return;
  pushState();
  const nw = JSON.parse(JSON.stringify(w));
  nw.id = idCounter++;
  nw.x = Math.min(w.x + 0.05, 1 - w.width);
  nw.y = Math.min(w.y + 0.05, 1 - w.height);
  nw.zIndex = (Math.max(...widgets.map(x => x.zIndex || 1), 1) + 1);
  nw.parentId = null;
  nw.childIds = [];
  widgets.push(nw);
  renderWidget(nw);
  selectWidget(nw.id);
  updateHint();
  generateCode();
}
function toggleSnap(){
  snapEnabled = !snapEnabled;
  document.getElementById("snapBtn").innerHTML = '▦ <span class="lbl">Snap: ' + (snapEnabled ? "ON" : "OFF") + '</span>';
}
function zoomIn(){
  zoomLevel = Math.min(zoomLevel + 0.1, 2);
  updateZoom();
}
function zoomOut(){
  zoomLevel = Math.max(zoomLevel - 0.1, 0.5);
  updateZoom();
}
function updateZoom(){
  const z = Math.round(zoomLevel * 100);
  document.getElementById("zoomLabel").textContent = z + "%";
  document.getElementById("zoomBadge").textContent = z + "%";
  document.getElementById("canvas").style.transform = "scale(" + zoomLevel + ")";
}

// =====================================================
// DEFAULT PROPERTIES
// =====================================================
function getDefaultProps(type){
  const defaults = {
    Button: {text: "Button", font_size: 14, color: "#ffffff"},
    Label: {text: "Label", font_size: 14, color: "#e2e8f0"},
    TextInput: {hint_text: "Enter text...", font_size: 14, foreground_color: "#6b7280"},
    CheckBox: {color: "#3b82f6"},
    Slider: {min: 0, max: 100, value: 50, color: "#3b82f6"},
    Switch: {active: true},
    Spinner: {text: "Item 1", values: "Item 1,Item 2,Item 3", color: "#e2e8f0"},
    ProgressBar: {value: 60, max: 100, color: "#3b82f6"},
    Image: {source: "image.png"},
    BoxLayout: {orientation: "vertical", spacing: 10, padding: 10},
    GridLayout: {cols: 2, spacing: 10, padding: 10},
    ScrollView: {}
  };
  return defaults[type] || {};
}

// =====================================================
// PALETTE & CANVAS INTERACTION
// =====================================================
document.querySelectorAll(".witem").forEach(item => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".witem").forEach(i => i.classList.remove("active"));
    item.classList.add("active");
    pendingType = item.dataset.type;
    document.getElementById("canvas").classList.add("placing");
    document.getElementById("hintbar").style.display = "block";
    document.getElementById("selinfo").textContent = "Click canvas to place " + pendingType + " (click inside layout to parent)";
  });
});

document.getElementById("canvas").addEventListener("mousemove", ev => {
  if(!pendingType) return;
  const rect = document.getElementById("canvas").getBoundingClientRect();
  const size = rect.width;
  const x = (ev.clientX - rect.left) / zoomLevel / size;
  const y = (ev.clientY - rect.top) / zoomLevel / size;
  const layoutId = findLayoutAtPoint(x, y);
  if(layoutId !== hoveredLayoutId){
    hoveredLayoutId = layoutId;
    highlightLayout(layoutId);
    const canvas = document.getElementById("canvas");
    if(layoutId){
      canvas.classList.remove("placing");
      canvas.classList.add("placing-inside");
    } else {
      canvas.classList.remove("placing-inside");
      canvas.classList.add("placing");
    }
  }
});

document.getElementById("canvas").addEventListener("click", ev => {
  if(!pendingType) return;
  const rect = document.getElementById("canvas").getBoundingClientRect();
  const size = rect.width;
  const x = (ev.clientX - rect.left) / zoomLevel / size;
  const y = (ev.clientY - rect.top) / zoomLevel / size;

  const layoutId = findLayoutAtPoint(x, y);
  const isChild = layoutId !== null;

  const w = 0.2, h = 0.1;
  const newWidget = {
    id: idCounter++,
    type: pendingType,
    x: snap(Math.max(0, Math.min(x - w/2, 1 - w))),
    y: snap(Math.max(0, Math.min(y - h/2, 1 - h))),
    width: w,
    height: h,
    zIndex: (Math.max(...widgets.map(x => x.zIndex || 1), 1) + 1),
    parentId: null,
    childIds: [],
    props: getDefaultProps(pendingType)
  };
  pushState();
  widgets.push(newWidget);
  renderWidget(newWidget);

  if(isChild && layoutId){
    addToLayout(newWidget.id, layoutId);
  } else {
    selectWidget(newWidget.id);
  }

  updateHint();
  generateCode();
  pendingType = null;
  hoveredLayoutId = null;
  highlightLayout(null);
  document.querySelectorAll(".witem").forEach(i => i.classList.remove("active"));
  document.getElementById("canvas").classList.remove("placing");
  document.getElementById("canvas").classList.remove("placing-inside");
  document.getElementById("hintbar").style.display = "none";
});

document.addEventListener("keydown", ev => {
  if(ev.key === "Escape" && pendingType){
    pendingType = null;
    hoveredLayoutId = null;
    highlightLayout(null);
    document.querySelectorAll(".witem").forEach(i => i.classList.remove("active"));
    document.getElementById("canvas").classList.remove("placing");
    document.getElementById("canvas").classList.remove("placing-inside");
    document.getElementById("hintbar").style.display = "none";
  }
  if(ev.key === "Delete" && selectedId){
    pushState();
    deleteWidget(selectedId);
  }
  if(ev.key === "d" && ev.ctrlKey && selectedId){
    ev.preventDefault();
    duplicateSelected();
  }
  if(ev.key === "z" && ev.ctrlKey){
    ev.preventDefault();
    undo();
  }
  if(ev.key === "y" && ev.ctrlKey){
    ev.preventDefault();
    redo();
  }
  if(ev.key === "s" && ev.ctrlKey){
    ev.preventDefault();
    saveProject();
  }
  if(selectedId && ["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(ev.key)){
    ev.preventDefault();
    const w = widgets.find(x => x.id === selectedId);
    if(!w) return;
    pushState();
    const step = 0.01;
    if(ev.key === "ArrowUp") w.y = Math.max(0, w.y - step);
    if(ev.key === "ArrowDown") w.y = Math.min(1 - w.height, w.y + step);
    if(ev.key === "ArrowLeft") w.x = Math.max(0, w.x - step);
    if(ev.key === "ArrowRight") w.x = Math.min(1 - w.width, w.x + step);
    const size = document.getElementById("canvas").offsetWidth;
    const el = document.getElementById("cw_" + w.id);
    if(el){
      el.style.left = (w.x * size) + "px";
      el.style.top = (w.y * size) + "px";
    }
    if(isLayout(w.type)) arrangeLayoutChildren(w.id);
    if(w.parentId) arrangeLayoutChildren(w.parentId);
    syncPos(w);
    updateSelInfo(w);
    generateCode();
  }
});
// =====================================================
// RENDER WIDGET
// =====================================================
function makeInner(w){
  const d=document.createElement("div");
  d.className="kv-inner";
  const bg = w.props.background_color || "transparent";
  const fg = w.props.color || w.props.foreground_color || "#e2e8f0";

  switch(w.type){
    case "Button":{
      d.classList.add("kv-Button");
      d.style.fontSize=(w.props.font_size||14)+"px";
      d.textContent=w.props.text||"Button";
      if(bg && bg!=="transparent") d.style.background=bg;
      if(fg) d.style.color=fg;
      break;}
    case "Label":{
      d.classList.add("kv-Label");
      d.style.fontSize=(w.props.font_size||14)+"px";
      d.textContent=w.props.text||"Label";
      if(bg && bg!=="transparent"){d.style.background=bg;d.style.padding="4px 8px";d.style.borderRadius="4px";}
      if(fg) d.style.color=fg;
      break;}
    case "TextInput":{
      d.classList.add("kv-TextInput");
      d.textContent=w.props.hint_text||"Enter text...";
      if(bg && bg!=="transparent") d.style.background=bg;
      if(w.props.foreground_color) d.style.color=w.props.foreground_color;
      break;}
    case "CheckBox":{
      d.classList.add("kv-CheckBox");
      const checkColor = w.props.color || "#3b82f6";
      d.innerHTML="<span style=\"font-size:20px;color:"+checkColor+"\">☑</span><span>Check</span>";
      break;}
    case "Slider":{
      d.classList.add("kv-Slider");
      const trackColor = w.props.background_color || "#374151";
      const thumbColor = w.props.color || "#3b82f6";
      d.innerHTML="<div class=\"kv-slider-wrap\" style=\"background:"+trackColor+"\"><div style=\"position:absolute;left:0;top:0;width:50%;height:100%;background:"+thumbColor+";border-radius:3px\"></div><div style=\"position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:16px;height:16px;background:"+thumbColor+";border-radius:50%\"></div></div>";
      break;}
    case "Switch":{
      d.classList.add("kv-Switch");
      const swBg = w.props.background_color || "#10b981";
      d.innerHTML="<div class=\"sw-track\" style=\"background:"+swBg+"\"></div><span>ON</span>";
      break;}
    case "Spinner":{
      d.classList.add("kv-Spinner");
      d.innerHTML="<span>"+(w.props.text||"Item 1")+"</span><span style=\"font-size:9px;color:#6b7280\">▼</span>";
      if(bg && bg!=="transparent") d.style.background=bg;
      if(fg) d.style.color=fg;
      break;}
    case "ProgressBar":{
      d.classList.add("kv-ProgressBar");
      const trackC = w.props.background_color || "#374151";
      const fillC = w.props.color || "#3b82f6";
      const pct=Math.round((parseFloat(w.props.value||60)/parseFloat(w.props.max||100))*100);
      d.innerHTML="<div style=\"width:100%;height:10px;background:"+trackC+";border-radius:5px;overflow:hidden\"><div style=\"height:100%;width:"+pct+"%;background:"+fillC+";border-radius:5px\"></div></div>";
      break;}
    case "Image":{
      d.classList.add("kv-Image");
      d.innerHTML="<div style=\"font-size:26px\">🖼</div><div>"+(w.props.source||"image")+"</div>";
      if(bg && bg!=="transparent") d.style.background=bg;
      break;}
    case "BoxLayout":{
      d.classList.add("kv-BoxLayout");
      d.innerHTML="<span>BoxLayout</span>";
      if(bg) d.style.background=bg;
      if(fg) d.style.color=fg;
      break;}
    case "GridLayout":{
      d.classList.add("kv-GridLayout");
      d.innerHTML="<span>GridLayout (cols="+(w.props.cols||2)+")</span>";
      if(bg) d.style.background=bg;
      if(fg) d.style.color=fg;
      break;}
    case "ScrollView":{
      d.classList.add("kv-ScrollView");
      d.textContent="ScrollView";
      if(bg) d.style.background=bg;
      if(fg) d.style.color=fg;
      break;}
  }
  return d;
}

function refreshInner(w){
  const el=document.getElementById("cw_"+w.id); if(!el) return;
  const old=el.querySelector(".kv-inner");
  if(old) el.replaceChild(makeInner(w),old);
}

function refreshLayoutPreview(w){
  const el=document.getElementById("cw_"+w.id); if(!el) return;
  let prev=el.querySelector(".layout-children-preview");
  let hint=el.querySelector(".layout-drop-hint");
  if(prev) prev.remove();
  if(hint) hint.remove();

  if(isLayout(w.type)){
    hint=document.createElement("div");
    hint.className="layout-drop-hint";
    hint.innerHTML="+ DROP CHILD HERE";
    el.appendChild(hint);
  }

  if(w.childIds.length>0){
    prev=document.createElement("div");
    prev.className="layout-children-preview";
    const isHoriz=w.props.orientation && (w.props.orientation.includes("horiz") || w.props.orientation === "horizontal");
    if(isHoriz) prev.style.flexDirection="row";
    w.childIds.forEach(cid=>{
      const cw=widgets.find(x=>x.id===cid); if(!cw) return;
      const bar=document.createElement("div");
      bar.className="layout-child-preview";
      bar.style.background="rgba(0,229,255,.12)";
      bar.title=cw.type;
      bar.innerHTML="<span style=\"font-size:8px;padding:1px 3px;color:#00e5ff\">"+cw.type+"</span>";
      prev.appendChild(bar);
    });
    el.appendChild(prev);
  }
}

function renderWidget(w){
  const el=document.createElement("div");
  el.className="cv-widget"+(isLayout(w.type)?" layout-widget":"");
  el.id="cw_"+w.id;
  const size = document.getElementById("canvas").offsetWidth;
  const px=w.x*size, py=w.y*size, pw=w.width*size, ph=w.height*size;
  el.style.cssText="left:"+px+"px;top:"+py+"px;width:"+pw+"px;height:"+ph+"px;z-index:"+(w.zIndex||1);

  const tag=document.createElement("div");
  tag.className="wtag";
  tag.textContent=w.type+(w.parentId?" [child]":"")+" #"+w.id;
  el.appendChild(tag);

  const del=document.createElement("button");
  del.className="wdel"; del.textContent="✕";
  del.addEventListener("mousedown",ev=>{ev.stopPropagation();pushState();deleteWidget(w.id);});
  el.appendChild(del);

  const zup=document.createElement("button");
  zup.className="zup"; zup.innerHTML="▲";
  zup.title="Bring to front";
  zup.addEventListener("mousedown",ev=>{ev.stopPropagation();bringToFront(w.id);});
  el.appendChild(zup);

  const zdn=document.createElement("button");
  zdn.className="zdn"; zdn.innerHTML="▼";
  zdn.title="Send to back";
  zdn.addEventListener("mousedown",ev=>{ev.stopPropagation();sendToBack(w.id);});
  el.appendChild(zdn);

  if(w.parentId){
    const badge=document.createElement("div");
    badge.className="child-badge";
    badge.textContent="child";
    el.appendChild(badge);
  }

  el.appendChild(makeInner(w));

  const rh=document.createElement("div");
  rh.className="rh";
  el.appendChild(rh);

  el.addEventListener("mousedown", ev=>{
    if(ev.target===rh||ev.target===del||ev.target===zup||ev.target===zdn) return;
    if(pendingType) return;
    ev.stopPropagation();
    selectWidget(w.id);
    const sx=ev.clientX, sy=ev.clientY, ox=w.x, oy=w.y;
    const childOffsets={};
    w.childIds.forEach(cid=>{
      const cw=widgets.find(x=>x.id===cid);
      if(cw) childOffsets[cid]={dx:cw.x-ox, dy:cw.y-oy};
    });
    let moved=false;
    const size = document.getElementById("canvas").offsetWidth;

    function onMove(me){
      if(!moved){moved=true; pushState();}
      const dx=(me.clientX-sx)/zoomLevel / size;
      const dy=(me.clientY-sy)/zoomLevel / size;
      w.x=Math.max(0,Math.min(snap(ox+dx),1-w.width));
      w.y=Math.max(0,Math.min(snap(oy+dy),1-w.height));
      const wEl=document.getElementById("cw_"+w.id);
      if(wEl){wEl.style.left=(w.x*size)+"px";wEl.style.top=(w.y*size)+"px";}
      w.childIds.forEach(cid=>{
        const cw=widgets.find(x=>x.id===cid);
        if(!cw) return;
        cw.x=w.x+childOffsets[cid].dx;
        cw.y=w.y+childOffsets[cid].dy;
        const cEl=document.getElementById("cw_"+cid);
        if(cEl){cEl.style.left=(cw.x*size)+"px";cEl.style.top=(cw.y*size)+"px";}
      });
      syncPos(w); updateSelInfo(w); generateCode();
    }
    function onUp(){window.removeEventListener("mousemove",onMove);window.removeEventListener("mouseup",onUp);}
    window.addEventListener("mousemove",onMove);
    window.addEventListener("mouseup",onUp);
  });

  rh.addEventListener("mousedown", ev=>{
    ev.stopPropagation();
    pushState();
    const sx=ev.clientX, sy=ev.clientY, sw=w.width, sh=w.height;
    const size = document.getElementById("canvas").offsetWidth;
    function onMove(me){
      w.width =Math.max(0.05, Math.min(snap(sw+(me.clientX-sx)/zoomLevel/size),1-w.x));
      w.height=Math.max(0.04, Math.min(snap(sh+(me.clientY-sy)/zoomLevel/size),1-w.y));
      const wEl=document.getElementById("cw_"+w.id);
      if(wEl){wEl.style.width=(w.width*size)+"px";wEl.style.height=(w.height*size)+"px";}
      refreshInner(w); syncSize(w); updateSelInfo(w); generateCode();
      if(isLayout(w.type)) arrangeLayoutChildren(w.id);
    }
    function onUp(){window.removeEventListener("mousemove",onMove);window.removeEventListener("mouseup",onUp);}
    window.addEventListener("mousemove",onMove);
    window.addEventListener("mouseup",onUp);
  });

  document.getElementById("canvas").appendChild(el);
  refreshLayoutPreview(w);
}

// =====================================================
// SELECT / DESELECT
// =====================================================
function selectWidget(id){
  document.querySelectorAll(".cv-widget").forEach(e=>e.classList.remove("selected"));
  selectedId=id;
  const el=document.getElementById("cw_"+id); if(el) el.classList.add("selected");
  const w=widgets.find(x=>x.id===id);
  if(w){renderProps(w);updateSelInfo(w);}
}
function deselectAll(){
  document.querySelectorAll(".cv-widget").forEach(e=>e.classList.remove("selected"));
  selectedId=null;
  document.getElementById("propsContent").innerHTML="<div class=\"no-sel\"><div class=\"ico\">◉</div>Select a widget to edit<br><span style=\"font-size:10px\">Ctrl+D to duplicate</span></div>";
  document.getElementById("selinfo").textContent="Click a palette item to start";
}
function updateSelInfo(w){
  let info=w.type+" #"+w.id+" | x:"+(w.x*100).toFixed(1)+"% y:"+(w.y*100).toFixed(1)+"% | "+(w.width*100).toFixed(1)+"%×"+(w.height*100).toFixed(1)+"%";
  if(w.parentId) info+=" | child of #"+w.parentId;
  if(w.childIds.length) info+=" | "+w.childIds.length+" children";
  document.getElementById("selinfo").textContent=info;
}
function syncPos(w){
  const xi=document.getElementById("pi_x"),yi=document.getElementById("pi_y");
  if(xi)xi.value=(w.x*100).toFixed(1); if(yi)yi.value=(w.y*100).toFixed(1);
}
function syncSize(w){
  const wi=document.getElementById("pi_w"),hi=document.getElementById("pi_h");
  if(wi)wi.value=(w.width*100).toFixed(1); if(hi)hi.value=(w.height*100).toFixed(1);
}
// =====================================================
// PROPERTIES PANEL
// =====================================================
function renderProps(w){
  let h="<div class=\"pbody\">";

  if(w.parentId){
    const parent = widgets.find(x => x.id === w.parentId);
    h+="<div class=\"pgroup\"><div class=\"pgt\" style=\"color:var(--accent3)\">📎 Parent Layout</div>";
    h+="<div class=\"prow\"><div class=\"plbl\" style=\"width:100%\">Child of "+(parent?parent.type:"Layout")+" #"+w.parentId+"</div></div>";
    h+="<div class=\"pbtn-row\"><button class=\"pbtn\" onclick=\"removeFromLayout("+w.id+")\" style=\"background:var(--warn);color:#000\">🔗 Detach from Layout</button></div>";
    h+="</div>";
  } else if(!isLayout(w.type)) {
    const layouts = widgets.filter(x => isLayout(x.type) && !x.parentId);
    if(layouts.length > 0){
      h+="<div class=\"pgroup\"><div class=\"pgt\" style=\"color:var(--accent2)\">📎 Add to Layout</div>";
      h+="<div class=\"pbtn-row\">";
      layouts.forEach(lw => {
        h+="<button class=\"pbtn\" onclick=\"addToLayout("+w.id+","+lw.id+")\">"+lw.type+" #"+lw.id+"</button>";
      });
      h+="</div></div>";
    }
  }

  if(w.childIds.length){
    h+="<div class=\"pgroup\"><div class=\"pgt\" style=\"color:var(--accent2)\">👶 Children ("+w.childIds.length+")</div>";
    w.childIds.forEach(cid => {
      const cw = widgets.find(x => x.id === cid);
      if(cw){
        h+="<div class=\"prow\"><div class=\"plbl\" style=\"width:100%;font-size:10px\">• "+cw.type+" #"+cid+"</div></div>";
      }
    });
    h+="</div>";
  }

  h+="<div class=\"pgroup\"><div class=\"pgt\">Layout (% of screen)</div>";
  h+=prowPct("pos_x","pi_x",(w.x*100).toFixed(1),"uLay("+w.id+",&#39;x&#39;,this.value)");
  h+=prowPct("pos_y","pi_y",(w.y*100).toFixed(1),"uLay("+w.id+",&#39;y&#39;,this.value)");
  h+=prowPct("size_x","pi_w",(w.width*100).toFixed(1),"uLay("+w.id+",&#39;width&#39;,this.value)");
  h+=prowPct("size_y","pi_h",(w.height*100).toFixed(1),"uLay("+w.id+",&#39;height&#39;,this.value)");
  h+="</div>";

  h+="<div class=\"pgroup\"><div class=\"pgt\">Actions</div>";
  h+="<div class=\"pbtn-row\">";
  h+="<button class=\"pbtn\" onclick=\"pushState();duplicateSelected()\">🔄 Duplicate</button>";
  h+="<button class=\"pbtn\" onclick=\"pushState();deleteWidget("+w.id+")\">🗑 Delete</button>";
  h+="</div><div class=\"pbtn-row\">";
  h+="<button class=\"pbtn\" onclick=\"bringToFront("+w.id+")\">▲ To Front</button>";
  h+="<button class=\"pbtn\" onclick=\"sendToBack("+w.id+")\">▼ To Back</button>";
  h+="</div></div>";

  h+="<div class=\"pgroup\"><div class=\"pgt\">Colors</div>";
  const hasBg = w.props.hasOwnProperty("background_color");
  const hasFg = w.props.hasOwnProperty("color") || w.props.hasOwnProperty("foreground_color");

  if(hasBg){
    const bgVal = w.props.background_color || "transparent";
    const bgColorVal = bgVal==="transparent"?"#000000":bgVal;
    h+="<div class=\"prow\"><div class=\"plbl\">bg_color</div><input class=\"pinput\" type=\"color\" value=\""+bgColorVal+"\" onchange=\"uColor("+w.id+",&#39;background_color&#39;,this.value)\"><input class=\"pinput\" type=\"text\" value=\""+bgVal+"\" onchange=\"uColor("+w.id+",&#39;background_color&#39;,this.value)\" style=\"flex:1\"></div>";
  }
  if(w.props.hasOwnProperty("color")){
    const fgVal = w.props.color || "#e2e8f0";
    h+="<div class=\"prow\"><div class=\"plbl\">color</div><input class=\"pinput\" type=\"color\" value=\""+fgVal+"\" onchange=\"uColor("+w.id+",&#39;color&#39;,this.value)\"><input class=\"pinput\" type=\"text\" value=\""+fgVal+"\" onchange=\"uColor("+w.id+",&#39;color&#39;,this.value)\" style=\"flex:1\"></div>";
  }
  if(w.props.hasOwnProperty("foreground_color")){
    const fgVal = w.props.foreground_color || "#6b7280";
    h+="<div class=\"prow\"><div class=\"plbl\">fg_color</div><input class=\"pinput\" type=\"color\" value=\""+fgVal+"\" onchange=\"uColor("+w.id+",&#39;foreground_color&#39;,this.value)\"><input class=\"pinput\" type=\"text\" value=\""+fgVal+"\" onchange=\"uColor("+w.id+",&#39;foreground_color&#39;,this.value)\" style=\"flex:1\"></div>";
  }
  h+="</div>";

  h+="<div class=\"pgroup\"><div class=\"pgt\">Kivy Properties</div>";
  for(const[k,v] of Object.entries(w.props)){
    if(k==="background_color"||k==="color"||k==="foreground_color") continue;
    h+="<div class=\"prow\"><div class=\"plbl\">"+k+"</div><input class=\"pinput\" type=\"text\" value=\""+v+"\" onchange=\"uProp("+w.id+",&#39;"+k+"&#39;,this.value)\"></div>";
  }
  h+="</div></div>";
  document.getElementById("propsContent").innerHTML=h;
}
function prowPct(label,id,val,cb){
  return "<div class=\"prow\"><div class=\"plbl\">"+label+"</div><input class=\"pinput\" id=\""+id+"\" type=\"number\" step=\"0.1\" min=\"0\" max=\"100\" value=\""+val+"\" onchange=\""+cb+"\"><span class=\"pct-label\">%</span></div>";
}
window.uLay=(id,k,v)=>{
  const w=widgets.find(x=>x.id===id); if(!w) return;
  const n=(parseFloat(v)||0)/100;
  const ox=w.x, oy=w.y;
  if(k==="x")      w.x=Math.max(0,Math.min(n,1-w.width));
  else if(k==="y") w.y=Math.max(0,Math.min(n,1-w.height));
  else if(k==="width")  w.width =Math.max(0.05,n);
  else if(k==="height") w.height=Math.max(0.04,n);
  if(k==="x"||k==="y"){
    const ddx=w.x-ox, ddy=w.y-oy;
    w.childIds.forEach(cid=>{
      const cw=widgets.find(x=>x.id===cid); if(!cw) return;
      cw.x+=ddx; cw.y+=ddy;
      const cEl=document.getElementById("cw_"+cid);
      const size = document.getElementById("canvas").offsetWidth;
      if(cEl){cEl.style.left=(cw.x*size)+"px";cEl.style.top=(cw.y*size)+"px";}
    });
  }
  const el=document.getElementById("cw_"+id);
  const size = document.getElementById("canvas").offsetWidth;
  if(el){el.style.left=(w.x*size)+"px";el.style.top=(w.y*size)+"px";el.style.width=(w.width*size)+"px";el.style.height=(w.height*size)+"px";}
  refreshInner(w); updateSelInfo(w); generateCode();
  // Re-arrange children if this is a layout
  if(isLayout(w.type)) arrangeLayoutChildren(w.id);
};
window.uProp=(id,k,v)=>{
  const w=widgets.find(x=>x.id===id); if(!w) return;
  w.props[k]=v; refreshInner(w); generateCode();
  // If layout property changed, re-arrange children
  if(isLayout(w.type) && (k==="orientation" || k==="cols" || k==="spacing" || k==="padding")){
    arrangeLayoutChildren(w.id);
  }
};
window.uColor=(id,k,v)=>{
  const w=widgets.find(x=>x.id===id); if(!w) return;
  w.props[k]=v; refreshInner(w); generateCode();
};

// =====================================================
// DELETE / CLEAR
// =====================================================
window.deleteWidget=id=>{
  const w=widgets.find(x=>x.id===id); if(!w) return;
  if(w.parentId){
    const p=widgets.find(x=>x.id===w.parentId);
    if(p){p.childIds=p.childIds.filter(c=>c!==id); refreshLayoutPreview(p);}
  }
  [...w.childIds].forEach(cid=>deleteWidget(cid));
  widgets=widgets.filter(x=>x.id!==id);
  const el=document.getElementById("cw_"+id); if(el) el.remove();
  deselectAll(); updateHint(); generateCode();
};
window.clearCanvas=()=>{
  if(!widgets.length) return;
  pushState();
  widgets=[];
  document.querySelectorAll(".cv-widget").forEach(e=>e.remove());
  deselectAll(); updateHint(); generateCode();
  toast("Canvas cleared");
};
function updateHint(){
  const top=widgets.filter(w=>!w.parentId);
  document.getElementById("drophint").classList.toggle("hidden",widgets.length>0);
  document.getElementById("wcount").textContent=widgets.length+" widget"+(widgets.length!==1?"s":"")+" ("+top.length+" top-level)";
}

// =====================================================
// SAVE / LOAD
// =====================================================
function saveProject(){
  const data={version:3,widgets,idCounter,created:new Date().toISOString()};
  const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  a.download="kivy_designer_project.json";
  a.click();
  toast("Project saved");
}
function loadProject(){
  document.getElementById("fileInput").click();
}
function handleFileLoad(e){
  const file=e.target.files[0]; if(!file) return;
  const reader=new FileReader();
  reader.onload=ev=>{
    try{
      const data=JSON.parse(ev.target.result);
      if(!data.widgets){toast("Invalid project file");return;}
      pushState();
      widgets=data.widgets;
      idCounter=data.idCounter||widgets.reduce((m,w)=>Math.max(m,w.id),0)+1;
      rebuildAll();
      toast("Project loaded");
    }catch(err){toast("Error loading file");}
  };
  reader.readAsText(file);
  e.target.value="";
}
// =====================================================
// CODE GENERATION
// =====================================================
const KIVY_IMPORTS={
  Button:"from kivy.uix.button import Button",
  Label:"from kivy.uix.label import Label",
  TextInput:"from kivy.uix.textinput import TextInput",
  CheckBox:"from kivy.uix.checkbox import CheckBox",
  Slider:"from kivy.uix.slider import Slider",
  Switch:"from kivy.uix.switch import Switch",
  Spinner:"from kivy.uix.spinner import Spinner",
  ProgressBar:"from kivy.uix.progressbar import ProgressBar",
  Image:"from kivy.uix.image import Image",
  BoxLayout:"from kivy.uix.boxlayout import BoxLayout",
  GridLayout:"from kivy.uix.gridlayout import GridLayout",
  ScrollView:"from kivy.uix.scrollview import ScrollView",
};

function propLine(k,v){
  if(v === "transparent" || v === "" || v == null) return "";
  if(v.startsWith && v.startsWith("rgba(")) return "";
  if(BOOLPROPS.has(k)) return `            ${k}=${v},\n`;
  if(NUMPROPS.has(k)) return `            ${k}=${v},\n`;
  if(RAWPROPS.has(k)) return `            ${k}=${v},\n`;
  if(COLORPROPS.has(k)) return `            ${k}="${v}",\n`;
  return `            ${k}="${v}",\n`;
}

function widgetCode(w, indent, varSuffix){
  const vn=w.type.toLowerCase()+"_"+varSuffix;
  let c=indent+"# "+w.type+(w.parentId?" (child)":"")+"\n";
  c+=indent+vn+" = "+w.type+"(\n";
  for(const[k,v] of Object.entries(w.props)){
    c+=indent+"  "+propLine(k,v).trimStart();
  }
  // Only add pos_hint/size_hint for top-level widgets (not children inside layouts)
  if(!w.parentId){
    c+=indent+"  pos_hint={'x': "+w.x.toFixed(4)+", 'y': "+(1-w.y-w.height).toFixed(4)+"},\n";
    c+=indent+"  size_hint=("+w.width.toFixed(4)+", "+w.height.toFixed(4)+"),\n";
  }
  c+=indent+")\n";
  return {vn,code:c};
}

function buildCode(){
  const used=[...new Set(widgets.map(w=>w.type))];
  let c="from kivy.app import App\n";
  c+="from kivy.uix.floatlayout import FloatLayout\n";
  used.forEach(t=>{if(KIVY_IMPORTS[t])c+=KIVY_IMPORTS[t]+"\n";});
  c+="\n\nclass MyLayout(FloatLayout):\n";
  c+="    def __init__(self, **kwargs):\n";
  c+="        super().__init__(**kwargs)\n";
  if(!widgets.length){
    c+="        pass\n";
  } else {
    let idx=0;
    const varNames={};
    widgets.forEach(w=>{
      const {vn,code}=widgetCode(w,"        ",idx++);
      varNames[w.id]=vn;
      c+="\n"+code;
    });
    c+="\n";
    widgets.filter(w=>!w.parentId).forEach(w=>{
      c+="        self.add_widget("+varNames[w.id]+")\n";
    });
    widgets.filter(w=>w.parentId).forEach(w=>{
      c+="        "+varNames[w.parentId]+".add_widget("+varNames[w.id]+")\n";
    });
  }
  c+="\n\nclass MyApp(App):\n    def build(self):\n        return MyLayout()\n\n\n";
  c+="if __name__ == '__main__':\n    MyApp().run()\n";
  return c;
}

// =====================================================
// KV LANGUAGE GENERATION
// =====================================================
function buildKv(){
  if(!widgets.length) return "# No widgets on canvas\n";
  let kv="<MyLayout>:\n";

  function kvPropLine(k,v){
    if(v === "transparent" || v === "" || v == null) return "";
    if(v.startsWith && v.startsWith("rgba(")) return "";
    if(BOOLPROPS.has(k)) return `        ${k}: ${v}\n`;
    if(NUMPROPS.has(k)) return `        ${k}: ${v}\n`;
    if(RAWPROPS.has(k)) return `        ${k}: ${v}\n`;
    if(COLORPROPS.has(k)) return `        ${k}: "${v}"\n`;
    return `        ${k}: "${v}"\n`;
  }

  function indent(level){ return "    ".repeat(level); }

  function renderKvWidget(w, level){
    let s="";
    s+=indent(level)+w.type+":\n";
    // Only add pos_hint/size_hint for top-level widgets
    if(!w.parentId){
      s+=indent(level+1)+"pos_hint: {'x': "+w.x.toFixed(4)+", 'y': "+(1-w.y-w.height).toFixed(4)+"}\n";
      s+=indent(level+1)+"size_hint: "+w.width.toFixed(4)+", "+w.height.toFixed(4)+"\n";
    }
    for(const[k,v] of Object.entries(w.props)){
      s+=indent(level+1)+kvPropLine(k,v).trimStart();
    }
    const children=widgets.filter(c=>c.parentId===w.id);
    children.forEach(c=>{
      s+=renderKvWidget(c, level+1);
    });
    return s;
  }

  const topLevel=widgets.filter(w=>!w.parentId);
  topLevel.forEach(w=>{
    kv+=renderKvWidget(w, 1);
  });

  return kv;
}

function hl(code){
  return code
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    .replace(/\b(from|import|class|def|if|return|pass|__name__|__main__|True|False|None|self|super|pos_hint|size_hint|add_widget|build|run)\b/g,"<span class=\"kw\">$1</span>")
    .replace(/\b(App|FloatLayout|Button|Label|TextInput|CheckBox|Slider|Switch|Spinner|ProgressBar|Image|BoxLayout|GridLayout|ScrollView|MyLayout|MyApp)\b/g,"<span class=\"cls\">$1</span>")
    .replace(/(#[^\n]*)/g,"<span class=\"cm\">$1</span>")
    .replace(/('[^']*')/g,"<span class=\"str\">$1</span>")
    .replace(/\b(\d+\.?\d*)\b/g,"<span class=\"num\">$1</span>")
}
function generateCode(){
  document.getElementById("codePre").innerHTML=hl(buildCode());
  document.getElementById("kvPre").innerHTML=hl(buildKv());
}

// =====================================================
// UI ACTIONS
// =====================================================
window.toggleCode=()=>{
  const p=document.getElementById("codePanel");
  p.classList.toggle("collapsed");
  document.getElementById("codeToggle").textContent=p.classList.contains("collapsed")?"▼ Expand":"▲ Collapse";
  savePanelState();
};

window.switchCodeTab=(ev,tab)=>{
  ev.stopPropagation();
  currentCodeTab=tab;
  document.querySelectorAll(".code-tab").forEach(t=>t.classList.remove("active"));
  document.querySelectorAll(".code-body").forEach(b=>b.classList.remove("active"));
  document.getElementById("tab-"+tab).classList.add("active");
  document.getElementById("body-"+tab).classList.add("active");
};

window.exportPy=()=>{
  const code=buildCode();
  const blob=new Blob([code],{type:"text/x-python"});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  a.download="my_kivy_app.py";
  a.click();
  toast("Exported .py");
};

window.exportKv=()=>{
  const code=buildKv();
  const blob=new Blob([code],{type:"text/plain"});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  a.download="my_kivy_app.kv";
  a.click();
  toast("Exported .kv");
};

window.copyCode=()=>{
  const code=currentCodeTab==="py"?buildCode():buildKv();
  navigator.clipboard.writeText(code).then(()=>{
    toast("Code copied to clipboard!");
  }).catch(()=>{
    const ta=document.createElement("textarea");
    ta.value=code; document.body.appendChild(ta);
    ta.select(); document.execCommand("copy");
    document.body.removeChild(ta);
    toast("Code copied to clipboard!");
  });
};

// =====================================================
// INIT
// =====================================================
window.addEventListener("DOMContentLoaded", ()=>{
  setupResize(document.getElementById("pResize"), document.getElementById("palette"), 180, 380, "left");
  setupResize(document.getElementById("rResize"), document.getElementById("propsPanel"), 180, 380, "right");
  loadPanelState();
  fitCanvas();
  generateCode();
});

window.addEventListener("resize", ()=>{
  fitCanvas();
});

generateCode();
</script>

<!-- Developer Credit Footer -->
<div class="dev-footer">
  <span class="dev-name">👨‍💻 Developer: Husam Doughmosch</span>
  <span class="sep">|</span>
  <a href="https://www.linkedin.com/in/husam-doughmosch/" target="_blank" rel="noopener">🔗 LinkedIn</a>
  <span class="sep">|</span>
  <a href="https://x.com/HusamDoughmosch" target="_blank" rel="noopener">🐦 X (Twitter)</a>
  <span class="sep">|</span>
  <a href="https://github.com/Hdoughmosch" target="_blank" rel="noopener">🐙 GitHub</a>
</div>

</body>
</html>"""

@app.route("/")
def index():
    response.content_type = "text/html; charset=utf-8"
    return HTML

@app.route("/export", method="POST")
def export_py():
    data = request.json
    code = data.get("code", "")
    filename = data.get("filename", "my_kivy_app.py")
    response.content_type = "text/plain"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return code

if __name__ == "__main__":
    print("=" * 50)
    print("  Kivy UI Designer  v3.1 Layout Parenting")
    print("  Open: http://localhost:8080")
    print("  Press Ctrl+C to stop")
    print("=" * 50)
    run(app, host="localhost", port=8080, debug=True, reloader=False)
