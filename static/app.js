document.addEventListener("DOMContentLoaded", () => {

    const searchBar = document.getElementById("searchBar");
    const resultsBox = document.getElementById("searchResultsBox");
    const resultsList = document.getElementById("searchResults");
    const problemInput = document.getElementById("problemInput");

    document.getElementById("submitBtn").addEventListener("click", submitProblem);

    loadRecent();
    loadTrending();

    // =========================
    // 🔍 LIVE SEARCH (FIXED)
    // =========================
    searchBar.addEventListener("input", async function () {

        const query = this.value.trim();

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
                body: JSON.stringify({ query })
            });

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
                    problemInput.value = item;
                    resultsBox.style.display = "none";
                };

                resultsList.appendChild(li);
            });

        } catch {
            resultsList.innerHTML = "<li>Error</li>";
        }
    });


    // =========================
    // 🧠 AUTO PROBLEM SUBMIT
    // =========================
    let typingTimer;

    problemInput.addEventListener("input", function () {

        clearTimeout(typingTimer);

        const text = this.value.trim();
        if (text.length < 5) return;

        typingTimer = setTimeout(() => {
            submitProblem();
        }, 800);
    });


    // =========================
    // ❌ AUTO CLOSE UI
    // =========================
    document.addEventListener("click", function (e) {

        if (!resultsBox.contains(e.target) && e.target !== searchBar) {
            resultsBox.style.display = "none";
        }

        document.querySelectorAll(".sidebar li").forEach(li => {
            if (!li.contains(e.target)) {
                li.classList.remove("active");
                const sub = li.querySelector(".sub-list");
                if (sub) sub.innerHTML = "";
            }
        });
    });

});


// =========================
// 🚀 SUBMIT
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

        // 💡 Suggestions
        data.suggestions.forEach(s => {
            const li = document.createElement("li");
            li.innerText = s;
            li.style.whiteSpace = "pre-line";
            li.classList.add("fade-in");
            suggestions.appendChild(li);
        });

        // 🔎 Similar Problems
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

        // 🧠 Memory
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

        input.value = "";
        loadRecent();
        loadTrending();

        setTimeout(() => message.innerText = "", 800);

    } catch {
        message.innerText = "Error";
    }
}


// =========================
// 🧾 RECENT
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
// 📈 TRENDING
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
// 📂 CATEGORY
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