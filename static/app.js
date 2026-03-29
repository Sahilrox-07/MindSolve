let timeout = null;

document.addEventListener("DOMContentLoaded", function () {

    const searchBar = document.getElementById("searchBar");
    const resultsBox = document.getElementById("searchResultsBox");
    const resultsList = document.getElementById("searchResults");
    const submitBtn = document.getElementById("submitBtn");

    submitBtn.addEventListener("click", submitProblem);

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

                        const input = document.getElementById("problemInput");
                        input.value = item;
                        input.focus();

                        resultsBox.style.display = "none";
                    };

                    resultsList.appendChild(li);
                });

            } catch (err) {
                console.error(err);
                resultsList.innerHTML = "<li>Error loading results</li>";
            }

        }, 300);
    });

    // Close search dropdown when clicking outside
    document.addEventListener("click", function (e) {
        if (!resultsBox.contains(e.target) && e.target !== searchBar) {
            resultsBox.style.display = "none";
        }
    });

});


// 🔥 SUBMIT WITH ANIMATION
async function submitProblem() {

    const input = document.getElementById("problemInput");
    const message = document.getElementById("message");
    const suggestions = document.getElementById("suggestions");
    const similar = document.getElementById("similarProblems");
    const feed = document.getElementById("problemFeed");

    const text = input.value.trim();
    if (!text) return;

    // Show animation
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

        const li = document.createElement("li");
        li.innerText = text;
        feed.prepend(li);

        while (feed.children.length > 10) {
            feed.removeChild(feed.lastChild);
        }

        input.value = "";

        // Remove animation
        message.innerText = "";
        message.classList.remove("loading");

    } catch (err) {
        console.error(err);
        message.innerText = "Server error. Try again.";
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

    try {
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
                document.getElementById("problemInput").value = problem;
                submitProblem();
            };

            subList.appendChild(li);
        });

    } catch (err) {
        console.error(err);
    }
}