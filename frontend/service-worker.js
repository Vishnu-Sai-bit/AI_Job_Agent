/* ==========================================================
   JobCopilot Service Worker (PWA Offline & Asset Caching)
   ========================================================== */

const CACHE_NAME = "jobcopilot-cache-v1";
const STATIC_ASSETS = [
    "/",
    "/index.html",
    "/style.css",
    "/app.js",
    "/manifest.json"
];

// Install Event
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS).catch(() => {
                // Ignore failure for missing remote URLs
            });
        })
    );
    self.skipWaiting();
});

// Activate Event
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch Event - Network first, fallback to cache for shell assets
self.addEventListener("fetch", (event) => {
    // Only handle GET requests
    if (event.request.method !== "GET") return;

    // Do not cache API requests or external services
    const url = new URL(event.request.url);
    if (url.pathname.startsWith("/api") || 
        url.pathname.startsWith("/auth") || 
        url.pathname.startsWith("/admin") || 
        url.hostname.includes("googleapis.com") || 
        url.hostname.includes("onrender.com")) {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then((networkResponse) => {
                if (networkResponse && networkResponse.status === 200) {
                    const clonedResponse = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, clonedResponse);
                    });
                }
                return networkResponse;
            })
            .catch(() => caches.match(event.request))
    );
});
