/* ---------------------------------------------------------------------------
   Site background — the WebGL version of body.bg-aurora.

   Raw WebGL on purpose. This runs on every page, and pulling a 3D engine in
   to draw one full-screen quad would cost ~170KB gzipped on a school site
   whose visitors are mostly on Nigerian mobile data. This file is ~3KB.

   The four colours are the CSS aurora's own washes, resolved against paper:
   they are what those rgba() layers already composite to, so this reads as a
   smoother version of the background rather than a new one.

   If anything here bails — reduced motion, save-data, a weak device, no
   WebGL — no canvas is added and body.bg-aurora::before stays visible. The
   CSS gradient is the fallback, not a thing to delete.
--------------------------------------------------------------------------- */
(function () {
  "use strict";

  var mq = window.matchMedia;
  if (mq && mq("(prefers-reduced-motion: reduce)").matches) return;

  var nav = navigator;
  var conn = nav.connection || nav.mozConnection || nav.webkitConnection;
  if (conn && (conn.saveData === true || /2g/.test(conn.effectiveType || ""))) return;
  if ((nav.deviceMemory || 8) < 4) return;
  if ((nav.hardwareConcurrency || 8) < 4) return;

  var canvas = document.createElement("canvas");
  canvas.className = "bg-webgl";
  canvas.setAttribute("aria-hidden", "true");

  var opts = { antialias: false, alpha: false, depth: false, stencil: false, powerPreference: "low-power" };
  var gl = canvas.getContext("webgl", opts) || canvas.getContext("experimental-webgl", opts);
  if (!gl) return;

  var VERT = [
    "attribute vec2 aPos;",
    "varying vec2 vUv;",
    "void main() {",
    "  vUv = aPos * 0.5 + 0.5;",
    "  gl_Position = vec4(aPos, 0.0, 1.0);",
    "}"
  ].join("\n");

  var FRAG = [
    "precision mediump float;",
    "varying vec2 vUv;",
    "uniform float uTime;",
    "uniform float uAspect;",
    "uniform vec3 c1;",
    "uniform vec3 c2;",
    "uniform vec3 c3;",
    "uniform vec3 c4;",
    "float blob(vec2 p, vec2 c, float r) {",
    "  return smoothstep(r, 0.0, length((p - c) * vec2(uAspect, 1.0)));",
    "}",
    "void main() {",
    "  vec2 p = vUv;",
    "  float t = uTime * 0.30;",
    /* One shared warp keeps the three washes moving as one field rather than
       as three independent blobs drifting past each other. */
    "  vec2 q = p + 0.13 * vec2(sin(t * 1.15 + p.y * 3.0), cos(t * 0.92 + p.x * 2.6));",
    "  float a = blob(q, vec2(0.14 + 0.19 * sin(t * 0.81), 0.10 + 0.16 * cos(t * 1.11)), 1.05);",
    "  float b = blob(q, vec2(0.90 + 0.17 * cos(t * 0.99), 0.26 + 0.18 * sin(t * 0.74)), 0.98);",
    "  float d = blob(q, vec2(0.22 + 0.19 * sin(t * 0.63 + 1.7), 0.90 + 0.15 * cos(t * 0.88)), 1.02);",
    "  vec3 col = c1;",
    "  col = mix(col, c2, a * 0.92);",
    "  col = mix(col, c3, b * 0.72);",
    "  col = mix(col, c4, d * 0.78);",
    /* A little grain stops wide flat washes from banding on 8-bit screens. */
    "  float g = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);",
    "  col += (g - 0.5) * 0.013;",
    "  gl_FragColor = vec4(col, 1.0);",
    "}"
  ].join("\n");

  function compile(type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { gl.deleteShader(s); return null; }
    return s;
  }

  var vs = compile(gl.VERTEX_SHADER, VERT);
  var fs = compile(gl.FRAGMENT_SHADER, FRAG);
  if (!vs || !fs) return;

  var prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
  gl.useProgram(prog);

  /* One oversized triangle covers the viewport with no seam down the middle. */
  var buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var aPos = gl.getAttribLocation(prog, "aPos");
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

  function rgb(hex) {
    return [
      ((hex >> 16) & 255) / 255,
      ((hex >> 8) & 255) / 255,
      (hex & 255) / 255
    ];
  }

  var uTime = gl.getUniformLocation(prog, "uTime");
  var uAspect = gl.getUniformLocation(prog, "uAspect");
  gl.uniform3fv(gl.getUniformLocation(prog, "c1"), rgb(0xFBF3E7)); /* paper */
  gl.uniform3fv(gl.getUniformLocation(prog, "c2"), rgb(0xF0D9AC)); /* gold over paper */
  gl.uniform3fv(gl.getUniformLocation(prog, "c3"), rgb(0xD7BCB7)); /* indigo over paper */
  gl.uniform3fv(gl.getUniformLocation(prog, "c4"), rgb(0xD9CAB9)); /* sage over paper */

  document.body.appendChild(canvas);
  document.body.classList.add("webgl-bg");

  var dpr = Math.min(window.devicePixelRatio || 1, 1.5);

  function resize() {
    var w = Math.max(1, Math.round(window.innerWidth * dpr));
    var h = Math.max(1, Math.round(window.innerHeight * dpr));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
      gl.viewport(0, 0, w, h);
      gl.uniform1f(uAspect, w / h);
    }
  }
  window.addEventListener("resize", resize);
  resize();

  /* Stop drawing while the tab is hidden or the context is gone. */
  var running = true;
  canvas.addEventListener("webglcontextlost", function (e) {
    e.preventDefault();
    running = false;
    document.body.classList.remove("webgl-bg");
  });

  var start = 0;
  var last = 0;
  function frame(now) {
    if (!running) return;
    /* Re-schedule first. Returning before this on a hidden frame would end
       the loop for good, and the canvas would sit on its cleared black. */
    requestAnimationFrame(frame);
    if (document.hidden) return;
    /* Hold time still across a hidden stretch so the field doesn't jump. */
    if (!start) { start = now; last = now; }
    start += now - last;
    last = now;
    resize();
    gl.uniform1f(uTime, (now - start) / 1000);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
  requestAnimationFrame(frame);
})();
