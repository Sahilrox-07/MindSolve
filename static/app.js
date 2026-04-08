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

                if (!res.ok) throw new Error();

                const data = await res.json();

                resultsList.innerHTML = "";

                if (!data.results || !data.results.length) {
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

            } catch {
                resultsList.innerHTML = "<li>Error</li>";
            }

        }, 300);
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

        if (!res.ok) throw new Error();

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

        // memory
        const memoryList = document.getElementById("memoryList");
        if (memoryList && data.history) {
            memoryList.innerHTML = "";

            data.history.forEach(item => {
                const li = document.createElement("li");
                li.innerText = item;

                li.onclick = () => {
                    input.value = item;
                    submitProblem();
                };

                memoryList.appendChild(li);
            });
        }

        loadRecent();
        loadTrending();

        setTimeout(() => {
            message.innerText = "";
        }, 800);

    } catch {
        message.innerText = "Server error";
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

        if (!res.ok) throw new Error();

        const data = await res.json();

        subList.innerHTML = "";

        (data.problems || []).slice(0, 3).forEach(problem => {
            const li = document.createElement("li");
            li.innerText = problem;
            li.classList.add("fade-in");

            li.onclick = (e) => {
                e.stopPropagation();
                document.getElementById("problemInput").value = problem;
                submitProblem();
            };

            subList.appendChild(li);
        });

    } catch {}
}