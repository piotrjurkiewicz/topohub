window.addEventListener('load', (event) => {
    const menu = document.querySelectorAll(".wy-menu ul li.toctree-l1")
    for (let elem of menu) {
        if (!elem.classList.contains("current")) {
            elem.classList.add("current")
        }
    }
});
