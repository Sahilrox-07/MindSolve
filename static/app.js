let timeout = null;
let controller = null;

document.addEventListener("DOMContentLoaded", () => {

    const searchBar = document.getElementById("searchBar");
    const resultsBox = document.getElementById("searchResultsBox");
    const resultsList = document.getElementById("searchResults");

    document.getElementById("submitBtn").addEventListener("click", submitProblem);

    loadRecent();
    loadTrending();

    // SEARCH
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
                        document.getElementById("problemInput").value = item;
                        resultsBox.style.display = "none";
                    };

                    resultsList.appendChild(li);
                });

            } catch {}
        }, 300);
    });

    // ENTER SUPPORT
    searchBar.addEventListener("keydown", e => {
        if (e.key === "Enter") {
            e.preventDefault();
            const first = document.querySelector("#searchResults li");
            if (first) first.click();
        }
    });

    document.getElementById("problemInput")
    .addEventListener("keydown", e => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submitProblem();
        }
    });

});


// =========================
// SUBMIT
// =========================
async function submitProblem() {

    const input = document.getElementById("problemInput");
    const message = document.getElementById("message");
    const suggestions = document.getElementById("suggestions");
    const similar = document.getElementById("similarProblems");

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

        data.suggestions.forEach(s => {
            const li = document.createElement("li");
            li.innerText = s;
            li.style.whiteSpace = "pre-line";
            li.style.marginBottom = "10px";
            suggestions.appendChild(li);
        });

        (data.similar || []).forEach(s => {
            const li = document.createElement("li");
            li.innerText = s;
            similar.appendChild(li);
        });

        input.value = "";
        loadRecent();
        loadTrending();

    } catch {
        message.innerText = "Server error";
    }

    message.innerText = "";
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
            feed.appendChild(li);
        });

    } catch {}
}


// =========================
// TRENDING
// =========================
async function loadTrending() {
    try {
        const res = await fetch("/trending");
        const data = await res.json();

        const list = document.getElementById("trendingList");
        if (!list) return;

        list.innerHTML = "";

        data.trending.forEach(t => {
            const li = document.createElement("li");
            li.innerText = t;
            list.appendChild(li);
        });

    } catch {}
}