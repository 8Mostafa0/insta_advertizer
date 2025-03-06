import webview
import time
import threading
import json
import os
from urllib.parse import urlparse

def create_browser():
    # File to store cookies, token, and local storage
    storage_file = "session_data.json"

    # Load saved session data if it exists
    session_data = {}
    if os.path.exists(storage_file):
        with open(storage_file, 'r') as f:
            session_data = json.load(f)
        print(f"Loaded session data: {session_data}")

    # Create the webview window
    window = webview.create_window(
        "Instagram",
        "https://www.instagram.com",
        width=400,
        height=800,
        resizable=True,
        hidden=False
    )

    # JavaScript code with enhanced session handling
    js_code = r'''
    // Store navigation history
    let historyStack = [window.location.href];
    let currentIndex = 0;
    let lastUrl = window.location.href;

    // Inject saved cookies and local storage immediately
    let savedCookies = %s;  // Placeholder for cookies from Python
    let savedToken = %s;    // Placeholder for token from Python
    let savedLocalStorage = %s;  // Placeholder for local storage from Python
    if (savedCookies) {
        for (let name in savedCookies) {
            document.cookie = `${name}=${savedCookies[name]}; domain=.instagram.com; path=/; SameSite=Lax; Secure`;
        }
        console.log('Injected saved cookies:', savedCookies);
    }
    if (savedToken) {
        localStorage.setItem('userToken', savedToken);
        document.cookie = `sessionid=${savedToken}; domain=.instagram.com; path=/; SameSite=Lax; Secure`;
        console.log('Injected saved token as sessionid:', savedToken);
    }
    if (savedLocalStorage) {
        for (let key in savedLocalStorage) {
            localStorage.setItem(key, savedLocalStorage[key]);
        }
        console.log('Injected saved local storage:', savedLocalStorage);
    }

    // Auto-reload once after injection if on login page
    if (document.cookie.includes('sessionid')) {
        window.location.reload();
    }

    function addButtons() {
        if (!document.body) {
            console.log('document.body is null, delaying button addition');
            return;
        }

        var existingContainer = document.getElementById('custom-buttons');
        if (existingContainer) {
            existingContainer.remove();
        }

        var buttonContainer = document.createElement('div');
        buttonContainer.id = 'custom-buttons';
        buttonContainer.style.position = 'fixed';
        buttonContainer.style.bottom = '20px';
        buttonContainer.style.left = '20px';
        buttonContainer.style.zIndex = '10000';
        buttonContainer.style.background = '#fff';
        buttonContainer.style.padding = '5px';
        buttonContainer.style.borderRadius = '5px';
        buttonContainer.style.display = 'flex';
        buttonContainer.style.flexDirection = 'column';

        var backButton = document.createElement('button');
        backButton.textContent = 'Back';
        backButton.style.marginBottom = '5px';
        backButton.onclick = function() {
            if (currentIndex > 0) {
                currentIndex--;
                window.location.href = historyStack[currentIndex];
                console.log('Back to:', historyStack[currentIndex], 'Index:', currentIndex, 'Stack:', historyStack);
            } else {
                console.log('No back history available. Index:', currentIndex, 'Stack:', historyStack);
            }
        };
        buttonContainer.appendChild(backButton);

        var searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.id = 'search-input';
        searchInput.style.marginBottom = '5px';
        searchInput.style.padding = '2px';
        searchInput.style.color = 'black';
        buttonContainer.appendChild(searchInput);

        var searchButton = document.createElement('button');
        searchButton.textContent = 'Search';
        searchButton.style.marginBottom = '5px';
        searchButton.onclick = function() {
            var searchText = document.getElementById('search-input').value.trim();
            if (searchText) {
                var highlighted = document.querySelectorAll('.highlight-search');
                highlighted.forEach(el => el.classList.remove('highlight-search'));

                var elements = document.getElementsByTagName('*');
                for (var i = 0; i < elements.length; i++) {
                    var el = elements[i];
                    var textContent = el.textContent || '';
                    var href = el.getAttribute('href') || '';
                    if ((textContent.toLowerCase().includes(searchText.toLowerCase()) && el.children.length === 0) ||
                        href.toLowerCase().includes(searchText.toLowerCase())) {
                        el.classList.add('highlight-search');
                    }
                }
                console.log('Searched for:', searchText);
            }
        };
        buttonContainer.appendChild(searchButton);

        var callFunctionsButton = document.createElement('button');
        callFunctionsButton.textContent = 'Call Functions';
        callFunctionsButton.style.marginBottom = '5px';
        callFunctionsButton.onclick = function() {
            var searchText = document.getElementById('search-input').value.trim();
            if (searchText) {
                var highlighted = document.querySelectorAll('.highlight-search');
                highlighted.forEach(el => el.classList.remove('highlight-search'));

                var elements = document.getElementsByTagName('*');
                var foundMatch = false;
                for (var i = 0; i < elements.length; i++) {
                    var el = elements[i];
                    var textContent = el.textContent || '';
                    var href = el.getAttribute('href') || '';
                    if ((textContent.toLowerCase().includes(searchText.toLowerCase()) && el.children.length === 0) ||
                        href.toLowerCase().includes(searchText.toLowerCase())) {
                        foundMatch = true;
                        el.classList.add('highlight-search');
                        
                        var onclick = el.getAttribute('onclick');
                        if (onclick) {
                            console.log('onclick attribute found:', onclick, 'on element:', el);
                            var funcMatch = onclick.match(/(\w+)\s*\(/) || onclick.match(/^\s*(\w+)\s*$/);
                            if (funcMatch) {
                                var funcName = funcMatch[1];
                                console.log('Extracted function name:', funcName);
                                try {
                                    if (typeof window[funcName] === 'function') {
                                        window[funcName]();
                                        console.log('Successfully called:', funcName);
                                    } else {
                                        console.log('Function not found in window, trying click:', funcName);
                                        el.click();
                                    }
                                } catch (e) {
                                    console.log('Error calling function:', funcName, 'Error:', e);
                                    el.click();
                                }
                            } else {
                                console.log('No function name matched, simulating click on:', el);
                                el.click();
                            }
                        } else {
                            console.log('No onclick attribute, simulating click on:', el);
                            el.click();
                        }
                    }
                }
                
                if (!foundMatch) {
                    console.log('No elements matched the search term:', searchText);
                } else {
                    console.log('Processed all matches for:', searchText);
                }
            } else {
                console.log('No search text provided');
            }
        };
        buttonContainer.appendChild(callFunctionsButton);

        var reloadButton = document.createElement('button');
        reloadButton.textContent = 'Reload';
        reloadButton.onclick = function() {
            window.location.reload();
        };
        buttonContainer.appendChild(reloadButton);

        var style = document.createElement('style');
        style.textContent = '.highlight-search { background-color: yellow !important; }';
        document.head.appendChild(style);

        document.body.appendChild(buttonContainer);
    }

    window.ensureButtons = function() {
        if (!document.body) {
            console.log('document.body is null, skipping ensureButtons');
            return;
        }
        if (!document.getElementById('custom-buttons')) {
            addButtons();
        }
    };

    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        addButtons();
    } else {
        window.addEventListener('DOMContentLoaded', addButtons);
    }

    document.addEventListener('click', function(event) {
        setTimeout(function() {
            let newUrl = window.location.href;
            if (newUrl !== lastUrl) {
                if (currentIndex < historyStack.length - 1) {
                    historyStack = historyStack.slice(0, currentIndex + 1);
                }
                historyStack.push(newUrl);
                currentIndex = historyStack.length - 1;
                lastUrl = newUrl;
                window.ensureButtons();
                console.log('History updated after click:', historyStack, 'Index:', currentIndex);
            }
        }, 500);
    });

    window.addEventListener('popstate', function() {
        setTimeout(function() {
            let newUrl = window.location.href;
            if (newUrl !== lastUrl) {
                currentIndex = historyStack.indexOf(newUrl);
                if (currentIndex === -1) {
                    historyStack.push(newUrl);
                    currentIndex = historyStack.length - 1;
                }
                lastUrl = newUrl;
                window.ensureButtons();
                console.log('Popstate:', historyStack, 'Index:', currentIndex);
            }
        }, 500);
    });

    function checkUrlChange() {
        let newUrl = window.location.href;
        if (newUrl !== lastUrl) {
            if (currentIndex < historyStack.length - 1) {
                historyStack = historyStack.slice(0, currentIndex + 1);
            }
            historyStack.push(newUrl);
            currentIndex = historyStack.length - 1;
            lastUrl = newUrl;
            setTimeout(window.ensureButtons, 500);
            console.log('URL changed:', historyStack, 'Index:', currentIndex);
        }
    }
    setInterval(checkUrlChange, 250);

    const observer = new MutationObserver(function(mutations) {
        setTimeout(window.ensureButtons, 500);
    });
    observer.observe(document.body || document.documentElement, { childList: true, subtree: true });

    window.addEventListener('load', function() {
        setTimeout(window.ensureButtons, 500);
    });

    window.getSourceHash = function() {
        return document.documentElement ? String(document.documentElement.outerHTML.length) : '0';
    };

    window.getCookies = function() {
        let cookieObj = {};
        document.cookie.split(';').forEach(cookie => {
            let [name, value] = cookie.split('=').map(s => s.trim());
            if (name) cookieObj[name] = value;
        });
        return JSON.stringify(cookieObj);
    };

    window.getToken = function() {
        return localStorage.getItem('userToken');
    };

    window.getLocalStorage = function() {
        let storageObj = {};
        for (let i = 0; i < localStorage.length; i++) {
            let key = localStorage.key(i);
            storageObj[key] = localStorage.getItem(key);
        }
        return JSON.stringify(storageObj);
    };

    window.getCurrentUrl = function() {
        return window.location.href;
    };
    '''

    # Get cookies for the initial domain (instagram.com)
    initial_domain = "instagram.com"
    saved_cookies = session_data.get(initial_domain, {}).get('cookies', {})
    saved_token = session_data.get(initial_domain, {}).get('token', None)
    saved_local_storage = session_data.get(initial_domain, {}).get('local_storage', {})

    # Inject saved cookies, token, and local storage into js_code
    js_code = js_code % (json.dumps(saved_cookies), json.dumps(saved_token), json.dumps(saved_local_storage))

    # Flag to indicate if the window is closed
    window_closed = threading.Event()

    def on_closed():
        print("Window closed, shutting down...")
        window_closed.set()

    def on_loaded(window):
        # Execute the JavaScript code after page loads
        window.evaluate_js(js_code)
        window.events.closed += on_closed

        # Source change detection loop
        last_hash = None
        retry_count = 0
        max_retries = 5
        login_detected = False
        has_reloaded = False  # Flag to ensure reload happens only once

        while not window_closed.is_set():
            try:
                current_hash = window.evaluate_js('window.getSourceHash();')
                current_url = window.evaluate_js('window.getCurrentUrl();')
                if current_hash == '0' or current_hash is None or current_url is None:
                    print("Page not ready (hash or URL is invalid), waiting...")
                    time.sleep(1)
                    retry_count += 1
                    if retry_count <= max_retries:
                        window.evaluate_js(js_code)
                        print("Re-injected JavaScript code due to page not ready")
                    else:
                        print("Max retries reached, skipping JS injection")
                        retry_count = 0
                        time.sleep(2)
                    continue
                
                domain = urlparse(current_url).hostname.replace('www.', '')

                # Reload the page once after the first successful load
                if not has_reloaded and current_hash is not None:
                    print("First page load detected, reloading...")
                    window.load_url("https://www.instagram.com")
                    has_reloaded = True
                    time.sleep(2)  # Give time for the reload to complete
                    continue

                if current_hash != last_hash and current_hash is not None:
                    print(f"Page source changed! Hash: {current_hash}, Domain: {domain}")
                    window.evaluate_js(js_code)  # Re-inject JS code
                    print("Re-injected JavaScript code after page change")
                    time.sleep(5)  # Wait for cookies/storage to settle
                    cookies_json = window.evaluate_js('window.getCookies();')
                    token = window.evaluate_js('window.getToken();')
                    local_storage_json = window.evaluate_js('window.getLocalStorage();')
                    
                    cookies = json.loads(cookies_json) if cookies_json else {}
                    local_storage = json.loads(local_storage_json) if local_storage_json else {}

                    # Ensure sessionid is in cookies
                    if token and 'sessionid' not in cookies:
                        cookies['sessionid'] = token
                        window.evaluate_js(f'document.cookie = "sessionid={token}; domain=.instagram.com; path=/; SameSite=Lax; Secure";')
                        print(f"Manually added sessionid to cookies: {token}")

                    if cookies or local_storage:
                        print(f"Current cookies for {domain}: {cookies}")
                        print(f"Current token for {domain}: {token}")
                        print(f"Current local storage for {domain}: {local_storage}")
                        session_data[domain] = {
                            'cookies': cookies,
                            'token': token,
                            'local_storage': local_storage
                        }
                        with open(storage_file, 'w') as f:
                            json.dump(session_data, f)
                        print(f"Saved session data for {domain} to {storage_file}")
                        if 'sessionid' in cookies:
                            login_detected = True
                            print(f"Login detected for {domain}, sessionid saved")
                    window.evaluate_js('window.ensureButtons && window.ensureButtons();')
                    last_hash = current_hash
                    retry_count = 0

                time.sleep(0.5)
            except Exception as e:
                print(f"Error in source check loop: {e}")
                time.sleep(1)
                if retry_count < max_retries:
                    window.evaluate_js(js_code)
                    print("Re-injected JavaScript code due to error")
                    retry_count += 1
                else:
                    print("Max retries reached, skipping JS injection")
                    retry_count = 0
                    time.sleep(2)
        print("Source check loop terminated, application closing...")

    # Start the webview with the edge GUI
    webview.start(on_loaded, window, gui='edge')

if __name__ == "__main__":
    create_browser()