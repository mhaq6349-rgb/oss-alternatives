(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- ledger prints in sequence, once ---------- */

  var rows = Array.prototype.slice.call(document.querySelectorAll(".lines tbody tr"));
  if (rows.length) {
    if (reduce) {
      rows.forEach(function (r) { r.style.opacity = 1; });
    } else {
      rows.forEach(function (row, i) {
        window.setTimeout(function () { row.classList.add("print"); }, 160 + i * 95);
      });
    }
  }

  /* ---------- running total counts up as rows enter view ---------- */

  var rail = document.getElementById("railTotal");
  if (rail && rows.length) {
    var running = 0;
    var shown = 0;
    var raf = null;

    var paint = function (from, to) {
      var start = performance.now();
      var dur = reduce ? 0 : 460;
      if (raf) cancelAnimationFrame(raf);
      var frame = function (now) {
        var t = dur === 0 ? 1 : Math.min(1, (now - start) / dur);
        var eased = 1 - Math.pow(1 - t, 3);
        shown = Math.round(from + (to - from) * eased);
        rail.textContent = "$" + shown.toLocaleString("en-US");
        if (t < 1) raf = requestAnimationFrame(frame);
      };
      raf = requestAnimationFrame(frame);
    };

    if ("IntersectionObserver" in window) {
      var seen = new WeakSet();
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting || seen.has(entry.target)) return;
          seen.add(entry.target);
          var save = parseInt(entry.target.getAttribute("data-save") || "0", 10);
          if (!save) return;
          var from = shown;
          running += save;
          paint(from, running);
        });
      }, { threshold: 0.6 });
      rows.forEach(function (r) { io.observe(r); });
    } else {
      running = rows.reduce(function (sum, r) {
        return sum + parseInt(r.getAttribute("data-save") || "0", 10);
      }, 0);
      rail.textContent = "$" + running.toLocaleString("en-US");
    }
  }

  /* ---------- calculator ---------- */

  var seats = document.getElementById("seats");
  var price = document.getElementById("price");
  var vendors = document.getElementById("vendors");

  if (seats && price && vendors) {
    var seatsOut = document.getElementById("seatsOut");
    var priceOut = document.getElementById("priceOut");
    var vendorsOut = document.getElementById("vendorsOut");
    var spendEl = document.getElementById("spend");
    var recoverEl = document.getElementById("recover");
    var beEl = document.getElementById("breakeven");
    var rangeText = document.getElementById("rangeText");

    var FEE = 900;
    var current = { spend: 0, recover: 0 };

    var rateFor = function (v) {
      if (v <= 3) return 0.18;
      if (v <= 6) return 0.28;
      return 0.34;
    };

    var money = function (n) {
      return "$" + Math.round(n).toLocaleString("en-US");
    };

    var tween = function (el, from, to) {
      if (reduce) { el.textContent = money(to); return; }
      var start = performance.now();
      var dur = 320;
      var frame = function (now) {
        var t = Math.min(1, (now - start) / dur);
        var eased = 1 - Math.pow(1 - t, 3);
        el.textContent = money(from + (to - from) * eased);
        if (t < 1) requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    };

    var fill = function (input) {
      var min = Number(input.min);
      var max = Number(input.max);
      var val = Number(input.value);
      input.style.setProperty("--fill", ((val - min) / (max - min)) * 100 + "%");
    };

    var update = function () {
      var s = Number(seats.value);
      var p = Number(price.value);
      var v = Number(vendors.value);

      seatsOut.textContent = s;
      priceOut.textContent = "$" + p;
      vendorsOut.textContent = v;

      fill(seats); fill(price); fill(vendors);

      var spend = s * p * 12 * v;
      var base = rateFor(v);
      var low = spend * Math.max(0.1, base - 0.06);
      var high = spend * (base + 0.06);
      var mid = (low + high) / 2;

      tween(spendEl, current.spend, spend);
      current.spend = spend;

      tween(recoverEl, current.recover, mid);
      current.recover = mid;
      rangeText.textContent = money(low) + "\u2013" + money(high);

      var multiple = mid / FEE;
      beEl.textContent = multiple >= 1
        ? Math.round(multiple) + "\u00d7 the fee"
        : "under the fee";
    };

    [seats, price, vendors].forEach(function (input) {
      input.addEventListener("input", update);
    });

    update();
  }
})();
