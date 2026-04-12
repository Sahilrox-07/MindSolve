let timeout = null;
let controller = null;
let isProcessing = false;

// =========================
// INIT
// =========================
document.addEventListener("DOMContentLoaded", () => {

    const searchBar = document.getElementById("searchBar");
    const resultsBox = document.getElementById("searchResultsBox");
    const resultsList = document.getElementById("searchResults");

    const problemInput = document.getElementById("problemInput");
    const clearBtn = document.getElementById("clearBtn");
    const submitBtn = document.getElementById("submitBtn");
    const feedbackBtn = document.getElementById("sendFeedbackBtn");

    // ENTER KEY SUBMIT
    problemInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submitProblem();
        }
    });

    // SIDEBAR FIX
    document.querySelectorAll(".sidebar li").forEach(li => {
        li.addEventListener("click", function () {
            const category = this.dataset.category;
            if (category) toggleCategory(this, category);
        });
    });

    // CLEAR BUTTON
    clearBtn.addEventListener("click", () => {
        problemInput.value = "";
        resetUI();
    });

    // SUBMIT BUTTON
    submitBtn.addEventListener("click", submitProblem);

    // FEEDBACK
    if (feedbackBtn) {
        feedbackBtn.addEventListener("click", sendFeedback);
    }

    // LIVE SEARCH
    searchBar.addEventListener("input", function () {

        const query = this.value.trim();
        clearTimeout(timeout);

        if (query.length < 2) {
            resultsBox.style.display = "none";
            return;
        }

        resultsBox.style.display = "block";
        resultsList.innerHTML = "<li>Searching...</li>";

        timeout = setTimeout(async () => {

            if (controller) controller.abort();
            controller = new AbortController();

            try {
                const res = await fetch("/search", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ query }),
                    signal: controller.signal
                });

                if (!res.ok) throw new Error("Search failed");

                const data = await res.json();
                resultsList.innerHTML = "";

                if (!data.results.length) {
                    resultsList.innerHTML = "<li>No results</li>";
                    return;
                }

                data.results.forEach(item => {
                    const li = document.createElement("li");
                    li.innerText = item;

                    li.onclick = () => {
                        problemInput.value = item;
                        resultsBox.style.display = "none";
                        submitProblem();
                    };

                    resultsList.appendChild(li);
                });

            } catch (err) {
                if (err.name !== "AbortError") {
                    resultsList.innerHTML = "<li>Error</li>";
                }
            }

        }, 400);
    });

    // CLICK OUTSIDE FIX
    document.addEventListener("click", (e) => {

        if (!e.target.closest(".search-container")) {
            resultsBox.style.display = "none";
        }

        if (!e.target.closest(".sidebar")) {
            document.querySelectorAll(".sidebar li").forEach(li => {
                li.classList.remove("active");
                const ul = li.querySelector(".sub-list");
                if (ul) ul.innerHTML = "";
            });
        }
    });

    // INITIAL LOAD
    loadRecent();
    loadTrending();
});


// =========================
// RESET UI
// =========================
function resetUI() {
    document.getElementById("suggestions").innerHTML = "";
    document.getElementById("similarProblems").innerHTML = "";
    document.getElementById("feedbackBox").classList.add("hidden");
    document.getElementById("message").innerText = "";
}


// =========================
// SUBMIT PROBLEM
// =========================
async function submitProblem() {

    const input = document.getElementById("problemInput");
    const message = document.getElementById("message");
    const suggestions = document.getElementById("suggestions");
    const similar = document.getElementById("similarProblems");
    const feedbackBox = document.getElementById("feedbackBox");
    const submitBtn = document.getElementById("submitBtn");

    const text = input.value.trim();
    if (!text) return;

    if (isProcessing) {
        message.innerText = "Please wait...";
        return;
    }

    resetUI();

    isProcessing = true;
    submitBtn.disabled = true;
    submitBtn.innerText = "Processing...";
    message.innerText = "Processing...";

    try {
        const res = await fetch("/problem", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ text })
        });

        if (!res.ok) throw new Error("Server error");

        const data = await res.json();
        const type = data.type || "normal";

        // FEEDBACK VISIBILITY
        if (type === "normal") {
            feedbackBox.classList.remove("hidden");
            loadFeedbackHistory();
        } else {
            feedbackBox.classList.add("hidden");
        }

        // SUGGESTIONS
        (data.suggestions || []).forEach(s => {
            const li = document.createElement("li");
            li.innerText = s;
            li.style.whiteSpace = "pre-line";
            li.classList.add("fade-in");
            suggestions.appendChild(li);
        });

        // SIMILAR
        if (data.similar && data.similar.length) {
            data.similar.forEach(s => {
                const li = document.createElement("li");
                li.innerText = s;

                li.onclick = () => {
                    input.value = s;
                    submitProblem();
                };

                similar.appendChild(li);
            });
        } else {
            similar.innerHTML = "<li>No similar problems found</li>";
        }

        message.innerText = "";

        if (type === "normal") {
            document.getElementById("suggestionsSection")
                .scrollIntoView({ behavior: "smooth" });
        }

    } catch (err) {
        message.innerText = "Something broke. Try again.";
    }

    submitBtn.disabled = false;
    submitBtn.innerText = "Submit Problem";
    isProcessing = false;
}


// =========================
// SEND FEEDBACK
// =========================
async function sendFeedback() {

    const input = document.getElementById("feedbackInput");
    const status = document.getElementById("feedbackStatus");

    const text = input.value.trim();
    if (!text) return;

    try {
        const res = await fetch("/feedback", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ feedback: text })
        });

        const data = await res.json();

        if (data.status === "ok") {
            status.innerText = "Feedback sent ✅";
            input.value = "";
            loadFeedbackHistory();
        } else {
            status.innerText = "Failed to send";
        }

    } catch {
        status.innerText = "Error sending feedback";
    }
}


// =========================
// FEEDBACK HISTORY
// =========================
async function loadFeedbackHistory() {

    try {
        const res = await fetch("/feedback/history");
        if (!res.ok) return;

        const data = await res.json();
        const list = document.getElementById("feedbackHistory");

        if (!list) return;

        list.innerHTML = "";

        (data.feedback || []).forEach(f => {
            const li = document.createElement("li");
            li.innerText = f;
            list.appendChild(li);
        });

    } catch {}
}


// =========================
// RECENT
// =========================
async function loadRecent() {

    const feed = document.getElementById("problemFeed");

    try {
        const res = await fetch("/recent");
        if (!res.ok) return;

        const data = await res.json();
        feed.innerHTML = "";

        (data.problems || []).forEach(p => {
            const li = document.createElement("li");
            li.innerText = p;

            li.onclick = () => {
                document.getElementById("problemInput").value = p;
                submitProblem();
            };

            feed.appendChild(li);
        });

    } catch {}
}


// =========================
// TRENDING
// =========================
async function loadTrending() {

    const list = document.getElementById("trendingList");

    try {
        const res = await fetch("/trending");
        if (!res.ok) return;

        const data = await res.json();
        list.innerHTML = "";

        (data.trending || []).forEach(t => {
            const li = document.createElement("li");
            li.innerText = t;

            li.onclick = () => {
                document.getElementById("problemInput").value = t;
                submitProblem();
            };

            list.appendChild(li);
        });

    } catch {}
}


// =========================
// CATEGORY
// =========================
async function toggleCategory(element, category) {

    const subList = element.querySelector(".sub-list");

    if (element.classList.contains("active")) {
        element.classList.remove("active");
        subList.innerHTML = "";
        return;
    }

    document.querySelectorAll(".sidebar li").forEach(li => {
        li.classList.remove("active");
        const ul = li.querySelector(".sub-list");
        if (ul) ul.innerHTML = "";
    });

    element.classList.add("active");

    try {
        const res = await fetch("/category", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ category })
        });

        if (!res.ok) throw new Error("Category failed");

        const data = await res.json();
        subList.innerHTML = "";

        (data.problems || []).slice(0, 3).forEach(problem => {
            const li = document.createElement("li");
            li.innerText = problem;

            li.onclick = (e) => {
                e.stopPropagation();
                document.getElementById("problemInput").value = problem;
                submitProblem();
            };

            subList.appendChild(li);
        });

    } catch {}
}