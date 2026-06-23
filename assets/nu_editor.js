/**
 * Nova U rich editor — dictation, paste, drag-drop media, video embeds.
 */
(function () {
    "use strict";

    const recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let activeRecognizer = null;
    let dictateTarget = null;
    let activeStatusId = "nu-editor-dictate-status";
    let activeDictateBtn = null;
    let manualStop = false;
    let restartTimer = null;

    function apiBase(wrap) {
        return (wrap && wrap.dataset.apiBase) || "http://127.0.0.1:8000/api/v1";
    }

    function mediaUrl(api, path) {
        if (path.startsWith("http")) return path;
        const base = api.replace(/\/api\/v1\/?$/, "");
        return base + path;
    }

    function syncEditorToTextarea() {
        const surface = document.getElementById("nu-rich-editor-surface");
        const hidden = document.getElementById("nu-editor-rich-content");
        if (surface && hidden) {
            hidden.value = surface.innerHTML;
        }
    }

    function loadEditorFromTextarea() {
        const surface = document.getElementById("nu-rich-editor-surface");
        const hidden = document.getElementById("nu-editor-rich-content");
        if (surface && hidden) {
            surface.innerHTML = hidden.value || "";
        }
    }

    function setDictateStatus(msg, statusId) {
        const id = statusId || activeStatusId || "nu-editor-dictate-status";
        const el = document.getElementById(id);
        if (el) el.textContent = msg || "";
    }

    function clearRestartTimer() {
        if (restartTimer) {
            clearTimeout(restartTimer);
            restartTimer = null;
        }
    }

    function setFieldValue(el, newVal) {
        if (!el || el.isContentEditable) return;
        const proto =
            el.tagName === "TEXTAREA"
                ? window.HTMLTextAreaElement.prototype
                : window.HTMLInputElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, "value");
        if (setter && setter.set) {
            setter.set.call(el, newVal);
        } else {
            el.value = newVal;
        }
        ["input", "change"].forEach(function (type) {
            const ev = new Event(type, { bubbles: true, cancelable: true });
            try {
                Object.defineProperty(ev, "target", {
                    value: el,
                    enumerable: true,
                });
            } catch (e) {
                /* ignore */
            }
            el.dispatchEvent(ev);
        });
    }

    function appendTranscript(target, text) {
        const chunk = (text || "").trim();
        if (!chunk || !target) return;
        if (target.isContentEditable) {
            target.focus();
            document.execCommand("insertText", false, chunk + " ");
            syncEditorToTextarea();
            return;
        }
        const existing = target.value || "";
        const needsSpace =
            existing.length > 0 && !/\s$/.test(existing) && !/^[,.!?;:]/.test(chunk);
        setFieldValue(target, existing + (needsSpace ? " " : "") + chunk);
    }

    function resetDictateButtons() {
        document.querySelectorAll(".nu-dictate-btn.listening").forEach(function (btn) {
            btn.classList.remove("listening");
            btn.textContent = "🎤 Dictate";
        });
        activeDictateBtn = null;
    }

    function stopDictation() {
        manualStop = true;
        clearRestartTimer();
        if (activeRecognizer) {
            try {
                activeRecognizer.stop();
            } catch (e) {
                /* ignore */
            }
            activeRecognizer = null;
        }
        resetDictateButtons();
        dictateTarget = null;
        setDictateStatus("");
    }

    function scheduleDictationRestart(rec, target) {
        clearRestartTimer();
        if (manualStop || !dictateTarget || activeRecognizer !== rec) {
            return;
        }
        restartTimer = setTimeout(function () {
            if (manualStop || !dictateTarget || activeRecognizer !== rec) {
                return;
            }
            try {
                rec.start();
            } catch (e) {
                restartTimer = setTimeout(function () {
                    if (!manualStop && dictateTarget && activeRecognizer === rec) {
                        try {
                            rec.start();
                        } catch (e2) {
                            setDictateStatus(
                                "Dictation paused — click Dictate to continue.",
                                activeStatusId
                            );
                            stopDictation();
                        }
                    }
                }, 250);
            }
        }, 120);
    }

    function startDictation(targetId, statusId, btn) {
        if (!recognition) {
            setDictateStatus(
                "Speech recognition requires Chrome or Edge.",
                statusId || activeStatusId
            );
            return;
        }
        stopDictation();
        const target = document.getElementById(targetId);
        if (!target) {
            setDictateStatus("Could not find field to dictate into.", statusId);
            return;
        }

        manualStop = false;
        dictateTarget = target;
        activeStatusId = statusId || "nu-editor-dictate-status";
        activeDictateBtn = btn || null;

        const rec = new recognition();
        rec.continuous = true;
        rec.interimResults = true;
        rec.lang = "en-AU";
        rec.maxAlternatives = 1;

        rec.onresult = function (event) {
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    appendTranscript(target, event.results[i][0].transcript);
                }
            }
            if (!manualStop) {
                setDictateStatus(
                    "Listening… speak now (click Stop when finished).",
                    activeStatusId
                );
            }
        };

        rec.onerror = function (event) {
            if (event.error === "no-speech" || event.error === "aborted") {
                return;
            }
            if (event.error === "not-allowed") {
                setDictateStatus("Microphone permission denied.", activeStatusId);
            } else {
                setDictateStatus("Dictation error — try again.", activeStatusId);
            }
            stopDictation();
        };

        rec.onend = function () {
            if (manualStop || activeRecognizer !== rec) {
                return;
            }
            scheduleDictationRestart(rec, target);
        };

        activeRecognizer = rec;
        try {
            rec.start();
            setDictateStatus(
                "Listening… speak now (click Stop when finished).",
                activeStatusId
            );
        } catch (e) {
            setDictateStatus("Could not start microphone — check permissions.", activeStatusId);
            stopDictation();
        }
    }

    function exec(cmd, value) {
        const surface = document.getElementById("nu-rich-editor-surface");
        if (!surface) return;
        surface.focus();
        document.execCommand(cmd, false, value || null);
        syncEditorToTextarea();
    }

    function embedVideoInEditor(url) {
        const surface = document.getElementById("nu-rich-editor-surface");
        if (!surface || !url) return;
        const embed = toEmbedUrl(url.trim());
        if (!embed) return;
        const html =
            '<div class="nu-inline-video" contenteditable="false">' +
            '<iframe src="' +
            embed +
            '" frameborder="0" allowfullscreen ' +
            'style="width:100%;height:360px;border:0;border-radius:8px;"></iframe></div><p><br></p>';
        surface.focus();
        document.execCommand("insertHTML", false, html);
        syncEditorToTextarea();
    }

    function toEmbedUrl(url) {
        let m = url.match(/loom\.com\/share\/([a-zA-Z0-9]+)/);
        if (m) return "https://www.loom.com/embed/" + m[1];
        m = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{6,})/);
        if (m) return "https://www.youtube.com/embed/" + m[1];
        m = url.match(/vimeo\.com\/(\d+)/);
        if (m) return "https://player.vimeo.com/video/" + m[1];
        if (url.indexOf("/embed/") >= 0) return url;
        return null;
    }

    async function uploadFile(file, wrap) {
        const api = apiBase(wrap);
        const form = new FormData();
        form.append("file", file);
        const resp = await fetch(api + "/training/media/upload", {
            method: "POST",
            body: form,
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err.detail || "Upload failed");
        }
        return resp.json();
    }

    function insertMedia(url, kind) {
        const surface = document.getElementById("nu-rich-editor-surface");
        if (!surface) return;
        let html;
        if (kind === "video") {
            html =
                '<video controls src="' +
                url +
                '" style="max-width:100%;border-radius:8px;"></video><p><br></p>';
        } else {
            html =
                '<img src="' +
                url +
                '" alt="Training image" style="max-width:100%;border-radius:8px;" /><p><br></p>';
        }
        surface.focus();
        document.execCommand("insertHTML", false, html);
        syncEditorToTextarea();
    }

    async function handleFiles(files, wrap) {
        const api = apiBase(wrap);
        for (const file of files) {
            if (!file.type.startsWith("image/") && !file.type.startsWith("video/")) {
                setDictateStatus("Skipped unsupported file: " + file.name);
                continue;
            }
            try {
                setDictateStatus("Uploading " + file.name + "…");
                const data = await uploadFile(file, wrap);
                insertMedia(mediaUrl(api, data.url), data.kind);
                setDictateStatus("Inserted " + file.name);
            } catch (err) {
                setDictateStatus(err.message || "Upload failed");
            }
        }
        setTimeout(() => setDictateStatus(""), 2500);
    }

    function bindRichEditor(wrap) {
        if (!wrap || wrap.dataset.nuBound === "1") return;
        wrap.dataset.nuBound = "1";

        const surface = wrap.querySelector(".nu-rich-editor-surface");
        if (!surface) return;

        surface.addEventListener("input", syncEditorToTextarea);
        surface.addEventListener("blur", syncEditorToTextarea);

        surface.addEventListener("paste", function (e) {
            const text = (e.clipboardData || window.clipboardData).getData("text");
            if (text && /^https?:\/\//i.test(text.trim()) && toEmbedUrl(text.trim())) {
                e.preventDefault();
                embedVideoInEditor(text.trim());
            }
        });

        ["dragenter", "dragover"].forEach((ev) => {
            surface.addEventListener(ev, function (e) {
                e.preventDefault();
                e.stopPropagation();
                surface.classList.add("nu-drag-over");
            });
        });
        ["dragleave", "drop"].forEach((ev) => {
            surface.addEventListener(ev, function (e) {
                e.preventDefault();
                e.stopPropagation();
                surface.classList.remove("nu-drag-over");
            });
        });
        surface.addEventListener("drop", function (e) {
            const files = e.dataTransfer && e.dataTransfer.files;
            if (files && files.length) handleFiles(files, wrap);
        });

        wrap.querySelectorAll(".nu-rich-cmd").forEach((btn) => {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                const cmd = btn.dataset.cmd;
                if (cmd === "embedVideo") {
                    const url = window.prompt("Paste Loom, YouTube, or Vimeo URL:");
                    if (url) embedVideoInEditor(url);
                } else if (cmd === "formatBlock") {
                    exec("formatBlock", btn.dataset.value || "p");
                } else if (cmd === "createLink") {
                    const url = window.prompt("Link URL:");
                    if (url) exec("createLink", url);
                } else {
                    exec(cmd);
                }
            });
        });

        const embedBtn = document.getElementById("nu-editor-embed-video-btn");
        if (embedBtn && !embedBtn.dataset.nuBound) {
            embedBtn.dataset.nuBound = "1";
            embedBtn.addEventListener("click", function () {
                const input = document.getElementById("nu-editor-video-embed");
                if (input && input.value) embedVideoInEditor(input.value);
            });
        }
    }

    function bindDictateButtons() {
        document.querySelectorAll(".nu-dictate-btn").forEach(function (btn) {
            if (btn.dataset.nuDictateBound === "1") return;
            btn.dataset.nuDictateBound = "1";
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                const targetId = btn.dataset.target;
                const statusId = btn.dataset.status || "nu-editor-dictate-status";
                if (!targetId) return;
                if (btn.classList.contains("listening")) {
                    stopDictation();
                    return;
                }
                document.querySelectorAll(".nu-dictate-btn").forEach(function (b) {
                    b.classList.remove("listening");
                    b.textContent = "🎤 Dictate";
                });
                btn.classList.add("listening");
                btn.textContent = "⏹ Stop";
                startDictation(targetId, statusId, btn);
            });
        });
    }

    function initNovaUEditors() {
        const wrap = document.getElementById("nu-rich-editor-wrap");
        if (wrap) bindRichEditor(wrap);
        bindDictateButtons();
    }

    document.addEventListener("mousedown", function (e) {
        if (e.target.closest("#nu-editor-save-btn")) {
            syncEditorToTextarea();
        }
    }, true);

    document.addEventListener("DOMContentLoaded", initNovaUEditors);

    const observer = new MutationObserver(function () {
        initNovaUEditors();
        const modal = document.getElementById("nu-editor-modal");
        if (modal && modal.classList.contains("show")) {
            loadEditorFromTextarea();
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });

    window.nuEditorLoadContent = loadEditorFromTextarea;
    window.nuEditorSyncContent = syncEditorToTextarea;
})();
