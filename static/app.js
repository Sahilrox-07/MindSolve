let timeout = null;

document.addEventListener("DOMContentLoaded", function () {

    const searchBar = document.getElementById("searchBar");
    const resultsBox = document.getElementById("searchResultsBox");
    const resultsList = document.getElementById("searchResults");
    const submitBtn = document.getElementById("submitBtn");

    submitBtn.addEventListener("click", submitProblem);

    // 🔥 LOAD RECENT FROM MONGO
    loadRecent();

    // 🔍 SEARCH
    searchBar.addEventListener("input", function () {

        const query = this.value.trim().toLowerCase();
        clearTimeout(timeout);

        timeout = setTimeout(async () => {

            if (query.length < 2) {
                resultsBox.style.display = "none";
                resultsList.innerHTML = "";
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

                if (!data.results.length) {
                    resultsList.innerHTML = "<li>No results</li>";
                    return;
                }

                data.results.forEach(item => {
                    const li = document.createElement("li");
                    li.innerText = item;

                    li.onclick = () => {
                        searchBar.value = item;
                        document.getElementById("problemInput").value = item;
                        resultsBox.style.display = "none";
                    };

                    resultsList.appendChild(li);
                });

            } catch (err) {
                console.error(err);
                resultsList.innerHTML = "<li>Error</li>";
            }

        }, 300);
    });

    // CLOSE SEARCH
    document.addEventListener("click", function (e) {
        if (!resultsBox.contains(e.target) && e.target !== searchBar) {
            resultsBox.style.display = "none";
        }
    });

    // CLOSE SIDEBAR
    document.addEventListener("click", function (e) {
        if (!e.target.closest(".sidebar")) {
            document.querySelectorAll(".sidebar li").forEach(li => {
                li.classList.remove("active");
                const sub = li.querySelector(".sub-list");
                if (sub) sub.innerHTML = "";
            });
        }
    });

});


// 🧠 LOAD RECENT
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

    } catch (err) {
        console.error(err);
    }
}


// 🔥 SUBMIT
async function submitProblem() {

    const input = document.getElementById("problemInput");
    const message = document.getElementById("message");
    const suggestions = document.getElementById("suggestions");
    const similar = document.getElementById("similarProblems");

    const text = input.value.trim();
    if (!text) return;

    message.innerText = "Processing";
    message.classList.add("loading");

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
            suggestions.appendChild(li);
        });

        data.similar.forEach(s => {
            const li = document.createElement("li");
            li.innerText = s;
            similar.appendChild(li);
        });

        input.value = "";
        loadRecent();

        message.innerText = "";
        message.classList.remove("loading");

    } catch (err) {
        console.error(err);
        message.innerText = "Server error";
        message.classList.remove("loading");
    }
}


// 📂 CATEGORY
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

    const res = await fetch("/category", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ category })
    });

    const data = await res.json();
    subList.innerHTML = "";

    data.problems.slice(0, 3).forEach(problem => {
        const li = document.createElement("li");
        li.innerText = problem;

        li.onclick = (e) => {
            e.stopPropagation();

            document.querySelectorAll(".sub-list li").forEach(el => {
                el.classList.remove("active-item");
            });

            li.classList.add("active-item");

            document.getElementById("problemInput").value = problem;
            submitProblem();

            setTimeout(() => {
                document.querySelectorAll(".sidebar li").forEach(li => {
                    li.classList.remove("active");
                    const ul = li.querySelector(".sub-list");
                    if (ul) ul.innerHTML = "";
                });
            }, 200);
        };

        subList.appendChild(li);
    });
}