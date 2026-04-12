let timeout = null;
let controller = null;

document.addEventListener("DOMContentLoaded", () => {

    // =========================
    // ELEMENTS
    // =========================
    const searchBar = document.getElementById("searchBar");
    const resultsBox = document.getElementById("searchResultsBox");
    const resultsList = document.getElementById("searchResults");

    const problemInput = document.getElementById("problemInput");
    const suggestions = document.getElementById("suggestions");
    const similar = document.getElementById("similarProblems");

    const clearBtn = document.getElementById("clearBtn");
    const submitBtn = document.getElementById("submitBtn");
    const message = document.getElementById("message");

    // 🔥 FEEDBACK
    const feedbackBox = document.getElementById("feedbackBox");
    const feedbackInput = document.getElementById("feedbackInput");
    const sendFeedbackBtn = document.getElementById("sendFeedbackBtn");
    const feedbackStatus = document.getElementById("feedbackStatus");
    const feedbackHistory = document.getElementById("feedbackHistory");
    const btnText = document.getElementById("btnText");

    // =========================
    // ENTER KEY SUBMIT
    // =========================
    problemInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submitProblem();
        }
    });

    // =========================
    // CLEAR BUTTON
    // =========================
    clearBtn.addEventListener("click", () => {
        problemInput.value = "";
        suggestions.innerHTML = "";
        similar.innerHTML = "";
        message.innerText = "";
        feedbackBox.style.display = "none";
        resultsBox.style.display = "none";
    });

    // =========================
    // SUBMIT
    // =========================
    submitBtn.addEventListener("click", submitProblem);

    // =========================
    // LIVE SEARCH
    // =========================
    searchBar.addEventListener("input", function () {

        const query = this.value.trim();
        clearTimeout(timeout);

        timeout = setTimeout(async () => {

            if (controller) controller.abort();
            controller = new AbortController();

            if (query.length < 2) {
                resultsBox.style.display = "none";
                return;
            }

            resultsBox.style.display = "block";
            resultsList.innerHTML = "<li>Searching...</li>";

            try {
                const res = await fetch("/search", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ query }),
                    signal: controller.signal
                });

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

    // =========================
    // CLICK OUTSIDE
    // =========================
    document.addEventListener("click", (e) => {

        if (!e.target.closest(".search-container")) {
            resultsBox.style.display = "none";
        }

        document.querySelectorAll(".sidebar li").forEach(li => {
            li.classList.remove("active");
            const ul = li.querySelector(".sub-list");
            if (ul) ul.innerHTML = "";
        });

    });

    // =========================
    // FEEDBACK SYSTEM
    // =========================
    sendFeedbackBtn.addEventListener("click", async () => {

        const text = feedbackInput.value.trim();
        if (!text) return;

        sendFeedbackBtn.disabled = true;
        btnText.innerText = "Sending...";

        try {
            const res = await fetch("/feedback", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ feedback: text })
            });

            const data = await res.json();

            feedbackStatus.innerText = "Feedback sent ✅";
            feedbackStatus.style.display = "block";

            const li = document.createElement("li");
            li.innerText = text;
            feedbackHistory.prepend(li);

            feedbackInput.value = "";

        } catch {
            feedbackStatus.innerText = "Failed ❌";
        }

        sendFeedbackBtn.disabled = false;
        btnText.innerText = "Send Feedback";
    });

    // =========================
    // INITIAL LOAD
    // =========================
    loadRecent();
    loadTrending();
});


// =========================
// SUBMIT FUNCTION
// =========================
async function submitProblem() {

    const input = document.getElementById("problemInput");
    const message = document.getElementById("message");
    const suggestions = document.getElementById("suggestions");
    const similar = document.getElementById("similarProblems");
    const feedbackBox = document.getElementById("feedbackBox");

    const text = input.value.trim();
    if (!text) return;

    message.innerText = "Processing...";

    try {
        const res = await fetch("/problem", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ text })
        });

        const data = await res.json();

        suggestions.innerHTML = "";
        similar.innerHTML = "";

        // suggestions
        data.suggestions.forEach(s => {
            const li = document.createElement("li");
            li.innerText = s;
            li.style.whiteSpace = "pre-line";
            li.classList.add("fade-in");
            suggestions.appendChild(li);
        });

        // similar
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

        // 🔥 SHOW FEEDBACK IF NEGATIVE
        if (data.suggestions[0].toLowerCase().includes("sorry")) {
            feedbackBox.style.display = "block";
        } else {
            feedbackBox.style.display = "none";
        }

        // memory
        const memoryList = document.getElementById("memoryList");
        if (memoryList && data.history) {
            memoryList.innerHTML = "";

            data.history.forEach(item => {
                const li = document.createElement("li");
                li.innerText = "🧠 " + item;

                li.onclick = () => {
                    input.value = item;
                    submitProblem();
                };

                memoryList.appendChild(li);
            });
        }

        // scroll fix
        document.getElementById("suggestionsSection").scrollIntoView({
            behavior: "smooth"
        });

        setTimeout(() => message.innerText = "", 800);

    } catch {
        message.innerText = "Error";
    }
}


// =========================
// RECENT
// =========================
async function loadRecent() {
    const feed = document.getElementById("problemFeed");

    try {
        const res = await fetch("/recent");
        const data = await res.json();

        feed.innerHTML = "";

        data.problems.forEach(p => {
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
        const data = await res.json();

        list.innerHTML = "";

        data.trending.forEach(t => {
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