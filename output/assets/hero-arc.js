/* ---------------------------------------------------------------------------
   Homepage hero — the arc, in three dimensions.

   Replaces the flat SVG arc with the same curve swept through space, carrying
   the three stages as objects a child actually meets in order: an alphabet
   block for Nursery, an open book for Primary, a mortarboard for Secondary.

   Things worth knowing before editing:

   - The curve is the SVG's own path, "M20 190 C 90 60, 310 60, 380 190",
     mapped out of its 400x220 viewBox. Change one and change the other, or
     the fallback stops matching what it falls back from.
   - Each object leans by a *fraction* of the curve's tangent angle. Aligning
     fully tips the end pieces past 50 degrees and they read as fallen over.
   - The camera is fitted to the scene that was actually built, so rescaling a
     piece can't quietly push it out of frame.
   - The travelling gold sun is the same motif the SVG already animates along
     the path. It carries a point light, so it lights each piece as it passes.
   - Navigation does not live in here. The three .arc-caption links below the
     canvas are the real navigation and are untouched, so keyboard and screen
     reader users are unaffected whether or not any of this runs. Clicking the
     3D objects is a convenience on top.
--------------------------------------------------------------------------- */
(function () {
  "use strict";

  if (!window.THREE) return;

  var wrap = document.querySelector(".arc-wrap");
  if (!wrap) return;

  var mq = window.matchMedia;
  if (mq && mq("(prefers-reduced-motion: reduce)").matches) return;

  var nav = navigator;
  var conn = nav.connection || nav.mozConnection || nav.webkitConnection;
  if (conn && (conn.saveData === true || /2g/.test(conn.effectiveType || ""))) return;
  if ((nav.deviceMemory || 8) < 4) return;
  if ((nav.hardwareConcurrency || 8) < 4) return;

  /* Width is the one condition that changes after load. Checking it once meant
     a window opened narrow and then maximised never got the arc at all. */
  function wideEnough() {
    return !(mq && mq("(max-width: 860px)").matches);
  }

  function build() {
    var T = window.THREE;

    var COL = {
      indigo:   0x6E1E2E,
      gold:     0xD9A73B,
      goldSoft: 0xF0CE86,
      paper:    0xFBF3E7
    };

    var ASPECT = 2.0;

    /* ---------- the curve ----------------------------------------------- */

    /* viewBox 400x220 -> world. SVG y grows downward, so it is flipped.
       z bows the arc toward the viewer at its crown; without it the arc is a
       flat ribbon and reads as a drawing that happens to have lighting. */
    function pt(x, y, z) {
      return new T.Vector3((x - 200) / 100, -(y - 125) / 100, z);
    }

    var curve = new T.CubicBezierCurve3(
      pt(20, 190, -0.26),
      pt(90, 60, 0.34),
      pt(310, 60, 0.34),
      pt(380, 190, -0.26)
    );

    /* In-plane normal, pointing away from the arch's centre. Stands the pieces
       off the curve instead of lifting them on world Y, which would leave the
       end pieces floating beside the line rather than sitting on it. */
    function normalAt(t) {
      var tan = curve.getTangentAt(t);
      var n = new T.Vector3(-tan.y, tan.x, 0);
      if (n.y < 0) n.negate();
      return n.normalize();
    }

    function leanAt(t) {
      var tan = curve.getTangentAt(t);
      return Math.atan2(tan.y, tan.x) * 0.18;
    }

    /* ---------- scene ---------------------------------------------------- */

    var canvas = document.createElement("canvas");
    canvas.className = "arc-canvas";
    canvas.setAttribute("aria-hidden", "true");

    var renderer;
    try {
      renderer = new T.WebGLRenderer({
        canvas: canvas,
        antialias: true,
        alpha: true,
        powerPreference: "low-power"
      });
    } catch (e) {
      return;
    }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    renderer.outputColorSpace = T.SRGBColorSpace;

    var scene = new T.Scene();
    var camera = new T.PerspectiveCamera(30, ASPECT, 0.1, 60);

    scene.add(new T.AmbientLight(0xffffff, 0.62));

    var key = new T.DirectionalLight(0xFFF6E8, 2.0);
    key.position.set(2.6, 3.4, 4.2);
    scene.add(key);

    var rim = new T.DirectionalLight(COL.goldSoft, 1.0);
    rim.position.set(-3.6, 1.4, -2.4);
    scene.add(rim);

    var bounce = new T.DirectionalLight(COL.indigo, 0.5);
    bounce.position.set(-1.0, -2.6, 1.6);
    scene.add(bounce);

    var root = new T.Group();
    scene.add(root);

    /* Content sits one level in so it can be re-centred once its true size is
       known; root keeps doing the rotating. */
    var stage = new T.Group();
    root.add(stage);

    function mat(hex, rough, metal) {
      return new T.MeshStandardMaterial({
        color: hex,
        roughness: rough === undefined ? 0.55 : rough,
        metalness: metal === undefined ? 0.06 : metal
      });
    }

    /* ---------- the arc itself ------------------------------------------- */

    stage.add(new T.Mesh(
      new T.TubeGeometry(curve, 320, 0.023, 16, false),
      mat(COL.indigo, 0.52, 0.10)
    ));

    /* Round ends, matching the SVG's stroke-linecap="round". */
    [0, 1].forEach(function (t) {
      var cap = new T.Mesh(new T.SphereGeometry(0.023, 20, 14), mat(COL.indigo, 0.52, 0.10));
      cap.position.copy(curve.getPointAt(t));
      stage.add(cap);
    });

    /* ---------- pieces --------------------------------------------------- */

    /* A rounded cube, made by pushing a sphere out to a superellipsoid. The
       core library has no RoundedBoxGeometry, and a hard-edged cube is the one
       shape here that reads as "computer graphics" rather than "toy". */
    function roundedBox(size, roundness, material) {
      var geo = new T.SphereGeometry(1, 64, 48);
      var pos = geo.attributes.position;
      var v = new T.Vector3();
      for (var i = 0; i < pos.count; i++) {
        v.fromBufferAttribute(pos, i).normalize();
        var d = Math.pow(
          Math.pow(Math.abs(v.x), roundness) +
          Math.pow(Math.abs(v.y), roundness) +
          Math.pow(Math.abs(v.z), roundness),
          -1 / roundness
        );
        pos.setXYZ(i, v.x * d * size, v.y * d * size, v.z * d * size);
      }
      geo.computeVertexNormals();
      return new T.Mesh(geo, material);
    }

    function letterDecal(ch, size) {
      var s = 256;
      var cv = document.createElement("canvas");
      cv.width = cv.height = s;
      var g = cv.getContext("2d");
      g.clearRect(0, 0, s, s);
      g.fillStyle = "#6E1E2E";
      g.font = "600 168px Fraunces, Georgia, serif";
      g.textAlign = "center";
      g.textBaseline = "middle";
      g.fillText(ch, s / 2, s / 2 + 10);

      var tex = new T.CanvasTexture(cv);
      tex.colorSpace = T.SRGBColorSpace;
      tex.anisotropy = 4;

      return new T.Mesh(
        new T.PlaneGeometry(size, size),
        new T.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false })
      );
    }

    function alphabetBlock() {
      var g = new T.Group();
      g.add(roundedBox(0.30, 7, mat(COL.goldSoft, 0.68, 0.02)));

      /* Letters as decals rather than a cube texture — the superellipsoid
         carries spherical UVs, which would smear a face texture. */
      var front = letterDecal("A", 0.30);
      front.position.z = 0.301;
      g.add(front);

      var right = letterDecal("B", 0.30);
      right.position.x = 0.301;
      right.rotation.y = Math.PI / 2;
      g.add(right);

      var top = letterDecal("C", 0.30);
      top.position.y = 0.301;
      top.rotation.x = -Math.PI / 2;
      g.add(top);

      return g;
    }

    function openBook() {
      var g = new T.Group();
      var cover = mat(COL.indigo, 0.60, 0.03);
      var paper = mat(COL.paper, 0.88, 0.0);

      [-1, 1].forEach(function (side) {
        var half = new T.Group();
        var c = new T.Mesh(new T.BoxGeometry(0.46, 0.035, 0.60), cover);
        var pg = new T.Mesh(new T.BoxGeometry(0.42, 0.042, 0.55), paper);
        pg.position.y = 0.037;
        half.add(c, pg);
        half.position.x = side * 0.235;
        half.rotation.z = side * -0.20;
        g.add(half);
      });

      var spine = new T.Mesh(
        new T.CylinderGeometry(0.035, 0.035, 0.60, 16, 1, false, 0, Math.PI), cover);
      spine.rotation.z = Math.PI / 2;
      spine.rotation.y = Math.PI / 2;
      spine.position.y = 0.012;
      g.add(spine);

      /* Ribbon marker — the one place gold appears on this piece. */
      var ribbon = new T.Mesh(new T.BoxGeometry(0.03, 0.006, 0.34), mat(COL.gold, 0.5, 0.25));
      ribbon.position.set(0.05, 0.06, 0.18);
      ribbon.rotation.x = 0.16;
      g.add(ribbon);

      /* Positive X tilts the top toward a camera on +Z. Negative shows the
         reader the underside, which is what this did for a while. */
      g.rotation.x = 0.55;
      return g;
    }

    function mortarboard() {
      var g = new T.Group();
      var cloth = mat(COL.indigo, 0.66, 0.04);

      var crown = new T.Mesh(new T.CylinderGeometry(0.175, 0.205, 0.16, 48), cloth);
      crown.position.y = -0.075;
      g.add(crown);

      var board = new T.Mesh(new T.BoxGeometry(0.62, 0.028, 0.62), cloth);
      board.position.y = 0.022;
      board.rotation.y = Math.PI / 4;
      g.add(board);

      var button = new T.Mesh(new T.SphereGeometry(0.030, 20, 14), mat(COL.gold, 0.34, 0.62));
      button.position.y = 0.048;
      g.add(button);

      /* The tassel hangs on a curve. A straight cylinder for a cord is the
         detail that gives the whole piece away as untouched by hand. */
      var cordMat = mat(COL.gold, 0.46, 0.34);
      var cordCurve = new T.QuadraticBezierCurve3(
        new T.Vector3(0, 0.045, 0),
        new T.Vector3(0.24, 0.035, 0.24),
        new T.Vector3(0.30, -0.26, 0.30)
      );
      g.add(new T.Mesh(new T.TubeGeometry(cordCurve, 40, 0.008, 8, false), cordMat));

      var bundle = new T.Mesh(new T.CylinderGeometry(0.026, 0.042, 0.15, 14), cordMat);
      bundle.position.set(0.30, -0.335, 0.30);
      g.add(bundle);

      /* Tip the board toward the viewer — flat on, it is an unreadable edge. */
      g.rotation.x = 0.40;
      return g;
    }

    /* ---------- place them on the arc ------------------------------------ */

    var STAGES = [
      { t: 0.045, href: "#nursery",   make: alphabetBlock, stand: 0.46 },
      { t: 0.500, href: "#primary",   make: openBook,      stand: 0.30 },
      { t: 0.955, href: "#secondary", make: mortarboard,   stand: 0.34 }
    ];

    var SCALE = 1.45;

    var pieces = STAGES.map(function (s, i) {
      var pivot = new T.Group();
      var base = curve.getPointAt(s.t).clone().addScaledVector(normalAt(s.t), s.stand);
      pivot.position.copy(base);
      pivot.rotation.z = leanAt(s.t);

      var inner = new T.Group();
      inner.add(s.make());
      inner.scale.setScalar(SCALE);
      pivot.add(inner);
      stage.add(pivot);

      return {
        pivot: pivot,
        inner: inner,
        baseY: base.y,
        href: s.href,
        phase: i * 2.1,
        hover: 0
      };
    });

    /* ---------- the travelling sun --------------------------------------- */

    var sun = new T.Mesh(
      new T.SphereGeometry(0.048, 24, 16),
      new T.MeshBasicMaterial({ color: COL.gold })
    );
    sun.add(new T.Mesh(
      new T.SphereGeometry(0.115, 20, 14),
      new T.MeshBasicMaterial({
        color: COL.goldSoft, transparent: true, opacity: 0.22, depthWrite: false
      })
    ));
    sun.add(new T.PointLight(COL.gold, 2.2, 2.4, 2));
    stage.add(sun);

    /* ---------- frame it -------------------------------------------------- */

    /* Fitted to what was actually built, with room for the idle sway, the
       hover scale and the parallax. Hand-set camera distances kept clipping
       the end pieces every time something was rescaled. */
    var box = new T.Box3().setFromObject(stage);
    var centre = box.getCenter(new T.Vector3());
    var size = box.getSize(new T.Vector3());

    stage.position.sub(centre);

    var halfFov = (camera.fov * Math.PI / 180) / 2;
    var forHeight = (size.y / 2) / Math.tan(halfFov);
    var forWidth = (size.x / 2) / (Math.tan(halfFov) * ASPECT);

    camera.position.set(0, 0, Math.max(forHeight, forWidth) * 1.08 + size.z * 0.4);
    camera.lookAt(0, 0, 0);

    /* ---------- pointer --------------------------------------------------- */

    var ray = new T.Raycaster();
    var ndc = new T.Vector2(-2, -2);
    var parallax = new T.Vector2(0, 0);
    var hovered = null;

    wrap.addEventListener("pointermove", function (e) {
      var r = canvas.getBoundingClientRect();
      if (!r.width || !r.height) return;
      ndc.x = ((e.clientX - r.left) / r.width) * 2 - 1;
      ndc.y = -((e.clientY - r.top) / r.height) * 2 + 1;
      parallax.set(ndc.x, ndc.y);
    });

    wrap.addEventListener("pointerleave", function () {
      ndc.set(-2, -2);
      parallax.set(0, 0);
    });

    canvas.addEventListener("click", function () {
      if (hovered) window.location.hash = hovered.href;
    });

    /* ---------- loop ------------------------------------------------------ */

    function resize() {
      var r = wrap.getBoundingClientRect();
      var w = Math.max(1, Math.round(r.width));
      var h = Math.max(1, Math.round(w / ASPECT));
      canvas.style.height = h + "px";
      renderer.setSize(w, h, false);
    }

    var clock = new T.Clock();
    var elapsed = 0;
    var alive = true;

    canvas.addEventListener("webglcontextlost", function (e) {
      e.preventDefault();
      alive = false;
      wrap.classList.remove("webgl-arc");
    });

    function frame() {
      if (!alive) return;
      /* Re-schedule first: bailing before this on a hidden frame would end the
         loop for good. */
      requestAnimationFrame(frame);
      if (document.hidden) return;
      /* Under 860px the CSS hides this canvas and shows the SVG again. */
      if (canvas.offsetParent === null) return;

      elapsed += Math.min(clock.getDelta(), 0.05);
      resize();

      /* The group breathes rather than spins. A continuous rotation beside a
         headline pulls the eye off the words. */
      root.rotation.y = Math.sin(elapsed * 0.22) * 0.085 + parallax.x * 0.075;
      root.rotation.x = Math.sin(elapsed * 0.17) * 0.045 - parallax.y * 0.05;

      /* Sun runs 0 -> 1 -> 0, eased at the turns, matching the SVG's 6s loop. */
      var cycle = (elapsed % 6) / 6;
      var st = cycle < 0.5 ? cycle * 2 : (1 - cycle) * 2;
      st = st * st * (3 - 2 * st);
      sun.position.copy(curve.getPointAt(Math.min(0.999, Math.max(0.001, st))));

      ray.setFromCamera(ndc, camera);
      var hit = null;
      for (var i = 0; i < pieces.length; i++) {
        if (ray.intersectObject(pieces[i].inner, true).length) { hit = pieces[i]; break; }
      }
      hovered = hit;
      canvas.style.cursor = hit ? "pointer" : "";

      for (var j = 0; j < pieces.length; j++) {
        var pc = pieces[j];
        pc.hover += ((pc === hit ? 1 : 0) - pc.hover) * 0.12;
        pc.pivot.position.y = pc.baseY +
          Math.sin(elapsed * 0.62 + pc.phase) * 0.022 + pc.hover * 0.035;
        pc.inner.scale.setScalar(SCALE * (1 + pc.hover * 0.09));
        pc.inner.rotation.y = Math.sin(elapsed * 0.30 + pc.phase) * 0.20;
      }

      renderer.render(scene, camera);
    }

    /* Insert above .arc-caption, or hiding the SVG leaves the stage labels
       sitting on top of the arc instead of under it. */
    var caption = wrap.querySelector(".arc-caption");
    if (caption) wrap.insertBefore(canvas, caption);
    else wrap.appendChild(canvas);

    wrap.classList.add("webgl-arc");
    resize();
    requestAnimationFrame(frame);
  }

  if (wideEnough()) {
    build();
  } else {
    var waitForWidth = function () {
      if (!wideEnough()) return;
      window.removeEventListener("resize", waitForWidth);
      build();
    };
    window.addEventListener("resize", waitForWidth);
  }
})();
