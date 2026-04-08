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

                if (!data.results.length || !data.results.length) {
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

        setTimeout(() => {
            message.innerText = "";
        }, 800);

// suggestions
        data.suggestions.forEach(s => {
            const li = document.createElement("li");
            li.innerText = s;
            li.style.whiteSpace = "pre-line";
            li.style.marginBottom = "10px";
            li.classList.add("fade-in");
            suggestions.appendChild(li);
        });

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

        message.innerText = "Done";

    } catch (err) {
        message.innerText = "Error processing problem";
        console.error(err);
    }
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

// CATEGORY (FIXED)
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

    } catch (err) {
        console.error(err);
    }
}