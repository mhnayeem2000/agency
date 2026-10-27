/* ==========================================================================
   Bright Abroad China — front-end behaviours (vanilla JS, no dependencies)
   Sliders · type animation · counters · media fallbacks · mobile app shell
   ========================================================================== */
(function () {
    "use strict";

    var doc = document;
    var reduceMotion = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    var FALLBACK_IMAGE = window.AGENCY_MEDIA_FALLBACK || "";
    var ICON_PREV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>';
    var ICON_NEXT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>';
    var HERO_IMAGES = [
        { src: "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ef/Tsinghua_University_campus_1.jpg/960px-Tsinghua_University_campus_1.jpg", name: "Tsinghua University, Beijing" },
        { src: "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/0f/Campus_No.3%2C_Peking_University%2C_Gate.jpg/960px-Campus_No.3%2C_Peking_University%2C_Gate.jpg", name: "Peking University, Beijing" },
        { src: "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2d/Fudan_University_Jiangwan_Campus.jpg/960px-Fudan_University_Jiangwan_Campus.jpg", name: "Fudan University, Shanghai" },
        { src: "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/9c/After_snow_-_International_Campus%2C_Zhejiang_University.png/960px-After_snow_-_International_Campus%2C_Zhejiang_University.png", name: "Zhejiang University International Campus, Haining" },
        { src: "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/10/A_panorama_of_Shanghai_Jiao_Tong_University_school_campus.jpg/960px-A_panorama_of_Shanghai_Jiao_Tong_University_school_campus.jpg", name: "Shanghai Jiao Tong University" },
        { src: "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/45/Wuhan_University_Gate_Info_Campus_2014.jpg/960px-Wuhan_University_Gate_Info_Campus_2014.jpg", name: "Wuhan University" },
        { src: "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5e/Nanjing_University_Gulou_Campus_2010-11.jpg/960px-Nanjing_University_Gulou_Campus_2010-11.jpg", name: "Nanjing University, Gulou Campus" },
        { src: "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/55/Guangzhou_South_Campus%2C_Sun_Yat-sen_University.jpg/960px-Guangzhou_South_Campus%2C_Sun_Yat-sen_University.jpg", name: "Sun Yat-sen University, Guangzhou" },
        { src: "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b7/20220522_Longzihu_Campus_of_Henan_University_of_Chinese_Medicine_01.jpg/960px-20220522_Longzihu_Campus_of_Henan_University_of_Chinese_Medicine_01.jpg", name: "Henan University of Chinese Medicine, Zhengzhou" },
        { src: "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/42/%28CHN-Fujian%29_Xiamen_University_Siming_Campus_West_Gate_2025-03-20.jpg/960px-%28CHN-Fujian%29_Xiamen_University_Siming_Campus_West_Gate_2025-03-20.jpg", name: "Xiamen University, Siming Campus" }
    ];

    /* ------------------------------------------------------------------ *
     * 1. Remote image guard — swap in a local placeholder, then a gradient
     * ------------------------------------------------------------------ */
    function markFallback(img) {
        var holder = img.closest ? img.closest(".media") : null;
        if (holder) {
            holder.classList.add("is-fallback");
        } else {
            img.style.visibility = "hidden";
        }
    }

    function guardImage(img) {
        function fail() {
            if (img.dataset.mediaState === "placeholder" || !FALLBACK_IMAGE) {
                markFallback(img);
                return;
            }
            img.dataset.mediaState = "placeholder";
            img.src = FALLBACK_IMAGE;
        }

        img.addEventListener("error", function () {
            img.dataset.mediaState = "failed";
            fail();
        });

        if (img.complete && img.naturalWidth === 0) {
            fail();
        }
    }

    /* ------------------------------------------------------------------ *
     * 2. Slider engine — scroll-snap track + arrows + dots + autoplay
     * ------------------------------------------------------------------ */
    function initInfiniteSlider(root, track, slides, prevBtn, nextBtn, mobileOnly) {
        var direction = root.dataset.sliderLoop === "right" ? -1 : 1;
        var speed = parseFloat(root.dataset.sliderSpeed || "35");
        var clones = [];
        var cycleWidth = 0;
        var active = false;
        var visible = true;
        var paused = reduceMotion;
        var frame = 0;
        var position = 0;
        var lastFrameTime = 0;
        var resizeTimer = null;
        var moveTimer = null;
        var observer = null;
        var mobileQuery = window.matchMedia("(max-width: 780px)");

        function canRun() {
            return !mobileOnly || mobileQuery.matches;
        }

        function tick(time) {
            frame = 0;
            if (!active || paused || !visible || document.hidden) {
                lastFrameTime = 0;
                return;
            }
            if (lastFrameTime) {
                var elapsed = Math.min(time - lastFrameTime, 50);
                position += direction * speed * elapsed / 1000;
                if (direction > 0 && position >= cycleWidth * 2) {
                    position -= cycleWidth;
                } else if (direction < 0 && position < cycleWidth) {
                    position += cycleWidth;
                }
                track.scrollLeft = position;
            }
            lastFrameTime = time;
            frame = window.requestAnimationFrame(tick);
        }

        function play() {
            if (!frame && !moveTimer && active && !paused && visible && !document.hidden) {
                position = track.scrollLeft;
                frame = window.requestAnimationFrame(tick);
            }
        }

        function stop() {
            if (frame) {
                window.cancelAnimationFrame(frame);
                frame = 0;
            }
            lastFrameTime = 0;
            position = track.scrollLeft;
        }

        function removeClones() {
            clones.forEach(function (clone) { clone.remove(); });
            clones = [];
            active = false;
            cycleWidth = 0;
            window.clearTimeout(moveTimer);
            moveTimer = null;
            root.classList.remove("slider--infinite");
            track.scrollLeft = 0;
            position = 0;
            stop();
        }

        function start() {
            if (active || !canRun()) { return; }
            track.style.paddingRight = "";
            function createCloneGroup() {
                return slides.map(function (slide) {
                    var clone = slide.cloneNode(true);
                    clone.setAttribute("aria-hidden", "true");
                    Array.prototype.forEach.call(
                        clone.querySelectorAll("a, button, input, select, textarea, [tabindex]"),
                        function (element) { element.setAttribute("tabindex", "-1"); }
                    );
                    return clone;
                });
            }
            function appendCloneGroup(group) {
                group.forEach(function (clone) { track.appendChild(clone); });
            }
            function prependCloneGroup(group) {
                var fragment = document.createDocumentFragment();
                group.forEach(function (clone) { fragment.appendChild(clone); });
                track.insertBefore(fragment, track.firstChild);
            }

            var afterGroup = createCloneGroup();
            appendCloneGroup(afterGroup);
            cycleWidth = afterGroup[0].offsetLeft - slides[0].offsetLeft;
            if (!(cycleWidth > 0)) {
                afterGroup.forEach(function (clone) { clone.remove(); });
                removeClones();
                return;
            }
            var coverageGroups = Math.max(1, Math.ceil(track.clientWidth / cycleWidth));
            clones = afterGroup.slice();
            for (var groupIndex = 1; groupIndex < coverageGroups; groupIndex += 1) {
                var nextGroup = createCloneGroup();
                appendCloneGroup(nextGroup);
                clones = clones.concat(nextGroup);
            }
            for (var beforeIndex = 0; beforeIndex < coverageGroups; beforeIndex += 1) {
                var previousGroup = createCloneGroup();
                prependCloneGroup(previousGroup);
                clones = clones.concat(previousGroup);
            }
            root.classList.add("slider--infinite");
            active = true;
            track.scrollLeft = cycleWidth;
            position = track.scrollLeft;
            play();
        }

        function restartForViewport() {
            if (active) { removeClones(); }
            start();
        }

        function move(step) {
            if (!active) { return; }
            var gap = parseFloat(window.getComputedStyle(track).columnGap) || 0;
            var distance = slides[0].getBoundingClientRect().width + gap;
            var target = track.scrollLeft + step * distance;
            stop();
            track.scrollTo({
                left: target,
                behavior: reduceMotion ? "auto" : "smooth"
            });
            window.clearTimeout(moveTimer);
            moveTimer = window.setTimeout(function () {
                moveTimer = null;
                var current = track.scrollLeft;
                if (current < cycleWidth) {
                    current += cycleWidth;
                } else if (current >= cycleWidth * 2) {
                    current -= cycleWidth;
                }
                track.scrollLeft = current;
                position = current;
                play();
            }, reduceMotion ? 0 : 450);
        }

        if (prevBtn) {
            prevBtn.addEventListener("click", function () { move(-1); });
        }
        if (nextBtn) {
            nextBtn.addEventListener("click", function () { move(1); });
        }

        root.addEventListener("pointerenter", function () { paused = true; stop(); });
        root.addEventListener("pointerleave", function () { paused = reduceMotion; play(); });
        root.addEventListener("focusin", function () { paused = true; stop(); });
        root.addEventListener("focusout", function (event) {
            if (!root.contains(event.relatedTarget)) {
                paused = reduceMotion;
                play();
            }
        });
        root.addEventListener("touchstart", function () { paused = true; stop(); }, { passive: true });
        root.addEventListener("touchend", function () {
            window.setTimeout(function () { paused = reduceMotion; play(); }, 900);
        }, { passive: true });
        document.addEventListener("visibilitychange", function () {
            if (document.hidden) { stop(); } else { play(); }
        });

        if ("IntersectionObserver" in window) {
            observer = new IntersectionObserver(function (entries) {
                visible = entries[0].isIntersecting;
                if (visible) { play(); } else { stop(); }
            });
            observer.observe(root);
        }

        if (mobileQuery.addEventListener) {
            mobileQuery.addEventListener("change", restartForViewport);
        } else {
            mobileQuery.addListener(restartForViewport);
        }
        window.addEventListener("resize", function () {
            window.clearTimeout(resizeTimer);
            resizeTimer = window.setTimeout(restartForViewport, 120);
        }, { passive: true });

        start();
    }

    function initSlider(root) {
        var track = root.querySelector("[data-slider-track]");
        if (!track || !track.children.length) {
            return;
        }

        var slides = Array.prototype.slice.call(track.children);
        var navHost = root.dataset.sliderNav ? doc.querySelector(root.dataset.sliderNav) : null;
        var dotsHost = root.querySelector("[data-slider-dots]");
        var autoplayMs = parseInt(root.dataset.sliderAutoplay || "0", 10);
        var mobileOnly = root.hasAttribute("data-slider-mobile-only");

        if (navHost && !navHost.children.length) {
            navHost.innerHTML =
                '<button class="slider-btn" type="button" data-slider-prev aria-label="Previous">' + ICON_PREV + "</button>" +
                '<button class="slider-btn" type="button" data-slider-next aria-label="Next">' + ICON_NEXT + "</button>";
        }

        var prevBtn = root.querySelector("[data-slider-prev]") || (navHost && navHost.querySelector("[data-slider-prev]"));
        var nextBtn = root.querySelector("[data-slider-next]") || (navHost && navHost.querySelector("[data-slider-next]"));

        if (root.dataset.sliderLoop) {
            initInfiniteSlider(root, track, slides, prevBtn, nextBtn, mobileOnly);
            return;
        }

        if (dotsHost && !dotsHost.children.length && slides.length > 1) {
            dotsHost.innerHTML = slides
                .map(function (slide, index) {
                    return '<button class="slider-dot" type="button" data-slider-dot="' + index + '" aria-label="Go to item ' + (index + 1) + '"></button>';
                })
                .join("");
        }

        var dots = dotsHost ? Array.prototype.slice.call(dotsHost.children) : [];

        function updateEndPadding() {
            if (mobileOnly && !window.matchMedia("(max-width: 780px)").matches) {
                track.style.paddingRight = "";
                return;
            }
            var styles = window.getComputedStyle(track);
            var leftPadding = parseFloat(styles.paddingLeft) || 0;
            var firstSlideWidth = slides[0].getBoundingClientRect().width;
            track.style.paddingRight = Math.max(
                0,
                track.clientWidth - firstSlideWidth - leftPadding
            ) + "px";
        }

        function slideOffset(index) {
            var trackLeft = track.getBoundingClientRect().left + track.clientLeft;
            var leftPadding = parseFloat(window.getComputedStyle(track).paddingLeft) || 0;
            return slides[index].getBoundingClientRect().left - trackLeft + track.scrollLeft - leftPadding;
        }

        function currentIndex() {
            var nearest = 0;
            var nearestDistance = Infinity;
            slides.forEach(function (slide, index) {
                var distance = Math.abs(slideOffset(index) - track.scrollLeft);
                if (distance < nearestDistance) {
                    nearest = index;
                    nearestDistance = distance;
                }
            });
            return nearest;
        }

        function goTo(index) {
            var last = slides.length - 1;
            var target = index > last ? 0 : (index < 0 ? last : index);
            track.scrollTo({ left: slideOffset(target), behavior: reduceMotion ? "auto" : "smooth" });
        }

        function sync() {
            var active = currentIndex();
            dots.forEach(function (dot, index) {
                var isActive = index === active;
                dot.classList.toggle("is-active", isActive);
                dot.setAttribute("aria-current", isActive ? "true" : "false");
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener("click", function () { goTo(currentIndex() - 1); });
        }
        if (nextBtn) {
            nextBtn.addEventListener("click", function () { goTo(currentIndex() + 1); });
        }
        dots.forEach(function (dot, index) {
            dot.addEventListener("click", function () { goTo(index); });
        });

        track.setAttribute("tabindex", "0");
        track.addEventListener("keydown", function (event) {
            if (event.key === "ArrowRight") { event.preventDefault(); goTo(currentIndex() + 1); }
            if (event.key === "ArrowLeft") { event.preventDefault(); goTo(currentIndex() - 1); }
        });

        var framePending = false;
        track.addEventListener("scroll", function () {
            if (framePending) { return; }
            framePending = true;
            window.requestAnimationFrame(function () { framePending = false; sync(); });
        }, { passive: true });

        updateEndPadding();
        window.addEventListener("resize", updateEndPadding, { passive: true });

        /* desktop drag-to-scroll */
        var isDown = false;
        var startX = 0;
        var startScroll = 0;
        var dragged = false;

        track.addEventListener("pointerdown", function (event) {
            if (event.pointerType !== "mouse") { return; }
            isDown = true;
            dragged = false;
            startX = event.clientX;
            startScroll = track.scrollLeft;
        });

        track.addEventListener("pointermove", function (event) {
            if (!isDown) { return; }
            var delta = event.clientX - startX;
            if (Math.abs(delta) > 5) {
                dragged = true;
                track.classList.add("is-dragging");
            }
            track.scrollLeft = startScroll - delta;
        });

        function endDrag() {
            if (!isDown) { return; }
            isDown = false;
            track.classList.remove("is-dragging");
            if (dragged) { goTo(currentIndex()); }
        }

        track.addEventListener("pointerup", endDrag);
        track.addEventListener("pointerleave", endDrag);
        window.addEventListener("pointerup", endDrag);
        track.addEventListener("click", function (event) {
            if (dragged) { event.preventDefault(); }
        }, true);

        initSliderAutoplay(root, track, slides, autoplayMs, goTo, currentIndex);
        sync();
    }

    /* Autoplay pauses on interaction, hover and when the slider is off-screen */
    function initSliderAutoplay(root, track, slides, autoplayMs, goTo, currentIndex) {
        if (!(autoplayMs > 0) || slides.length < 2 || reduceMotion) {
            return;
        }

        var timer = null;
        var paused = false;

        function play() {
            if (timer || paused) { return; }
            timer = window.setInterval(function () { goTo(currentIndex() + 1); }, autoplayMs);
        }

        function stop() {
            if (timer) {
                window.clearInterval(timer);
                timer = null;
            }
        }

        function pauseFor(ms) {
            paused = true;
            stop();
            window.setTimeout(function () { paused = false; play(); }, ms);
        }

        ["pointerdown", "touchstart", "wheel"].forEach(function (name) {
            track.addEventListener(name, function () { pauseFor(12000); }, { passive: true });
        });

        root.addEventListener("mouseenter", function () { paused = true; stop(); });
        root.addEventListener("mouseleave", function () { paused = false; play(); });

        doc.addEventListener("visibilitychange", function () {
            if (doc.hidden) { stop(); } else { play(); }
        });

        if ("IntersectionObserver" in window) {
            var watcher = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) { play(); } else { stop(); }
                });
            }, { threshold: 0.25 });
            watcher.observe(root);
        } else {
            play();
        }
    }

    /* ------------------------------------------------------------------ *
     * 3. Type animation — rotating headline words (react-type-animation feel)
     * ------------------------------------------------------------------ */
    function initTypewriter() {
        Array.prototype.forEach.call(doc.querySelectorAll("[data-type-words]"), function (node) {
            var words = (node.getAttribute("data-type-words") || "").split("|").filter(Boolean);
            if (!words.length) { return; }

            node.textContent = words[0];

            if (reduceMotion) { return; }

            var wordIndex = 0;
            var charIndex = words[0].length;
            var deleting = true;

            function tick() {
                var word = words[wordIndex];

                if (deleting) {
                    charIndex -= 1;
                    node.textContent = word.slice(0, Math.max(0, charIndex));
                    if (charIndex <= 0) {
                        deleting = false;
                        wordIndex = (wordIndex + 1) % words.length;
                        charIndex = 0;
                        return window.setTimeout(tick, 300);
                    }
                    return window.setTimeout(tick, 42);
                }

                charIndex += 1;
                node.textContent = word.slice(0, charIndex);
                if (charIndex >= word.length) {
                    deleting = true;
                    return window.setTimeout(tick, 2100);
                }
                return window.setTimeout(tick, 76);
            }

            window.setTimeout(tick, 2300);
        });
    }

    /* ------------------------------------------------------------------ *
     * 4. Animated counters for the hero statistics
     * ------------------------------------------------------------------ */
    function runCounter(node) {
        var target = parseFloat(node.getAttribute("data-count")) || 0;
        var decimals = parseInt(node.getAttribute("data-count-decimals") || "0", 10);
        var prefix = node.getAttribute("data-count-prefix") || "";
        var suffix = node.getAttribute("data-count-suffix") || "";
        var duration = parseInt(node.getAttribute("data-count-duration") || "1500", 10);

        if (reduceMotion) {
            node.textContent = prefix + target.toLocaleString("en-US") + suffix;
            return;
        }

        var startTime = null;

        function frame(timestamp) {
            if (startTime === null) { startTime = timestamp; }
            var progress = Math.min((timestamp - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            node.textContent = prefix + (target * eased).toLocaleString("en-US", {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            }) + suffix;
            if (progress < 1) { window.requestAnimationFrame(frame); }
        }

        window.requestAnimationFrame(frame);
    }

    function initCounters() {
        var nodes = Array.prototype.slice.call(doc.querySelectorAll("[data-count]"));
        if (!nodes.length) { return; }

        if (reduceMotion || !("IntersectionObserver" in window)) {
            nodes.forEach(runCounter);
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    runCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.35 });

        nodes.forEach(function (node) { observer.observe(node); });
    }

    function initHeroImage() {
        var image = doc.querySelector("[data-hero-image]");
        if (!image || HERO_IMAGES.length < 2) { return; }

        var previousIndex = -1;
        try {
            previousIndex = parseInt(window.localStorage.getItem("brightabroadchina:hero-image"), 10);
        } catch (error) {
            console.warn("The previous hero image could not be read.", error);
        }

        var index = Math.floor(Math.random() * HERO_IMAGES.length);
        if (previousIndex >= 0 && previousIndex < HERO_IMAGES.length) {
            var randomSlot = Math.floor(Math.random() * (HERO_IMAGES.length - 1));
            index = randomSlot >= previousIndex ? randomSlot + 1 : randomSlot;
        }

        var selected = HERO_IMAGES[index];
        image.src = selected.src;
        image.alt = "Campus at " + selected.name;
        var media = image.closest(".media");
        if (media) { media.dataset.mediaLabel = selected.name; }

        try {
            window.localStorage.setItem("brightabroadchina:hero-image", String(index));
        } catch (error) {
            console.warn("The selected hero image could not be saved.", error);
        }
    }

    function initResponsiveBlogTables() {
        Array.prototype.forEach.call(doc.querySelectorAll(".blog-rich-content table"), function (table) {
            if (table.parentElement && table.parentElement.classList.contains("blog-table-scroll")) { return; }
            var wrapper = doc.createElement("div");
            wrapper.className = "blog-table-scroll";
            wrapper.setAttribute("role", "region");
            wrapper.setAttribute("aria-label", "Scrollable table");
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        });
    }

    /* ------------------------------------------------------------------ *
     * 5. Mobile app shell — drawer, notification sheet, progress, tab bar
     * ------------------------------------------------------------------ */
    function initAppShell() {
        var nav = doc.querySelector("#primary-navigation");
        var toggle = doc.querySelector(".menu-toggle");
        var drawerClose = doc.querySelector("[data-drawer-close]");
        var navScrim = doc.querySelector("#nav-scrim");
        var bell = doc.querySelector("#bell-toggle");
        var sheet = doc.querySelector("#notify-sheet");
        var sheetScrim = doc.querySelector("#sheet-scrim");
        var sheetClose = doc.querySelector("[data-sheet-close]");
        var body = doc.body;

        function isPhone() {
            return window.matchMedia("(max-width: 780px)").matches;
        }

        function syncNavState() {
            if (!nav) { return; }
            var open = nav.classList.contains("is-open");
            if (navScrim) { navScrim.classList.toggle("is-visible", open); }
            body.classList.toggle("nav-open", open);
        }

        function closeNav() {
            if (!nav) { return; }
            nav.classList.remove("is-open");
            if (toggle) {
                toggle.setAttribute("aria-expanded", "false");
                toggle.setAttribute("aria-label", "Open navigation menu");
            }
            syncNavState();
        }

        if (toggle) {
            /* the base template toggles .is-open — mirror that state here */
            toggle.addEventListener("click", function () {
                window.setTimeout(syncNavState, 0);
            });
        }
        if (drawerClose) { drawerClose.addEventListener("click", closeNav); }
        if (navScrim) { navScrim.addEventListener("click", closeNav); }
        if (nav) {
            nav.addEventListener("click", function (event) {
                if (event.target.closest("a")) { window.setTimeout(closeNav, 140); }
            });
        }

        function openSheet() {
            if (!sheet) { return; }
            closeNav();
            sheet.classList.add("is-open");
            sheet.setAttribute("aria-hidden", "false");
            if (sheetScrim) { sheetScrim.classList.add("is-visible"); }
            if (bell) { bell.setAttribute("aria-expanded", "true"); }
            body.classList.add("sheet-open");
        }

        function closeSheet() {
            if (!sheet) { return; }
            sheet.classList.remove("is-open");
            sheet.setAttribute("aria-hidden", "true");
            if (sheetScrim) { sheetScrim.classList.remove("is-visible"); }
            if (bell) { bell.setAttribute("aria-expanded", "false"); }
            body.classList.remove("sheet-open");
        }

        if (bell && sheet) {
            bell.addEventListener("click", function () {
                if (sheet.classList.contains("is-open")) { closeSheet(); } else { openSheet(); }
            });
        }
        if (sheetScrim) { sheetScrim.addEventListener("click", closeSheet); }
        if (sheetClose) { sheetClose.addEventListener("click", closeSheet); }

        /* swipe the sheet down to dismiss */
        if (sheet) {
            var startY = null;

            sheet.addEventListener("touchstart", function (event) {
                startY = event.touches[0].clientY;
            }, { passive: true });

            sheet.addEventListener("touchmove", function (event) {
                if (startY === null) { return; }
                var delta = event.touches[0].clientY - startY;
                if (delta > 0) { sheet.style.transform = "translateY(" + delta + "px)"; }
            }, { passive: true });

            sheet.addEventListener("touchend", function () {
                if (startY === null) { return; }
                var match = (sheet.style.transform || "").match(/-?\d+(\.\d+)?/);
                var delta = match ? parseFloat(match[0]) : 0;
                sheet.style.transform = "";
                startY = null;
                if (delta > 80) { closeSheet(); }
            });
        }

        doc.addEventListener("keydown", function (event) {
            if (event.key !== "Escape") { return; }
            if (sheet && sheet.classList.contains("is-open")) { closeSheet(); return; }
            closeNav();
        });

        /* bottom navigation "Alerts" tab opens the inbox sheet on phones */
        Array.prototype.forEach.call(doc.querySelectorAll("[data-sheet-open]"), function (el) {
            el.addEventListener("click", function (event) {
                if (!sheet) { return; }
                event.preventDefault();
                openSheet();
            });
        });

        initScrollChrome(sheet);
    }

    /* Reading progress bar + auto-hiding bottom tab bar */
    function initScrollChrome(sheet) {
        var bar = doc.querySelector("#scroll-progress span");
        var tabBar = doc.querySelector("#bottom-nav");
        var lastY = window.scrollY;
        var queued = false;

        function onScroll() {
            if (queued) { return; }
            queued = true;
            window.requestAnimationFrame(function () {
                var y = window.scrollY;
                var max = doc.documentElement.scrollHeight - window.innerHeight;

                if (bar && max > 8) {
                    bar.style.width = Math.min(100, Math.max(0, (y / max) * 100)) + "%";
                }

                if (tabBar) {
                    var sheetOpen = !!(sheet && sheet.classList.contains("is-open"));
                    if (y < 90 || sheetOpen) {
                        tabBar.classList.remove("is-hidden");
                    } else if (y > lastY + 8) {
                        tabBar.classList.add("is-hidden");
                    } else if (y < lastY - 8) {
                        tabBar.classList.remove("is-hidden");
                    }
                }

                lastY = y;
                queued = false;
            });
        }

        window.addEventListener("scroll", onScroll, { passive: true });
        window.addEventListener("resize", onScroll);
        onScroll();
    }

    function initPreparationChecklist() {
        var checklist = doc.querySelector("[data-prep-checklist]");
        if (!checklist) { return; }

        var studentId = checklist.dataset.studentId || "unknown";
        var storageKey = "brightabroadchina:document-readiness:" + studentId;
        var legacyStorageKey = ["global", "edu", "link"].join("") + ":document-readiness:" + studentId;
        var items = Array.prototype.slice.call(checklist.querySelectorAll("[data-checklist-item]"));
        var countNode = checklist.querySelector("[data-checklist-count]");
        var progressNode = checklist.querySelector("[data-checklist-progress]");
        var progressTrack = checklist.querySelector("[role='progressbar']");
        var saved = {};

        try {
            var storedChecklist = window.localStorage.getItem(storageKey);
            if (storedChecklist === null) {
                storedChecklist = window.localStorage.getItem(legacyStorageKey);
            }
            saved = JSON.parse(storedChecklist || "{}") || {};
        } catch (error) {
            saved = {};
        }

        function render() {
            var completed = 0;
            items.forEach(function (item) {
                var checkbox = item.querySelector("input[type='checkbox']");
                checkbox.checked = saved[item.dataset.checklistKey] === true;
                item.classList.toggle("is-ready", checkbox.checked);
                if (checkbox.checked) { completed += 1; }
            });
            if (countNode) { countNode.textContent = String(completed); }
            if (progressNode) {
                progressNode.style.width = (items.length ? completed / items.length * 100 : 0) + "%";
            }
            if (progressTrack) { progressTrack.setAttribute("aria-valuenow", String(completed)); }
        }

        items.forEach(function (item) {
            var checkbox = item.querySelector("input[type='checkbox']");
            checkbox.addEventListener("change", function () {
                saved[item.dataset.checklistKey] = checkbox.checked;
                try {
                    window.localStorage.setItem(storageKey, JSON.stringify(saved));
                } catch (error) {
                    // Keep the checklist usable for this page view if storage is unavailable.
                }
                render();
            });
        });

        render();
    }

    /* ------------------------------------------------------------------ *
     * 6. Boot
     * ------------------------------------------------------------------ */
    function boot() {
        Array.prototype.forEach.call(doc.querySelectorAll("[data-slider]"), initSlider);
        Array.prototype.forEach.call(doc.querySelectorAll("img[data-media-fallback], img[src^='http']"), guardImage);
        initHeroImage();
        initResponsiveBlogTables();
        initTypewriter();
        initCounters();
        initAppShell();
        initPreparationChecklist();
    }

    if (doc.readyState === "loading") {
        doc.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }

    // GENERATED-BLOCK-END





})();
