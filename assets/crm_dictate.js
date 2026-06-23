/**
 * CRM note dictation — continuous Web Speech API session.
 * Click Dictate to start; Stop (or Dictate again) to end.
 */
(function () {
    const state = {
        rec: null,
        active: false,
        manualStop: false,
        restartTimer: null,
    };

    function getNoteEl() {
        return document.getElementById("crm-note-body");
    }

    function getStatusEl() {
        return document.getElementById("crm-note-dictate-status");
    }

    function getStopBtn() {
        return document.getElementById("crm-note-dictate-stop-btn");
    }

    function setStatus(msg) {
        const el = getStatusEl();
        if (el) {
            el.textContent = msg || "";
        }
    }

    function setStopVisible(visible) {
        const btn = getStopBtn();
        if (btn) {
            btn.style.display = visible ? "inline-block" : "none";
        }
    }

    function setNoteValue(newVal) {
        const el = getNoteEl();
        if (!el) {
            return;
        }
        const proto = window.HTMLTextAreaElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, "value");
        if (setter && setter.set) {
            setter.set.call(el, newVal);
        } else {
            el.value = newVal;
        }
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function appendTranscript(text) {
        const chunk = (text || "").trim();
        if (!chunk) {
            return;
        }
        const existing = getNoteEl() ? getNoteEl().value : "";
        const needsSpace =
            existing.length > 0 && !/\s$/.test(existing) && !/^[,.!?;:]/.test(chunk);
        setNoteValue(existing + (needsSpace ? " " : "") + chunk);
    }

    function clearRestartTimer() {
        if (state.restartTimer) {
            clearTimeout(state.restartTimer);
            state.restartTimer = null;
        }
    }

    function stopDictation() {
        state.manualStop = true;
        state.active = false;
        clearRestartTimer();
        if (state.rec) {
            try {
                state.rec.stop();
            } catch (err) {
                /* ignore */
            }
            state.rec = null;
        }
        setStopVisible(false);
        setStatus("");
    }

    function scheduleRestart() {
        clearRestartTimer();
        if (!state.active || state.manualStop) {
            return;
        }
        state.restartTimer = setTimeout(function () {
            if (!state.active || state.manualStop || !state.rec) {
                return;
            }
            try {
                state.rec.start();
            } catch (err) {
                /* Chrome may throw if called too soon; retry once */
                state.restartTimer = setTimeout(function () {
                    if (state.active && state.rec && !state.manualStop) {
                        try {
                            state.rec.start();
                        } catch (e2) {
                            setStatus("Dictation paused — click Dictate to continue.");
                            state.active = false;
                            setStopVisible(false);
                        }
                    }
                }, 250);
            }
        }, 120);
    }

    function startDictation() {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) {
            setStatus("Speech recognition requires Chrome or Edge.");
            return;
        }
        if (state.active) {
            stopDictation();
            return;
        }

        state.manualStop = false;
        state.active = true;

        const rec = new SR();
        state.rec = rec;
        rec.lang = "en-AU";
        rec.continuous = true;
        rec.interimResults = true;
        rec.maxAlternatives = 1;

        rec.onresult = function (event) {
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    appendTranscript(event.results[i][0].transcript);
                }
            }
            if (state.active) {
                setStatus("Listening… speak now (click Stop when finished)");
            }
        };

        rec.onerror = function (event) {
            if (event.error === "no-speech" || event.error === "aborted") {
                return;
            }
            if (event.error === "not-allowed") {
                setStatus("Microphone permission denied.");
                stopDictation();
                return;
            }
            setStatus("Dictation error — click Dictate to try again.");
            stopDictation();
        };

        rec.onend = function () {
            if (state.manualStop || !state.active) {
                setStopVisible(false);
                if (state.manualStop) {
                    setStatus("");
                }
                return;
            }
            scheduleRestart();
        };

        try {
            rec.start();
            setStopVisible(true);
            setStatus("Listening… speak now (click Stop when finished)");
        } catch (err) {
            state.active = false;
            state.rec = null;
            setStatus("Could not start microphone — check permissions.");
        }
    }

    document.addEventListener(
        "click",
        function (ev) {
            if (ev.target.closest("#crm-note-dictate-btn")) {
                ev.preventDefault();
                startDictation();
                return;
            }
            if (ev.target.closest("#crm-note-dictate-stop-btn")) {
                ev.preventDefault();
                stopDictation();
            }
        },
        true
    );
})();
